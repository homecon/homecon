#!/usr/bin/env python3
######################################################################################
#    Copyright 2016 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import logging
import jwt
import datetime


logger = logging.getLogger('')


class Authentication(object):
    def __init__(self,database,secret,algorithm='HS256',token_exp=30*24*3600):
        """
        Parameters:
            db:             the database instance
            secret:         string
            algorithm:      string
        """

        self._db = database
        self._secret = secret
        self._algorithm = algorithm

        self._token_exp = token_exp

        # load the groups and users from the database

        self.groups = {group['groupname']: group for group in self._db.get_groups()}
        self.users = {user['username']: user for user in self._db.get_users()}
        self.group_users = {}

        for gu in self._db.get_group_users():
            try:
                self.group_users[gu['group']].append(gu['user'])
            except:
                self.group_users[gu['group']] = [ gu['user'] ]


        # add the admin group and user if they do not exist

        self.add_group('admin',permission=9)
        self.add_user('admin','homecon',permission=9)
        self.add_user_to_group(self.users['admin'],self.groups['admin'])


    def add_user(self,username,password,permission=1):
        success = self._db.add_user(username,password,permission=permission)
        
        if success:
            user = self._db.get_user(username)
            success = False
            if not user == None:
                success = True
                self.users[user['username']] = user

        return success

    def add_group(self,groupname,permission=1):
        success = self._db.add_group(groupname,permission=permission)
        
        if success:
            group = self._db.get_group(groupname)
            success = False
            if not group == None:
                success = True
                self.groups[group['groupname']] = group

        return success

    def add_user_to_group(self,user,group):
        success = self._db.add_user_to_group(user['id'],group['id'])
        if success:
            try:
                self.group_users[group['id']].append(user['id'])
            except:
                self.group_users[group['id']] = [user['id']]

        return success

    def request_token(self,username,password):
        user = self._db.verify_user(username,password)
        
        if user:
            # return the token
            iat = datetime.datetime.utcnow()
            exp = iat + datetime.timedelta(seconds=self._token_exp)

            payload = {'id': user[0], 'username':user[1], 'permission':user[2], 'exp':exp, 'iat':iat}

            return self._encode(payload)
        else:
            return False

    def renew_token(self,token):

        payload = self._decode(token)
        
        if payload:
            # return a new token
            iat = datetime.datetime.utcnow()
            exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._token_exp)

            payload['exp'] = exp

            return self._encode(payload)
        else:
            return False

    def check_token(self,token):
        return self._decode(token)

    def _encode(self,payload):
        """
        Parameters:
            payload:        dict
        """
        return jwt.encode(payload, self._secret, self._algorithm).decode('utf-8')

    def _decode(self,token):
        """
        Parameters:
            token:          string
        """
        try:
            return jwt.decode(token.encode('utf-8'), self._secret, algorithms=[self._algorithm])
        except:
            return False



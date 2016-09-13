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
    def __init__(self,database,secret,algorithm='HS256',token_exp=7*24*3600):
        """

        Parameters
        ----------
            database : database object
                the homecon database instance

            secret : string
                the secret key used to encode json web tokens signatures

            algorithm: string
                the algorithm used to encode json web tokens signatures

            token_exp: number
                duration of validity of supplied tokens in seconds
        """

        self._db = database
        self._secret = secret
        self._algorithm = algorithm

        self._token_exp = token_exp

        # load the groups and users from the database
        self.groups = {group['id']: group for group in self._db.groups_GET()}
        self.users = {user['id']: user for user in self._db.users_GET()}

        self.usernames = {user['username']: user['id'] for key,user in self.users.items()}
        self.groupnames = {group['groupname']: group['id'] for key,group in self.groups.items()}

        # initialize dictionaries with the users in a group and the groups a user is in
        self.group_users = {}
        for group in self.groups:
            self.group_users[group] = []

        self.user_groups = {}
        for user in self.users:
            self.user_groups[user] = []

        for gu in self._db.group_users_GET():
            self.group_users[gu['group']].append(gu['user'])
            self.user_groups[gu['user']].append(gu['group'])
            

        # add the admin group and user if they do not exist
        self.add_group('admin',permission=9)
        self.add_user('admin','homecon',permission=9)
        self.add_user_to_group(self.users[self.usernames['admin']],self.groups[self.groupnames['admin']])

        # add the default group and add the admin user to it
        self.add_group('default',permission=1)
        self.add_user_to_group(self.users[self.usernames['admin']],self.groups[self.groupnames['default']])



        # create a dict of websocket commands
        self.ws_commands = {
            'register': self._ws_register,
            'add_user': self._ws_add_user,
            'update_user_permission': self._ws_update_user_permission,
            'request_token': self._ws_request_token,
            'authenticate': self._ws_authenticate,
        }


    def add_user(self,username,password,permission=0):
        success = self._db.users_POST(username=username,password=password,permission=permission)
        
        if success:
            user = self._db.users_GET(username=username)

            if not user == None:
                self.users[user['id']] = user
                self.usernames[user['username']] = user['id']
                self.user_groups[user['id']] = []

                return user

        return False


    def update_user(self,**kwargs):
        success = self._db.users_PUT(**kwargs)

        if success:
            # update the local user reference
            user = self._db.users_GET(**kwargs)
            self.users[user['id']] = user

        return success


    def add_group(self,groupname,permission=1):
        success = self._db.groups_POST(groupname=groupname,permission=permission)
        
        if success:
            group = self._db.groups_GET(groupname=groupname)

            success = False
            if not group == None:
                success = True

                self.groups[group['id']] = group
                self.groupnames[group['groupname']] = group['id']
                self.group_users[group['id']] = []

                return group

        return False

    def add_user_to_group(self,user,group):
        success = self._db.group_users_POST(user['id'],group['id'])
        if success:
            self.group_users[group['id']].append(user['id'])
            self.user_groups[user['id']].append(group['id'])

        return success

    def get_user_permission(self,user):
        
        user_permission = self.users[user['id']]['permission']

        groups = self.user_groups[user['id']]
        try:
            group_permission = max([self.groups[groupid]['permission'] for groupid in groups])
        except:
            group_permission = 0

        return max( user_permission,group_permission )

    def request_token(self,username,password):
        user = self._db.users_VERIFY(username,password)

        if user:
            # return the token
            iat = datetime.datetime.utcnow()
            exp = iat + datetime.timedelta(seconds=self._token_exp)

            payload = {'userid': user['id'], 'groupids': self.user_groups[user['id']], 'username':user['username'], 'permission':self.get_user_permission(user), 'exp':exp, 'iat':iat}

            return self._encode(payload)

        return False

    def renew_token(self,token):

        payload = self._decode(token)
        
        if payload:
            # return a new token
            iat = datetime.datetime.utcnow()
            exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._token_exp)

            user = self._db.users_GET(id=payload['userid'])
            if not user == None:

                payload = {'userid': user['id'], 'groupids': self.user_groups[user['id']], 'username':user['username'], 'permission':self.get_user_permission(user), 'exp':exp, 'iat':iat}
                return self._encode(payload)

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


    ############################################################################
    # websocket commands
    ############################################################################
    def _ws_register(self,client,data,tokenpayload):
        """
        An aspirant user can register themselves but recieve permission 0.
        An admin must verify the user
        """

        if data['password']==data['repeatpassword']:

            user = self.add_user(data['username'],data['password'],permission=0)

            if not user==False:
                logger.debug("Client {0} registerd as {1}".format(client.addr,user))
                return {'cmd':'register', 'user':user}

        logger.debug("Client {0} tried to register with username {1}".format(client.addr,data['username']))
        return {'cmd':'register', 'user':None}

    def _ws_add_user(self,client,data,tokenpayload):
        """
        An admin can add users with permission 1
        """

        success = False

        if tokenpayload and self.get_user_permission(tokenpayload['userid'])>=9:
            if data['password']==data['repeatpassword']:

                success = self.add_user(data['username'],data['password'],permission=1)

                if not user==False:
                    success = self.add_user_to_group(self.users[self.usernames[data['username']]],self.groups[self.groupnames['default']])
                
        if success:
            logger.debug("Client {0} added a user {1}".format(client.addr,user))
            return {'cmd':'add_user', 'user':user}
        else:
            logger.debug("Client {0} tried to add a user".format(client.addr))
            return {'cmd':'add_user', 'user':None}


    def _ws_update_user_permission(self,client,data,tokenpayload):
        """
        An admin can change the users permission. You can not change your own permissions
        """

        success = False
        if tokenpayload and self.get_user_permission(self.users[tokenpayload['userid']])>=9 and 'id' in data and 'permission' in data and not data['id']==tokenpayload['userid']:

            success = self.update_user(id=data['id'],permission=data['permission'])

        if success:
            logger.debug("Client {0} updated user with id {1}".format(client.addr,data['id']))
            return {'cmd':'update_user_permission', 'permission':data['permission']}
        else:
            logger.debug("Client {0} tried to update a user".format(client.addr))
            return {'cmd':'update_user_permission', 'permission':False}


    def _ws_request_token(self,client,data,tokenpayload):
        """
        a client must request a token using their username and password
        """

        token = self.request_token(data['username'],data['password'])

        logger.debug("Client {0} recieved a token".format(client.addr))
        return {'cmd': 'request_token', 'token': token}


    def _ws_authenticate(self,client,data,tokenpayload):
        """
        a client must supply a token to smarthome to recieve incomming messages
        """
        success = False

        if tokenpayload and self.get_user_permission(self.users[tokenpayload['userid']]) >=1:
            client.user = tokenpayload
            logger.debug("Client {0} authenticated with a valid token".format(client.addr))
            success = True

        else:
            logger.debug("Client {0} tried to authenticate with an invalid token".format(client.addr))

        
        return {'cmd':'authenticate', 'val': success}



    




#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import passlib.hash
import jwt

from . import database
from .plugin import BasePlugin
from . import config



jwt_algorithm = 'HS256'

def jwt_encode(payload):
    """
    Parameters
    ----------
    payload : dict
        a payload dictionary

    Returns
    -------
    a JSON web token

    """

    return jwt.encode(payload, config.jwt_secret, jwt_algorithm).decode('utf-8')


def jwt_decode(token):
    """
    Checks if a token is valid
    
    Parameters
    ----------
    token : string
        a jwt

    Returns
    -------
    the token payload or False

    """

    try:
        return jwt.decode(token.encode('utf-8'), config.jwt_secret, algorithms=[jwt_algorithm])
    except:
        return False




class Authentication(BasePlugin):
    """
    Authentication class

    All permissions are built up like the unix permission numbers using 3 bits:

    :code::
        read / write / change
          4      2        1

        0-3: no permissions
        4 : read
        5 : read + change
        6 : read + write
        7 : read + write + change

    read allows a user to read the value, write allows the user to change the
    value and change allows a user to change configuration parameters

    """

    def initialize(self):
        """
        Initialize the authentication module
        """
        # create database tables
        self._db = database.Database(database='homecon.db')
        self._db_users = database.Table(self._db,'users',[
            {'name':'username',      'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'password',      'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'permission',    'type':'int(2)',     'null': '',  'default':'',  'unique':''},
        ])

        self._db_groups = database.Table(self._db,'groups',[
            {'name':'groupname',     'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'permission',    'type':'int(2)',   'null': '',  'default':'',  'unique':''},
        ])
        self._db_group_users = database.Table(self._db,'group_users',[
            {'name':'group',    'type':'int(8)',   'null': '',  'default':'',  'unique':''},
            {'name':'user',     'type':'int(8)',   'null': '',  'default':'',  'unique':''},
        ])
        

        self._token_exp = 7*24*3600


        # load the groups and users from the database
        self.users = {user['id']: user for user in self._db_users.GET()}#columns=['id','username','permission']
        self.groups = {group['id']: group for group in self._db_groups.GET()}#columns=['id','groupname','permission']
        
        self.usernames = {user['username']: user['id'] for user in self.users.values()}
        self.groupnames = {group['groupname']: group['id'] for group in self.groups.values()}

        # initialize dictionaries with the users in a group and the groups a user is in
        self.group_users = {}
        for group in self.groups:
            self.group_users[group] = []

        self.user_groups = {}
        for user in self.users:
            self.user_groups[user] = []

        for gu in self._db_group_users.GET():
            self.group_users[gu['group']].append(gu['user'])
            self.user_groups[gu['user']].append(gu['group'])
            

        # create admin and default groups
        self.add_group('admin',permission=9)
        self.add_group('default',permission=1)

        # add the admin user if they do not exist
        self.add_user('admin','homecon',permission=9)
        self.add_user_to_group(self.usernames['admin'],self.groupnames['default'])
        self.add_user_to_group(self.usernames['admin'],self.groupnames['admin'])

      

    def add_user(self,username,password,permission):
        """
        add a user

        Parameters
        ----------
        username : string
            the users username
        
        password : string
            the users password, unhashed
        
        permission : int
            the users permission

        Returns
        -------
        a user dictionary or False
        """

        if not username in [user['username'] for user in self.users.values()]:
            passwordhash = self.encrypt_password(password)
            self._db_users.POST(username=username,password=passwordhash,permission=permission)
            user = self._db_users.GET(columns=['id','username','permission'],order='id',desc=True,limit=1)[0]

            # add the user to the several lists
            self.users[user['id']] = user
            self.usernames[user['username']] = user['id']
            self.user_groups[user['id']] = []

            return user

        else:
            return False



    def add_group(self,groupname,permission):
        """
        Add a group

        Parameters
        ----------
        groupname : string
            the group groupname

        permission : int
            the group permission

        Returns
        -------
        a group dictionary or False

        """

        if not groupname in [group['groupname'] for group in self.groups.values()]:
            self._db_groups.POST(groupname=groupname,permission=permission)
            group = self._db_groups.GET(columns=['id','groupname','permission'],order='id',desc=True,limit=1)[0]

            # add the groups to the groupslist
            self.groups[group['id']] = group
            self.groupnames[group['groupname']] = group['id']
            self.group_users[group['id']] = []

            return group

        else:
            return False


    def add_user_to_group(self,userid,groupid):
        """
        Add a a user to a group

        Parameters
        ----------
        userid : int
            the id of a user

        groupid : int
            the id of a group

        Returns
        -------
        True or False
        """

        if not groupid in self.user_groups[userid]:
            self._db_group_users.POST(user=userid,group=groupid)
            self.group_users[groupid].append(self.users[userid])
            self.user_groups[userid].append(self.groups[groupid])

            return True

        else:
            return False

    def user_permission(self,userid):
        """
        returns the maximum user permission based on the user and the groups the
        user is in

        Parameters
        ----------
        userid : int
            the id of a user

        Returns
        -------
        a permission number

        """

        user_permission = self.users[userid]['permission']

        groups = self.user_groups[userid]
        try:
            group_permission = max([self.groups[groupid]['permission'] for group in groups.values])
        except:
            group_permission = 0

        return max( user_permission,group_permission )


    def request_token(self,username,password):
        """
        Request a token with a username, password combination

        Parameters
        ----------
        payload : dict
            a payload dictionary

        Returns
        -------
        a JSON web token of False

        """

        user = self.verify_user(username,password)

        if user:
            # return the token
            iat = datetime.datetime.utcnow()
            exp = iat + datetime.timedelta(seconds=self._token_exp)

            groupids = [groupid for groupid in self.user_groups[user['id']]]
            payload = {'userid': user['id'], 'groupids': groupids, 'username':user['username'], 'permission':self.user_permission(user['id']), 'exp':exp, 'iat':iat}

            return jwt_encode(payload)

        return False

    def renew_token(self,token):
        """
        Renew a token using an old token

        Parameters
        ----------
        payload : dict
            a payload dictionary

        Returns
        -------
        a JSON web token of False

        """

        payload = jwt_decode(token)
        
        if payload:
            # return a new token
            iat = datetime.datetime.utcnow()
            exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._token_exp)

            users = self._db_users.GET(id=payload['userid'])
            if len(users)==1:
                user = users[0]
                payload = {'userid': user['id'], 'groupids': self.user_groups[user['id']], 'username':user['username'], 'permission':self.user_permission(user), 'exp':exp, 'iat':iat}
                return jwt_encode(payload)

        return False






    def encrypt_password(self,password):
        return passlib.hash.pbkdf2_sha256.encrypt(password, rounds=10, salt_size=16)


    def verify_password(self,password,hash):
        return passlib.hash.pbkdf2_sha256.verify(password, hash)


    def verify_user(self,username,password):
        """
        verify a username - password combination

        Parameters
        ----------
        username : string
            the username

        password : string
            the password, unhashed

        """
        result = False
        users = self._db_users.GET(columns=['id','username','password','permission'],username=username)


        if len(users) == 1:
            user = users[0]
            if self.verify_password(password, user['password']):
                result = {'id':user['id'],'username':user['username'],'permission':user['permission']}
            else:
                logging.warning('Failed login attempt detected for user {}'.format(username))
                result = False
        else:
            logging.warning('User {} does not exist'.format(username))
            result = False

        return result
        

    def listen_register(self,event):
        user = self.add_user(event.data['username'],event.data['password'],0)
        if user:
            pass


    def listen_add_user(self,event):
        user = self.add_user(event.data['username'],event.data['password'],event.data['permission'])
        if user:
            # add the user to the default user group
            self.add_user_to_group(user['id'],self.groupnames['default'])


    def listen_add_group(self,event):
        group = self.add_group(event.data['groupname'],event.data['permission'])
        if group:
            pass


    def listen_add_user_to_group(self,event):
        success = self.add_user_to_group(event.data['userid'],event.data['groupid'])
        if success:
            pass


    def listen_request_token(self,event):
        token = self.request_token(event.data['username'],event.data['password'])
        if token:
            self.fire('send_to',{'event':'request_token', 'token':token, 'clients':[event.client]})


    def listen_renew_token(self,event):
        token = self.renew_token(event.data['token'])
        if token:
            self.fire('send_to',{'event':'renew_token', 'token':token,'clients':[event.client]})


    def listen_authenticate(self,event):
        payload = jwt_decode(event.data['token'])
        if payload:
            event.client.tokenpayload = payload
            self.fire('send_to',{'event':'authenticate', 'authenticated':True, 'clients':[event.client]})



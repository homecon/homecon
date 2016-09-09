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
import pymysql
import datetime
import json
from passlib.hash import pbkdf2_sha256


logger = logging.getLogger('')

class Mysql(object):
    """
    low level database functions
    """

    def __init__(self,db_name,db_user,db_pass):
        """
        A mysql object is created
        and mysql tables required for homecon are created
        
        Parameters:
            db_name       database name
            db_user       database user
            db_pass       database user password
        """

        self._db_name = db_name
        self._db_user = db_user
        self._db_pass = db_pass

        # perpare the database
        con,cur = self._create_cursor()
        
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS settings (id int(11) NOT NULL AUTO_INCREMENT,setting varchar(255)  NOT NULL,value varchar(255) NOT NULL,PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS groups (id int(11) NOT NULL AUTO_INCREMENT,groupname varchar(255) NOT NULL,permission tinyint(4) NOT NULL DEFAULT \'1\',PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS users (id int(11) NOT NULL AUTO_INCREMENT,username varchar(255) NOT NULL,password varchar(255) NOT NULL,permission tinyint(4) NOT NULL DEFAULT \'1\',PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS group_users (id int(11) NOT NULL AUTO_INCREMENT,`group` int(11) NOT NULL,user int(11) NOT NULL,PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS items (id int(11) NOT NULL AUTO_INCREMENT,path varchar(255) NOT NULL,conf varchar(255),persist tinyint(4) NOT NULL DEFAULT \'1\',label varchar(63),description varchar(255),unit varchar(63),PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        

        # set location data
        #query = "UPDATE data SET latitude=%f,longitude=%f,elevation=%f WHERE id=1" % (float(self._sh._lat),float(self._sh._lon),float(self._sh._elev))
        #try:
        #    cur.execute( query )
        #except:
        #    logger.warning("Could not add location to database")


        con.commit()    
        con.close()
        logger.info("HomeCon database initialized")


################################################################################
# users
################################################################################
    def user_POST(self,**kwargs):
        """
        post to the users table
        """
        success = False

        if 'username' in kwargs and 'password' in kwargs and 'permission' in kwargs:
            con,cur = self._create_cursor()
            self._execute_query(cur,'SELECT * FROM users WHERE username=%s', (kwargs['username'],))
            if cur.fetchone() == None:
                self._execute_query(cur,'INSERT INTO users (username,password,permission) VALUES (%s,%s,%s)', (kwargs['username'],self.encrypt_password(kwargs['password']),kwargs['permission'],))
                success = True
            else:
                logger.warning('username {} allready exists'.format(kwargs['username']))
                success = False

            con.commit()
            con.close()

        return success


    def user_GET(self,**kwargs):
        """
        get a user or all users
        """

        result = False
        if 'id' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,username,permission FROM users WHERE id=%s', (kwargs['id'],))
            result = cur.fetchone()
            con.commit()
            con.close()

        elif 'username' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,username,permission FROM users WHERE username=%s', (kwargs['username'],))
            result = cur.fetchone()
            con.commit()
            con.close()
        else:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,username,permission FROM users')
            result = cur.fetchall()
            con.commit()
            con.close()

        return result


    def user_PUT(self,**kwargs):
        """
        edit a user
        """
        success = False

        user = self.user_GET(**kwargs)
        if not user == None:
            fields = []
            data = [] 
            if 'username' in kwargs:
                fields.append('username')
                data.append(kwargs['username'])

            if 'password' in kwargs:
                fields.append('password')
                data.append(self.encrypt_password(kwargs['password']))

            if 'permission' in kwargs:
                fields.append('permission')
                data.append(kwargs['permission'])

            data.append(user['id'])

            con,cur = self._create_cursor()
            self._execute_query(cur,'UPDATE `users` SET {} WHERE id=%s'.format(', '.join(['{}=%s'.format(f) for f in fields])), tuple(data) )
            con.commit()
            con.close()
            success = True

        return success


    def user_DELETE(self,**kwargs):
        """
        delete a user
        """
        success = False

        user = self.user_GET(**kwargs)
        if not user == None:

            con,cur = self._create_cursor()
            self._execute_query(cur,"DELETE FROM `users` WHERE id=%s", (user['id'],))
            con.commit()
            con.close()

            success = True

        return success


    def user_VERIFY(self,username,password):
        """
        verify a username - password combination
        """
        result = False

        con,cur = self._create_dict_cursor()
        self._execute_query(cur,'SELECT id,username,permission,password FROM users WHERE username=%s', (username,))
        user = cur.fetchone()
        con.commit()
        con.close()

        if not user == None:
            
            if self.verify_password(password, user['password']):
                result = {'id':user['id'],'username':user['username'],'permission':user['permission']}
            else:
                logger.warning('Failed login attempt detected for user {}'.format(username))
                result = False
        else:
            logger.warning('User {} does not exist'.format(username))
            result = False

        return result


    def encrypt_password(self,password):
        return pbkdf2_sha256.encrypt(password, rounds=10, salt_size=16)

    def verify_password(self,password,hash):
        return pbkdf2_sha256.verify(password, hash)


################################################################################
# groups
################################################################################
    def group_POST(self,**kwargs):
        """
        post to the groups table
        """
        success = False

        if 'groupname' in kwargs and 'permission' in kwargs:
            con,cur = self._create_cursor()
            self._execute_query(cur,'SELECT * FROM groups WHERE groupname=%s', (kwargs['groupname'],))
            if cur.fetchone() == None:
                self._execute_query(cur,'INSERT INTO groups (groupname,permission) VALUES (%s,%s)', (kwargs['groupname'],kwargs['permission'],))
                success = True
            else:
                logger.warning('groupname {} allready exists'.format(kwargs['groupname']))
                success = False

            con.commit()
            con.close()

        return success


    def group_GET(self,**kwargs):
        """
        get a group or all groups
        """

        result = False
        if 'id' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,groupname,permission FROM groups WHERE id=%s', (kwargs['id'],))
            result = cur.fetchone()
            con.commit()
            con.close()

        elif 'username' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,groupname,permission FROM groups WHERE groupname=%s', (kwargs['groupname'],))
            result = cur.fetchone()
            con.commit()
            con.close()
        else:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,groupname,permission FROM groups')
            result = cur.fetchall()
            con.commit()
            con.close()

        return result


    def group_PUT(self,**kwargs):
        """
        edit a group
        """
        success = False

        group = self.group_GET(**kwargs)
        if not group == None:
            fields = []
            data = [] 
            if 'groupname' in kwargs:
                fields.append('groupname')
                data.append(kwargs['groupname'])

            if 'permission' in kwargs:
                fields.append('permission')
                data.append(kwargs['permission'])

            data.append(group['id'])

            con,cur = self._create_cursor()
            self._execute_query(cur,'UPDATE `groups` SET {} WHERE id=%s'.format(', '.join(['{}=%s'.format(f) for f in fields])), tuple(data) )
            con.commit()
            con.close()
            success = True

        return success


    def group_DELETE(self,**kwargs):
        """
        delete a group
        """
        success = False

        group = self.group_GET(**kwargs)
        if not group == None:

            con,cur = self._create_cursor()
            self._execute_query(cur,"DELETE FROM `groups` WHERE id=%s", (group['id'],))
            con.commit()
            con.close()

            success = True

        return success



    def group_users_POST(self,userid,groupid):
        """
        add a user to a group
        """
        success = False

        con,cur = self._create_cursor()
        self._execute_query(cur,'SELECT * FROM group_users WHERE `group`=%s AND `user`=%s', (groupid,userid,))
        if cur.fetchone() == None:
            self._execute_query(cur,'INSERT INTO group_users (`group`,`user`) VALUES (%s,%s)', (groupid,userid,))
            success = True
        else:
            logger.warning('user {} is allready in group {}'.format(userid,groupid))
            success = False

        con.commit()
        con.close()

        return success


    def group_users_GET(self,**kwargs):

        result = False
        if 'userid' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT `id`,`group`,`user` FROM group_users WHERE user=%s', (kwargs['userid'],))
            result = cur.fetchone()
            con.commit()
            con.close()

        elif 'groupid' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT `id`,`group`,`user` FROM group_users WHERE group=%s', (kwargs['groupid'],))
            result = cur.fetchone()
            con.commit()
            con.close()
        else:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT `id`,`group`,`user` FROM group_users')
            result = cur.fetchall()
            con.commit()
            con.close()

        return result


    def group_users_DELETE(self,user,group):
        return False



################################################################################
# settings
################################################################################
    def setting_POST(self,**kwargs):
        """
        post to the settings table
        """
        success = False

        if 'setting' in kwargs and 'value' in kwargs:
            con,cur = self._create_cursor()
            self._execute_query(cur,'SELECT * FROM settings WHERE setting=%s', (kwargs['setting'],))
            if cur.fetchone() == None:
                self._execute_query(cur,'INSERT INTO settings (setting,value) VALUES (%s,%s)', (kwargs['setting'],kwargs['value'],))
                success = True
            else:
                logger.warning('setting {} allready exists'.format(kwargs['setting']))
                success = False

            con.commit()
            con.close()

        return success


    def setting_GET(self,**kwargs):
        """
        get a setting or all settings
        """

        result = False
        if 'id' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,setting,value FROM settings WHERE id=%s', (kwargs['id'],))
            result = cur.fetchone()
            con.commit()
            con.close()

        elif 'setting' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,setting,value FROM settings WHERE setting=%s', (kwargs['setting'],))
            result = cur.fetchone()
            con.commit()
            con.close()
        else:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,setting,value FROM settings')
            result = cur.fetchall()
            con.commit()
            con.close()

        return result


    def setting_PUT(self,**kwargs):
        """
        edit a setting
        """
        success = False

        setting = self.setting_GET(**kwargs)
        if not setting == None:
            fields = []
            data = [] 
            if 'value' in kwargs:
                fields.append('value')
                data.append(kwargs['value'])

            data.append(setting['id'])

            con,cur = self._create_cursor()
            self._execute_query(cur,'UPDATE `settings` SET {} WHERE id=%s'.format(', '.join(['{}=%s'.format(f) for f in fields])), tuple(data) )
            con.commit()
            con.close()
            success = True

        return success


    def setting_DELETE(self,**kwargs):
        """
        delete a setting
        """
        success = False

        setting = self.setting_GET(**kwargs)
        if not setting == None:

            con,cur = self._create_cursor()
            self._execute_query(cur,"DELETE FROM `settings` WHERE id=%s", (setting['id'],))
            con.commit()
            con.close()

            success = True

        return success


################################################################################
# items
################################################################################

    def item_POST(self,**kwargs):
        """
        post to the items table
        """
        success = False

        if 'path' in kwargs and 'conf' in kwargs and 'persist' in kwargs and 'label' in kwargs and 'description' in kwargs and 'unit' in kwargs:
            con,cur = self._create_cursor()
            self._execute_query(cur,'SELECT `id` FROM items WHERE path=%s', (kwargs['path'],))
            if cur.fetchone() == None:
                self._execute_query(cur,'INSERT INTO `items` (`path`,`conf`,`persist`,`label`,`description`,`unit`) VALUES (%s,%s,%s,%s,%s,%s)', (kwargs['path'],kwargs['conf'],kwargs['persist'],kwargs['label'],kwargs['description'],kwargs['unit'],))
                success = True
            else:
                logger.warning('item {} allready exists'.format(kwargs['path']))
                success = False

            con.commit()
            con.close()

        return success


    def item_GET(self,**kwargs):
        """
        get an item or all items
        """

        result = False
        if 'id' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT `id`,`path`,`conf`,`persist`,`label`,`description`,`unit` FROM items WHERE id=%s', (kwargs['id'],))
            result = cur.fetchone()
            con.commit()
            con.close()

        elif 'path' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT `id`,`path`,`conf`,`persist`,`label`,`description`,`unit` FROM items WHERE path=%s', (kwargs['path'],))
            
            result = cur.fetchone()
            con.commit()
            con.close()

        else:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT `id`,`path`,`conf`,`persist`,`label`,`description`,`unit` FROM items')
            result = cur.fetchall()
            con.commit()
            con.close()

        if result == None:
            result = False

        return result


    def item_PUT(self,**kwargs):
        """
        edit an item
        """
        success = False

        item = self.item_GET(**kwargs)
        if not item == None:
            fields = []
            data = [] 
            if 'conf' in kwargs:
                fields.append('conf')
                data.append(kwargs['conf'])
            if 'persist' in kwargs:
                fields.append('persist')
                data.append(kwargs['persist'])
            if 'label' in kwargs:
                fields.append('label')
                data.append(kwargs['label'])
            if 'description' in kwargs:
                fields.append('description')
                data.append(kwargs['description'])
            if 'unit' in kwargs:
                fields.append('unit')
                data.append(kwargs['unit'])

            data.append(item['id'])

            con,cur = self._create_cursor()
            self._execute_query(cur,'UPDATE `items` SET {} WHERE id=%s'.format(', '.join(['{}=%s'.format(f) for f in fields])), tuple(data) )
            con.commit()
            con.close()
            success = True

        return success


    def item_DELETE(self,**kwargs):
        """
        delete an item
        """
        success = False

        item = self.item_GET(**kwargs)
        if not item == None:

            con,cur = self._create_cursor()
            self._execute_query(cur,"DELETE FROM `items` WHERE id=%s", (item['id'],))
            con.commit()
            con.close()

            success = True

        return success




################################################################################
# private
################################################################################
    def _create_cursor(self):
        con = pymysql.connect('localhost', self._db_user, self._db_pass, self._db_name)
        cur = con.cursor()

        return con,cur


    def _create_dict_cursor(self):
        con = pymysql.connect('localhost', self._db_user, self._db_pass, self._db_name)
        cur = con.cursor(pymysql.cursors.DictCursor)

        return con,cur

    def _execute_query(self,cur,query,insert=()):
        try:
            cur.execute(query,insert)
        except:
            logger.error('There was a problem executing query: {}'.format(query))









################################################################################
# generic functions, fixme
################################################################################

    def _POST(self,table,required_fields,unique_fields,**kwargs):
        """
        post
        """
        success = False

        # check if the required fields are present
        for field in required_fields:
            if not field in kwargs:
                return False

        for field in unique_fields:
            if not field in kwargs:
                return False

        # check if the value allredy exists in the database
        con,cur = self._create_cursor()
        self._execute_query(cur,'SELECT * FROM {} WHERE {}'.format(table,' OR '.join(['{}=%s'.format(field) for field in unique_fields])), tuple([kwargs[field] for field in unique_fields]))

        if cur.fetchone() == None:

            # execute the querry
            self._execute_query(cur,'INSERT INTO {} ({}) VALUES ({})'.format(table,','.join(required_fields), ','.join(['%s' for field in required_fields]) ), tuple([kwargs[field] for field in required_fields]))
            success = True

        con.commit()
        con.close()

        return success


    def _GET(self,table,selector_fields,return_fields,**kwargs):
        """
        get
        """

        result = False
        if 'id' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,groupname,permission FROM groups WHERE id=%s', (kwargs['id'],))
            result = cur.fetchone()
            con.commit()
            con.close()

        elif 'username' in kwargs:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,groupname,permission FROM groups WHERE groupname=%s', (kwargs['groupname'],))
            result = cur.fetchone()
            con.commit()
            con.close()
        else:
            con,cur = self._create_dict_cursor()
            self._execute_query(cur,'SELECT id,groupname,permission FROM groups')
            result = cur.fetchall()
            con.commit()
            con.close()

        return result


    def _PUT(self,**kwargs):
        """
        put
        """
        success = False

        group = self.group_GET(**kwargs)
        if not group == None:
            fields = []
            data = [] 
            if 'groupname' in kwargs:
                fields.append('groupname')
                data.append(kwargs['groupname'])

            if 'permission' in kwargs:
                fields.append('permission')
                data.append(kwargs['permission'])

            data.append(group['id'])

            self._execute_query(cur,'UPDATE `groups` SET {} WHERE id=%s'.format(', '.join(['{}=%s'.format(f) for f in fields])), tuple(data) )
            con.commit()
            con.close()
            success = True

        return success


    def _DELETE(self,**kwargs):
        """
        delete
        """
        success = False

        group = self.group_GET(**kwargs)
        if not group == None:

            con,cur = self._create_cursor()
            self._execute_query(cur,"DELETE FROM `groups` WHERE id=%s", (group['id'],))
            con.commit()
            con.close()

            success = True

        return success










# old

    def POST(self,table,data):
        keys = []
        vals = []

        for key,val in data.items():
            keys.append('`'+key+'`')
            vals.append('\''+val+'\'')

        query = "INSERT INTO `{}` ({}) VALUES ({})".format(table,','.join(keys),','.join(vals))    
        id_query = "SELECT LAST_INSERT_ID()"

        con,cur = self.create_cursor()

        try:
            self.execute_query(cur,query)
            cur = self.execute_query(cur,id_query)

            id = cur[0][0]
        except:
            id = None

        con.commit()
        con.close()

        return id


    def GET(self,table,selector=None):

        if selector==None:
            query = "SELECT {} FROM `{}`".format('*',table)
        else:
            query = "SELECT {} FROM `{}` WHERE {}".format('*',table,selector)

        con,cur = self.create_dict_cursor()
        try:
            self.execute_query(cur,query)
            values = list( cur.fetchall() )
        except:
            values = []

        con.commit()
        con.close()

        return values

    def GET_JSON(self,table,selector=None):
        values = self.GET(table,selector=None)

        for value in values:
            for key,val in value.items():
                if isinstance(val, str):
                    value[key] = json.loads( val )

        return values

    def PUT(self,table,selector,data):

        keyvals = []
        for key,val in data.items():
            keyvals.append(key+' = \''+val+'\'')

        query = "UPDATE `{}` SET {} WHERE {}".format(table,','.join(keyvals),selector)

        con,cur = self.create_cursor()
        try:
            self.execute_query(cur,query)
        except:
            pass

        con.commit()
        con.close()

    def DELETE(self,table,selector):

        query = "DELETE {} FROM `{}` WHERE {}".format('*',table,selector)

        con,cur = self.create_cursor()
        try:
            self.execute_query(cur,query)
        except:
            pass

        con.commit()
        con.close()


    def backup(self):
        """
        backup mysql data without measurements to backupdir
        """
        pass


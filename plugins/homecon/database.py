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
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS users (id int(11) NOT NULL AUTO_INCREMENT,username varchar(255) NOT NULL,password varchar(255) NOT NULL,permission tinyint(4) NOT NULL DEFAULT \'1\',PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS items (id int(11) NOT NULL AUTO_INCREMENT,path varchar(255) NOT NULL,conf varchar(255),persist tinyint(4) NOT NULL DEFAULT \'1\',label varchar(63),description varchar(255),unit varchar(63),PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        

        # add the admin user if required
        self._execute_query(cur,'INSERT IGNORE INTO users (id,username,password,permission) VALUES (1,\'admin\',\'{}\',9)'.format(self.encrypt_password('homecon')))



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
    def add_user(self,username,password,permission=1):
        con,cur = self._create_cursor()

        self._execute_query(cur,'SELECT * FROM users WHERE username=\'{}\''.format(username))
        if cur.fetchone() == None:
            self._execute_query(cur,'INSERT INTO users (username,password,permission) VALUES (\'{}\',\'{}\',{})'.format(username,self.encrypt_password(password),permission))
            success = True
        else:
            logger.warning('username {} allready exists'.format(username))
            success = False

        con.commit()
        con.close()

        return success

    def delete_user(self,username):

        if not username == 'admin':
            con,cur = self._create_cursor()
            self._execute_query(cur,"DELETE FROM `users` WHERE username=\'{}\'".format(username))
            con.commit()
            con.close()
            return True
        else:
            return False

    def change_user_password(self,username,oldpassword,newpassword):

        user = self.verify_user(username,oldpassword)
        if user:
            con,cur = self._create_cursor()
            self._execute_query(cur,'UPDATE `users` SET password=\'{}\' WHERE id=\'{}\''.format(self.encrypt_password(newpassword),user[0]))
            con.commit()
            con.close()

    def update_user(self,permission):
        pass


    def verify_user(self,username,password):
        """
        """
        con,cur = self._create_dict_cursor()
        
        self._execute_query(cur,'SELECT * FROM users WHERE username=\'{}\''.format(username))
        result = cur.fetchone()
        con.commit()
        con.close()

        if result:
            if self.verify_password(password, result['password']):
                return (result['id'],result['username'],result['permission'])
            else:
                logger.warning('Failed login attempt detected for user {}'.format(username))
                return False
        else:
            logger.warning('User {} does not exist'.format(username))
            return False

    def encrypt_password(self,password):
        return pbkdf2_sha256.encrypt(password, rounds=10, salt_size=16)

    def verify_password(self,password,hash):
        return pbkdf2_sha256.verify(password, hash)



################################################################################
# settings
################################################################################
    def add_setting(self,setting,value):
        """
        """
        con,cur = self._create_cursor()
        self._execute_query(cur,'SELECT * FROM settings WHERE setting=\'{}\''.format(setting))
        if cur.fetchone() == None:
            self._execute_query(cur,'INSERT INTO `settings` (`setting`,`value`) VALUES (\'{}\',\'{}\')'.format(setting,value))
            success = True
        else:
            logger.warning('setting {} allready exists'.format(setting))
            success = False
        con.commit()
        con.close()
        return success

    def update_setting(self,setting,value):
        """
        """
        con,cur = self._create_cursor()
        self._execute_query(cur,'UPDATE `settings` SET value=\'{}\' WHERE setting=\'{}\''.format(value,setting))
        con.commit()
        con.close()


################################################################################
# items
################################################################################
    def add_item(self,path,conf,persist,label,description,unit):
        """
        """
        con,cur = self._create_cursor()
        self._execute_query(cur,'SELECT * FROM items WHERE path=\'{}\''.format(path))
        if cur.fetchone() == None:
            self._execute_query(cur,'INSERT INTO `items` (`path`,`conf`,`persist`,`label`,`description`,`unit`) VALUES (\'{}\',\'{}\',{},\'{}\',\'{}\',\'{}\')'.format(path,conf,persist,label,description,unit))
            success = True
        else:
            logger.debug('item {} allready exists'.format(path))
            success = False
        con.commit()
        con.close()
        return success

    def update_item(self,path,conf,persist,label,description,unit):
        """
        """
        con,cur = self._create_cursor()
        self._execute_query(cur,'UPDATE `items` SET conf=\'{}\', persist={}, label=\'{}\', description=\'{}\', unit=\'{}\' WHERE path=\'{}\''.format(conf,persist,label,description,unit,path))
        con.commit()
        con.close()

    def get_items(self):
        con,cur = self._create_dict_cursor()
        self._execute_query(cur,'SELECT * FROM items')
        return cur.fetchall()
        con.commit()
        con.close()

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

    def _execute_query(self,cur,query):
        try:
            cur.execute( query )
        except:
            logger.error('There was a problem executing query: {}'.format(query))




















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


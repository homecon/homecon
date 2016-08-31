#!/usr/bin/env python3

import logging
import pymysql
import datetime
import json
from passlib.hash import pbkdf2_sha256


logger = logging.getLogger('')

class Mysql(object):

    def __init__(self,homecon,db='homecon',db_user='homecon',db_pass='homecon'):
        """
        A mysql object is created
        and mysql tables required for homecon are created
        
        Parameters:
            homecon                 the homecon instance
            db='homecon'            database name
            db_user='homecon'       database user
            db_pass='homecon'       database user password
        """

        self.homecon = homecon
        self._db = db
        self._db_user = db_user
        self._db_pass = db_pass

        # perpare the database
        con,cur = self._create_cursor()
        
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS settings (id int(11) NOT NULL AUTO_INCREMENT,setting varchar(255)  NOT NULL,value varchar(255) NOT NULL,PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS users (id int(11) NOT NULL AUTO_INCREMENT,username varchar(255) NOT NULL,password varchar(255) NOT NULL,permission tinyint(4) NOT NULL DEFAULT \'1\',PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        self._execute_query(cur,'CREATE TABLE IF NOT EXISTS items (id int(11) NOT NULL AUTO_INCREMENT,item varchar(255) NOT NULL,conf varchar(255) NOT NULL,persist tinyint(4) NOT NULL DEFAULT \'1\',PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
        

        #self.add_admin_user()


        # set location data
        #query = "UPDATE data SET latitude=%f,longitude=%f,elevation=%f WHERE id=1" % (float(self._sh._lat),float(self._sh._lon),float(self._sh._elev))
        #try:
        #    cur.execute( query )
        #except:
        #    logger.warning("Could not add location to database")


        con.commit()    
        con.close()
        logger.info("Homecon database initialized")


    def add_user(self,username,password,permission=1):
        con,cur = self._create_cursor()

        self._execute_query(cur,'SELECT * FROM users WHERE username=\'{}\''.format(username))
        if cur.fetchone() == None:
            self._execute_query(cur,'INSERT INTO users (username,password,permission) VALUES (\'{}\',\'{}\',{})'.format(username,pbkdf2_sha256.encrypt(password, rounds=10, salt_size=16),permission))
            success = True
        else:
            logger.warning('username {} allready exists'.format(username))
            success = False

        con.commit()
        con.close()

        return success

    def add_admin_user(self):
        con,cur = self._create_cursor()
        self._execute_query(cur,'INSERT IGNORE INTO users (id,username,password,permission) VALUES (1,\'admin\',\'{}\',9)'.format(pbkdf2_sha256.encrypt('homecon', rounds=10, salt_size=16)))

        con.commit()
        con.close()

        return True

    def verify_user(self,username,password):

        con,cur = self._create_dict_cursor()
        
        self._execute_query(cur,'SELECT * FROM users WHERE username=\'{}\''.format(username))
        result = cur.fetchone()
        con.commit()
        con.close()

        if pbkdf2_sha256.verify(password, result['password']):
            return (result['id'],result['username'],result['permission'])
        else:
            logger.warning('Failed login attempt detected for user {}'.format(username))
            return False


    def add_setting(self,setting,value):
        con,cur = self._create_cursor()
        self._execute_query(cur,'INSERT INTO `settings` (`setting`,`value`) VALUES (\'{setting}\',\'{value}\')'.format(value=value,setting=setting))
        con.commit()
        con.close()

    def update_setting(self,setting,value):
        con,cur = self._create_cursor()
        self._execute_query(cur,'UPDATE `settings` SET value=\'{value}\' WHERE setting=\'{setting}\''.format(value=value,setting=setting))
        con.commit()
        con.close()

    def _create_cursor(self):
        con = pymysql.connect('localhost', self._db_user, self._db_pass, self._db)
        cur = con.cursor()

        return con,cur


    def _create_dict_cursor(self):
        con = pymysql.connect('localhost', self._db_user, self._db_pass, self._db)
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


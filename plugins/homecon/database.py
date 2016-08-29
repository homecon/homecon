#!/usr/bin/env python3

import logging
import pymysql
import datetime
import json

logger = logging.getLogger('')

class Mysql(object):

    def __init__(self,homecon, db='homecon',db_user='homecon',db_pass='homecon'):
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

        con,cur = self._create_cursor()





        # set location data
        #query = "UPDATE data SET latitude=%f,longitude=%f,elevation=%f WHERE id=1" % (float(self._sh._lat),float(self._sh._lon),float(self._sh._elev))
        #try:
        #    cur.execute( query )
        #except:
        #    logger.warning("Could not add location to database")


        con.commit()    
        con.close()
        logger.info("Homecon database initialized")

        

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
            logger.error('There was a problem executing query {}.'.format(query))




















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


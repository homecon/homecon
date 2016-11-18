#!/usr/bin/env python3
# -*- coding: utf-8 -*-



BACKEND = 'sqlite3'

if BACKEND == 'sqlite3':
    import sqlite3
else:
    import pymysql

    
class Database(object):
    """
    Class for interfacing a sqlite3 or mysql database
    """
    def __init__(self,host='',user='',password='',database=''):
    
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        
    def create_connection(self):
        if BACKEND == 'sqlite3':
            connection = sqlite3.connect(self.database)
        else:
            connection = pymysql.connect(self.host,self.user,self.password,self.database)
        return connection
        
    def create_cursor(self):
    
        connection = self.create_connection()
        cursor = connection.cursor()
        
        return connection,cursor
        
    def create_dict_cursor(self):
        if BACKEND == 'sqlite3':
            connection = self.create_connection()
            connection.row_factory = self._dict_factory
            cursor = connection.cursor()
        else:
            connection = self.create_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        return connection,cursor    
        
    def execute_query(self,query,data=None):
        connection,cursor = self.create_dict_cursor()
        
        try:
            if data == None:
                cursor.execute(query)
            else:
                if BACKEND == 'sqlite3':
                    newdata = []
                    for d in data:
                        if isinstance(d, str):
                            d = '\'' + d + '\''
                        newdata.append(d) 
                    cursor.execute(query%tuple(newdata))
                else:
                    cursor.execute(query,data)
                
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(e)
        
        return cursor
        
    #def table_description(table):
    #    connection = self.create_connection()
    #    connection.row_factory = sqlite3.Row
    #    cursor = connection.cursor()
    #    cursor.execute('select * from {}'.format(table))
    #    row = cursor.fetchone()


    def _dict_factory(self,cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
        
        
class Table(object):
    """
    Class to work with a database table
    """
    def __init__(self,database,name,columns=[]):
        """
        Initialize a Table instance and creates the database table if it does not exist
        """
        
        self.database = database
        self.name = name
        
        # create the table if it does not exist
        if BACKEND == 'sqlite3':
            query = 'CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY)'.format(self.name)
        else:
            query = 'CREATE TABLE IF NOT EXISTS {} (id int(11) NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))'.format(self.name)
        self.database.execute_query( query )
        

        # load all existing columns
        query = 'SELECT * FROM {}'.format(self.name)
        cursor = self.database.execute_query( query )

        if cursor == None:
            self.columns = []
        else:
            cursor.fetchall()
            self.columns = [col[0] for col in cursor.description]


        # add columns
        for column in columns:
            if not column['name'] in self.columns:

                if BACKEND == 'sqlite3':
                    query = 'ALTER TABLE `{}` ADD COLUMN `{}` {}'.format(self.name,column['name'],column['type'])
                    cursor = self.database.execute_query( query )
                    
                else:
                    query = 'ALTER TABLE `{}` ADD `{}`'.format(self.name,column['name'])
                    cursor = self.database.execute_query( query )

                    query = 'ALTER TABLE `{}` MODIFY `{}` {} {} {} '.format(self.name,column['name'],column['type'],column['null'],column['default'],column['unique'])
                    cursor = self.database.execute_query( query )

                self.columns.append(column)

            else:
                # edit the column
                pass
        
        if not 'id' in self.columns:
            self.columns.append('id')

    
    def GET(self,columns=None,order=None,desc=False,limit=None,**kwargs):
        """
        Gets data from the database
        """
        
        if columns == None:
            columns = '*'
        else:
            columns = '`' + '`,`'.join(columns) + '`'
        
        # parse where statements in the kwargs
        data = []
        if len(kwargs) == 0:
            where = ''
        else:
            where = []
            for key,val in kwargs.items():
                if key[-4:] == '__ge':
                    where.append(key[:-4] + ' >= %s')
                    data.append(val)
                elif key[-4:] == '__le':
                    where.append(key[:-4] + ' <= %s')
                    data.append(val)
                else:
                    where.append(key + ' = %s')
                    data.append(val)
                    
            where = 'WHERE ' + ' AND '.join(where)
            
        data = tuple(data)
        
        query = 'SELECT {} FROM {} {}'.format(columns,self.name,where)

        if not order is None:
            query = query + ' ORDER BY '+order
            if desc:
                query = query + ' DESC'

        if not limit is None:
            query = query + ' LIMIT {}'.format(limit)

        cursor = self.database.execute_query( query, data )
        
        if cursor == None:
            return []
        else:
            return cursor.fetchall()
        
        
    def POST(self,**kwargs):
    
        columns = []
        values = []
        data = []
        for key,val in kwargs.items():
            columns.append(key)
            values.append('%s')
            data.append(val)
            
        columns = '`' + '`,`'.join(columns) + '`'
        values = ','.join(values)
        data = tuple(data)
        
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(self.name,columns,values)
        
        cursor = self.database.execute_query( query, data )
        
    def PUT(self,where='',**kwargs):
    
        columnsvalues = []
        data = []
        for key,val in kwargs.items():
            columnsvalues.append('`'+key+'` = %s')
           
            data.append(val)
            
        columnsvalues = ','.join(columnsvalues)
        data = tuple(data)
        
        query = 'UPDATE {} SET {} WHERE {}'.format(self.name,columnsvalues,where)

        cursor = self.database.execute_query( query, data )
        
    def DELETE(self,where=''):
    
        query = 'DELETE FROM {} WHERE {}'.format(self.name,where)
        cursor = self.database.execute_query( query )

        
        
# Example usage
if __name__ == '__main__':

    db = Database(database = 'test.db')
    users = Table(db,'users',[
        {'name':'username',   'type':'char(255)', 'null': '',  'default':'',  'unique':'UNIQUE'},
        {'name':'password',   'type':'char(255)', 'null': '',  'default':'',  'unique':''},
        {'name':'permission', 'type':'int',       'null': '',  'default':'',  'unique':''},
    ])
    
    users.POST(username='user1',password='test',permission=1)
    users.POST(username='user2',password='test',permission=1)
    users.POST(username='user3',password='test',permission=1)
    
    usrs = users.GET(columns=['username','permission'])
    for u in usrs:
        print(u)
     

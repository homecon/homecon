#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os


logger = logging.getLogger(__name__)

BACKEND = 'sqlite3'

if BACKEND == 'sqlite3':
    import sqlite3
else:
    import pymysql


database_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

_database = None
_measurements_database = None


def get_database():
    global _database
    if _database is None:
        _database = Database(database=os.path.join(database_path, 'homecon.db'))
    return _database


def get_measurements_database():
    global _measurements_database
    if _measurements_database is None:
        _measurements_database = Database(database=os.path.join(database_path, 'measurements.db'))
    return _measurements_database


class Database(object):
    """
    Class for interfacing a sqlite3 or mysql database
    """
    def __init__(self, host='', user='', password='', database=''):
    
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        
    def create_connection(self):
        if BACKEND == 'sqlite3':
            connection = sqlite3.connect(self.database)
        else:
            connection = pymysql.connect(self.host, self.user, self.password, self.database)
        return connection
        
    def create_cursor(self):
    
        connection = self.create_connection()
        cursor = connection.cursor()
        
        return connection, cursor
        
    def create_dict_cursor(self):
        if BACKEND == 'sqlite3':
            connection = self.create_connection()
            connection.row_factory = self._dict_factory
            cursor = connection.cursor()
        else:
            connection = self.create_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        return connection, cursor
        
    def execute_query(self, query, data=None):
        connection, cursor = self.create_dict_cursor()
        try:
            if data is None:
                cursor.execute(query)
            else:
                if BACKEND == 'sqlite3':
                    new_data = []
                    for d in data:
                        if isinstance(d, str):
                            d = '\'' + d + '\''
                        new_data.append(d)
                    cursor.execute(query % tuple(new_data))
                else:
                    cursor.execute(query, data)
                
            connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error('Database query \'{}\' raised an exception exception {}'.format(query, e))
        
        return cursor
        
    # def table_description(table):
    #     connection = self.create_connection()
    #     connection.row_factory = sqlite3.Row
    #     cursor = connection.cursor()
    #     cursor.execute('select * from {}'.format(table))
    #     row = cursor.fetchone()

    @staticmethod
    def _dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.database)


class Table(object):
    """
    Class to work with a database table
    """
    def __init__(self, database, name, columns=None):
        """
        Initialize a Table instance and creates the database table if it does not exist
        """
        
        self.database = database
        self.name = name

        if columns is None:
            columns = []

        # create the table if it does not exist
        if BACKEND == 'sqlite3':
            query = 'CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY)'.format(self.name)
        else:
            query = 'CREATE TABLE IF NOT EXISTS {} (id int(11) NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))'\
                .format(self.name)
        self.database.execute_query(query)

        # load all existing columns
        query = 'SELECT * FROM {}'.format(self.name)
        cursor = self.database.execute_query(query)

        if cursor is None:
            self.columns = []
        else:
            cursor.fetchall()
            self.columns = [col[0] for col in cursor.description]

        # add columns
        for column in columns:
            if not column['name'] in self.columns:

                if BACKEND == 'sqlite3':
                    query = 'ALTER TABLE `{}` ADD COLUMN `{}` {}'.format(self.name, column['name'], column['type'])
                    self.database.execute_query(query)
                else:
                    query = 'ALTER TABLE `{}` ADD `{}`'.format(self.name, column['name'])
                    self.database.execute_query(query)

                    query = 'ALTER TABLE `{}` MODIFY `{}` {} {} {} '\
                        .format(self.name, column['name'], column['type'], column['null'], column['default'],
                                column['unique'])
                    self.database.execute_query(query)
                self.columns.append(column)
            else:
                # edit the column
                pass

        if 'id' not in self.columns:
            self.columns.append('id')

    def get(self, columns=None, order=None, desc=False, limit=None, **kwargs):
        """
        Gets data from the database
        """
        if columns is None:
            columns = '*'
        else:
            columns = '`' + '`,`'.join(columns) + '`'
        
        # parse where statements in the kwargs
        data = []
        if len(kwargs) == 0:
            where = ''
        else:
            where = []
            for key, val in kwargs.items():
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
        
        query = 'SELECT {} FROM {} {}'.format(columns, self.name, where)
        if order is not None:
            query += ' ORDER BY '+order
            if desc:
                query += ' DESC'

        if limit is not None:
            query += ' LIMIT {}'.format(limit)

        logger.debug(query)
        cursor = self.database.execute_query(query, data)

        if cursor is None:
            return []
        else:
            return cursor.fetchall()
        
    def post(self, **kwargs):
        columns = []
        values = []
        data = []
        for key, val in kwargs.items():
            columns.append(key)
            values.append('%s')
            data.append(val)
            
        columns = '`' + '`,`'.join(columns) + '`'
        values = ','.join(values)
        data = tuple(data)
        
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(self.name, columns, values)

        logger.debug(query)
        self.database.execute_query(query, data)
        
    def put(self, where='', **kwargs):
        columns_values = []
        data = []
        for key, val in kwargs.items():
            columns_values.append('`'+key+'` = %s')
            data.append(val)
            
        columns_values = ','.join(columns_values)
        data = tuple(data)
        
        query = 'UPDATE {} SET {} WHERE {}'.format(self.name, columns_values, where)

        logger.debug(query)
        self.database.execute_query(query, data)
        
    def delete(self, **kwargs):
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
        query = 'DELETE FROM {} {}'.format(self.name, where)
        logger.debug(query)
        self.database.execute_query(query, data)

    def __repr__(self):
        return '<{} {} database={}>'.format(self.__class__.__name__, self.name, self.database.database)


# Example usage
if __name__ == '__main__':

    db = Database(database='test.db')
    users = Table(db, 'users', [
        {'name': 'username',   'type': 'char(255)', 'null': '',  'default': '',  'unique': 'UNIQUE'},
        {'name': 'password',   'type': 'char(255)', 'null': '',  'default': '',  'unique': ''},
        {'name': 'permission', 'type': 'int',       'null': '',  'default': '',  'unique': ''},
    ])
    
    users.post(username='user1', password='test', permission=1)
    users.post(username='user2', password='test', permission=1)
    users.post(username='user3', password='test', permission=1)

    for u in users.get(columns=['username', 'permission']):
        print(u)

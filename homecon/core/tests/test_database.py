#!/usr/bin/env python3
################################################################################
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
################################################################################


from homecon.tests import common

import homecon.core


class DatabaseTests(common.TestCase):
    

    def test_create_connection(self):
        db = homecon.core.database.Database(database='{}.db'.format(common.dbname))
        con = db.create_connection()


    def test_create_table(self):
        db = homecon.core.database.Database(database='{}.db'.format(common.dbname))
        users = homecon.core.database.Table(db,'users',[
            {'name':'username',   'type':'char(255)', 'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'password',   'type':'char(255)', 'null': '',  'default':'',  'unique':''},
            {'name':'permission', 'type':'int',       'null': '',  'default':'',  'unique':''},
        ])


    def test_post(self):
        db = homecon.core.database.Database(database='{}.db'.format(common.dbname))
        users = homecon.core.database.Table(db,'users',[
            {'name':'username',   'type':'char(255)', 'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'password',   'type':'char(255)', 'null': '',  'default':'',  'unique':''},
            {'name':'permission', 'type':'int',       'null': '',  'default':'',  'unique':''},
        ])
        
        users.post(username='user1', password='test', permission=1)
        users.post(username='user2', password='test', permission=1)
        users.post(username='user3', password='test', permission=1)


    def test_get(self):
        db = homecon.core.database.Database(database='{}.db'.format(common.dbname))
        users = homecon.core.database.Table(db,'users',[
            {'name':'username',   'type':'char(255)', 'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'password',   'type':'char(255)', 'null': '',  'default':'',  'unique':''},
            {'name':'permission', 'type':'int',       'null': '',  'default':'',  'unique':''},
        ])
        
        users.post(username='user1', password='test', permission=1)
        users.post(username='user2', password='test', permission=1)
        users.post(username='user3', password='test', permission=1)
        
        db_users = users.get(columns=['id', 'username', 'permission'])
        self.assertEqual(db_users,[{'id':1,'username': 'user1', 'permission': 1}, {'id':2,'username': 'user2', 'permission': 1}, {'id':3,'username': 'user3', 'permission': 1}])


    def test_put(self):
        db = homecon.core.database.Database(database='{}.db'.format(common.dbname))
        users = homecon.core.database.Table(db,'users',[
            {'name':'username',   'type':'char(255)', 'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'password',   'type':'char(255)', 'null': '',  'default':'',  'unique':''},
            {'name':'permission', 'type':'int',       'null': '',  'default':'',  'unique':''},
        ])
        
        users.post(username='user1', password='test', permission=1)
        users.post(username='user2', password='test', permission=1)
        users.post(username='user3', password='test', permission=1)
        
        users.put(username='user4', permission=9, where='username=\'user3\'')

        db_users = users.get(columns=['username', 'permission'])
        self.assertEqual(db_users,[{'username': 'user1', 'permission': 1}, {'username': 'user2', 'permission': 1}, {'username': 'user4', 'permission': 9}])


    def test_reconnect_to_table(self):
        db = homecon.core.database.Database(database='{}.db'.format(common.dbname))
        users = homecon.core.database.Table(db,'users',[
            {'name':'username',   'type':'char(255)', 'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'password',   'type':'char(255)', 'null': '',  'default':'',  'unique':''},
            {'name':'permission', 'type':'int',       'null': '',  'default':'',  'unique':''},
        ])
        
        users.post(username='user1', password='test', permission=1)
        users.post(username='user2', password='test', permission=1)
        users.post(username='user3', password='test', permission=1)

        del users
        del db

        db = homecon.core.database.Database(database='{}.db'.format(common.dbname))
        users = homecon.core.database.Table(db,'users')

        db_users = users.get(columns=['username', 'permission'])
        self.assertEqual(db_users,[{'username': 'user1', 'permission': 1}, {'username': 'user2', 'permission': 1}, {'username': 'user3', 'permission': 1}])




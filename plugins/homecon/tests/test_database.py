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

import unittest
import time

from common import HomeConTestCase,import_homecon_module

database = import_homecon_module('database')



class DatabaseTests(HomeConTestCase):

    def test_initialize_database(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        con,cur = self.create_database_connection()
        cur.execute('SHOW TABLES')
        result = cur.fetchall()
        con.close()

        self.assertIn(('settings',),result)
        self.assertIn(('users',),result)
        self.assertIn(('items',),result)

    def test_user_POST(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.user_POST(username='someusername',password='somepassword',permission=1)
        user = db.user_VERIFY('someusername','somepassword')

        self.assertEqual(user['username'],'someusername')
        self.assertEqual(user['permission'],1)


    def test_user_POST_double(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.user_POST(username='someusername',password='somepassword',permission=1)
        success = db.user_POST(username='someusername',password='somepassword',permission=1)
        
        self.assertEqual(success,False)


    def test_user_PUT_password(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        
        db.user_POST(username='someusername',password='somepassword',permission=1)
        user = db.user_VERIFY('someusername','somepassword')
        self.assertEqual(user['username'],'someusername')

        db.user_PUT(username='someusername',password='test123')

        # delete the db object and see if the user is still present
        del db
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        
        user = db.user_VERIFY('someusername','test123')
        self.assertEqual(user['username'],'someusername')


    def test_user_DELETE(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.user_POST(username='someusername',password='somepassword',permission=1)
        db.user_DELETE(username='someusername')

        user = db.user_VERIFY('someusername','somepassword')

        self.assertEqual(user,False)


    def test_user_VERIFY_wrong_password(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.user_POST(username='someusername',password='somepassword',permission=1)
        user = db.user_VERIFY('someusername','test123')

        self.assertEqual(user,False)

    def test_user_GET_without_users(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        user = db.user_GET()

        self.assertEqual(user,())


    def test_setting_POST(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.setting_POST(setting='test',value='123')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM settings WHERE setting=\'test\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual(result[2],'123')

    def test_setting_PUT(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.setting_POST(setting='test',value='123')
        db.setting_PUT(setting='test',value='1234')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM settings WHERE setting=\'test\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual(result[2],'1234')


    def test_setting_PUT_nonexistent(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.setting_POST(setting='test',value='123')
        db.setting_PUT(setting='tested',value='1234')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM settings WHERE setting=\'test\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual(result[2],'123')


    def test_item_POST(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.item_POST(path='homecon',conf='{}',persist=1,label='',description='',unit='')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM items WHERE path=\'homecon\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual(result[1],'homecon')


    def test_item_PUT(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.item_POST(path='someitem',conf='{}',persist=1,label='',description='',unit='')
        db.item_PUT(path='someitem',conf='{someconf}',persist=1,label='somelabel',description='somedescription',unit='someunit')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM items WHERE path=\'someitem\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual(result[6],'someunit')


if __name__ == '__main__':
    # run tests
    unittest.main()


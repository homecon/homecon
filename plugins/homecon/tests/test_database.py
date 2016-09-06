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

    def test_add_user(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.add_user('someusername','somepassword')
        user = db.verify_user('someusername','somepassword')

        self.assertEqual(user[1],'someusername')
        self.assertEqual(user[2],1)


    def test_add_user_double(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.add_user('someusername','somepassword')
        result = db.add_user('someusername','someotherpassword')
        
        self.assertEqual(result,False)


    def test_change_user_password(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        
        db.add_user('someusername','somepassword')
        user = db.verify_user('someusername','somepassword')
        self.assertEqual(user[1],'someusername')

        db.change_user_password('someusername','somepassword','test123')

        # delete the db object and see if admin is still present
        del db
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        
        user = db.verify_user('someusername','test123')
        self.assertEqual(user[1],'someusername')


    def test_delete_user(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.add_user('someusername','somepassword')
        db.delete_user('someusername')

        user = db.verify_user('someusername','somepassword')

        self.assertEqual(user,False)

    def test_verify_user_wrong_password(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.add_user('someusername','somepassword')
        user = db.verify_user('someusername','someotherpassword')

        self.assertEqual(user,False)


    def test_add_setting(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.add_setting('test','123')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM settings WHERE setting=\'test\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual('123',result[2])

    def test_update_setting(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.add_setting('test','123')
        db.update_setting('test','1234')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM settings WHERE setting=\'test\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual('1234',result[2])

    def test_update_nonexistent_setting(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.add_setting('test','123')
        db.update_setting('tested','1234')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM settings WHERE setting=\'test\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual('123',result[2])

    def test_add_item(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.add_item('homecon','{}',1,'','','')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM items WHERE path=\'homecon\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual('homecon',result[1])

    def test_update_item(self):

        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')

        db.add_item('someitem','{someconf}',1,'somelabel','somedescription','degC')
        db.update_item('someitem','{someconf}',1,'somelabel','somedescription','someunit')

        con,cur = self.create_database_connection()
        cur.execute('SELECT * FROM items WHERE path=\'someitem\'')
        result = cur.fetchone()
        con.close()

        self.assertEqual('someunit',result[6])

        """
        self.start_smarthome()
        time.sleep(2)

        con,cur = self.create_database_connection()
        cur.execute('SHOW TABLES')
        result = cur.fetchall()

        self.assertIn(('settings',),result)
        self.assertIn(('users',),result)
        self.assertIn(('items',),result)

        self.stop_smarthome()
        con.close()
        """
    
if __name__ == '__main__':
    # run tests
    unittest.main()


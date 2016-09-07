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
authentication = import_homecon_module('authentication')

class AuthenticationTests(HomeConTestCase):

    def test_initialize_authentication(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')

        self.assertEqual(auth.groups,{1: {'id':1,'groupname':'admin','permission':9}, 2: {'id':2,'default':'admin','permission':1} })
        self.assertEqual(auth.users,{1: {'id':1,'username':'admin','permission':9} })
        self.assertEqual(auth.group_users,{1:[1]})
        self.assertEqual(auth.user_groups,{1:[1]})


    def test_reinitialize_authentication(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')

        self.assertEqual(auth.groups,{1: {'id':1,'groupname':'admin','permission':9}, 2: {'id':2,'default':'admin','permission':1} })
        self.assertEqual(auth.users,{1: {'id':1,'username':'admin','permission':9} })
        self.assertEqual(auth.group_users,{1:[1]})
        self.assertEqual(auth.user_groups,{1:[1]})


    def test_add_user(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')

        auth.add_user('someusername','somepassword')
        self.assertIn('someusername',[user['username'] for key,user in auth.users.items()])


    def test_request_token(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')

        auth.add_user('someusername','somepassword')
        
        token = auth.request_token('someusername','somepassword')
        self.assertNotEqual(token, False)


    def test_request_token_wrong_password(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')

        auth.add_user('someusername','somepassword')
        
        token = auth.request_token('someusername','somepassword2')
        self.assertEqual(token, False)


    def test_request_token_wrong_username(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')

        auth.add_user('someusername','somepassword')
        
        token = auth.request_token('someusername2','somepassword')
        self.assertEqual(token, False)


    def test_renew_token(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')

        auth.add_user('someusername','somepassword')
        
        token = auth.request_token('someusername','somepassword')
        token = auth.renew_token(token)

        self.assertNotEqual(token, False)

if __name__ == '__main__':
    # run tests
    unittest.main()


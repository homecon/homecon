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

import unittest
import time

from common import HomeConTestCase,Client,import_homecon_module

database = import_homecon_module('database')
authentication = import_homecon_module('authentication')

class AuthenticationTests(HomeConTestCase):
    """
    Authentication tests
    """

    def test_initialize_authentication(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')

        self.assertEqual(auth.groups,{1: {'id':1,'groupname':'admin','permission':9}, 2: {'id':2,'groupname':'default','permission':1} })
        self.assertEqual(auth.users,{1: {'id':1,'username':'admin','permission':9} })
        self.assertEqual(auth.group_users,{1:[1],2:[1]})
        self.assertEqual(auth.user_groups,{1:[1,2]})


    def test_reinitialize_authentication(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')
        auth  = authentication.Authentication(db,'SLSJDNIZZ03J24SDSOZS923JSLD92L')

        self.assertEqual(auth.groups,{1: {'id':1,'groupname':'admin','permission':9}, 2: {'id':2,'groupname':'default','permission':1} })
        self.assertEqual(auth.users,{1: {'id':1,'username':'admin','permission':9} })
        self.assertEqual(auth.group_users,{1:[1],2:[1]})
        self.assertEqual(auth.user_groups,{1:[1,2]})


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


class AuthenticationWebSocketTests(HomeConTestCase):
    """
    Authentication tests through the websocket
    """

    def test_request_token(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'request_token','username':'admin','password':'homecon'})
        time.sleep(1)

        result = client.recv()
        client.close()

        self.stop_smarthome()

        self.save_smarthome_log()

        self.assertEqual(result['cmd'],'request_token')
        self.assertNotEqual(result['token'],False)


    def test_request_token_wrong_password(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'request_token','username':'admin','password':'test'})
        time.sleep(1)

        result = client.recv()
        client.close()

        self.stop_smarthome()

        self.save_smarthome_log()
        
        self.assertEqual(result['cmd'],'request_token')
        self.assertEqual(result['token'],False)


    def test_authenticate(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'request_token','username':'admin','password':'homecon'})
        time.sleep(1)
        result = client.recv()

        client.send({'cmd':'authenticate','token':'{}'.format(result['token'])})
        time.sleep(1)
        result = client.recv()


        client.close()

        self.stop_smarthome()

        self.save_smarthome_log()

        self.assertEqual(result['cmd'],'authenticate')
        self.assertEqual(result['authenticated'],True)


    def test_authenticate_after_restart(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'request_token','username':'admin','password':'homecon'})
        time.sleep(1)
        result = client.recv()
        client.close()

        self.stop_smarthome()
        self.save_smarthome_log('_1')

        self.start_smarthome(5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'authenticate','token':'{}'.format(result['token'])})
        time.sleep(1)
        result = client.recv()

        client.close()

        self.stop_smarthome()

        self.save_smarthome_log('_2')

        self.assertEqual(result['cmd'],'authenticate')
        self.assertEqual(result['authenticated'],True)


    def test_register(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'register','username':'myname','password':'somepass','repeatpassword':'somepass'})
        time.sleep(1)
        result = client.recv()

        client.close()

        self.stop_smarthome()
        self.save_smarthome_log()

        self.assertEqual(result['cmd'],'register')
        self.assertEqual(result['user']['permission'],0)


    def test_register_username_taken(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'register','username':'admin','password':'somepass','repeatpassword':'somepass'})
        time.sleep(1)
        result = client.recv()

        client.close()

        self.stop_smarthome()
        self.save_smarthome_log()

        self.assertEqual(result['cmd'],'register')
        self.assertEqual(result['user'],None)


    def test_register_passwords_do_not_match(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'register','username':'myname','password':'somepass','repeatpassword':'someotherpass'})
        time.sleep(1)
        result = client.recv()

        client.close()

        self.stop_smarthome()
        self.save_smarthome_log()

        
        self.assertEqual(result['cmd'],'register')
        self.assertEqual(result['user'],None)


    def test_authenticate_without_permission(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'register','username':'myname','password':'somepass','repeatpassword':'somepass'})
        time.sleep(1)
        result = client.recv()

        client.send({'cmd':'request_token','username':'myname','password':'somepass'})
        time.sleep(1)
        result = client.recv()

        client.send({'cmd':'authenticate','token':'{}'.format(result['token'])})
        time.sleep(1)
        result = client.recv()

        client.close()

        self.stop_smarthome()
        self.save_smarthome_log()

        self.assertEqual(result['cmd'],'authenticate')
        self.assertEqual(result['authenticated'],False)


    def test_update_permission(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'register','username':'myname','password':'somepass','repeatpassword':'somepass'})
        time.sleep(1)
        result = client.recv()

        
        client.send({'cmd':'request_token','username':'admin','password':'homecon'})
        time.sleep(1)
        result = client.recv()

        client.send({'cmd':'update_user_permission','token':'{}'.format(result['token']),'id':2,'permission':5})
        time.sleep(1)
        result = client.recv()

        client.send({'cmd':'request_token','username':'myname','password':'somepass'})
        time.sleep(1)
        result = client.recv()
        
        client.send({'cmd':'authenticate','token':'{}'.format(result['token'])})
        time.sleep(1)
        result = client.recv()

        client.close()

        self.stop_smarthome()
        self.save_smarthome_log()

        self.assertEqual(result['cmd'],'authenticate')
        self.assertEqual(result['authenticated'],True)




if __name__ == '__main__':
    # run tests
    unittest.main()


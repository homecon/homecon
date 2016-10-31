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
import json
import sys
import os
import asyncio

from common import HomeConTestCase, Client

sys.path.append(os.path.abspath('..'))
from homecon import HomeCon
from core.plugin import Event
from core.authentication import Authentication



class AuthenticationTests(HomeConTestCase):

    def test_initialize(self):
        queue = asyncio.Queue()

        self.clear_database()
        authentication = Authentication(queue)


        self.assertEqual(authentication.users,{1: {'id': 1, 'permission': 9, 'username': 'admin'}})
        self.assertEqual(authentication.groups,{1: {'groupname': 'admin', 'id': 1, 'permission': 9}, 2: {'groupname': 'default', 'id': 2, 'permission': 1}})

    
    def test_add_user(self):
        queue = asyncio.Queue()

        self.clear_database()
        authentication = Authentication(queue)

        authentication.add_user('testuser','testpassword',5)

        userid = authentication.usernames['testuser']
        
        self.assertEqual(authentication.users[userid], {'id': userid, 'permission': 5, 'username': 'testuser'})
        

    
    def test_add_group(self):
        queue = asyncio.Queue()

        self.clear_database()
        authentication = Authentication(queue)

        authentication.add_group('testgroup',2)


        groupid = authentication.groupnames['testgroup']
        
        self.assertEqual(authentication.groups[groupid], {'id': groupid, 'permission': 2, 'groupname': 'testgroup'})


    def test_request_token(self):
        queue = asyncio.Queue()

        self.clear_database()
        authentication = Authentication(queue)

        authentication.add_user('testuser','testpassword',5)
        token = authentication.request_token('testuser','testpassword')
        payload = authentication.jwt_decode(token)


        userid = authentication.usernames['testuser']

        self.assertEqual(payload['userid'], userid)
        self.assertEqual(payload['groupids'], [])
        self.assertEqual(payload['permission'], 5)

    
    def test_request_token_admin(self):
        queue = asyncio.Queue()

        self.clear_database()
        authentication = Authentication(queue)

        token = authentication.request_token('admin','homecon')
        payload = authentication.jwt_decode(token)

        userid = authentication.usernames['admin']

        self.assertEqual(payload['userid'], userid)
        self.assertIn(1,payload['groupids'])
        self.assertIn(2,payload['groupids'])
        self.assertEqual(payload['permission'], 9)

    
    def test_request_token_event(self):
        queue = asyncio.Queue()

        self.clear_database()
        authentication = Authentication(queue)

        event = Event('request_token',{'username':'admin','password':'homecon'},self,None)
        authentication.listen(event)

        # run the loop to fire events
        self.run_event_loop(authentication._loop)

        # check if there is an event in the queue
        event = queue.get_nowait()

        self.assertEqual(event.type,'send_to')
        self.assertEqual(event.data['event'],'request_token')
        self.assertIn('token',event.data)


    def test_authenticate_event(self):
        queue = asyncio.Queue()

        self.clear_database()
        authentication = Authentication(queue)
        token = authentication.request_token('admin','homecon')

        event = Event('authenticate',{'token':token},self,None)
        authentication.listen(event)

        # run the loop to fire events
        self.run_event_loop(authentication._loop)

        # check if there is an event in the queue
        event = queue.get_nowait()

        self.assertEqual(event.type,'send_to')
        self.assertEqual(event.data['event'],'authenticate')
        self.assertEqual(event.data['authenticated'],True)

"""
class AuthenticationWebsocketTests(HomeConTestCase):
    
    def test_request_token(self):
        hc = self.start_homecon()
        client = Client('ws://127.0.0.1:9024')
        client.send({'event':'request_token','username':'admin','password':'homecon'})
        

        result = client.recv()
        client.close()
        
        self.stop_homecon(hc)

        self.assertIn('token',result)
"""

if __name__ == '__main__':
    # run tests
    unittest.main()


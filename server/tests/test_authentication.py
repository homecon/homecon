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

from common import HomeConTestCase, Client

sys.path.append(os.path.abspath('..'))
from homecon import HomeCon



class AuthenticationTests(HomeConTestCase):
    

    def test_initialize(self):
        self.clear_database()
        hc = self.start_homecon()
        hc.stop()


        self.assertEqual(hc.authentication.users,{1: {'id': 1, 'permission': 9, 'username': 'admin'}})
        self.assertEqual(hc.authentication.groups,{1: {'groupname': 'admin', 'id': 1, 'permission': 9}, 2: {'groupname': 'default', 'id': 2, 'permission': 1}})


    def test_add_user(self):
        self.clear_database()
        hc = self.start_homecon()
        hc.authentication.add_user('testuser','testpassword',5)
        hc.stop()

        userid = hc.authentication.usernames['testuser']
        
        self.assertEqual(hc.authentication.users[userid], {'id': userid, 'permission': 5, 'username': 'testuser'})
        

    def test_add_group(self):
        self.clear_database()
        hc = self.start_homecon()
        hc.authentication.add_group('testgroup',2)
        hc.stop()

        groupid = hc.authentication.groupnames['testgroup']
        
        self.assertEqual(hc.authentication.groups[groupid], {'id': groupid, 'permission': 2, 'groupname': 'testgroup'})


    def test_request_token(self):
        self.clear_database()
        hc = self.start_homecon()
        hc.authentication.add_user('testuser','testpassword',5)
        token = hc.authentication.request_token('testuser','testpassword')
        payload = hc.authentication.jwt_decode(token)
        hc.stop()

        userid = hc.authentication.usernames['testuser']

        self.assertEqual(payload['userid'], userid)
        self.assertEqual(payload['groupids'], [])
        self.assertEqual(payload['permission'], 5)



class AuthenticationWebsocketTests(HomeConTestCase):
    pass
    




if __name__ == '__main__':
    # run tests
    unittest.main()


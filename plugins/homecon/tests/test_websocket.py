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
import json
from websocket import create_connection

from common import HomeConTestCase


class WebsocketTests(HomeConTestCase):

    def test_send_message(self):
        
        self.start_smarthome(sleep=5)
        
        client = create_connection("ws://127.0.0.1:9024")
        client.send('{"somekey":"somevalue"}')
        client.close()

        self.stop_smarthome()
        self.save_smarthome_log()

        # check for success in the log
        with open(self.logfile) as f:
            success = False
            for l in f:
                if 'sent {\'somekey\': \'somevalue\'}' in l:
                    success = True

            self.assertEqual(success,True)


    def test_request_token(self):
        self.start_smarthome(sleep=5)

        client = create_connection("ws://127.0.0.1:9024")
        client.send('{"cmd":"request_token","username":"admin","password":"homecon"}')
        time.sleep(1)

        result = json.loads( client.recv() )
        client.close()

        self.stop_smarthome()

        self.save_smarthome_log()

        self.assertEqual(result['cmd'],'request_token')
        self.assertNotEqual(result['token'],False)


    def test_request_token_invalid(self):
        self.start_smarthome(sleep=5)

        client = create_connection("ws://127.0.0.1:9024")
        client.send('{"cmd":"request_token","username":"admin","password":"test"}')
        time.sleep(1)

        result = json.loads( client.recv() )
        client.close()

        self.stop_smarthome()

        self.save_smarthome_log()
        
        self.assertEqual(result['cmd'],'request_token')
        self.assertEqual(result['token'],False)


    def test_authenticate(self):
        self.start_smarthome(sleep=5)

        client = create_connection("ws://127.0.0.1:9024")
        client.send('{"cmd":"request_token","username":"admin","password":"homecon"}')
        time.sleep(1)
        result = json.loads( client.recv() )

        client.send('{{"cmd":"authenticate","token":"{}"}}'.format(result['token']) )
        time.sleep(1)
        result = json.loads( client.recv() )


        client.close()

        self.stop_smarthome()

        self.save_smarthome_log()

        self.assertEqual(result['cmd'],'authenticate')
        self.assertEqual(result['authenticated'],True)


    def test_authenticate_after_restart(self):
        self.start_smarthome(sleep=5)

        client = create_connection("ws://127.0.0.1:9024")
        client.send('{"cmd":"request_token","username":"admin","password":"homecon"}')
        time.sleep(1)
        result = json.loads( client.recv() )
        client.close()

        self.stop_smarthome()
        self.save_smarthome_log('_1')

        self.start_smarthome(5)

        client = create_connection("ws://127.0.0.1:9024")
        client.send('{{"cmd":"authenticate","token":"{}"}}'.format(result['token']) )
        time.sleep(1)
        result = json.loads( client.recv() )

        client.close()

        self.stop_smarthome()

        self.save_smarthome_log('_2')

        self.assertEqual(result['cmd'],'authenticate')
        self.assertEqual(result['authenticated'],True)



if __name__ == '__main__':
    # run tests
    unittest.main()


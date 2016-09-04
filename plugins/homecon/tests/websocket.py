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
import sys
import os
import _thread

from common import HomeConTestCase

sys.path.insert(0, os.path.abspath('../../../../smarthome'))
import lib.connection


class WebsocketTests(HomeConTestCase):

    def create_client(self):
        self.connections = lib.connection.Connections()
        self.client = lib.connection.Client('127.0.0.1',9024)
        self.client.connect()

        self.client.send(b'Sec-WebSocket-Version: 13\n'+b'Sec-WebSocket-Key: abcd'+b'\r\n\r\n')
        self.connections.poll()

    def send_message(self,message):
        message = '0' + chr(len(message)) + message
        self.client.send(message.encode('utf-8'))
        self.connections.poll()
        time.sleep(0.01)

    def close_client(self):
        self.client.close()
        self.connections.close()

    def test_send_message(self):
        
        self.start_smarthome()
        time.sleep(3)

        self.create_client()
        self.send_message('{"somekey":"somevalue"}')
        self.close_client()

        self.stop_smarthome()

        self.save_smarthome_log()

        # check for success in the log
        with open(self.logfile) as f:
            success = False
            for l in f:
                if 'sent \'{"somekey":"somevalue"}\'' in l:
                    success = True

            self.assertEqual(success,True)


    def test_request_token(self):
        self.start_smarthome()
        time.sleep(3)

        self.create_client()
        self.send_message('{"cmd":"requesttoken","username":"admin","password":"homecon"}')
        time.sleep(1)
        self.close_client()

        self.stop_smarthome()

        self.save_smarthome_log()

        # check for success in the log
        with open(self.logfile) as f:
            success = False
            for l in f:
                if 'recieved token:' in l:
                    success = True

            self.assertEqual(success,True)


if __name__ == '__main__':
    # run tests
    unittest.main()


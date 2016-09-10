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

from common import HomeConTestCase,Client,import_homecon_module

class SettingsTests(HomeConTestCase):
    pass



class SettingsWebSocketTests(HomeConTestCase):
    """
    Settings tests through the websocket
    """

    def test_update_setting(self):
        self.start_smarthome(sleep=5)

        client = Client('ws://127.0.0.1:9024')
        client.send({'cmd':'request_token','username':'admin','password':'homecon'})
        time.sleep(1)
        result = client.recv()
        token = result['token']

        client.send({'cmd':'update_setting','setting':'lat','val':80,'token':token})
        time.sleep(1)
        result = client.recv()

        client.close()

        self.stop_smarthome()

        self.save_smarthome_log()
        print(result)
        self.assertEqual(result['cmd'],'update_setting')
        self.assertEqual(result['setting'],{'setting':'lat','val':80})


if __name__ == '__main__':
    # run tests
    unittest.main()


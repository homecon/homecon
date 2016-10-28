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
import sys
import os
import asyncio

from common import HomeConTestCase, Client

sys.path.append(os.path.abspath('..'))
from homecon import HomeCon
from core.plugin import Event


class EventsTests(HomeConTestCase):

    def test_fire_event(self):
        hc = self.start_homecon()
        
        event = Event('some_event',{'key': 'value'},'thesource',None)
        hc.fire(event)

        time.sleep(1)
        self.stop_homecon(hc)
        self.save_homecon_log()

        # check for success in the log
        with open(self.logfile) as f:
            success = False
            for l in f:
                if 'Event: some_event, data: {\'key\': \'value\'}, source: str, client: None' in l:
                    success = True

            self.assertEqual(success,True)

    def test_fire_event_from_plugin(self):
        hc = self.start_homecon()
        
        hc.states.fire('some_event',{'key': 'value'})


        time.sleep(1)
        self.stop_homecon(hc)
        self.save_homecon_log()

        # check for success in the log
        with open(self.logfile) as f:
            success = False
            for l in f:
                if 'Event: some_event, data: {\'key\': \'value\'}, source: States, client: None' in l:
                    success = True

            self.assertEqual(success,True)





if __name__ == '__main__':
    # run tests
    unittest.main()


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



class StatesTests(HomeConTestCase):
    
    def test_add_state(self):
        hc = self.start_homecon()
        hc.states.add('mystate')
        self.stop_homecon(hc)

        self.assertEqual(hc.states['mystate'].path, 'mystate')
    

    
    def test_children(self):
        hc = self.start_homecon()
        hc.states.add('parent')
        hc.states.add('parent.child0')
        hc.states.add('parent.child1')
        self.stop_homecon(hc)

        children = hc.states['parent'].children

        self.assertIn(hc.states['parent.child0'], children)
        self.assertIn(hc.states['parent.child1'], children)
    
    
    def test_parent(self):
        hc = self.start_homecon()
        hc.states.add('parent')
        hc.states.add('parent.child')
        self.stop_homecon(hc)

        parent = hc.states['parent.child'].parent

        self.assertEqual(hc.states['parent'], parent)
    
    def test_set(self):

        hc = self.start_homecon()
        hc.states.add('somestate')

        hc.states['somestate'].value = 1

        self.stop_homecon(hc)
        self.save_homecon_log()

        self.assertEqual(hc.states['somestate'].value,1)

        # check for success in the log
        with open(self.logfile) as f:
            success = False
            for l in f:
                if 'Event: state_changed' in l:
                    success = True

            self.assertEqual(success,True)
        


class StatesWebsocketTests(HomeConTestCase):

    def test_add_state(self):
        
        hc = self.start_homecon(print_log=True)

        client = Client('ws://127.0.0.1:9024')
        client.send({'event':'state_add','path':'somepath','config':{}})
        client.close()

        self.stop_homecon(hc)
        self.save_homecon_log()




if __name__ == '__main__':
    # run tests
    unittest.main()


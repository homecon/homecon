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

from core.plugin import Event
from core.states import States
from core.components import Components
from core.plugins.states import States as StatesPlugin
from core.plugins.websocket import DummyAdminClient


class StatesPluginTests(HomeConTestCase):

    def test_set(self):
        self.clear_database()

        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        statesPlugin = StatesPlugin(queue,states,components)
        s = states.add('somestate')


        states['somestate'].value = 1

        # run the loop to fire events
        self.run_event_loop(states._loop)

        # check if there is an event in the queue
        event = queue.get_nowait()
        self.assertEqual(event.type,'state_changed')
        self.assertEqual(event.data['state'],s)
        self.assertEqual(event.data['value'],1)
        self.assertIn('oldvalue',event.data)


    def test_add_state_event(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        statesPlugin = StatesPlugin(queue,states,components)
        event = Event('add_state',{'path':'mystate','config':{'prop1':'val1'}},self,None)
        statesPlugin._listen(event)

        self.assertEqual(states['mystate'].path, 'mystate')
        self.assertEqual(states['mystate'].config['prop1'], 'val1')


    def test_state_event_set(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        statesPlugin = StatesPlugin(queue,states,components)
        states.add('somestate',config={'prop1':'val1'})

        client = DummyAdminClient()

        event = Event('state',{'path':'somestate','value':1},self,client)
        statesPlugin._listen(event)

        # run the loop to fire events
        self.run_event_loop(states._loop)
        
        # check if there is an event in the queue
        event = queue.get_nowait()
        self.assertEqual(event.type,'state_changed')
        self.assertEqual(event.data['state'].path,'somestate')
        self.assertEqual(event.data['value'],1)
        self.assertIn('oldvalue',event.data)


    def test_state_event_get(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        statesPlugin = StatesPlugin(queue,states,components)
        states.add('somestate',config={'prop1':'val1'})

        client = DummyAdminClient()

        event = Event('state',{'path':'somestate'},self,client)
        statesPlugin._listen(event)

        # run the loop to fire events
        self.run_event_loop(states._loop)

        # check if there is an event in the queue
        event = queue.get_nowait()
        self.assertEqual(event.type,'send_to')
        self.assertEqual(event.data['path'],'somestate')
        self.assertEqual(event.data['clients'],[client])
        self.assertIn('value',event.data)


if __name__ == '__main__':
    # run tests
    unittest.main()


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
from core.states import States


class StatesTests(HomeConTestCase):
    
    def test_add(self):
        queue = asyncio.Queue()

        states = States(queue)
        states.add('mystate')

        self.assertEqual(states['mystate'].path, 'mystate')


    def test_add_state_event(self):
        queue = asyncio.Queue()

        states = States(queue)
        event = Event('add_state',{'path':'mystate','config':{'prop1':'val1'}},self,None)
        states.listen(event)

        self.assertEqual(states['mystate'].path, 'mystate')
        self.assertEqual(states['mystate'].config['prop1'], 'val1')


    def test_children(self):
        queue = asyncio.Queue()

        states = States(queue)
        states.add('parent')
        states.add('parent.child0')
        states.add('parent.child1')

        children = states['parent'].children

        self.assertIn(states['parent.child0'], children)
        self.assertIn(states['parent.child1'], children)


    def test_parent(self):
        queue = asyncio.Queue()

        states = States(queue)
        states.add('parent')
        states.add('parent.child')

        parent = states['parent.child'].parent

        self.assertEqual(states['parent'], parent)


    def test_set(self):
        queue = asyncio.Queue()

        states = States(queue)
        s = states.add('somestate')

        states['somestate'].value = 1

        # run the loop to fire fire events
        async def spam():
            asyncio.sleep(0.1)
        states._loop.run_until_complete(spam())

        # check if there is an event in the queue
        event = queue.get_nowait()
        self.assertEqual(event.type,'state_changed')
        self.assertEqual(event.data['state'],s)
        self.assertEqual(event.data['value'],1)
        self.assertIn('oldvalue',event.data)


    def test_set_state_event(self):
        queue = asyncio.Queue()

        states = States(queue)
        event = Event('add_state',{'path':'somestate','config':{'prop1':'val1'}},self,None)
        states.listen(event)

        event = Event('set_state',{'path':'somestate','value':1},self,None)
        states.listen(event)

        # run the loop to fire fire events
        async def spam():
            asyncio.sleep(0.1)
        states._loop.run_until_complete(spam())

        # check if there is an event in the queue
        event = queue.get_nowait()
        self.assertEqual(event.type,'state_changed')
        self.assertEqual(event.data['state'].path,'somestate')
        self.assertEqual(event.data['value'],1)
        self.assertIn('oldvalue',event.data)

if __name__ == '__main__':
    # run tests
    unittest.main()


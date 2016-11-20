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

from core.states import States


class StatesTests(HomeConTestCase):
    
    def test_add(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States()
        states.add('mystate')

        self.assertEqual(states['mystate'].path, 'mystate')


    def test_reinitialize(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States()
        states.add('mystate')
        
        states = States()

        self.assertEqual(states['mystate'].path, 'mystate')


    def test_children(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States()
        states.add('parent')
        states.add('parent/child0')
        states.add('parent/child1')

        children = states['parent'].children

        self.assertIn(states['parent/child0'], children)
        self.assertIn(states['parent/child1'], children)


    def test_parent(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States()
        states.add('parent')
        states.add('parent/child')

        parent = states['parent/child'].parent

        self.assertEqual(states['parent'], parent)


if __name__ == '__main__':
    # run tests
    unittest.main()


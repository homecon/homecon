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

sys.path.append(os.path.abspath('..'))
from homecon import HomeCon

class StatesTests(unittest.TestCase):

    def test_add_state(self):
        hc = HomeCon()
        hc.states.add('mystate')

        self.assertEqual(hc.states['mystate'].path, 'mystate')
        hc.stop()


    def test_children(self):
        hc = HomeCon()
        hc.states.add('parent')
        hc.states.add('parent.child0')
        hc.states.add('parent.child1')

        children = hc.states['parent'].children

        self.assertIn(hc.states['parent.child0'], children)
        self.assertIn(hc.states['parent.child1'], children)
        hc.stop()


    def test_parent(self):
        hc = HomeCon()
        hc.states.add('parent')
        hc.states.add('parent.child')

        parent = hc.states['parent.child'].parent

        self.assertEqual(hc.states['parent'], parent)
        hc.stop()

if __name__ == '__main__':
    # run tests
    unittest.main()


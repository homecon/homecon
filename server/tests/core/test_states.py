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

sys.path.append(os.path.abspath('..'))
import common

import homecon.core.state
import homecon.core.event as event
import homecon.coreplugins.states

class StatesTests(unittest.TestCase):

    def test_add(self):
        common.clear_database()
        states = homecon.core.state.States()

        states.add('mystate')

        self.assertEqual(states['mystate'].path, 'mystate')


    def test_reinitialize(self):
        common.clear_database()
        states = homecon.core.state.States()

        states.add('mystate')

        states = None
        homecon.core.state.State.container = {}

        states = homecon.core.state.States()
        self.assertEqual(states['mystate'].path, 'mystate')


    def test_trigger(self):
        common.clear_database()
        states = homecon.core.state.States()

        states.add('mystate',config={'someattr':True})
        states.add('myotherstate',config={'someattr':True})
        states.add('mycomputedstate',config={'triggers':'[state.path for state in states.values() if (`someattr` in state.config and state.config[`someattr`])]','computed':'5*states[`mystate`].value'})

        self.assertEqual(states['mystate'].trigger, [states['mycomputedstate']])
        self.assertEqual(states['myotherstate'].trigger, [states['mycomputedstate']])
        self.assertEqual(states['mycomputedstate'].trigger, [])


    def test_trigger_reinitialize(self):
        common.clear_database()
        states = homecon.core.state.States()

        states.add('mystate',config={'someattr':True})
        states.add('myotherstate',config={'someattr':True})
        states.add('mycomputedstate',config={'triggers':'[state.path for state in states.values() if (`someattr` in state.config and state.config[`someattr`])]','computed':'5*states[`mystate`].value'})

        states = None
        homecon.core.state.State.container = {}

        states = homecon.core.state.States()

        self.assertEqual(states['mystate'].trigger, [states['mycomputedstate']])
        self.assertEqual(states['myotherstate'].trigger, [states['mycomputedstate']])
        self.assertEqual(states['mycomputedstate'].trigger, [])


    def test_trigger_delete(self):
        common.clear_database()
        states = homecon.core.state.States()

        states.add('mystate',config={'someattr':True})
        states.add('myotherstate',config={'someattr':True})
        states.add('mycomputedstate',config={'triggers':'[state.path for state in states.values() if (`someattr` in state.config and state.config[`someattr`])]','computed':'5*states[`mystate`].value'})

        states.delete('myotherstate')
        self.assertEqual(states['mystate'].trigger, [states['mycomputedstate']])
        self.assertEqual(states['mycomputedstate'].trigger, [])


    def test_computed(self):
        common.clear_database()
        states = homecon.core.state.States()

        states.add('mystate',config={'someattr':True})
        states.add('myotherstate',config={'someattr':True})
        states.add('mycomputedstate',config={'triggers':'[state.path for state in states.values() if (`someattr` in state.config and state.config[`someattr`])]','computed':'sum([state.value for state in states.values() if (`someattr` in state.config and state.config[`someattr`])])'})

        # set values
        states['mystate'].set(10,async=False)
        states['myotherstate'].set(20,async=False)

        self.assertEqual(states['mycomputedstate'].value, 10+20)

if __name__ == '__main__':
    # run tests
    unittest.main()


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
import sys
import os

sys.path.append(os.path.abspath('..'))
import common

import homecon.core.state
import homecon.core.component

class Mycomponent(homecon.core.component.Component):
    pass

class Mysubcomponent(Mycomponent):
    pass


class ComponentsTests(unittest.TestCase):

    def test_register_component(self):
        common.clear_database()

        states = homecon.core.state.States()
        components = homecon.core.component.Components()
        components.register(Mycomponent)

        self.assertEqual(components._component_types,{'mycomponent':Mycomponent})


    def test_add(self):
        common.clear_database()

        states = homecon.core.state.States()
        components = homecon.core.component.Components()
        components.register(Mycomponent)

        components.add('mycomponent1','mycomponent')
        self.assertEqual(components['mycomponent1'].path, 'mycomponent1')


    def test_reinitialize(self):
        common.clear_database()

        states = homecon.core.state.States()
        components = homecon.core.component.Components()
        components.register(Mycomponent)

        components.add('mycomponent1','mycomponent')
        
        components = None
        homecon.core.component.Component.container = {}

        components = homecon.core.component.Components()
        components.register(Mycomponent)
        components.load()

        self.assertEqual(components['mycomponent1'].path, 'mycomponent1')


    def test_type(self):
        common.clear_database()

        states = homecon.core.state.States()
        components = homecon.core.component.Components()
        components.register(Mycomponent)
        components.register(Mysubcomponent)

        components.add('mycomponent1','mysubcomponent')
        self.assertEqual(components['mycomponent1'].type, 'mysubcomponent')


    def test_find_type(self):
        common.clear_database()

        states = homecon.core.state.States()
        components = homecon.core.component.Components()
        components.register(Mycomponent)
        components.register(Mysubcomponent)

        components.add('mycomponent1','mycomponent')
        components.add('mycomponent2','mycomponent')
        components.add('mycomponent3','mysubcomponent')
        components.add('mycomponent4','mysubcomponent')

        found = components.find(type='mycomponent')
        self.assertIn(components['mycomponent1'],found)
        self.assertIn(components['mycomponent2'],found)
        self.assertIn(components['mycomponent3'],found)
        self.assertIn(components['mycomponent4'],found)

        found = components.find(type='mysubcomponent')
        self.assertNotIn(components['mycomponent1'],found)
        self.assertNotIn(components['mycomponent2'],found)
        self.assertIn(components['mycomponent3'],found)
        self.assertIn(components['mycomponent4'],found)


    def test_find_type_strict(self):
        common.clear_database()

        states = homecon.core.state.States()
        components = homecon.core.component.Components()
        components.register(Mycomponent)
        components.register(Mysubcomponent)

        components.add('mycomponent1','mycomponent')
        components.add('mycomponent2','mycomponent')
        components.add('mycomponent3','mysubcomponent')
        components.add('mycomponent4','mysubcomponent')

        found = components.find(type_strict='mycomponent')
        self.assertIn(components['mycomponent1'],found)
        self.assertIn(components['mycomponent2'],found)
        self.assertNotIn(components['mycomponent3'],found)
        self.assertNotIn(components['mycomponent4'],found)


if __name__ == '__main__':
    # run tests
    unittest.main()


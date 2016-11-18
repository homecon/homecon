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
from core.plugins.components import Components as ComponentsPlugin
from core.plugins.websocket import DummyAdminClient


class ComponentsPluginTests(HomeConTestCase):

    def test_initialize(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = States(queue)
        components = Components(queue,states)

        componentsPlugin = ComponentsPlugin(queue,states,components)


    def test_add_component_event_value(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = States(queue)
        components = Components(queue,states)

        componentsPlugin = ComponentsPlugin(queue,states,components)
        event = Event('add_component',{'path':'mycomponent','type':'value','config':{'prop1':'val1'}},self,None)
        componentsPlugin._listen(event)

        self.assertEqual(components['mycomponent'].path, 'mycomponent')
        self.assertEqual(components['mycomponent'].config['prop1'], 'val1')
        self.assertIn('mycomponent/value',states)

    def test_list(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = States(queue)
        components = Components(queue,states)

        componentsPlugin = ComponentsPlugin(queue,states,components)
        event = Event('add_component',{'path':'mycomponent1','type':'value','config':{'prop1':'val1'}},self,None)
        componentsPlugin._listen(event)
        event = Event('add_component',{'path':'mycomponent2','type':'value','config':{'prop1':'val1'}},self,None)
        componentsPlugin._listen(event)

        componentslist = componentsPlugin.list()

        self.assertEqual(componentslist[0]['path'], 'mycomponent1')
        self.assertEqual(componentslist[1]['path'], 'mycomponent2')
        self.assertEqual(componentslist[0]['states'], ['mycomponent1/value'])
        self.assertEqual(componentslist[1]['states'], ['mycomponent2/value'])



if __name__ == '__main__':
    # run tests
    unittest.main()


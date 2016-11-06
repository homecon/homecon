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
from core.plugin import Plugins


class PluginsTests(HomeConTestCase):
    
    def test_initialize(self):
        queue = asyncio.Queue()


        self.clear_database()
        states = States(queue)
        plugins = Plugins(queue,states)

    def test_activate_plugin(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States(queue)
        plugins = Plugins(queue,states)
        plugins.activate('knx')

        self.assertIn('knx',plugins.keys())

    def test_remember_active_plugins(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States(queue)
        plugins = Plugins(queue,states)
        plugins.activate('knx')

        del plugins
        del states

        states = States(queue)
        plugins = Plugins(queue,states)

        self.assertIn('knx',plugins.keys())


if __name__ == '__main__':
    # run tests
    unittest.main()


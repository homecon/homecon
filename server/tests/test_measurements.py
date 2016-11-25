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
import datetime
import json
import sys
import os
import asyncio

from common import HomeConTestCase, Client

sys.path.append(os.path.abspath('..'))

from core.plugin import Event
from core.states import States
from core.components import Components
from core.plugins.measurements import Measurements
from core.plugins.websocket import DummyAdminClient


class MeasurementsPluginTests(HomeConTestCase):

    def test_initialize(self):
        self.clear_database()

        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        measurements = Measurements(queue,states,components)


    def test_add(self):
        self.clear_database()

        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        measurements = Measurements(queue,states,components)

        s = states.add('somestate')
        s.value = 1

        measurements.add(s.path,s.value)
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = int( (dt_now-dt_ref).total_seconds() )

        data = measurements._db_measurements.GET(path=s.path)

        self.assertEqual(len(data),1)
        self.assertEqual(data[0]['path'],'somestate')
        self.assertEqual(json.loads(data[0]['value']),1)
        self.assertLess(abs(data[0]['time']-timestamp_now),2)

        self.assertEqual(measurements.measurements,{})


    def test_add_two(self):
        self.clear_database()

        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        measurements = Measurements(queue,states,components)

        s = states.add('somestate')
        s.value = 1

        measurements.add(s.path,1)
        measurements.add(s.path,0)

        data = measurements._db_measurements.GET(path=s.path)

        self.assertEqual(len(data),2)


    def test_get(self):
        self.clear_database()

        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        measurements = Measurements(queue,states,components)

        s = states.add('somestate')
        s.value = 1

        measurements.add(s.path,1)
        measurements.add(s.path,0)


        data = measurements.get(path=s.path)
        self.assertEqual(len(data),2)


    def test_get_cache(self):
        self.clear_database()

        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        measurements = Measurements(queue,states,components)

        s = states.add('somestate')
        s.value = 1

        measurements.add(s.path,1)
        measurements.add(s.path,0)

        measurements.get(path=s.path)

        data = measurements.measurements[s.path]

        self.assertEqual(len(data),2)


if __name__ == '__main__':
    # run tests
    unittest.main()


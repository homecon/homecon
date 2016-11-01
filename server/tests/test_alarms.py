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
import json
import sys
import os
import datetime
import pytz
import asyncio

from common import HomeConTestCase, Client

sys.path.append(os.path.abspath('..'))
#from homecon import HomeCon
from core.plugin import Event
from core.states import States
from core.alarms import Alarms
from core.websocket import DummyAdminClient


class AlarmsTests(HomeConTestCase):
    
    def test_initialize(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States(queue)
        alarms = Alarms(queue,states)


    def test_schedule_alarm(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States(queue)
        alarms = Alarms(queue,states)

        states['settings/timezone'].value = 'Europe/Brussels'

        state = states.add('alarms/myalarm/1',config={'type':'alarm'})
        state.value = {
            'year': None,
            'month': None,
            'day': None,
            'hour': 20,
            'minute': 0,
            'mon': None,
            'tue': None,
            'wed': None,
            'thu': None,
            'fri': None,
            'sat': None,
            'sun': None,
            'action': 'actions/myaction'
        }

        alarms.schedule_alarm(state)

        # convert when to a datetime
        timezone = pytz.timezone(states['settings/timezone'].value)
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = (dt_now-dt_ref).total_seconds()

        timestamp_when = timestamp_now + alarms._schedule['alarms/myalarm/1'].handle._when - alarms._loop.time()
        dt_when = pytz.utc.localize( datetime.datetime.utcfromtimestamp(timestamp_when) ).astimezone(timezone)

        self.assertIn('alarms/myalarm/1',alarms._schedule)
        self.assertEqual(dt_when.hour,20)
        self.assertEqual(dt_when.minute,0)
        self.assertLess(abs(alarms._schedule['alarms/myalarm/1'].timestamp-timestamp_when),5) # 5 second tolerance

    def test_reschedule_alarm(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States(queue)
        alarms = Alarms(queue,states)

        states['settings/timezone'].value = 'Europe/Brussels'
        


        state = states.add('alarms/myalarm/1',config={'type':'alarm'})
        state.value = {
            'year': None,
            'month': None,
            'day': None,
            'hour': 20,
            'minute': 0,
            'mon': None,
            'tue': None,
            'wed': None,
            'thu': None,
            'fri': None,
            'sat': None,
            'sun': None,
            'action': 'actions/myaction'
        }

        alarms.schedule_alarm(state)


        state.value['minute'] = 5

        alarms.schedule_alarm(state)

        # convert when to a datetime
        timezone = pytz.timezone(states['settings/timezone'].value)
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = (dt_now-dt_ref).total_seconds()

        timestamp_when = timestamp_now + alarms._schedule['alarms/myalarm/1'].handle._when - alarms._loop.time()
        dt_when = pytz.utc.localize( datetime.datetime.utcfromtimestamp(timestamp_when) ).astimezone(timezone)

        self.assertIn('alarms/myalarm/1',alarms._schedule)
        self.assertEqual(dt_when.hour,20)
        self.assertEqual(dt_when.minute,5)


    def test_restart_alarms(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States(queue)
        alarms = Alarms(queue,states)

        states['settings/timezone'].value = 'Europe/Brussels'

        state = states.add('alarms/myalarm/1',config={'type':'alarm'})
        state.value = {
            'year': None,
            'month': None,
            'day': None,
            'hour': 20,
            'minute': 0,
            'mon': None,
            'tue': None,
            'wed': None,
            'thu': None,
            'fri': None,
            'sat': None,
            'sun': None,
            'action': 'actions/myaction'
        }

        alarms.schedule_alarm(state)

        del alarms

        newalarms = Alarms(queue,states)

        # convert when to a datetime
        timezone = pytz.timezone(states['settings/timezone'].value)
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = (dt_now-dt_ref).total_seconds()

        timestamp_when = timestamp_now + newalarms._schedule['alarms/myalarm/1'].handle._when - newalarms._loop.time()
        dt_when = pytz.utc.localize( datetime.datetime.utcfromtimestamp(timestamp_when) ).astimezone(timezone)

        self.assertIn('alarms/myalarm/1',newalarms._schedule)
        self.assertEqual(dt_when.hour,20)
        self.assertEqual(dt_when.minute,0)


    def test_run_action(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States(queue)
        alarms = Alarms(queue,states)

        state1 = states.add('somestate',config={'type':'number'})
        state2 = states.add('someotherstate',config={'type':'number'})

        action = states.add('actions/myaction',config={'type':'action'})
        action.value = [
            ('somestate',20,0),
            ('someotherstate',10.1,2),
        ]

        alarms.run_action(action)

        # run the loop to fire events
        self.run_event_loop(alarms._loop)
        event = queue.get_nowait()
        states._listen(event)

        self.run_event_loop(alarms._loop)

        # check if there is an event in the queue
        event = queue.get_nowait()
        self.assertEqual(event.type,'state')
        self.assertEqual(event.data,{'path':'somestate','value':20})



if __name__ == '__main__':
    # run tests
    unittest.main()


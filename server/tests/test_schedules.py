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
from core.schedules import Schedules,Actions
from core.websocket import DummyAdminClient


class AlarmsTests(HomeConTestCase):
    
    def test_initialize(self):
        queue = asyncio.Queue()

        self.clear_database()
        schedules = Schedules(queue)


    def test_schedule(self):
        queue = asyncio.Queue()

        self.clear_database()
        schedules = Schedules(queue)

        # set the timezone
        schedules.listen_state_changed(Event('state_changed',{'path':'settings/timezone','value':'Europe/Brussels'},None,None))

        schedule = schedules.add(
            'myschedule',
            {'filters':[]},
            {
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
        )

        schedules.schedule(schedule)

        # convert when to a datetime
        timezone = schedules.timezone
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = (dt_now-dt_ref).total_seconds()

        timestamp_when = timestamp_now + schedules._scheduled['myschedule'].handle._when - schedules._loop.time()
        dt_when = pytz.utc.localize( datetime.datetime.utcfromtimestamp(timestamp_when) ).astimezone(timezone)

        self.assertIn('myschedule',schedules._scheduled)
        self.assertEqual(dt_when.hour,20)
        self.assertEqual(dt_when.minute,0)
        self.assertLess(abs(schedules._scheduled['myschedule'].timestamp-timestamp_when),5) # 5 second tolerance


    def test_reschedule_alarm(self):
        queue = asyncio.Queue()

        self.clear_database()
        schedules = Schedules(queue)

        # set the timezone
        schedules.listen_state_changed(Event('state_changed',{'path':'settings/timezone','value':'Europe/Brussels'},None,None))

        schedule = schedules.add(
            'myschedule',
            {'filters':[]},
            {
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
        )

        schedules.schedule(schedule)


        schedule.value['minute'] = 5

        schedules.schedule(schedule)

        # convert when to a datetime
        timezone = schedules.timezone
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = (dt_now-dt_ref).total_seconds()

        timestamp_when = timestamp_now + schedules._scheduled['myschedule'].handle._when - schedules._loop.time()
        dt_when = pytz.utc.localize( datetime.datetime.utcfromtimestamp(timestamp_when) ).astimezone(timezone)

        self.assertIn('myschedule',schedules._scheduled)
        self.assertEqual(dt_when.hour,20)
        self.assertEqual(dt_when.minute,5)


    def test_restart_alarms(self):
        queue = asyncio.Queue()

        self.clear_database()
        schedules = Schedules(queue)

        # set the timezone
        schedules.listen_state_changed(Event('state_changed',{'path':'settings/timezone','value':'Europe/Brussels'},None,None))

        schedule = schedules.add(
            'myschedule',
            {'filters':[]},
            {
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
        )

        schedules.schedule(schedule)

        del schedules

        schedules = Schedules(queue)

        # convert when to a datetime
        timezone = schedules.timezone
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = (dt_now-dt_ref).total_seconds()

        timestamp_when = timestamp_now + schedules._scheduled['myschedule'].handle._when - schedules._loop.time()
        dt_when = pytz.utc.localize( datetime.datetime.utcfromtimestamp(timestamp_when) ).astimezone(timezone)

        self.assertIn('myschedule',schedules._scheduled)
        self.assertEqual(dt_when.hour,20)
        self.assertEqual(dt_when.minute,0)


    def test_add_action(self):
        queue = asyncio.Queue()

        self.clear_database()
        actions = Actions(queue)

        action = actions.add(
            'myaction',
            {'type':'action'},
            [
                ('somestate',20,0),
                ('someotherstate',10.1,2),
            ]
        )

        self.assertIn('myaction',actions._actions)


    """
    def test_run_action(self):
        queue = asyncio.Queue()

        self.clear_database()
        states = States(queue)
        actions = Actions(queue)

        state1 = states.add('somestate',config={'type':'number'})
        state2 = states.add('someotherstate',config={'type':'number'})

        action = actions.add('actions/myaction',config={'type':'action'})
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
    """


if __name__ == '__main__':
    # run tests
    unittest.main()


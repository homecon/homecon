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

import datetime
import numpy as np
import time

from homecon.tests import common
from homecon.core.database import get_database
from homecon.core.state import State, get_states_table


class TestState(common.TestCase):
    def test_add(self):
        s = State.add('mystate')
        self.assertEqual('mystate', get_database()(get_states_table()).select()[0]['path'])
        self.assertTrue(get_states_table()._db._uri.endswith('test_homecon.db'))
        self.assertEqual('mystate', State.get(path='mystate').path)
        self.assertEqual('mystate', s.path)

    def test_read_write_speed(self):
        s = State.add('mystate')
        start = time.time()
        for i in range(100):
            s.value = i
            v = s.value
        stop = time.time()
        self.assertLess(stop-start, 1)

    def test_triggers(self):
        State.add('mystate', config={'someattr': True})
        State.add('myotherstate', config={'someattr': True})
        State.add('mycomputedstate', config={
            'triggers': '[state.path for state in State.all()'
                        ' if (`someattr` in state.config and state.config[`someattr`])]',
            'computed': '5*State.get(`mystate`).value + State.get(`myotherstate`).value'})
        self.assertEqual(State.get('mycomputedstate').triggers, ['mystate', 'myotherstate'])
        self.assertEqual(State.get('mystate').triggers, [])
        self.assertEqual(State.get('myotherstate').triggers, [])

    def test_computed(self):
        State.add('mystate', config={'someattr': True})
        State.add('myotherstate', config={'someattr': True})
        State.add('mycomputedstate', config={
            'triggers': '[state.path for state in State.all()'
                        ' if (`someattr` in state.config and state.config[`someattr`])]',
            'computed': '5*State.get(`mystate`).value + np.exp(State.get(`myotherstate`).value)'})
        State.get('mystate').value = 10
        State.get('myotherstate').value = 5
        self.assertEqual(State.get('mycomputedstate').computed, 50 + np.exp(5))


    # def test_trigger(self):
    #     State.add('mystate', config={'someattr': True})
    #     State.add('myotherstate', config={'someattr': True})
    #     State.add('mycomputedstate', config={
    #         'triggers': '[state.path for state in State.all()'
    #                     ' if (`someattr` in state.config and state.config[`someattr`])]',
    #         'computed': '5*states[`mystate`].value'})
    #
    #     self.assertEqual(State.get('mystate').triggers, ['mycomputedstate'])
    #     self.assertEqual(State.get('myotherstate').triggers, ['mycomputedstate'])
    #     self.assertEqual(State.get('mycomputedstate').triggers, [])

    #
    # def test_trigger_reinitialize(self):
    #     states = homecon.core.states
    #
    #     states.add('mystate',config={'someattr':True})
    #     states.add('myotherstate',config={'someattr':True})
    #     states.add('mycomputedstate',config={'triggers':'[state.path for state in states.values() if (`someattr` in state.config and state.config[`someattr`])]','computed':'5*states[`mystate`].value'})
    #
    #     states = None
    #     homecon.core.state.State.container = {}
    #
    #     states = homecon.core.states
    #
    #     self.assertEqual(states['mystate'].trigger, [states['mycomputedstate']])
    #     self.assertEqual(states['myotherstate'].trigger, [states['mycomputedstate']])
    #     self.assertEqual(states['mycomputedstate'].trigger, [])
    #
    #
    # def test_trigger_delete(self):
    #     states = homecon.core.states
    #
    #     states.add('mystate',config={'someattr':True})
    #     states.add('myotherstate',config={'someattr':True})
    #     states.add('mycomputedstate',config={'triggers':'[state.path for state in states.values() if (`someattr` in state.config and state.config[`someattr`])]','computed':'5*states[`mystate`].value'})
    #
    #     states.delete('myotherstate')
    #     self.assertEqual(states['mystate'].trigger, [states['mycomputedstate']])
    #     self.assertEqual(states['mycomputedstate'].trigger, [])
    #
    #
    # def test_computed(self):
    #     states = homecon.core.states
    #
    #     states.add('mystate',config={'someattr':True})
    #     states.add('myotherstate',config={'someattr':True})
    #     states.add('mycomputedstate',config={'triggers':'[state.path for state in states.values() if (`someattr` in state.config and state.config[`someattr`])]','computed':'sum([state.value for state in states.values() if (`someattr` in state.config and state.config[`someattr`])])'})
    #
    #     # set values
    #     states['mystate'].set(10,async=False)
    #     states['myotherstate'].set(20,async=False)
    #
    #     self.assertEqual(states['mycomputedstate'].value, 10+20)
    #
    #
    # def test_history(self):
    #     states = homecon.core.states
    #
    #     mystate = states.add('mystate')
    #
    #     # add data tot the database
    #     timestamps = np.array([ int( (datetime.datetime.utcnow()-datetime.datetime(1970, 1, 1)).total_seconds() ) + 100*(i-10) for i in range(10) ])
    #     values = np.array([i for i,ts in enumerate(timestamps)])
    #
    #
    #     connection,cursor = homecon.core.measurements_db.create_cursor()
    #     for ts,val in zip(timestamps,values):
    #         cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(ts,'\'{}\''.format(mystate.path),val  ))
    #     connection.commit()
    #     connection.close()
    #
    #     hist = mystate.history(timestamps)
    #
    #     self.assertEqual(max(abs(hist-values)), 0)
    #
    #
    # def test_history_interpolate(self):
    #     states = homecon.core.states
    #
    #     mystate = states.add('mystate')
    #
    #     # add data tot the database
    #     timestamps = np.array([ int( (datetime.datetime.utcnow()-datetime.datetime(1970, 1, 1)).total_seconds() ) + 100*(i-10) for i in range(10) ])
    #     values = np.array([i for i,ts in enumerate(timestamps)])
    #
    #
    #     connection,cursor = homecon.core.measurements_db.create_cursor()
    #     for ts,val in zip(timestamps,values):
    #         cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(ts,'\'{}\''.format(mystate.path),val  ))
    #     connection.commit()
    #     connection.close()
    #
    #     intermediatetimestamps = timestamps[1:]-50
    #     hist = mystate.history(intermediatetimestamps)
    #
    #     self.assertEqual(max(abs(hist-np.interp(intermediatetimestamps,timestamps,values))), 0)
    #
    #
    # def test_history_extrapolate(self):
    #     states = homecon.core.states
    #
    #     mystate = states.add('mystate')
    #
    #     # add data tot the database
    #     timestamps = np.array([ int( (datetime.datetime.utcnow()-datetime.datetime(1970, 1, 1)).total_seconds() ) + 100*(i-10) for i in range(10) ])
    #     values = np.array([i for i,ts in enumerate(timestamps)])
    #
    #
    #     connection,cursor = homecon.core.measurements_db.create_cursor()
    #     for ts,val in zip(timestamps,values):
    #         cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(ts,'\'{}\''.format(mystate.path),val  ))
    #     connection.commit()
    #     connection.close()
    #
    #     intermediatetimestamps = timestamps-250
    #     hist = mystate.history(intermediatetimestamps)
    #
    #     self.assertTrue(np.isnan(hist[0]))
    #     self.assertTrue(np.isnan(hist[1]))
    #     self.assertTrue(np.isnan(hist[2]))
    #
    #
    # def test_history_nodata(self):
    #     states = homecon.core.states
    #
    #     mystate = states.add('mystate')
    #
    #     timestamps = np.array([ int( (datetime.datetime.utcnow()-datetime.datetime(1970, 1, 1)).total_seconds() ) + 100*(i-10) for i in range(10) ])
    #     values = np.array([i for i,ts in enumerate(timestamps)])
    #
    #
    #     connection,cursor = homecon.core.measurements_db.create_cursor()
    #     for ts,val in zip(timestamps,values):
    #         cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(ts,'\'{}\''.format(mystate.path),val  ))
    #     connection.commit()
    #     connection.close()
    #
    #     hist = mystate.history(timestamps-10000)
    #     self.assertTrue(all(np.isnan(hist)))
    #
    #
    #
    #

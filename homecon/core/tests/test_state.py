#!/usr/bin/env python3
################################################################################
#    Copyright 2018 Brecht Baeten
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
from homecon.core.state import State


class TestState(common.TestCase):
    def test_add(self):
        s = State.add('mystate')
        db, table = State.get_table()
        self.assertEqual('mystate', db(db.states).select()[0]['name'])
        print(db._uri)
        self.assertTrue(db._uri.endswith('db_test/homecon.db'))
        self.assertEqual('mystate', State.get(path='/mystate').name)
        self.assertEqual('/mystate', s.path)

    def test_add_parent_id(self):
        s0 = State.add('mystate')
        kwargs = {'name': 'living', 'parent': 1, 'type': '', 'quantity': '', 'unit': '', 'label': '', 'description': '',
                  'config': {}}
        name =kwargs.pop('name')
        s1 = State.add(name, **kwargs)

    def test_re_add(self):
        s0 = State.add('mystate')
        s1 = State.add('mystate')
        self.assertEqual(s0, s1)

    def test_get(self):
        s1a = State.add('parent1')
        s1b = State.add('parent2')
        s2a = State.add('substate1', parent=s1a)
        s2b = State.add('substate1', parent=s1b)
        s = State.get(path='/parent2/substate1')
        self.assertEqual(s, s2b)
        s = State.get(path='/parent1')
        self.assertEqual(s, s1a)

    def test_update(self):
        s = State.add('mystate')
        s.update(name='test')
        self.assertEqual(s.name, 'test')

    def test_parent(self):
        s1 = State.add('mystate')
        s2 = State.add('substate', parent=s1)
        s3 = State.add('substate2', parent='/mystate')
        self.assertEqual('mystate', s2.parent.name)
        self.assertEqual('mystate', s3.parent.name)

    def test_full_path(self):
        s1 = State.add('mystate')
        s2 = State.add('substate', parent=s1)
        self.assertEqual('/mystate', s1.path)
        self.assertEqual('/mystate/substate', s2.path)

    def test_children(self):
        s1 = State.add('mystate')
        s2a = State.add('substate_a', parent=s1)
        s2b = State.add('substate_b', parent=s1)
        State.add('mynewstate')
        children = s1.children
        self.assertEqual(len(children), 2)
        self.assertIn(s2a, children)
        self.assertIn(s2b, children)

    def test_read_write_speed(self):
        s = State.add('mystate')
        start = time.time()
        for i in range(50):
            s.value = i
            v = s.value
        stop = time.time()
        self.assertLess(stop-start, 1)

    def test_all(self):
        State.add('mystate1')
        State.add('mystate2')
        states = State.all()
        self.assertEqual(states[0].path, '/mystate1')
        self.assertEqual(states[1].path, '/mystate2')

    def test_triggers(self):
        State.add('mystate', config={'someattr': True})
        State.add('myotherstate', config={'someattr': True})
        State.add('mycomputedstate', config={
            'triggers': '[state.path for state in State.all()'
                        ' if (`someattr` in state.config and state.config[`someattr`])]',
            'computed': '5*State.get(`mystate`).value + State.get(`myotherstate`).value'})
        self.assertEqual(State.get('mycomputedstate').triggers, ['/mystate', '/myotherstate'])
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

    def test_find(self):
        State.add('parent/child1/state')
        State.add('parent/child2/state')
        State.add('parent/aha/state')
        states = State.find('.*/child.*/state')
        print(states)

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

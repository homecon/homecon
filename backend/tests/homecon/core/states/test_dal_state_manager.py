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
import os
import shutil
import numpy as np
import time

from unittest import TestCase
from homecon.core.states.state import State
from homecon.core.states.dal_state_manager import DALStateManager
from homecon.core.event import EventManager


class TestDALStateManager(TestCase):
    DB_DIR = 'db'
    DB_URI = 'sqlite://test.db'

    def setUp(self):
        try:
            shutil.rmtree(self.DB_DIR)
        except FileNotFoundError:
            pass
        os.mkdir(self.DB_DIR)

    def tearDown(self):
        try:
            shutil.rmtree(self.DB_DIR)
        except FileNotFoundError:
            pass

    def test_add(self):
        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s = state_manager.add('mystate')

        assert s.name == 'mystate'
        assert s.parent is None
        assert s.value is None
        assert s.log_key == s.NO_LOGGING_KEY

        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s = state_manager.get(key=s.key)
        assert s.name == 'mystate'
        assert s.parent is None
        assert s.value is None

    def test_add_child(self):
        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s0 = state_manager.add('parent')
        s1 = state_manager.add('child', parent=s0)

        assert s1.parent.name == 'parent'
        assert s0.children[0].name == 'child'

        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s0 = state_manager.get(key=s0.key)
        assert s0.children[0].name == 'child'

    def test_update(self):
        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s = state_manager.add('mystate')
        s.update(name='test')
        assert s.name == 'test'
        key = s.key
        print(key)

        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s = state_manager.get(path='/test')
        assert s.key == key

    def test_update_log_values(self):
        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s0 = state_manager.add('myotherstate', value=20, log_key=None)
        assert s0.log_key is not None

        s1 = state_manager.add('mystate', value=5, log_key=None)
        assert s1.log_key is not None

        s1.update(value={'test': 123})
        assert s1.value == {'test': 123}

        timeseries0 = state_manager.get_state_values_log(s0, since=0.)
        assert len(timeseries0) == 1
        assert timeseries0[0].value == 20

        timeseries1 = state_manager.get_state_values_log(s1, since=0.)
        assert len(timeseries1) == 2
        assert timeseries1[0].value == 5
        assert timeseries1[1].value == {'test': 123}

    def test_query_log_values_initial_value(self):
        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s0 = state_manager.add('myotherstate', value=0, log_key=None)
        s0.update(value=1)
        now = time.time()
        s0.update(value=0)

        timeseries0 = state_manager.get_state_values_log(s0, since=now)
        print(timeseries0)
        assert len(timeseries0) == 2
        assert timeseries0[0].value == 1
        assert timeseries0[1].value == 0
        assert timeseries0[0].timestamp < now
        assert timeseries0[1].timestamp >= now

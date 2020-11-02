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

        assert s.id == 1
        assert s.name == 'mystate'
        assert s.parent is None
        assert s.value is None

        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s = state_manager.get(id=1)
        assert s.id == 1
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
        s0 = state_manager.get(id=1)
        assert s0.children[0].name == 'child'

    def test_update(self):
        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s = state_manager.add('mystate')
        s.update(name='test')
        assert s.name == 'test'

        state_manager = DALStateManager(self.DB_DIR, self.DB_URI, EventManager())
        s = state_manager.get(path='/test')
        assert s.id == 1

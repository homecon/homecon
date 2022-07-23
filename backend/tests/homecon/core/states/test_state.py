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

from unittest import TestCase
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.event import EventManager


class TestState(TestCase):

    def test_add(self):
        state_manager = MemoryStateManager(EventManager())
        s = state_manager.add('mystate')

        assert s.name == 'mystate'
        assert s.parent is None
        assert s.value is None

    def test_full_path(self):
        state_manager = MemoryStateManager(EventManager())
        s1 = state_manager.add('mystate')
        s2 = state_manager.add('substate', parent=s1)
        assert s1.path == '/mystate'
        assert s2.path == '/mystate/substate'

    def test_children(self):
        state_manager = MemoryStateManager(EventManager())
        s1 = state_manager.add('mystate')
        s2a = state_manager.add('substate_a', parent=s1)
        s2b = state_manager.add('substate_b', parent=s1)
        state_manager.add('mynewstate')
        children = s1.children
        assert len(children) == 2
        assert s2a in children
        assert s2b in children

    def test_all(self):
        state_manager = MemoryStateManager(EventManager())
        state_manager.add('mystate1')
        state_manager.add('mystate2')
        states = state_manager.all()
        assert states[0].path == '/mystate1'
        assert states[1].path == '/mystate2'

    def test_find_single(self):
        state_manager = MemoryStateManager(EventManager())
        state_manager.add('mystate1')
        state_manager.add('mystate2')
        states = state_manager.find('/mystate1')
        assert len(states) == 1
        assert states[0].path == '/mystate1'

    def test_find_multiple(self):
        state_manager = MemoryStateManager(EventManager())
        s0 = state_manager.add('mystate1')
        s1 = state_manager.add('mystate2')
        s2 = state_manager.add('mystate3', parent=s1)

        s00 = state_manager.add('shading', parent=s0)
        s20 = state_manager.add('shading', parent=s2)

        state_manager.add('position', parent=s00)
        state_manager.add('position', parent=s20)

        states = state_manager.find('.*/shading/position')
        assert len(states) == 2
        assert states[0].path == '/mystate1/shading/position'
        assert states[1].path == '/mystate2/mystate3/shading/position'

    def test_export_import(self):
        state_manager = MemoryStateManager(EventManager())
        s0 = state_manager.add('mystate1')
        s1 = state_manager.add('mystate2')
        s2 = state_manager.add('mystate3', parent=s1)

        exported = state_manager.export_states()
        print(exported)
        assert exported[0]['key'] == s0.key
        assert exported[0]['name'] == s0.name
        assert exported[0]['parent'] is None

        assert exported[1]['key'] == s1.key
        assert exported[1]['name'] == s1.name
        assert exported[1]['parent'] is None

        assert exported[2]['key'] == s2.key
        assert exported[2]['name'] == s2.name
        assert exported[2]['parent'] == s2.parent.key

        state_manager.import_states(exported)
        s2i = state_manager.get('/mystate2/mystate3')

        assert s2i.parent.key == s1.key
        assert s2i.parent.name == s1.name
        assert s2i.parent.path == s1.path

    def test_import(self):
        state_manager = MemoryStateManager(EventManager())
        data = [{
            'key': '17dab170-1d71-4537-9022-d1c0d0622151', 'name': 'mystate3', 'parent': '9d609478-0f09-469c-a6c8-0f066f982faf',
            'type': None, 'quantity': None, 'unit': None, 'label': None, 'description': None, 'config': {}, 'value': None
        }, {
            'key': 'ddde8956-2472-4ac7-9a10-bf6ba2a39747', 'name': 'mystate1', 'parent': None,
            'type': None, 'quantity': None, 'unit': None, 'label': None, 'description': None, 'config': {}, 'value': None
        }, {
            'key': '9d609478-0f09-469c-a6c8-0f066f982faf', 'name': 'mystate2', 'parent': None,
            'type': None, 'quantity': None, 'unit': None, 'label': None, 'description': None, 'config': {}, 'value': None
        }]

        state_manager.import_states(data)
        s1 = state_manager.get('/mystate2')
        s2 = state_manager.get('/mystate2/mystate3')

        assert s2.parent == s1

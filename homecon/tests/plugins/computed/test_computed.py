import pytest

from unittest.mock import MagicMock

from homecon.core.event import Event
from homecon.core.states.state import MemoryStateManager
from homecon.core.pages.pages import IPagesManager
from homecon.tests.mocks import DummyEventManager
from homecon.plugins.computed.computed import ValueComputer, EvaluationError, Computed


class TestValueComputer:
    def test_value(self):
        state_manager = MemoryStateManager(DummyEventManager())
        a = state_manager.add('a', None)
        b = state_manager.add('b', parent=a, value=10)

        value_computer = ValueComputer(state_manager)
        value = value_computer.compute_value('10 * Value("/a/b")')
        assert value == 10 * b.value

    def test_values(self):
        state_manager = MemoryStateManager(DummyEventManager())
        a = state_manager.add('a', None)
        b = state_manager.add('b', parent=a, value=10)
        c = state_manager.add('c', parent=a, value=20)
        d = state_manager.add('d', parent=a, value=30)

        value_computer = ValueComputer(state_manager)
        value = value_computer.compute_value('sum(Values("/a/.*"))')
        assert value == b.value + c.value + d.value

    def test_exception(self):
        state_manager = MemoryStateManager(DummyEventManager())
        value_computer = ValueComputer(state_manager)
        with pytest.raises(EvaluationError):
            value_computer.compute_value('sum(Value("/a/.*"))')


class TestComputed:
    def test_listen_state_added(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        a = state_manager.add('a', config={'computed': 'test'})
        computed.listen_state_added(Event(event_manager, 'state_added', {'state': a}))
        assert computed._computed_mapping == {0: 'test'}

    def test_listen_state_deleted(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': 'test'})

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        computed.listen_state_deleted(Event(event_manager, 'state_deleted', {'state': a}))
        assert computed._computed_mapping == {}

    def test_listen_state_updated_remove_computed(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': 'test'})

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        a.config = {}
        computed.listen_state_updated(Event(event_manager, 'state_changed', {'state': a}))
        assert computed._computed_mapping == {}

    def test_listen_state_updated_add_computed(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={})

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        a.config = {'computed': 'test'}
        computed.listen_state_updated(Event(event_manager, 'state_changed', {'state': a}))
        assert computed._computed_mapping == {0: 'test'}

    def test_listen_state_updated_edit_computed(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': 'test'})

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        a.config = {'computed': '123'}
        computed.listen_state_updated(Event(event_manager, 'state_changed', {'state': a}))
        assert computed._computed_mapping == {0: '123'}

    def test_listen_state_value_changed(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': '10 * Value("/b")'})
        b = state_manager.add('b', value=5)

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        computed.start()
        computed.listen_state_value_changed(Event(event_manager, 'state_changed', {'state': b}))
        assert a.value == 50

    def test_listen_state_value_changed_equal(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': '10 * Value("/b")'}, value=50)
        a.set_value = MagicMock()
        b = state_manager.add('b', value=5)

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        computed.start()
        computed.listen_state_value_changed(Event(event_manager, 'state_changed', {'state': b}))

        assert not a.set_value.called

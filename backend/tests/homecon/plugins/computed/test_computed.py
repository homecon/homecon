import pytest

from unittest.mock import MagicMock
from dataclasses import asdict

from homecon.core.event import Event
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.pages.pages import IPagesManager
from homecon.plugins.computed.computed import ValueComputer, EvaluationError, Computed, ComputedConfig

from mocks import DummyEventManager


class TestValueComputer:
    def test_value(self):
        state_manager = MemoryStateManager(DummyEventManager())
        a = state_manager.add('a', None)
        b = state_manager.add('b', parent=a, value=10)

        value_computer = ValueComputer(state_manager)
        value = value_computer.compute_value('10 * Value("/a/b")')
        assert value == 10 * b.value

    def test_value_dict(self):
        state_manager = MemoryStateManager(DummyEventManager())
        a = state_manager.add('a', None)
        b = state_manager.add('b', parent=a, value={'mykey': 10})

        value_computer = ValueComputer(state_manager)
        value = value_computer.compute_value('10 * Value("/a/b")["mykey"]')
        assert value == 10 * b.value['mykey']

    def test_for_loop(self):
        state_manager = MemoryStateManager(DummyEventManager())
        a = state_manager.add('a', None)
        b = state_manager.add('0', parent=a, value=10)
        c = state_manager.add('1', parent=a, value=20)
        d = state_manager.add('2', parent=a, value=30)

        value_computer = ValueComputer(state_manager)
        value = value_computer.compute_value('sum(Value(f"/a/{i}") for i in range(3))')
        assert value == b.value + c.value + d.value

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
    test_config = ComputedConfig(
        '10 * Value("/b")',
        '/b'
    )

    def test_listen_state_added(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        a = state_manager.add('a', config={'computed': asdict(self.test_config)})
        computed.listen_state_added(Event(event_manager, 'state_added', {'state': a}))
        assert computed._computed_mapping == {a.key: self.test_config}

    def test_listen_state_added_mis_configured(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        a = state_manager.add('a', config={'computed': 'nonsense'})
        computed.listen_state_added(Event(event_manager, 'state_added', {'state': a}))
        assert computed._computed_mapping == {}

    def test_listen_state_deleted(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': asdict(self.test_config)})

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        computed.listen_state_deleted(Event(event_manager, 'state_deleted', {'state': a}))
        assert computed._computed_mapping == {}

    def test_listen_state_updated_remove_computed(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': asdict(self.test_config)})

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        a.config = {}
        computed.listen_state_updated(Event(event_manager, 'state_changed', {'state': a}))
        assert computed._computed_mapping == {}

    def test_listen_state_updated_add_computed(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={})

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        a.config = {'computed': asdict(self.test_config)}
        computed.listen_state_updated(Event(event_manager, 'state_changed', {'state': a}))
        assert computed._computed_mapping == {a.key: self.test_config}

    def test_listen_state_updated_edit_computed(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': asdict(self.test_config)})

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        new_config = ComputedConfig('123', '/c')
        a.config = {'computed': asdict(new_config)}
        computed.listen_state_updated(Event(event_manager, 'state_changed', {'state': a}))
        assert computed._computed_mapping == {a.key: new_config}

    def test_listen_state_value_changed(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': asdict(self.test_config)})
        b = state_manager.add('b', value=5)

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        computed.start()
        computed.listen_state_value_changed(Event(event_manager, 'state_changed', {'state': b}))
        assert a.value == 50

    def test_listen_state_value_changed_equal(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': asdict(self.test_config)}, value=50)
        a.set_value = MagicMock()
        b = state_manager.add('b', value=5)

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        computed.start()
        computed.listen_state_value_changed(Event(event_manager, 'state_changed', {'state': b}))

        assert not a.set_value.called

    def test_listen_state_value_changed_not_triggered(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        a = state_manager.add('a', config={'computed': asdict(self.test_config)}, value=1)
        a.set_value = MagicMock()
        b = state_manager.add('b', value=5)
        c = state_manager.add('c', value=1)

        computed = Computed('computed', event_manager, state_manager, IPagesManager)
        computed.start()
        computed.listen_state_value_changed(Event(event_manager, 'state_changed', {'state': c}))

        assert not a.set_value.called

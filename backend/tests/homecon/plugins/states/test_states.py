from homecon.core.event import Event
from homecon.core.pages.pages import IPagesManager
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.plugins.states.states import States
from mocks import DummyEventManager


class TestStates:

    def test_listen_state_value(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        states = States('states', event_manager, state_manager, IPagesManager)
        a = state_manager.add('a', value=1)
        states.listen_state_value(Event(event_manager, 'state_value', {'path': '/a', 'value': 2}, source='test'))

        assert event_manager.events[-1].type == 'state_value_changed'
        assert event_manager.events[-1].data == {'state': a, 'old': 1, 'new': 2}
        assert event_manager.events[-1].source == 'test'
        assert a.value == 2

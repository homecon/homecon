from unittest import TestCase

from homecon.homecon import HomeCon, IExecutor, SyncExecutor
from homecon.core.event import EventManager
from homecon.core.plugins.plugin import BasePlugin, IPluginManager
from homecon.core.states.state import State
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.pages.pages import MemoryPagesManager


class PluginManager(IPluginManager):
    def __init__(self, plugins: dict):
        self._plugins = plugins

    def start(self):
        pass

    def stop(self):
        pass

    def __getitem__(self, key: str):
        return self._plugins[key]

    def __iter__(self):
        return self._plugins.__iter__()

    def __contains__(self, key: str):
        return self._plugins.__contains__(key)

    def keys(self):
        return self._plugins.keys()

    def items(self):
        return self._plugins.items()

    def values(self):
        return self._plugins.values()


class MockPlugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handled_events = []

    def initialize(self):
        pass

    def listen_state_value_changed(self, event):
        self.handled_events.append(event)
        if event.data['state'].id == 0:
            state = self._state_manager.get(id=1)
            state.value = 1


class TestHomecon(TestCase):
    def test_homecon(self):
        event_manager = EventManager()
        state_manager = MemoryStateManager(event_manager)
        pages_manager = MemoryPagesManager()
        mock_plugin = MockPlugin('MockPlugin', event_manager, state_manager, pages_manager)
        plugin_manager = PluginManager({'MockPlugin': mock_plugin})

        hc = HomeCon(event_manager, plugin_manager, SyncExecutor())
        state1 = State(state_manager, event_manager, 0, 'test1')
        state2 = State(state_manager, event_manager, 1, 'test1')
        state_manager._states[0] = state1
        state_manager._states[1] = state2

        event = event_manager.fire('state_value_changed', {'state': state1})
        hc.get_and_handle_event()
        hc.get_and_handle_event()
        print(mock_plugin.handled_events)
        assert mock_plugin.handled_events[0] == event
        assert mock_plugin.handled_events[1].data['state'] == state2
        assert state2.value == 1

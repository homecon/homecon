from homecon.tests.mocks import DummyEventManager
from homecon.core.states.state import MemoryStateManager
from homecon.core.pages.pages import MemoryPagesManager
from homecon.core.event import Event

from homecon.plugins.knx import Knx, IKNXDConnection, Message
from knxpy.util import encode_dpt


class MockKNXDConnection(IKNXDConnection):
    def __init__(self):
        self.writes = []

    def connect(self, address: str, port: int) -> None:
        pass

    def listen(self, callback):
        pass

    def close(self) -> None:
        pass

    def group_read(self, key: str):
        pass

    def group_write(self, ga: str, value, dpt: str):
        self.writes.append({'ga': ga, 'value': value, 'dpt': dpt})


class TestKnx:
    def test_callback_eval_read(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        pages_manager = MemoryPagesManager()

        state_manager._create_state('test', parent=None, type='float',
                                    config={'knx_ga_read': '1/1/1', 'knx_dpt': '1', 'knx_eval_read': 'value / 255'})

        knx_plugin = Knx('knx', event_manager, state_manager, pages_manager)
        knx_plugin.connection = MockKNXDConnection()
        knx_plugin.start()

        message = Message('1/1/1', 1)
        knx_plugin.callback(message)
        assert state_manager.get('/test').value == 1 / 255

    def test_listen_state_value_changed_eval_write(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        pages_manager = MemoryPagesManager()

        state_manager._create_state('test', parent=None, type='float',
                                    config={Knx.KNX_GA_WRITE: '1/1/1', Knx.KNX_DPT: '1', Knx.KNX_EVAL_WRITE: 'value * 255'})

        knx_plugin = Knx('knx', event_manager, state_manager, pages_manager)
        knx_plugin.connection = MockKNXDConnection()
        knx_plugin.start()

        state = state_manager.get('/test')
        state.value = 1

        event = Event(event_manager, 'state_changed', data={'state': state})
        knx_plugin.listen_state_value_changed(event)
        assert knx_plugin.connection.writes[0] == {'ga': '1/1/1', 'value': 255, 'dpt': '1'}

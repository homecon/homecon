
from homecon.tests import common
from homecon.plugins.states import States


class TestStates(common.TestCase):
    def test_start_stop_states(self):
        states_plugin = States()
        states_plugin.start()
        states_plugin.stop()
        states_plugin.join()

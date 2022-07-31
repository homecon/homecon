from pytest import approx

from homecon.core.event import Event
from homecon.core.pages.pages import IPagesManager
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.states.state import StateEventsTypes
from homecon.plugins.heat_demand.heat_demand import HeatDemand
from mocks import DummyEventManager


class TestStateBasedHeatingCurveWantedHeatGainCalculator:
    def test_listen_state_value_changed(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)

        plugin = HeatDemand('heat_demand', event_manager, state_manager, IPagesManager())
        plugin.start()
        assert plugin._heat_demand_state.value == approx(857, abs=5)

        plugin._ambient_temperature_state.value = 20
        event = Event(
            event_manager, StateEventsTypes.STATE_VALUE_CHANGED, {'state': plugin._ambient_temperature_state, 'old': 15, 'source': 'myplugin'}
        )
        plugin.listen_state_value_changed(event)
        assert plugin._heat_demand_state.value == approx(-571, abs=5)

    def test_listen_state_updated(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)

        plugin = HeatDemand('heat_demand', event_manager, state_manager, IPagesManager())
        plugin.start()
        assert plugin._heat_demand_state.value == approx(857, abs=5)

        plugin._heat_demand_state.config = {'ambient_temperature_min': -10, 'ambient_temperature_max': 18,
                                            'indoor_temperature_correction_factor': 0.2, 'heat_demand_max': 16000}
        event = Event(
            event_manager, StateEventsTypes.STATE_UPDATED, {'state': plugin._heat_demand_state, 'source': 'myplugin'}
        )
        plugin.listen_state_updated(event)
        assert plugin._heat_demand_state.value == approx(1714, abs=5)


from datetime import datetime

from _pytest.python_api import approx

from homecon.core.event import IEventManager
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.states.state import State
from homecon.plugins.shading.domain import StateBasedShading
from mocks import DummyEventManager


class TestStateBasedShading:

    def test_get_maximum_heat_gain(self):
        state_manager = MemoryStateManager(DummyEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading = StateBasedShading('test', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0)
        date = datetime(2021, 1, 1, 12, 0)
        assert shading.get_maximum_heat_gain(date, cloud_cover=0.0) == approx(607, rel=0.05)
        assert shading.get_maximum_heat_gain(date, cloud_cover=1.0) == approx(256, rel=0.05)

    def test_get_heat_gain(self):
        state_manager = MemoryStateManager(DummyEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading = StateBasedShading('test', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0)
        date = datetime(2021, 1, 1, 12, 0)
        assert shading.get_heat_gain(0.2, date) == approx(0.8*607, rel=0.05)

    def test_get_shading_factor(self):
        state_manager = MemoryStateManager(DummyEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading = StateBasedShading('test', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0)
        assert shading.get_shading_factor(0.0) == 1.0
        assert shading.get_shading_factor(1.0) == 0.0
        assert shading.get_shading_factor(0.5) == 0.5

    def test_position_bounds(self):
        state_manager = MemoryStateManager(IEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading = StateBasedShading('test', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0)
        assert shading.minimum_position == 0.0
        assert shading.maximum_position == 1.0

        shading = StateBasedShading('test', position_state.value, lambda x: position_state.set_value(x), 0.2, 0.8)
        assert shading.minimum_position == 0.2
        assert shading.maximum_position == 0.8

    def test_set_positions(self):
        state_manager = MemoryStateManager(DummyEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading = StateBasedShading('test', position_state.value, lambda x: position_state.set_value(x), 0.2, 0.8)
        shading.set_position(0.5)
        assert position_state.value == 0.5

from datetime import datetime
from typing import Optional

from pytest import approx

from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.states.state import State

from homecon.plugins.shading.calculator import EqualShadingPositionCalculator, StateBasedHeatingCurveWantedHeatGainCalculator
from homecon.plugins.shading.domain import IShading
from mocks import DummyEventManager


class MockShading(IShading):
    def __init__(self, position=0.0, minimum_position=0.0, maximum_position=1.0, heat_gain=1000.):
        self._position = position
        self._minimum_position = minimum_position
        self._maximum_position = maximum_position
        self._heat_gain = heat_gain

    @property
    def position(self) -> float:
        return self._position

    def set_position(self, value) -> None:
        pass

    @property
    def minimum_position(self) -> float:
        return self._minimum_position

    @property
    def maximum_position(self) -> float:
        return self._maximum_position

    def get_heat_gain(self, position: float, date: datetime, cloud_cover: Optional[float] = 0.0) -> float:
        return (1-position) * (1-cloud_cover) * self._heat_gain


class TestEqualShadingPositionCalculator:

    def test_get_positions_empty(self):
        shadings = []
        calculator = EqualShadingPositionCalculator()
        positions = calculator.get_positions(shadings, 1000)
        assert positions == []

    def test_get_positions_equal(self):
        shadings = [MockShading(), MockShading()]
        calculator = EqualShadingPositionCalculator()
        positions = calculator.get_positions(shadings, 1000)
        assert positions == [0.5, 0.5]

    def test_get_positions_open(self):
        shadings = [MockShading(), MockShading()]
        calculator = EqualShadingPositionCalculator()
        positions = calculator.get_positions(shadings, 5000)
        assert positions == [0.0, 0.0]

    def test_get_positions_closed(self):
        shadings = [MockShading(), MockShading()]
        calculator = EqualShadingPositionCalculator()
        positions = calculator.get_positions(shadings, 0)
        assert positions == [1.0, 1.0]

    def test_get_positions_negative_heat_gain(self):
        shadings = [MockShading(), MockShading()]
        calculator = EqualShadingPositionCalculator()
        positions = calculator.get_positions(shadings, -5000)
        assert positions == [1.0, 1.0]

    def test_get_positions_different_gains(self):
        shadings = [MockShading(heat_gain=1000), MockShading(heat_gain=2000)]
        calculator = EqualShadingPositionCalculator()
        positions = calculator.get_positions(shadings, 1000)
        assert positions == [0.65, 0.65]

    def test_get_positions_different_bounds(self):
        shadings = [MockShading(heat_gain=1000, minimum_position=0.2, maximum_position=0.3),
                    MockShading(heat_gain=1000, minimum_position=0.7, maximum_position=0.8)]
        calculator = EqualShadingPositionCalculator()
        positions = calculator.get_positions(shadings, 5000)
        assert positions == [0.2, 0.7]

    def test_get_positions_threshold(self):
        shadings = [MockShading(heat_gain=20), MockShading(heat_gain=100)]
        calculator = EqualShadingPositionCalculator()
        positions = calculator.get_positions(shadings, -5000, cloud_cover=0.0)
        assert positions == [0.0, 1.0]


class TestStateBasedHeatingCurveWantedHeatGainCalculator:
    def test_calculate_wanted_heat_gain(self):
        state_manager = MemoryStateManager(DummyEventManager())
        calculator = StateBasedHeatingCurveWantedHeatGainCalculator(
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature', value=10.0),
            State(state_manager, DummyEventManager(), 1, 'indoor_temperature', value=20.0),
            State(state_manager, DummyEventManager(), 1, 'setpoint_temperature', value=20.0),
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature_min', value=-10.0),
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature_max', value=18.0),
            State(state_manager, DummyEventManager(), 1, 'heat_demand_max', value=8000.0),
            State(state_manager, DummyEventManager(), 1, 'indoor_temperature_correction_factor', value=0.2),

        )
        heat = calculator.calculate_wanted_heat_gain()
        assert heat == approx(2285, rel=0.01)

        calculator = StateBasedHeatingCurveWantedHeatGainCalculator(
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature', value=18.0),
            State(state_manager, DummyEventManager(), 1, 'indoor_temperature', value=20.0),
            State(state_manager, DummyEventManager(), 1, 'setpoint_temperature', value=20.0),
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature_min', value=-10.0),
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature_max', value=18.0),
            State(state_manager, DummyEventManager(), 1, 'heat_demand_max', value=8000.0),
            State(state_manager, DummyEventManager(), 1, 'indoor_temperature_correction_factor', value=0.2),

        )
        heat = calculator.calculate_wanted_heat_gain()
        assert heat == 0

        calculator = StateBasedHeatingCurveWantedHeatGainCalculator(
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature', value=18.0),
            State(state_manager, DummyEventManager(), 1, 'indoor_temperature', value=21.0),
            State(state_manager, DummyEventManager(), 1, 'setpoint_temperature', value=20.0),
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature_min', value=-10.0),
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature_max', value=18.0),
            State(state_manager, DummyEventManager(), 1, 'heat_demand_max', value=8000.0),
            State(state_manager, DummyEventManager(), 1, 'indoor_temperature_correction_factor', value=0.2),

        )
        heat = calculator.calculate_wanted_heat_gain()
        assert heat == -0.2 * 8000

        calculator = StateBasedHeatingCurveWantedHeatGainCalculator(
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'indoor_temperature', value=23.0),
            State(state_manager, DummyEventManager(), 1, 'setpoint_temperature', value=20.0),
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature_min', value=-10.0),
            State(state_manager, DummyEventManager(), 1, 'ambient_temperature_max', value=18.0),
            State(state_manager, DummyEventManager(), 1, 'heat_demand_max', value=8000.0),
            State(state_manager, DummyEventManager(), 1, 'indoor_temperature_correction_factor', value=0.2),

        )
        heat = calculator.calculate_wanted_heat_gain()
        assert heat == approx(342, rel=0.01)

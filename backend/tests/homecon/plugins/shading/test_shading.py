from datetime import datetime
from pytest import approx

from homecon.core.states.state import State
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.event import IEventManager, Event

from homecon.plugins.shading.shading import IShading, StateBasedShading, IWantedHeatGainCalculator, \
    EqualShadingPositionCalculator, StateBasedHeatingCurveWantedHeatGainCalculator, ShadingController
from mocks import DummyEventManager


class TestStateBasedShading:

    def test_get_maximum_heat_gain(self):
        state_manager = MemoryStateManager(DummyEventManager())
        shading = StateBasedShading(
            State(state_manager, DummyEventManager(), 1, 'position', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_min', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_max', value=1.0),
        )
        date = datetime(2021, 1, 1, 12, 0)
        assert shading.get_maximum_heat_gain(date) == approx(607, rel=0.01)

    def test_get_heat_gain(self):
        state_manager = MemoryStateManager(DummyEventManager())
        shading = StateBasedShading(
            State(state_manager, DummyEventManager(), 1, 'position', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_min', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_max', value=1.0),
        )
        date = datetime(2021, 1, 1, 12, 0)
        assert shading.get_heat_gain(0.2, date) == approx(0.8*607, rel=0.01)

    def test_get_shading_factor(self):
        state_manager = MemoryStateManager(DummyEventManager())
        shading = StateBasedShading(
            State(state_manager, DummyEventManager(), 1, 'position', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_min', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_max', value=1.0),
        )
        assert shading.get_shading_factor(0.0) == 1.0
        assert shading.get_shading_factor(1.0) == 0.0
        assert shading.get_shading_factor(0.5) == 0.5

    def test_position_bounds(self):
        state_manager = MemoryStateManager(IEventManager())
        shading = StateBasedShading(
            State(state_manager, DummyEventManager(), 1, 'position', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_min', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_max', value=1.0),
        )
        assert shading.minimum_position == 0.0
        assert shading.maximum_position == 1.0

        shading = StateBasedShading(
            State(state_manager, DummyEventManager(), 1, 'position', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_min', value=0.2),
            State(state_manager, DummyEventManager(), 1, 'position_max', value=0.8),
        )
        assert shading.minimum_position == 0.2
        assert shading.maximum_position == 0.8

    def test_set_positions(self):
        state_manager = MemoryStateManager(DummyEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading = StateBasedShading(
            position_state,
            State(state_manager, DummyEventManager(), 1, 'position_min', value=0.0),
            State(state_manager, DummyEventManager(), 1, 'position_max', value=1.0),
        )
        shading.set_position(0.5)
        assert position_state.value == 0.5


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

    def get_heat_gain(self, position: float, date: datetime) -> float:
        return (1-position) * self._heat_gain


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
        positions = calculator.get_positions(shadings, -1000)
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
        positions = calculator.get_positions(shadings, 0)
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


class MockHeatGainCalculator(IWantedHeatGainCalculator):
    def __init__(self, wanted_heat_gain = 0):
        self._wanted_heat_gain = wanted_heat_gain

    def calculate_wanted_heat_gain(self) -> float:
        return self._wanted_heat_gain


class TestShadingController:
    @staticmethod
    def create_shading_state(state_manager, name, config=None):
        shading = state_manager.add(
            name, None, type=ShadingController.SHADING_STATE_TYPE, config=config or {}
        )
        shading_position = state_manager.add(
            'position', shading
        )
        shading_minimum = state_manager.add(
            'minimum', shading
        )
        shading_maximum = state_manager.add(
            'maximum', shading
        )
        return shading, shading_position, shading_minimum, shading_maximum

    def test_run(self):
        state_manager = MemoryStateManager(DummyEventManager())
        shading1, shading_position1, shading_minimum1, shading_maximum1 = self.create_shading_state(
            state_manager, 'shading1', {'area': 1.0, 'azimuth': 90., 'tilt': 90., 'transparency': 0.0})
        shading2, shading_position2, shading_minimum2, shading_maximum2 = self.create_shading_state(
            state_manager, 'shading2', {'area': 2.0, 'azimuth': 180., 'tilt': 90., 'transparency': 0.0})
        shading3, shading_position3, shading_minimum3, shading_maximum3 = self.create_shading_state(
            state_manager, 'shading3', {'area': 3.0, 'azimuth': 270., 'tilt': 90., 'transparency': 0.0})

        controller = ShadingController(
            state_manager,
            MockHeatGainCalculator(8000),
            EqualShadingPositionCalculator(),
            State(state_manager, DummyEventManager(), 1, 'longitude', value=5),
            State(state_manager, DummyEventManager(), 2, 'latitude', value=50),
            State(state_manager, DummyEventManager(), 3, 'elevation', value=50),
        )
        controller.run()
        assert shading_position1.value == 0.0
        assert shading_position2.value == 0.0
        assert shading_position3.value == 0.0

        controller = ShadingController(
            state_manager,
            MockHeatGainCalculator(0),
            EqualShadingPositionCalculator(),
            State(state_manager, DummyEventManager(), 1, 'longitude', value=5),
            State(state_manager, DummyEventManager(), 2, 'latitude', value=50),
            State(state_manager, DummyEventManager(), 3, 'elevation', value=50),
        )
        controller.run()
        assert shading_position1.value == 1.0
        assert shading_position2.value == 1.0
        assert shading_position3.value == 1.0

    def test_run_maximum_position(self):
        state_manager = MemoryStateManager(DummyEventManager())
        shading1, shading_position1, shading_minimum1, shading_maximum1 = self.create_shading_state(
            state_manager, 'shading1', {'area': 1.0, 'azimuth': 90., 'tilt': 90., 'transparency': 0.0})
        shading2, shading_position2, shading_minimum2, shading_maximum2 = self.create_shading_state(
            state_manager, 'shading2', {'area': 2.0, 'azimuth': 180., 'tilt': 90., 'transparency': 0.0})
        shading3, shading_position3, shading_minimum3, shading_maximum3 = self.create_shading_state(
            state_manager, 'shading3', {'area': 3.0, 'azimuth': 270., 'tilt': 90., 'transparency': 0.0})

        shading_minimum1.value = 1.0
        shading_minimum2.value = 0.5

        controller = ShadingController(
            state_manager,
            MockHeatGainCalculator(8000),
            EqualShadingPositionCalculator(now=lambda: datetime(2021, 1, 1, 12, 0)),
            State(state_manager, DummyEventManager(), 1, 'longitude', value=5),
            State(state_manager, DummyEventManager(), 2, 'latitude', value=50),
            State(state_manager, DummyEventManager(), 3, 'elevation', value=50),
        )
        controller.run()
        assert shading_position1.value == 1.0
        assert shading_position2.value == 0.5
        assert shading_position3.value == 0.0

    def test_listen_state_value_changed(self):
        state_manager = MemoryStateManager(DummyEventManager())
        shading1, shading_position1, shading_minimum1, shading_maximum1 = self.create_shading_state(
            state_manager, 'shading1', {'area': 1.0, 'azimuth': 90., 'tilt': 90., 'transparency': 0.0})
        shading2, shading_position2, shading_minimum2, shading_maximum2 = self.create_shading_state(
            state_manager, 'shading2', {'area': 2.0, 'azimuth': 180., 'tilt': 90., 'transparency': 0.0})
        shading3, shading_position3, shading_minimum3, shading_maximum3 = self.create_shading_state(
            state_manager, 'shading3', {'area': 3.0, 'azimuth': 270., 'tilt': 90., 'transparency': 0.0})

        controller = ShadingController(
            state_manager,
            MockHeatGainCalculator(8000),
            EqualShadingPositionCalculator(now=lambda: datetime(2021, 1, 1, 12, 0)),
            State(state_manager, DummyEventManager(), 1, 'longitude', value=5),
            State(state_manager, DummyEventManager(), 2, 'latitude', value=50),
            State(state_manager, DummyEventManager(), 3, 'elevation', value=50),
        )
        controller.run()
        assert shading_position1.value == 0.0
        assert shading_position2.value == 0.0
        assert shading_position3.value == 0.0

        shading_minimum1.value = 1.0
        controller.listen_state_value_changed(
            Event(DummyEventManager(), 'state_value_changed', {'state': shading_minimum1})
        )

        assert shading_position1.value == 1.0
        assert shading_position2.value == 0.0
        assert shading_position3.value == 0.0

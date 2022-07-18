from datetime import datetime

from homecon.core.states.state import State
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.event import Event

from homecon.plugins.shading.controller import ShadingController
from homecon.plugins.shading.calculator import EqualShadingPositionCalculator, IWantedHeatGainCalculator, \
    ICloudCoverCalculator
from mocks import DummyEventManager


class MockHeatGainCalculator(IWantedHeatGainCalculator):
    def __init__(self, wanted_heat_gain: float = 0.0):
        self._wanted_heat_gain = wanted_heat_gain

    def calculate_wanted_heat_gain(self) -> float:
        return self._wanted_heat_gain


class MockCloudCoverCalculator(ICloudCoverCalculator):
    def calculate_cloud_cover(self) -> float:
        return 0.0


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
            'minimum_position', shading
        )
        shading_maximum = state_manager.add(
            'maximum_position', shading
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
        wanted_heat_gain_state = State(state_manager, state_manager.event_manager, 1, 'wanted_heat_gain')
        cloud_cover_state = State(state_manager, state_manager.event_manager, 1, 'cloud_cover')

        controller = ShadingController(
            state_manager,
            MockHeatGainCalculator(8000),
            wanted_heat_gain_state,
            MockCloudCoverCalculator(),
            cloud_cover_state,
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
            wanted_heat_gain_state,
            MockCloudCoverCalculator(),
            cloud_cover_state,
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
        wanted_heat_gain_state = State(state_manager, state_manager.event_manager, 1, 'wanted_heat_gain')
        cloud_cover_state = State(state_manager, state_manager.event_manager, 1, 'cloud_cover')

        shading_minimum1.value = 1.0
        shading_minimum2.value = 0.5

        controller = ShadingController(
            state_manager,
            MockHeatGainCalculator(8000),
            wanted_heat_gain_state,
            MockCloudCoverCalculator(),
            cloud_cover_state,
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
        wanted_heat_gain_state = State(state_manager, state_manager.event_manager, 1, 'wanted_heat_gain')
        cloud_cover_state = State(state_manager, state_manager.event_manager, 1, 'cloud_cover')

        controller = ShadingController(
            state_manager,
            MockHeatGainCalculator(8000),
            wanted_heat_gain_state,
            MockCloudCoverCalculator(),
            cloud_cover_state,
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

        assert controller._run_job is not None
        jobs = controller.scheduler.get_jobs()
        assert len(jobs) == 2

        # execute the job inline
        jobs[1].func()

        assert shading_position1.value == 1.0
        assert shading_position2.value == 0.0
        assert shading_position3.value == 0.0
        assert controller._run_job is None

        controller.listen_state_value_changed(
            Event(DummyEventManager(), 'state_value_changed', {'state': shading_minimum1})
        )
        assert controller._run_job is not None

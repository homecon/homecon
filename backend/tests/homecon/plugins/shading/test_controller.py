from datetime import datetime, timedelta

import pytz

from homecon.core.states.state import State
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.event import Event

from homecon.plugins.shading.controller import ShadingController
from homecon.plugins.shading.calculator import EqualShadingPositionCalculator, \
    ICloudCoverCalculator, IRainCalculator
from mocks import DummyEventManager


class MockCloudCoverCalculator(ICloudCoverCalculator):
    def calculate_cloud_cover(self) -> float:
        return 0.0


class MockRainCalculator(IRainCalculator):
    def calculate_rain(self) -> bool:
        return True


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
        state_manager.add(
            'controller_override', shading
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
        wanted_heat_gain_state = State(state_manager, state_manager.event_manager, 1, 'wanted_heat_gain', value=8000)
        cloud_cover_state = State(state_manager, state_manager.event_manager, 1, 'cloud_cover')

        controller = ShadingController(
            state_manager,
            wanted_heat_gain_state,
            MockCloudCoverCalculator(),
            cloud_cover_state,
            MockRainCalculator(),
            EqualShadingPositionCalculator(now=lambda: datetime(2022, 6, 18, 12, 0, 0)),
            State(state_manager, DummyEventManager(), 1, 'longitude', value=5),
            State(state_manager, DummyEventManager(), 2, 'latitude', value=50),
            State(state_manager, DummyEventManager(), 3, 'elevation', value=50),
        )
        controller.run()
        assert shading_position1.value == 0.0
        assert shading_position2.value == 0.0
        assert shading_position3.value == 0.0

        wanted_heat_gain_state.value = 0
        controller = ShadingController(
            state_manager,
            wanted_heat_gain_state,
            MockCloudCoverCalculator(),
            cloud_cover_state,
            MockRainCalculator(),
            EqualShadingPositionCalculator(now=lambda: datetime(2022, 6, 18, 12, 0, 0)),
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
        wanted_heat_gain_state = State(state_manager, state_manager.event_manager, 1, 'wanted_heat_gain', value=8000)
        cloud_cover_state = State(state_manager, state_manager.event_manager, 1, 'cloud_cover')

        shading_minimum1.value = 1.0
        shading_minimum2.value = 0.5

        controller = ShadingController(
            state_manager,
            wanted_heat_gain_state,
            MockCloudCoverCalculator(),
            cloud_cover_state,
            MockRainCalculator(),
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
        wanted_heat_gain_state = State(state_manager, state_manager.event_manager, 1, 'wanted_heat_gain', value=8000)
        cloud_cover_state = State(state_manager, state_manager.event_manager, 1, 'cloud_cover')

        controller = ShadingController(
            state_manager,
            wanted_heat_gain_state,
            MockCloudCoverCalculator(),
            cloud_cover_state,
            MockRainCalculator(),
            EqualShadingPositionCalculator(now=lambda: datetime(2021, 1, 1, 12, 0)),
            State(state_manager, DummyEventManager(), 1, 'longitude', value=5),
            State(state_manager, DummyEventManager(), 2, 'latitude', value=50),
            State(state_manager, DummyEventManager(), 3, 'elevation', value=50),
        )
        controller.start()
        controller.run()
        assert shading_position1.value == 0.0
        assert shading_position2.value == 0.0
        assert shading_position3.value == 0.0

        shading_minimum1.value = 1.0
        controller.listen_state_value_changed(
            Event(DummyEventManager(), 'state_value_changed', {'state': shading_minimum1, 'old': 0.1, 'new': 0.0})
        )
        controller.listen_state_value_changed(
            Event(DummyEventManager(), 'state_value_changed', {'state': shading_minimum1, 'old': 0.0, 'new': 0.2})
        )

        assert controller._run_job is not None
        jobs = controller.scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].next_run_time < datetime.now(tz=pytz.UTC) + timedelta(seconds=20)
        assert controller._run_job == jobs[0]

        # execute the job inline
        jobs[0].func()

        assert shading_position1.value == 1.0
        assert shading_position2.value == 0.0
        assert shading_position3.value == 0.0
        assert controller._run_job is not None
        assert controller._run_job.next_run_time > datetime.now(tz=pytz.UTC) + timedelta(seconds=20)
        assert len(controller.scheduler.get_jobs()) == 1

        controller.listen_state_value_changed(
            Event(DummyEventManager(), 'state_value_changed', {'state': shading_minimum1, 'old': 0.1, 'new': 0.0})
        )
        assert controller._run_job is not None
        assert controller._run_job.next_run_time < datetime.now(tz=pytz.UTC) + timedelta(seconds=20)
        assert len(controller.scheduler.get_jobs()) == 1
        controller.stop()

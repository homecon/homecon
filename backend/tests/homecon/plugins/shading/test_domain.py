from datetime import datetime, timedelta

from pytest import approx

from homecon.core.event import IEventManager
from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.states.state import State
from homecon.plugins.shading.domain import StateBasedShading
from mocks import DummyEventManager


class TestStateBasedShading:

    def test_get_maximum_heat_gain(self):
        state_manager = MemoryStateManager(DummyEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading = StateBasedShading('test', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0, area=2)
        date = datetime(2021, 1, 1, 12, 0)
        assert shading.get_heat_gain(0.,  date, cloud_cover=0.0) == approx(796, rel=0.05)
        assert shading.get_heat_gain(0.,  date, cloud_cover=1.0) == approx(226, rel=0.05)

    def test_get_heat_gain(self):
        state_manager = MemoryStateManager(DummyEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading = StateBasedShading('test', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0, area=2)
        date = datetime(2021, 1, 1, 12, 0)
        assert shading.get_heat_gain(0.2, date) == approx(0.8*796, rel=0.05)

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

    def test_get_blocking_factor(self):
        state_manager = MemoryStateManager(DummyEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading = StateBasedShading('test', position_state.value, lambda x: position_state.set_value(x), 0.2, 0.8)

        assert shading.get_blocking_factor(0, -10) == 0.
        assert shading.get_blocking_factor(0, 0) == 0.
        assert shading.get_blocking_factor(0, 2) == 0.4
        assert shading.get_blocking_factor(0, 5) == 1.
        assert shading.get_blocking_factor(0, 10) == 1.
        assert shading.get_blocking_factor(0, 20) == 1.

    def test_get_maximum_heat_gain_over_time(self):
        state_manager = MemoryStateManager(DummyEventManager())
        position_state = State(state_manager, DummyEventManager(), 1, 'position', value=0.0)
        shading_north = StateBasedShading('north', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0,
                                          azimuth=0, longitude=5.58, latitude=51.05, elevation=60)
        shading_east = StateBasedShading('east', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0,
                                         azimuth=90, longitude=5.58, latitude=51.05, elevation=60)
        shading_south = StateBasedShading('south', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0,
                                          azimuth=180, longitude=5.58, latitude=51.05, elevation=60)
        shading_west = StateBasedShading('west', position_state.value, lambda x: position_state.set_value(x), 0.0, 1.0,
                                         azimuth=-90, longitude=5.58, latitude=51.05, elevation=60)

        # summer
        for dates in [[datetime(2021, 7, 1, 0, 0) + timedelta(seconds=i) for i in range(0, 24*3600, 3600)],
                      [datetime(2021, 1, 1, 0, 0) + timedelta(seconds=i) for i in range(0, 24 * 3600, 3600)]]:
            cloud_cover = 0.0
            heat_gains_north = [shading_north.get_irradiance(0.0, date, cloud_cover=cloud_cover) for date in dates]
            heat_gains_east = [shading_east.get_irradiance(0.0, date, cloud_cover=cloud_cover) for date in dates]
            heat_gains_south = [shading_south.get_irradiance(0.0, date, cloud_cover=cloud_cover) for date in dates]
            heat_gains_west = [shading_west.get_irradiance(0.0, date, cloud_cover=cloud_cover) for date in dates]

            cloud_cover = 1.0
            heat_gains_north_min = [shading_north.get_irradiance(0.0, date, cloud_cover=cloud_cover) for date in dates]
            heat_gains_east_min = [shading_east.get_irradiance(0.0, date, cloud_cover=cloud_cover) for date in dates]
            heat_gains_south_min = [shading_south.get_irradiance(0.0, date, cloud_cover=cloud_cover) for date in dates]
            heat_gains_west_min = [shading_west.get_irradiance(0.0, date, cloud_cover=cloud_cover) for date in dates]

            print('')
            for d, n, e, s, w, n_min, e_min, s_min, w_min in zip(dates, heat_gains_north, heat_gains_east, heat_gains_south, heat_gains_west,
                                                                 heat_gains_north_min, heat_gains_east_min,
                                                                 heat_gains_south_min, heat_gains_west_min):
                print(f'{d}:    {n:>6.2f} -{n_min:>6.2f}    {e:>6.2f} -{e_min:>6.2f}    {s:>6.2f} -{s_min:>6.2f}    {w:>6.2f} -{w_min:>6.2f}')

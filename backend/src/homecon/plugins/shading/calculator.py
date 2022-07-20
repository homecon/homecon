import logging
from datetime import datetime
from typing import List, Optional, Callable

from homecon.core.states.state import State
from homecon.plugins.shading.domain import IShading


logger = logging.getLogger(__name__)


class IShadingPositionCalculator:
    def get_positions(self, shadings: List[IShading], wanted_heat_gain: float, cloud_cover: Optional[float] = 0.0) -> List[float]:
        raise NotImplementedError


class EqualShadingPositionCalculator(IShadingPositionCalculator):
    def __init__(self, heat_gain_threshold: float = 50, position_step: float = 0.05,
                 now: Callable[[], datetime] = datetime.now):
        self.position_step = position_step
        self.heat_gain_threshold = heat_gain_threshold
        self._now = now

    def get_positions(self, shadings: List[IShading], wanted_heat_gain: float, cloud_cover: Optional[float] = 0.0):
        logger.debug(f'get positions for shadings: {shadings}')
        date = self._now()

        maximum_heat_gains = [s.get_heat_gain(s.minimum_position, date, cloud_cover) for s in shadings]
        minimum_heat_gains = [s.get_heat_gain(s.maximum_position, date, cloud_cover) for s in shadings]

        logger.debug(f'calculated minimum_heat_gains: {minimum_heat_gains}')
        logger.debug(f'calculated maximum_heat_gains: {maximum_heat_gains}')

        if wanted_heat_gain > sum(maximum_heat_gains):
            return [s.minimum_position for s in shadings]

        elif wanted_heat_gain < sum(minimum_heat_gains):
            return [s.maximum_position if g > self.heat_gain_threshold else s.minimum_position
                    for s, g in zip(shadings, maximum_heat_gains)]

        else:
            def _get_positions(pos: float):
                return [min(max(pos, s.minimum_position), s.maximum_position)
                        if g > self.heat_gain_threshold else s.minimum_position
                        for s, g in zip(shadings, maximum_heat_gains)]

            p = 1
            while p > 0:
                positions = _get_positions(p)
                heat_gain = sum([s.get_heat_gain(p, date) for s, p in zip(shadings, positions)])
                if heat_gain >= wanted_heat_gain:
                    return positions

                p -= self.position_step
                p = round(p / self.position_step) * self.position_step
            return _get_positions(0)


class IWantedHeatGainCalculator:
    def calculate_wanted_heat_gain(self) -> float:
        raise NotImplementedError


class StateBasedHeatingCurveWantedHeatGainCalculator(IWantedHeatGainCalculator):
    def __init__(self, ambient_temperature_state: State, indoor_temperature_state: Optional[State] = None,
                 setpoint_temperature_state: Optional[State] = None,
                 ambient_temperature_min_state: Optional[State] = None,
                 ambient_temperature_max_state: Optional[State] = None,
                 heat_demand_max_state: Optional[State] = None,
                 indoor_temperature_correction_factor_state: Optional[State] = None):
        self._ambient_temperature_state = ambient_temperature_state
        self._indoor_temperature_state = indoor_temperature_state
        self._setpoint_temperature_state = setpoint_temperature_state
        self._ambient_temperature_min_state = ambient_temperature_min_state
        self._ambient_temperature_max_state = ambient_temperature_max_state
        self._heat_demand_max_state = heat_demand_max_state
        self._indoor_temperature_correction_factor_state = indoor_temperature_correction_factor_state

    def _get_ambient_temperature(self) -> float:
        return self._ambient_temperature_state.value

    def _get_indoor_temperature(self) -> float:
        default = 20.
        if self._indoor_temperature_state is not None:
            return self._indoor_temperature_state.value or default
        return default

    def _get_setpoint_temperature(self) -> float:
        default = 21.
        if self._setpoint_temperature_state is not None:
            return self._setpoint_temperature_state.value or default
        return default

    def _get_ambient_temperature_min(self) -> float:
        default = -10.
        if self._ambient_temperature_min_state is not None:
            return self._ambient_temperature_min_state.value or default
        return default

    def _get_ambient_temperature_max(self) -> float:
        default = 18.
        if self._ambient_temperature_max_state is not None:
            return self._ambient_temperature_max_state.value or default
        return default

    def _get_heat_demand_max(self) -> float:
        default = 8000.
        if self._heat_demand_max_state is not None:
            return self._heat_demand_max_state.value or default
        return default

    def _get_indoor_temperature_correction_factor(self) -> float:
        default = 0.2
        if self._indoor_temperature_correction_factor_state is not None:
            return self._indoor_temperature_correction_factor_state.value or default
        return default

    @staticmethod
    def _calculate_heat_demand(ambient_temperature, indoor_temperature, setpoint_temperature,
                               ambient_temperature_min, ambient_temperature_max, heat_demand_max,
                               indoor_temperature_correction_scale):

        indoor_temperature_factor = -indoor_temperature_correction_scale * (
                indoor_temperature - setpoint_temperature)
        outdoor_temperature_factor = (ambient_temperature_max - ambient_temperature) / (
            ambient_temperature_max - ambient_temperature_min)

        return (indoor_temperature_factor + outdoor_temperature_factor) * heat_demand_max

    def calculate_wanted_heat_gain(self) -> float:
        ambient_temperature = self._get_ambient_temperature()
        indoor_temperature = self._get_indoor_temperature()
        setpoint_temperature = self._get_setpoint_temperature()
        ambient_temperature_min = self._get_ambient_temperature_min()
        ambient_temperature_max = self._get_ambient_temperature_max()
        heat_demand_max = self._get_heat_demand_max()
        indoor_temperature_correction_scale = self._get_indoor_temperature_correction_factor()

        logger.debug(f'calculating heat demand from ambient_temperature: {ambient_temperature:.1f}, indoor_temperature: {indoor_temperature:.1f}, '
                     f'setpoint_temperature: {setpoint_temperature:.1f}, '
                     f'ambient_temperature_min: {ambient_temperature_min:.1f}, ambient_temperature_max: {ambient_temperature_max:.1f}, '
                     f'heat_demand_max: {heat_demand_max:.1f}, indoor_temperature_correction_scale: {indoor_temperature_correction_scale:.1f}')
        return self._calculate_heat_demand(ambient_temperature, indoor_temperature, setpoint_temperature,
                                           ambient_temperature_min, ambient_temperature_max, heat_demand_max,
                                           indoor_temperature_correction_scale)


class ICloudCoverCalculator:
    def calculate_cloud_cover(self) -> float:
        """0: no clouds, 1: fully clouded"""
        raise NotImplementedError


class DummyCloudCoverCalculator(ICloudCoverCalculator):
    def calculate_cloud_cover(self) -> float:
        return 0.0


class WeatherForecastCloudCoverCalculator(ICloudCoverCalculator):
    # "/weather/forecast/hourly/0"
    # {"timestamp":1657951200,"temperature":16.86,"pressure":1022,"relative_humidity":0.72,"dew_point":11.79,"cloud_cover":0.23,
    # "wind_speed":2.47,"wind_direction":294,"icon":"sun_3","rain":0}

    def __init__(self, forecast_state: State):
        self._forecast_state = forecast_state

    def calculate_cloud_cover(self) -> float:
        try:
            return self._forecast_state.value.get("cloud_cover", 0)
        except:
            logger.exception('cloud cover not available in forecast')
            return 0.0


class IRainCalculator:
    def calculate_rain(self) -> bool:
        raise NotImplementedError


class StateRainCalculator(IRainCalculator):
    def __init__(self, state):
        self._state = state

    def calculate_rain(self) -> bool:
        return self._state.value == 1

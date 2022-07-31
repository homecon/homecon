import logging
from datetime import datetime
from typing import List, Optional, Callable, Tuple

from homecon.core.states.state import State
from homecon.plugins.shading.domain import IShading


logger = logging.getLogger(__name__)


class IShadingPositionCalculator:
    def get_positions(self, shadings: List[IShading], wanted_heat_gain: float, cloud_cover: Optional[float] = 0.0) -> List[float]:
        raise NotImplementedError


class IrradianceThresholdPositionCalculator(IShadingPositionCalculator):
    def __init__(self, wanted_heat_gain_threshold: float = 0,
                 irradiance_thresholds: List[Tuple[float, float]] = None,
                 now: Callable[[], datetime] = datetime.now):
        self._wanted_heat_gain_threshold = wanted_heat_gain_threshold
        self._irradiance_thresholds = irradiance_thresholds or [(100, 1.0), (75, 0.5)]
        self._now = now

    def get_positions(self, shadings: List[IShading], wanted_heat_gain: float, cloud_cover: Optional[float] = 0.0):
        logger.debug(f'get positions for shadings: {shadings}')
        date = self._now()

        if wanted_heat_gain > self._wanted_heat_gain_threshold:
            # heating mode
            logger.debug(f'heating mode, returning minimum positions')
            return [s.minimum_position for s in shadings]

        else:
            # cooling mode
            logger.debug(f'cooling mode, calculating positions')
            positions = []
            for shading in shadings:
                p = 0.0
                irradiance = shading.get_irradiance(0.0, date, cloud_cover)
                for threshold, position in self._irradiance_thresholds:
                    if irradiance > threshold:
                        p = position
                        break

                pos = min(max(p, shading.minimum_position), shading.maximum_position)
                positions.append(pos)
                logger.debug(f'calculated position for {shading}: {pos} based on irradiance {irradiance:.1f} W/m2')
            return positions


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

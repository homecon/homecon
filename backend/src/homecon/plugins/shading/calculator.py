import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Callable, Tuple

from homecon.core.states.state import State
from homecon.plugins.shading.domain import IShading


logger = logging.getLogger(__name__)


class IShadingPositionCalculator:
    def get_positions(self, shadings: List[IShading], wanted_heat_gain: float, cloud_cover: Optional[float] = 0.0) -> List[float]:
        raise NotImplementedError


@dataclass
class IrradanceThreshold:
    irradiance: float
    position: float


class IIrradianceThresholdCalculator:
    def get_irradiance_thresholds(self, wanted_heat_gain: float) -> List[IrradanceThreshold]:
        raise NotImplementedError


class ConstantIrradianceThresholdCalculator(IIrradianceThresholdCalculator):
    def __init__(self, wanted_heat_gain_threshold: float = 0, irradiance_thresholds: List[IrradanceThreshold] = None):
        self._wanted_heat_gain_threshold = wanted_heat_gain_threshold
        self._irradiance_thresholds = irradiance_thresholds or [IrradanceThreshold(100, 1.0), IrradanceThreshold(75, 0.5)]

    def get_irradiance_thresholds(self, wanted_heat_gain: float) -> List[IrradanceThreshold]:
        if wanted_heat_gain > self._wanted_heat_gain_threshold:
            # heating mode
            logger.debug(f'heating mode')
            return []
        else:
            logger.debug(f'cooling mode')
            return self._irradiance_thresholds


class LinearIrradianceThresholdCalculator(IIrradianceThresholdCalculator):
    def __init__(self, minimum_wanted_heat_gain: float = -2000, zero_wanted_heat_gain: float = 0,
                 minimum_threshold: float = 20, zero_threshold: float = 100):
        self._zero_wanted_heat_gain = zero_wanted_heat_gain
        self._minimum_wanted_heat_gain = minimum_wanted_heat_gain
        self._minimum_threshold = minimum_threshold
        self._zero_threshold = zero_threshold

    def get_irradiance_thresholds(self, wanted_heat_gain: float) -> List[IrradanceThreshold]:
        if wanted_heat_gain > self._zero_wanted_heat_gain:
            logger.debug(f'heating mode')
            return []
        else:
            logger.debug(f'cooling mode')
            threshold = self._minimum_threshold + (
                    self._minimum_wanted_heat_gain - wanted_heat_gain
            ) / self._minimum_wanted_heat_gain * (self._zero_threshold - self._minimum_threshold)
            threshold = max(threshold, self._minimum_threshold)
            return [IrradanceThreshold(threshold, 1.0), IrradanceThreshold(0.75 * threshold, 0.5)]


class IrradianceThresholdPositionCalculator(IShadingPositionCalculator):
    def __init__(self, irradiance_threshold_calculator: IIrradianceThresholdCalculator = None,
                 now: Callable[[], datetime] = datetime.now):
        self._irradiance_threshold_calculator = irradiance_threshold_calculator or ConstantIrradianceThresholdCalculator()
        self._now = now

    def get_positions(self, shadings: List[IShading], wanted_heat_gain: float, cloud_cover: Optional[float] = 0.0):
        logger.debug(f'get positions for shadings: {shadings}')
        date = self._now()

        logger.debug(f'calculating positions')
        irradiance_thresholds = self._irradiance_threshold_calculator.get_irradiance_thresholds(wanted_heat_gain)
        logger.debug(f'calculated irradiance thresholds: {irradiance_thresholds}')

        positions = []
        for shading in shadings:
            p = 0.0
            irradiance = shading.get_irradiance(0.0, date, cloud_cover)
            for threshold in irradiance_thresholds:
                if irradiance > threshold.irradiance:
                    p = threshold.position
                    break

            pos = min(max(p, shading.minimum_position), shading.maximum_position)
            positions.append(pos)
            logger.debug(f'calculated position for {shading}: {pos} based on irradiance {irradiance:.1f} W/m2')
        return positions


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

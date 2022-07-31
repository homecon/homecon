import logging


logger = logging.getLogger(__name__)


class IHeatDemandCalculator:
    def calculate_wanted_heat_gain(self) -> float:
        raise NotImplementedError


class HeatingCurveHeatDemandCalculator(IHeatDemandCalculator):
    def __init__(self, ambient_temperature: float, indoor_temperature: float,
                 setpoint_temperature: float, ambient_temperature_min: float,
                 ambient_temperature_max: float, heat_demand_max: float,
                 indoor_temperature_correction_factor: float):
        self._ambient_temperature = ambient_temperature
        self._indoor_temperature = indoor_temperature
        self._setpoint_temperature = setpoint_temperature
        self._ambient_temperature_min = ambient_temperature_min
        self._ambient_temperature_max = ambient_temperature_max
        self._heat_demand_max = heat_demand_max
        self._indoor_temperature_correction_factor = indoor_temperature_correction_factor

    def calculate_wanted_heat_gain(self) -> float:
        indoor_temperature_factor = -self._indoor_temperature_correction_factor * (
                self._indoor_temperature - self._setpoint_temperature)
        outdoor_temperature_factor = (self._ambient_temperature_max - self._ambient_temperature) / (
                self._ambient_temperature_max - self._ambient_temperature_min)

        head_demand = (indoor_temperature_factor + outdoor_temperature_factor) * self._heat_demand_max
        logger.debug(
            f'calculated heat demand of {head_demand:.1f} from '
            f'ambient_temperature: {self._ambient_temperature:.1f}, indoor_temperature: {self._indoor_temperature:.1f}, '
            f'setpoint_temperature: {self._setpoint_temperature:.1f}, '
            f'ambient_temperature_min: {self._ambient_temperature_min:.1f}, ambient_temperature_max: {self._ambient_temperature_max:.1f}, '
            f'heat_demand_max: {self._heat_demand_max:.1f}, indoor_temperature_correction_scale: {self._indoor_temperature_correction_factor:.1f}')
        return head_demand

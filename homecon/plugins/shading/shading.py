#!/usr/bin/env python3

import logging
from typing import List, Optional, Callable
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from homecon.core.event import Event
from homecon.core.states.state import State, IStateManager
from homecon.core.plugins.plugin import BasePlugin

from homecon.util.weather import incidentirradiance, clearskyirrradiance, sunposition, cloudyskyirrradiance


logger = logging.getLogger(__name__)


class IShading:
    """
    position: 0 means fully open, maximum solar gains, 1 means fully closed, minimum solar gains
    """

    @property
    def position(self) -> float:
        raise NotImplementedError

    def set_position(self, value) -> None:
        raise NotImplementedError

    @property
    def minimum_position(self) -> float:
        raise NotImplementedError

    @property
    def maximum_position(self) -> float:
        raise NotImplementedError

    def get_heat_gain(self, position: float, date: datetime) -> float:
        raise NotImplementedError


class StateBasedShading(IShading):
    """
    position: 0 means fully open, 1 means fully closed
    """

    def __init__(self, position_state: Optional[State] = None,
                 minimum_position_state: Optional[State] = None,
                 maximum_position_state: Optional[State] = None,
                 area: float = 1., transparency: float = 0., azimuth: float = 180., tilt: float = 90.,
                 longitude: float = 0, latitude: float = 0, elevation: float = 80.):
        self.position_state = position_state
        self.minimum_position_state = minimum_position_state
        self.maximum_position_state = maximum_position_state
        self._area = area
        self.transparency = transparency
        self._azimuth = azimuth
        self._tilt = tilt
        self._longitude = longitude
        self._latitude = latitude
        self._elevation = elevation

    def get_shading_factor(self, position):
        return position * self.transparency + (1 - position) * 1

    def get_heat_gain(self, position: float, date: datetime) -> float:
        return self.get_shading_factor(position) * self.get_maximum_heat_gain(date)

    def get_maximum_heat_gain(self, date: datetime) -> float:
        solar_azimuth, solar_altitude = sunposition(self._latitude, self._longitude, self._elevation,
                                                    timestamp=int(date.timestamp()))
        irradiance_direct_clearsky, irradiance_diffuse_clearsky = clearskyirrradiance(solar_azimuth, solar_altitude)
        cloud_cover = 0.0
        irradiance_direct, irradiance_diffuse = cloudyskyirrradiance(
            irradiance_direct_clearsky, irradiance_diffuse_clearsky, cloud_cover, solar_azimuth, solar_altitude,
            timestamp=int(date.timestamp()))
        irradiance_total_surface, irradiance_direct_surface, irradiance_diffuse_surface, irradiance_ground_surface = \
            incidentirradiance(
                irradiance_direct, irradiance_diffuse, solar_azimuth, solar_altitude, self._azimuth, self._tilt)

        return irradiance_total_surface * self._area

    @property
    def minimum_position(self) -> float:
        if self.minimum_position_state is not None and self.minimum_position_state.value is not None:
            return self.minimum_position_state.value
        return 0.

    @property
    def maximum_position(self) -> float:
        if self.maximum_position_state is not None and self.maximum_position_state.value is not None:
            return self.maximum_position_state.value
        return 1.

    @property
    def position(self) -> float:
        if self.position_state is not None and self.position_state.value is not None:
            return self.position_state.value
        return 0.

    def set_position(self, value) -> None:
        if self.position_state is not None:
            self.position_state.set_value(value)
        else:
            logger.error('cannot set position, no state')


class IShadingPositionCalculator:
    def get_positions(self, shadings: List[IShading], wanted_heat_gain: float):
        raise NotImplementedError


class EqualShadingPositionCalculator(IShadingPositionCalculator):
    def __init__(self, heat_gain_threshold: float = 50, position_step: float = 0.05,
                 now: Callable[[], datetime] = datetime.now):
        self.position_step = position_step
        self.heat_gain_threshold = heat_gain_threshold
        self._now = now

    def get_positions(self, shadings: List[IShading], wanted_heat_gain):
        date = self._now()
        maximum_heat_gains = [s.get_heat_gain(s.minimum_position, date) for s in shadings]
        minimum_heat_gains = [s.get_heat_gain(s.maximum_position, date) for s in shadings]

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
        if self._indoor_temperature_state is not None:
            return self._indoor_temperature_state.value
        return 20.

    def _get_setpoint_temperature(self) -> float:
        if self._setpoint_temperature_state is not None:
            return self._setpoint_temperature_state.value
        return 20.

    def _get_ambient_temperature_min(self) -> float:
        if self._ambient_temperature_min_state is not None:
            return self._ambient_temperature_min_state.value
        return -10.

    def _get_ambient_temperature_max(self) -> float:
        if self._ambient_temperature_max_state is not None:
            return self._ambient_temperature_max_state.value
        return 18.

    def _get_heat_demand_max(self) -> float:
        if self._heat_demand_max_state is not None:
            return self._heat_demand_max_state.value
        return 8000.

    def _get_indoor_temperature_correction_factor(self) -> float:
        if self._indoor_temperature_correction_factor_state is not None:
            return self._indoor_temperature_correction_factor_state.value
        return 0.2

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

        return self._calculate_heat_demand(ambient_temperature, indoor_temperature, setpoint_temperature,
                                           ambient_temperature_min, ambient_temperature_max, heat_demand_max,
                                           indoor_temperature_correction_scale)


class ShadingController:

    SHADING_STATE_TYPE = 'shading'

    def __init__(self,
                 state_manager: IStateManager,
                 wanted_heat_gain_calculator: IWantedHeatGainCalculator,
                 position_calculator: IShadingPositionCalculator,
                 longitude_state: State, latitude_state: State, elevation_state: State,
                 interval: int = 1800):
        self._state_manager = state_manager
        self._wanted_heat_gain_calculator = wanted_heat_gain_calculator
        self._position_calculator = position_calculator

        self._longitude_state = longitude_state
        self._latitude_state = latitude_state
        self._elevation_state = elevation_state

        executors = {
            'default': ThreadPoolExecutor(5),
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 3,
            'misfire_grace_time': 3600
        }
        self.scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
        self.scheduler.add_job(self.run, trigger='interval', seconds=interval)

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown(wait=False)

    def _get_shading_from_state(self, state: State) -> StateBasedShading:
        position_state = None
        minimum_position_state = None
        maximum_position_state = None

        for child in state.children:
            if child.name == 'position':
                position_state = child
            if child.name == 'minimum':
                minimum_position_state = child
            if child.name == 'maximum':
                maximum_position_state = child

        return StateBasedShading(position_state=position_state,
                                 minimum_position_state=minimum_position_state,
                                 maximum_position_state=maximum_position_state,
                                 area=state.config.get('area', 1.0),
                                 transparency=state.config.get('transparency', 0.0),
                                 azimuth=state.config.get('azimuth', 0.0),
                                 tilt=state.config.get('tilt', 90.0),
                                 longitude=self._longitude_state.value or 0.0,
                                 latitude=self._latitude_state.value or 0.0,
                                 elevation=self._elevation_state.value or 0.0)

    def run(self):
        shadings = []
        for state in self._state_manager.all():
            if state.type == self.SHADING_STATE_TYPE:
                shadings.append(self._get_shading_from_state(state))

        wanted_heat_gain = self._wanted_heat_gain_calculator.calculate_wanted_heat_gain()
        positions = self._position_calculator.get_positions(shadings, wanted_heat_gain)

        for shading, position in zip(shadings, positions):
            shading.set_position(position)

    def listen_state_value_changed(self, event: Event):
        state = event.data['state']
        if state.parent.type == self.SHADING_STATE_TYPE:
            self.run()


class Shading(BasePlugin):
    """
    Class to control the HomeCon scheduler

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._state_manager.add('settings', type=None)
        self._state_manager.add('shading', type=None, parent_path='/settings')
        self._state_manager.add('heat_demand', type=None, parent_path='/settings/shading')
        ambient_temperature_state = self._state_manager.add(
            'ambient_temperature', parent_path='/settings/shading/heat_demand',
            type='float', quantity='Temperature', unit='degC',
            label='', description='Ambient temperature', value=15)
        indoor_temperature_state = self._state_manager.add(
            'indoor_temperature', parent_path='/settings/shading/heat_demand',
            type='float', quantity='Temperature', unit='degC',
            label='', description='Ambient temperature', value=20)
        setpoint_temperature_state = self._state_manager.add(
            'setpoint_temperature', parent_path='/settings/shading/heat_demand',
            type='float', quantity='Temperature', unit='degC',
            label='', description='Ambient temperature', value=15)

        self._state_manager.add('location', type=None, parent_path='/settings')
        longitude_state = self._state_manager.add(
            'longitude', parent_path='/settings/location',
            type='float', quantity='Angle', unit='deg',
            label='', description='Longitude', value=5)
        latitude_state = self._state_manager.add(
            'latitude', parent_path='/settings/location',
            type='float', quantity='Angle', unit='deg',
            label='', description='Latitude', value=52)
        elevation_state = self._state_manager.add(
            'elevation', parent_path='/settings/location',
            type='float', quantity='Height', unit='m',
            label='', description='Elevation above sea level', value=60)

        self.controller = ShadingController(
            self._state_manager,
            StateBasedHeatingCurveWantedHeatGainCalculator(
                ambient_temperature_state, indoor_temperature_state, setpoint_temperature_state
            ),
            EqualShadingPositionCalculator(),
            longitude_state, latitude_state, elevation_state
        )

    def start(self):
        self.controller.start()
        logger.debug('Shading plugin Initialized')

    def stop(self):
        super().stop()
        self.controller.stop()

    def listen_state_value_changed(self, event: Event):
        self.controller.listen_state_value_changed(event)

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

    def get_heat_gain(self, position: float, date: datetime, cloud_cover: Optional[float] = 0.0) -> float:
        raise NotImplementedError


class StateBasedShading(IShading):
    """
    position: 0 means fully open, 1 means fully closed
    """

    def __init__(self, name: str, position: float, set_position: Callable[[float], None],
                 minimum_position: Optional[float] = None,
                 maximum_position: Optional[float] = None,
                 area: float = 1., transparency: float = 0., azimuth: float = 180., tilt: float = 90.,
                 longitude: float = 0, latitude: float = 0, elevation: float = 80.):
        self._name = name
        self._position = position
        self._set_position = set_position
        self._minimum_position = minimum_position
        self._maximum_position = maximum_position
        self._area = area
        self.transparency = transparency
        self._azimuth = azimuth
        self._tilt = tilt
        self._longitude = longitude
        self._latitude = latitude
        self._elevation = elevation

    def get_shading_factor(self, position):
        return position * self.transparency + (1 - position) * 1

    def get_heat_gain(self, position: float, date: datetime, cloud_cover: Optional[float] = 0.0) -> float:
        return self.get_shading_factor(position) * self.get_maximum_heat_gain(date, cloud_cover)

    def get_maximum_heat_gain(self, date: datetime, cloud_cover: Optional[float] = 0.0) -> float:
        solar_azimuth, solar_altitude = sunposition(self._latitude, self._longitude, self._elevation,
                                                    timestamp=int(date.timestamp()))
        irradiance_direct_clearsky, irradiance_diffuse_clearsky = clearskyirrradiance(solar_azimuth, solar_altitude)

        irradiance_direct, irradiance_diffuse = cloudyskyirrradiance(
            irradiance_direct_clearsky, irradiance_diffuse_clearsky, cloud_cover, solar_azimuth, solar_altitude,
            timestamp=int(date.timestamp()))
        irradiance_total_surface, irradiance_direct_surface, irradiance_diffuse_surface, irradiance_ground_surface = \
            incidentirradiance(
                irradiance_direct, irradiance_diffuse, solar_azimuth, solar_altitude, self._azimuth, self._tilt)

        return irradiance_total_surface * self._area

    @property
    def minimum_position(self) -> float:
        return self._minimum_position or 0

    @property
    def maximum_position(self) -> float:
        return self._maximum_position or 1

    @property
    def position(self) -> float:
        return self._position

    def set_position(self, value) -> None:
        self._set_position(value)

    def __repr__(self):
        return f'<StateBasedShading {self._name}>'


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


class ShadingController:

    SHADING_STATE_TYPE = 'shading'

    def __init__(self,
                 state_manager: IStateManager,
                 wanted_heat_gain_calculator: IWantedHeatGainCalculator,
                 wanted_heat_gain_state: State,
                 cloud_cover_calculator: ICloudCoverCalculator,
                 cloud_cover_state: State,
                 position_calculator: IShadingPositionCalculator,
                 longitude_state: State, latitude_state: State, elevation_state: State,
                 interval: int = 1800):
        self._state_manager = state_manager
        self._wanted_heat_gain_calculator = wanted_heat_gain_calculator
        self._wanted_heat_gain_state = wanted_heat_gain_state

        self._cloud_cover_calculator = cloud_cover_calculator
        self._cloud_cover_state = cloud_cover_state

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
        logger.info('started shading controller')

    def stop(self):
        self.scheduler.shutdown(wait=False)

    def _get_shading_from_state(self, state: State) -> StateBasedShading:
        position_state = None
        minimum_position_state = None
        maximum_position_state = None

        for child in state.children:
            if child.name == 'position':
                position_state = child
            if child.name == 'minimum_position':
                minimum_position_state = child
            if child.name == 'maximum_position':
                maximum_position_state = child

        if position_state is None:
            raise ValueError('state must have a position child')

        return StateBasedShading(
            name=state.path,
            position=position_state.value,
            set_position=lambda x: position_state.set_value(x),
            minimum_position=minimum_position_state.value
            if minimum_position_state is not None and minimum_position_state.value is not None else None,
            maximum_position=maximum_position_state.value
            if maximum_position_state is not None and maximum_position_state.value is not None else None,
            area=state.config.get('area', 1.0),
            transparency=state.config.get('transparency', 0.0),
            azimuth=state.config.get('azimuth', 0.0),
            tilt=state.config.get('tilt', 90.0),
            longitude=self._longitude_state.value or 0.0,
            latitude=self._latitude_state.value or 0.0,
            elevation=self._elevation_state.value or 0.0
        )

    def run(self):
        logger.debug('running shading controller')
        shadings = []
        for state in self._state_manager.all():
            if state.type == self.SHADING_STATE_TYPE:
                logger.debug(f'creating shading object for state {state}')
                shadings.append(self._get_shading_from_state(state))

        wanted_heat_gain = self._wanted_heat_gain_calculator.calculate_wanted_heat_gain()
        logger.debug(f'calculated wanted heat gain: {wanted_heat_gain:.0f} W')
        self._wanted_heat_gain_state.set_value(wanted_heat_gain)

        cloud_cover = self._cloud_cover_calculator.calculate_cloud_cover()
        logger.debug(f'calculated cloud cover: {cloud_cover:.2f}')
        self._cloud_cover_state.set_value(cloud_cover)

        positions = self._position_calculator.get_positions(shadings, wanted_heat_gain, cloud_cover)
        logger.debug(f'calculated positions: {positions}')

        for shading, position in zip(shadings, positions):
            shading.set_position(position)

    def listen_state_value_changed(self, event: Event):
        state = event.data['state']
        if state.parent is not None and state.parent.type == self.SHADING_STATE_TYPE:
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
            label='', description='Indoor temperature', value=20)
        setpoint_temperature_state = self._state_manager.add(
            'setpoint_temperature', parent_path='/settings/shading/heat_demand',
            type='float', quantity='Temperature', unit='degC',
            label='', description='Setpoint temperature', value=20)
        wanted_heat_gain_state = self._state_manager.add(
            'wanted_heat_gain', parent_path='/settings/shading/heat_demand',
            type='float', quantity='Power', unit='W',
            label='', description='Wanted heat gain', value=15)
        cloud_cover_state = self._state_manager.add(
            'cloud_cover', parent_path='/settings/shading/heat_demand',
            type='float', quantity='', unit='-',
            label='', description='Cloud cover', value=0.)

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

        forecast_state = self._state_manager.get(path='/weather/forecast/hourly/0')
        if forecast_state is not None:
            cloud_cover_calculator = WeatherForecastCloudCoverCalculator(forecast_state)
        else:
            cloud_cover_calculator = DummyCloudCoverCalculator()

        self.controller = ShadingController(
            self._state_manager,
            StateBasedHeatingCurveWantedHeatGainCalculator(
                ambient_temperature_state, indoor_temperature_state, setpoint_temperature_state
            ),
            wanted_heat_gain_state,
            cloud_cover_calculator,
            cloud_cover_state,
            EqualShadingPositionCalculator(),
            longitude_state, latitude_state, elevation_state, interval=10
        )

    def start(self):
        self.controller.start()
        logger.debug('Shading plugin Initialized')

    def stop(self):
        super().stop()
        self.controller.stop()

    def listen_state_value_changed(self, event: Event):
        self.controller.listen_state_value_changed(event)

#!/usr/bin/env python3
import logging
from homecon.core.event import Event
from homecon.core.plugins.plugin import BasePlugin
from homecon.plugins.shading.controller import ShadingController
from homecon.plugins.shading.calculator import EqualShadingPositionCalculator, StateBasedHeatingCurveWantedHeatGainCalculator, \
    DummyCloudCoverCalculator, WeatherForecastCloudCoverCalculator, StateRainCalculator

logger = logging.getLogger(__name__)


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
        rain_state = self._state_manager.add(
            'rain', parent_path='/settings/rain',
            type='bool', quantity='', unit='-',
            label='', description='Rain or not', value=0)

        forecast_state = self._state_manager.get(path='/weather/forecast/hourly/0')
        if forecast_state is not None:
            cloud_cover_calculator = WeatherForecastCloudCoverCalculator(forecast_state)
        else:
            cloud_cover_calculator = DummyCloudCoverCalculator()

        rain_calculator = StateRainCalculator(rain_state)

        self.controller = ShadingController(
            self._state_manager,
            StateBasedHeatingCurveWantedHeatGainCalculator(
                ambient_temperature_state, indoor_temperature_state, setpoint_temperature_state
            ),
            wanted_heat_gain_state,
            cloud_cover_calculator,
            cloud_cover_state,
            rain_calculator,
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

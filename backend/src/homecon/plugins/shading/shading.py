#!/usr/bin/env python3
import logging
from homecon.core.event import Event
from homecon.core.plugins.plugin import BasePlugin
from homecon.plugins.shading.controller import ShadingController
from homecon.plugins.shading.calculator import IrradianceThresholdPositionCalculator, \
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

        wanted_heat_gain_state = self._state_manager.add(
            'wanted_heat_gain', parent_path='/settings/shading',
            type='float', quantity='Power', unit='W',
            label='', description='Wanted heat gain', value=0)
        cloud_cover_state = self._state_manager.add(
            'cloud_cover', parent_path='/settings/shading',
            type='float', quantity='', unit='-',
            label='', description='Cloud cover', value=0.)

        rain_state = self._state_manager.add(
            'rain', parent_path='/settings/shading',
            type='bool', quantity='', unit='-',
            label='', description='Rain or not', value=0)

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

        rain_calculator = StateRainCalculator(rain_state)

        self.controller = ShadingController(
            self._state_manager,
            wanted_heat_gain_state,
            cloud_cover_calculator,
            cloud_cover_state,
            rain_calculator,
            IrradianceThresholdPositionCalculator(),
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

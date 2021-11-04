#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from dataclasses import dataclass
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from homecon.core.plugins.plugin import IPlugin
from homecon.core.states.state import IStateManager
from homecon.core.event import IEventManager, Event
from homecon.util.weather import sunposition

logger = logging.getLogger(__name__)


@dataclass
class Forecast:
    timestamp: int
    temperature: float
    pressure: float
    relative_humidity: float
    dew_point: float
    cloud_cover: float
    wind_speed: float
    wind_direction: float
    icon: str
    rain: float


@dataclass
class DailyForecast:
    timestamp: int
    temperature_min: float
    temperature_max: float
    pressure: float
    relative_humidity: float
    dew_point: float
    cloud_cover: float
    wind_speed: float
    wind_direction: float
    rain: float
    icon: str


class NoForecastAvailableException(Exception):
    pass


class ForecastClient:
    def get_forecast(self) -> (List[DailyForecast], List[Forecast]):
        raise NotImplementedError


class Weather(IPlugin):
    """
    Class to control the HomeCon weather functions
    
    """
    def __init__(self, event_manager: IEventManager, state_manager: IStateManager, interval=300):
        self._event_manager = event_manager
        self._state_manager = state_manager

        weather = self._state_manager.add('weather')

        forecast = self._state_manager.add('forecast', parent=weather)
        self._state_manager.add('last_update', parent=forecast,
                                type='float', quantity='epoch', unit='s',
                                label='', description='', value=0)
        daily = self._state_manager.add('daily', parent=forecast)
        for i in range(7):
            self._state_manager.add(f'{i}', parent=daily)

        hourly = self._state_manager.add('hourly', parent=forecast)
        for i in range(72):
            self._state_manager.add(f'{i}', parent=hourly)

        # add weather states
        self._state_manager.add('temperature', parent=weather,
                                type='float', quantity='temperature', unit='°C',
                                label='Ambient', description='')
        self._state_manager.add('cloud_cover', parent=weather,
                                type='float', quantity='', unit='-',
                                label='Cloud cover', description='')

        sun = self._state_manager.add('sun', parent=weather)
        self.sun_azimuth = self._state_manager.add('azimuth', parent=sun,
                                                   type='float', quantity='angle', unit='°',
                                                   label='Solar Azimuth', description='')
        self.sun_altitude = self._state_manager.add('altitude', parent=sun,
                                                    type='float', quantity='angle', unit='°',
                                                    label='Solar Altitude', description='')

        irradiance = self._state_manager.add('irradiance', parent=sun)
        self._state_manager.add('direct', parent=irradiance,
                                type='float', quantity='irradiance', unit='W/m2',
                                label='Solar Direct Irradiance', description='')
        self._state_manager.add('diffuse', parent=irradiance,
                                type='float', quantity='irradiance', unit='W/m2',
                                label='Solar Diffuse Irradiance', description='')

        executors = {
            'default': ThreadPoolExecutor(5),
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 3,
            'misfire_grace_time': 3600
        }

        self.scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
        self.scheduler.add_job(self.set_sun_position, trigger='interval', seconds=interval)

        self._event_handlers = {}

    @property
    def name(self):
        return 'weather'

    def start(self):
        # schedule sun position updating
        self.scheduler.start()
        logger.info('Weather plugin Initialized')

    def stop(self):
        super().stop()
        self.scheduler.shutdown(wait=False)

    def handle_event(self, event: Event):
        handler = self._event_handlers.get(event.type)
        if handler is not None:
            handler(event)

    def set_sun_position(self):
        """
        Update the suns position
        """
        # calculate the current suns position
        latitude = self._state_manager.get(path='/settings/location/latitude').value    # N+
        longitude = self._state_manager.get(path='/settings/location/longitude').value   # E+
        elevation = self._state_manager.get(path='/settings/location/elevation').value

        if elevation is None:
            elevation = 0
            logging.warning('No elevation supplied, assuming 0 m')

        azimuth = None
        altitude = None
        if latitude is not None and longitude is not None:
            azimuth, altitude = sunposition(latitude, longitude, elevation)
            azimuth = round(float(azimuth), 2)
            altitude = round(float(altitude), 2)

        self._state_manager.get(path='/weather/sun/azimuth').set_value(azimuth, source=self.name)
        self._state_manager.get(path='/weather/sun/altitude').set_value(altitude, source=self.name)

#     def ambienttemperature(self):
#         """
#         Estimate the ambient temperature from the forecast and measurements
#
#         """
#
#         dt_ref = datetime.datetime(1970, 1, 1)
#         dt_now = datetime.datetime.utcnow()
#         timestamp_now = (dt_now-dt_ref).total_seconds()
#
#         # get the prediction closest to now
#         timestamps = []
#         values = []
#         for i in range(48):
#             forecast = core.states['weather/forecast/hourly/{}'.format(i)].value
#
#             if not forecast is None:
#                 timestamps.append(forecast['timestamp'])
#                 values.append(forecast['temperature'])
#
#                 if forecast['timestamp'] > timestamp_now:
#                     break
#
#         if len(timestamps)>0:
#             value_forecast = np.interp(timestamp_now,timestamps,values)
#         else:
#             value_forecast = None
#
#         # get ambient temperature measurements
#         value_sensors = []
#         confidence_sensors = []
#         for sensor in core.components.find(type='ambienttemperaturesensor'):
#             val = sensor.states['value'].value
#             if not val is None:
#                 value_sensors.append( val )
#                 confidence_sensors.append( sensor.config['confidence'] )
#
#         # combine
#         if not value_forecast is None:
#             value_sensors.append(value_forecast)
#             confidence_sensors.append(0.5)
#
#         if len(value_sensors) > 0:
#             value = sum([v*c for v,c in zip(value_sensors,confidence_sensors)])/sum(confidence_sensors)
#         else:
#             value = None
#
#         return value
#
#
#     def cloudcover(self):
#         """
#         Estimate the cloudcover from the forecast and measurements
#
#         """
#         dt_ref = datetime.datetime(1970, 1, 1)
#         dt_now = datetime.datetime.utcnow()
#         timestamp_now = (dt_now-dt_ref).total_seconds()
#
#         # get the prediction closest to now
#         timestamps = []
#         values = []
#         for i in range(48):
#             forecast = core.states['weather/forecast/hourly/{}'.format(i)].value
#
#             if not forecast is None:
#                 timestamps.append(forecast['timestamp'])
#                 values.append(forecast['cloudcover'])
#
#                 if forecast['timestamp'] > timestamp_now:
#                     break
#
#         if len(timestamps)>0:
#             value_forecast = np.interp(timestamp_now,timestamps,values)
#         else:
#             value_forecast = None
#
#
#
#         # get cloudcover measurements
#         value_sensors = []
#         confidence_sensors = []
#
#         solar_azimuth = core.states['weather/sun/azimuth'].value
#         solar_altitude = core.states['weather/sun/altitude'].value
#
#         if not solar_azimuth is None and not solar_altitude is None:
#             I_direct_clearsky,I_diffuse_clearsky = util.weather.clearskyirrradiance(solar_azimuth,solar_altitude)
#
#
#
#             if not I_direct_clearsky is None and not I_diffuse_clearsky is None:
#
#                 for sensor in core.components.find(type='irradiancesensor'):
#                     val = sensor.states['value'].value
#
#                     surface_azimuth = sensor.config['azimuth']
#                     surface_tilt = sensor.config['tilt']
#
#                     if not val is None:
#                         tempcloudcover = np.linspace(1.0,0.0,6)
#                         tempirradiance = []
#                         for c in tempcloudcover:
#                             I_direct_cloudy , I_diffuse_cloudy = util.weather.cloudyskyirrradiance(I_direct_clearsky,I_diffuse_clearsky,c,solar_azimuth,solar_altitude)
#                             I_total_surface, I_direct_surface, I_diffuse_surface, I_ground_surface = util.weather.incidentirradiance(I_direct_cloudy,I_diffuse_cloudy,solar_azimuth,solar_altitude,surface_azimuth,surface_tilt)
#                             tempirradiance.append(I_total_surface)
#
#                         tempirradiance = np.array(tempirradiance)
#
#
#                         if max(tempirradiance) > 0:
#                             cloudcover = np.interp(val,tempirradiance,tempcloudcover)
#                             cloudcover = max(0,min(1,cloudcover))
#
#                             value_sensors.append( cloudcover )
#                             confidence_sensors.append( sensor.config['confidence'] )
#
#
#         # combine
#         if not value_forecast is None:
#             value_sensors.append(value_forecast)
#             confidence_sensors.append(0.5)
#
#         if len(value_sensors) > 0:
#             value = sum([v*c for v,c in zip(value_sensors,confidence_sensors)])/sum(confidence_sensors)
#         else:
#             value = None
#
#         return value
#
#
#     def listen_state_updated(self,event):
#
#         if event.data['state'].path == 'weather/sun/altitude' or event.data['state'].path == 'weather/cloudcover':
#
#
#             cloudcover = core.states['weather/cloudcover'].value
#             if cloudcover is None:
#                 cloudcover = 0
#
#             # update the irradiance
#             solar_azimuth = core.states['weather/sun/azimuth'].value
#             solar_altitude = core.states['weather/sun/altitude'].value
#
#             if not solar_azimuth is None and not solar_altitude is None:
#
#                 I_direct_clearsky,I_diffuse_clearsky = util.weather.clearskyirrradiance(solar_azimuth,solar_altitude)
#                 I_direct_cloudy,I_diffuse_cloudy = util.weather.cloudyskyirrradiance(I_direct_clearsky,I_diffuse_clearsky,cloudcover,solar_azimuth,solar_altitude)
#                 core.states['weather/irradiancedirect'].value = round(float(I_direct_cloudy),2)
#                 core.states['weather/irradiancediffuse'].value = round(float(I_diffuse_cloudy),2)
#
#
#         if 'component' in event.data['state'].config:
#             component = core.components[event.data['state'].config['component']]
#
#             if component.type == 'ambienttemperaturesensor':
#                 ambienttemperature = self.ambienttemperature()
#                 if not ambienttemperature is None:
#                     core.states['weather/temperature'].value = round(ambienttemperature,2)
#
#             if component.type == 'irradiancesensor':
#                 cloudcover = self.cloudcover()
#                 if not cloudcover is None:
#                     core.states['weather/cloudcover'].value = round(cloudcover,3)
#
#
#     def listen_forecast_updated(self,event):
#
#         core.states['weather/temperature'].value = round(self.ambienttemperature(),2)
#         core.states['weather/cloudcover'].value = round(self.cloudcover(),3)
#
#
# class Ambienttemperaturesensor(core.component.Component):
#     """
#     a class implementing a temperature sensor
#
#     """
#
#     default_config = {
#         'confidence': 0.5,
#     }
#     linked_states = {
#         'value': {
#             'default_config': {},
#             'fixed_config': {},
#         },
#     }
#
#
# core.components.register(Ambienttemperaturesensor)
#
#
# class Irradiancesensor(core.component.Component):
#     """
#     a class implementing an irradiance sensor
#
#     """
#
#     default_config = {
#         'azimuth': 0,
#         'tilt': 0,
#         'confidence': 0.5,
#     }
#     linked_states = {
#         'value': {
#                 'default_config': {},
#                 'fixed_config': {},
#             },
#     }
#
# core.components.register(Irradiancesensor)
#
#
#

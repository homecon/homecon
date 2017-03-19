#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import concurrent.futures
import asyncio
import ephem
import numpy as np

from .. import core
from .. import util

class Weather(core.plugin.Plugin):
    """
    Class to control the HomeCon weather functions
    
    """

    def initialize(self):
        
        # create a thread pool executor for loading api data
        self.executor = concurrent.futures.ThreadPoolExecutor(7)


        # add forecast states
        core.states.add('weather/forecast/lastupdate', config={'datatype': 'number', 'quantity':'', 'unit':'','label':'', 'description':'', 'private':True})

        for i in range(7):
            core.states.add('weather/forecast/daily/{}'.format(i), config={'datatype': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False, 'private':True})
        
        for i in range(24*7):
            core.states.add('weather/forecast/hourly/{}'.format(i), config={'datatype': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False, 'private':True})


        # add weather states
        core.states.add('weather/temperature',       config={'datatype': 'number', 'quantity':'temperature', 'unit':'°C'  , 'label':'Ambient', 'description':''})
        core.states.add('weather/cloudcover',        config={'datatype': 'number', 'quantity':''           , 'unit':''    , 'label':'Cloud cover' , 'description':''})

        core.states.add('weather/sun/azimuth',           config={'datatype': 'number', 'quantity':'angle' , 'unit':'°', 'label':'Azimuth' , 'description':''})
        core.states.add('weather/sun/altitude',          config={'datatype': 'number', 'quantity':'angle' , 'unit':'°', 'label':'Altitude' , 'description':''})

        core.states.add('weather/irradiancedirect',  config={'datatype': 'number', 'quantity':'irradiance' , 'unit':'W/m2', 'label':'Direct' , 'description':''})
        core.states.add('weather/irradiancediffuse', config={'datatype': 'number', 'quantity':'irradiance' , 'unit':'W/m2', 'label':'Diffuse', 'description':''})


        # schedule sun position updating
        self._loop.create_task(self.schedule_sunposition())

        logging.debug('Weather plugin Initialized')



    async def schedule_sunposition(self):
        """
        Schedule updating of the suns position

        """

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = dt_now + datetime.timedelta(minutes=2)

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )


            # calculate the suns position
            latitude = core.states['settings/location/latitude'].value    # N+
            longitude = core.states['settings/location/longitude'].value   # E+
            elevation = core.states['settings/location/elevation'].value

            if elevation is None:
                elevation = 0
                logging.warning('No elevation supplied, assuming 0 m')

            azimuth = None
            altitude = None
            if not latitude is None and not longitude is None:
                azimuth,altitude = util.weather.sunposition(latitude,longitude,elevation)
                azimuth = round(float(azimuth),2)
                altitude = round(float(altitude),2)

            core.states['weather/sun/azimuth'].value = azimuth
            core.states['weather/sun/altitude'].value = altitude

            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)



    def ambienttemperature(self):
        """
        Estimate the ambient temperature from the forecast and measurements

        """

        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = (dt_now-dt_ref).total_seconds()

        # get the prediction closest to now
        timestamps = []
        values = []
        for i in range(48):
            forecast = core.states['weather/forecast/hourly/{}'.format(i)].value

            if not forecast is None:
                timestamps.append(forecast['timestamp'])
                values.append(forecast['temperature'])

                if forecast['timestamp'] > timestamp_now:
                    break

        if len(timestamps)>0:
            value_forecast = np.interp(timestamp_now,timestamps,values)
        else:
            value_forecast = None

        # get ambient temperature measurements
        value_sensors = []
        confidence_sensors = []
        for sensor in core.components.find(type='ambienttemperaturesensor'):
            val = sensor.states['value'].value
            if not val is None:
                value_sensors.append( val )
                confidence_sensors.append( sensor.config['confidence'] )

        # combine
        if not value_forecast is None:
            value_sensors.append(value_forecast)
            confidence_sensors.append(0.5)

        if len(value_sensors) > 0:
            value = sum([v*c for v,c in zip(value_sensors,confidence_sensors)])/sum(confidence_sensors)
        else:
            value = None

        return value


    def cloudcover(self):
        """
        Estimate the cloudcover from the forecast and measurements

        """
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = (dt_now-dt_ref).total_seconds()

        # get the prediction closest to now
        timestamps = []
        values = []
        for i in range(48):
            forecast = core.states['weather/forecast/hourly/{}'.format(i)].value

            if not forecast is None:
                timestamps.append(forecast['timestamp'])
                values.append(forecast['cloudcover'])

                if forecast['timestamp'] > timestamp_now:
                    break

        if len(timestamps)>0:
            value_forecast = np.interp(timestamp_now,timestamps,values)
        else:
            value_forecast = None



        # get cloudcover measurements
        value_sensors = []
        confidence_sensors = []

        solar_azimuth = core.states['weather/sun/azimuth'].value
        solar_altitude = core.states['weather/sun/altitude'].value

        if not solar_azimuth is None and not solar_altitude is None:
            I_direct_clearsky,I_diffuse_clearsky = util.weather.clearskyirrradiance(solar_azimuth,solar_altitude)



            if not I_direct_clearsky is None and not I_diffuse_clearsky is None:

                for sensor in core.components.find(type='irradiancesensor'):
                    val = sensor.states['value'].value

                    surface_azimuth = sensor.config['azimuth']
                    surface_tilt = sensor.config['tilt']

                    if not val is None:
                        tempcloudcover = np.linspace(1.0,0.0,6)
                        tempirradiance = []
                        for c in tempcloudcover:
                            I_direct_cloudy , I_diffuse_cloudy = util.weather.cloudyskyirrradiance(I_direct_clearsky,I_diffuse_clearsky,c,solar_azimuth,solar_altitude)
                            I_total_surface, I_direct_surface, I_diffuse_surface, I_ground_surface = util.weather.incidentirradiance(I_direct_cloudy,I_diffuse_cloudy,solar_azimuth,solar_altitude,surface_azimuth,surface_tilt)
                            tempirradiance.append(I_total_surface)
                            
                        tempirradiance = np.array(tempirradiance)

                        print(tempcloudcover)
                        print(tempirradiance)

                        if max(tempirradiance) > 0:
                            cloudcover = np.interp(val,tempirradiance,tempcloudcover)
                            cloudcover = max(0,min(1,cloudcover))

                            value_sensors.append( cloudcover )
                            confidence_sensors.append( sensor.config['confidence'] )


        # combine
        if not value_forecast is None:
            value_sensors.append(value_forecast)
            confidence_sensors.append(0.5)

        if len(value_sensors) > 0:
            value = sum([v*c for v,c in zip(value_sensors,confidence_sensors)])/sum(confidence_sensors)
        else:
            value = None

        return value


    def listen_state_changed(self,event):

        if event.data['state'].path == 'weather/sun/altitude' or event.data['state'].path == 'weather/cloudcover':
            

            cloudcover = core.states['weather/cloudcover'].value
            if cloudcover is None:
                cloudcover = 0

            # update the irradiance
            solar_azimuth = core.states['weather/sun/azimuth'].value
            solar_altitude = core.states['weather/sun/altitude'].value

            if not solar_azimuth is None and not solar_altitude is None:

                I_direct_clearsky,I_diffuse_clearsky = util.weather.clearskyirrradiance(solar_azimuth,solar_altitude)
                I_direct_cloudy,I_diffuse_cloudy = util.weather.cloudyskyirrradiance(I_direct_clearsky,I_diffuse_clearsky,cloudcover,solar_azimuth,solar_altitude)
                core.states['weather/irradiancedirect'].value = round(float(I_direct_cloudy),2)
                core.states['weather/irradiancediffuse'].value = round(float(I_diffuse_cloudy),2)


        if 'component' in event.data['state'].config:
            component = core.components[event.data['state'].config['component']]

            if component.type == 'ambienttemperaturesensor':
                ambienttemperature = self.ambienttemperature()
                if not ambienttemperature is None:
                    core.states['weather/temperature'].value = round(ambienttemperature,2)

            if component.type == 'irradiancesensor':
                cloudcover = self.cloudcover()
                if not cloudcover is None:
                    core.states['weather/cloudcover'].value = round(cloudcover,3)


    def listen_forecast_updated(self,event):

        core.states['weather/temperature'].value = round(self.ambienttemperature(),2)
        core.states['weather/cloudcover'].value = round(self.cloudcover(),3)


class Ambienttemperaturesensor(core.component.Component):
    """
    a class implementing a temperature sensor
    
    """

    default_config = {
        'confidence': 0.5,
    }
    linked_states = {
        'value': {
            'default_config': {},
            'fixed_config': {},
        },
    }


core.components.register(Ambienttemperaturesensor)


class Irradiancesensor(core.component.Component):
    """
    a class implementing a temperature sensor
    
    """

    default_config = {
        'azimuth': 0,
        'tilt': 0,
        'confidence': 0.5,
    }
    linked_states = {
        'value': {
                'default_config': {},
                'fixed_config': {},
            },
    }

core.components.register(Irradiancesensor)




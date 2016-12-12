#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import urllib.request
import json
import concurrent.futures
import asyncio
import aiohttp
import ephem
import numpy as np

from .. import plugin
from .. import components
from ..util import weather

class Weather(plugin.Plugin):
    """
    Class to control the HomeCon weather functions
    
    """

    def initialize(self):
        
        # create a thread pool executor for loading api data
        self.executor = concurrent.futures.ThreadPoolExecutor(7)

        # register components
        self.register_component(Ambienttemperaturesensor)
        self.register_component(Irradiancesensor)


        # add settings states
        self._states.add('settings/weather/service', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':''})
        self._states.add('settings/weather/apikey', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':''})
        self._states.add('weather/forecast/lastupdate', config={'type': 'number', 'quantity':'', 'unit':'','label':'', 'description':''})


        # add forecast states
        for i in range(7):
            self._states.add('weather/forecast/daily/{}'.format(i), config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})
        
        for i in range(24*7):
            self._states.add('weather/forecast/hourly/{}'.format(i), config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})


        # add weather states
        self._states.add('weather/temperature',       config={'type': 'number', 'quantity':'temperature', 'unit':'°C'  , 'label':'Ambient', 'description':''})
        self._states.add('weather/cloudcover',        config={'type': 'number', 'quantity':''           , 'unit':''    , 'label':'Cloud cover' , 'description':''})

        self._states.add('weather/sun/azimuth',           config={'type': 'number', 'quantity':'angle' , 'unit':'°', 'label':'Azimuth' , 'description':''})
        self._states.add('weather/sun/altitude',          config={'type': 'number', 'quantity':'angle' , 'unit':'°', 'label':'Altitude' , 'description':''})

        self._states.add('weather/irradiancedirect',  config={'type': 'number', 'quantity':'irradiance' , 'unit':'W/m2', 'label':'Direct' , 'description':''})
        self._states.add('weather/irradiancediffuse', config={'type': 'number', 'quantity':'irradiance' , 'unit':'W/m2', 'label':'Diffuse', 'description':''})


        # schedule forecast loading
        self._loop.create_task(self.schedule_forecast())

        # schedule sun position updating
        self._loop.create_task(self.schedule_sunposition())

        logging.debug('Weather plugin Initialized')


    async def schedule_forecast(self):
        """
        Schedule forecast loading from a webservice and schedules itself to run again an hour later

        """

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = (dt_now + datetime.timedelta(hours=1)).replace(minute=1,second=0,microsecond=0)

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )

            # check the last load time to avoid frequent loading upon restarts
            if self._states['weather/forecast/lastupdate'].value is None or self._states['weather/forecast/lastupdate'].value < timestamp_now-600:

                # load the forecast
                success = False
                if self._states['settings/weather/service'].value == 'darksky':
                    success = await self.darksky_forecast()

                if success:
                    self._states['weather/forecast/lastupdate'].value = round(timestamp_now)

                    self._states['weather/temperature'].value = round(self.ambienttemperature(),2)
                    self._states['weather/cloudcover'].value = round(self.cloudcover(),3)


            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)



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
            latitude = self._states['settings/location/latitude'].value    # N+
            longitude = self._states['settings/location/longitude'].value   # E+
            elevation = self._states['settings/location/elevation'].value

            if elevation is None:
                elevation = 0
                logging.warning('No elevation supplied, assuming 0 m')

            azimuth = None
            altitude = None
            if not latitude is None and not longitude is None:
                azimuth,altitude = weather.sunposition(latitude,longitude,elevation)
                azimuth = round(float(azimuth),2)
                altitude = round(float(altitude),2)

            self._states['weather/sun/azimuth'].value = azimuth
            self._states['weather/sun/altitude'].value = altitude

            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)



    async def darksky_forecast(self):
        """
        Loads a forecast from darksky.net
        """

        # everything is wrapped in a try except statement as things to avoid errors throug api outages etc.
        try:
            # create a list of times to poll
            now = datetime.datetime.utcnow().replace( second=0, microsecond=0)
            timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

            timestamplist = [timestamp+i*24*3600 for i in range(7)]

            forecast_daily = range(7)
            forecast_hourly = range(7*24)
 
            for i,timestamp in enumerate(timestamplist):
                url = 'https://api.darksky.net/forecast/{}/{},{},{}?units=si'.format(self._states['settings/weather/apikey'].value,self._states['settings/location/latitude'].value,self._states['settings/location/longitude'].value,timestamp)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        response = json.loads(await resp.text())

                        # daily values
                        data = response['daily']['data'][0]

                        forecast = {}
                        forecast['timestamp'] = data['time']
                        forecast['temperature_day'] = data['temperatureMax']
                        forecast['temperature_night'] = data['temperatureMin']
                        forecast['pressure'] = data['pressure']
                        forecast['humidity'] = data['humidity']
                        forecast['icon'] = data['icon']
                        try:
                            forecast['cloudcover'] = data['cloudCover']
                        except:
                            forecast['cloudcover'] = 0
                        forecast['wind_speed'] = data['windSpeed']
                        forecast['wind_direction'] = data['windBearing']
                        try:
                            forecast['precipitation_intensity'] = data['precipIntensity']
                        except:
                            forecast['precipitation_intensity'] = 0
                        try:
                            forecast['precipitation_probability'] = data['precipProbability']
                        except:
                            forecast['precipitation_probability'] = 0

                        #forecast_daily.append(forecast)
                        await self._states['weather/forecast/daily/{}'.format(i)].set( forecast )


                        # hourly values
                        for j,data in enumerate(response['hourly']['data']):
                            forecast = {}
                            forecast['timestamp'] = data['time']
                            forecast['temperature'] = data['temperature']
                            forecast['pressure'] = data['pressure']
                            forecast['humidity'] = data['humidity']
                            forecast['icon'] = data['icon']
                            try:
                                forecast['cloudcover'] = data['cloudCover']
                            except:
                                forecast['cloudcover'] = 0
                            forecast['wind_speed'] = data['windSpeed']
                            forecast['wind_direction'] = data['windBearing']
                            try:
                                forecast['precipitation_intensity'] = data['precipIntensity']
                            except:
                                forecast['precipitation_intensity'] = 0
                            try:
                                forecast['precipitation_probability'] = data['precipProbability']
                            except:
                                forecast['precipitation_probability'] = 0

                            #forecast_hourly.append(forecast)
                            await self._states['weather/forecast/hourly/{}'.format(i*24+j)].set( forecast )

            logging.debug('Weather forecast loaded from darksky.net')

            return True

        except Exception as e:
            logging.error('Could not load data from Darksky.net: {}'.format(e))

            return False


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
            forecast = self._states['weather/forecast/hourly/{}'.format(i)].value

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


        # combine
        value = value_forecast

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
            forecast = self._states['weather/forecast/hourly/{}'.format(i)].value

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


        # combine
        value = value_forecast

        return value


    def listen_state_changed(self,event):

        if event.data['state'].path == 'weather/sun/altitude' or event.data['state'].path == 'weather/cloudcover':
            

            cloudcover = self._states['weather/cloudcover'].value
            if cloudcover is None:
                cloudcover = 0

            # update the irradiance
            solar_azimuth = self._states['weather/sun/azimuth'].value
            solar_altitude = self._states['weather/sun/altitude'].value

            if not solar_azimuth is None and not solar_altitude is None:

                I_direct_clearsky,I_diffuse_clearsky = weather.clearskyirrradiance(solar_azimuth,solar_altitude)
                I_direct_cloudy,I_diffuse_cloudy = weather.cloudyskyirrradiance(I_direct_clearsky,I_diffuse_clearsky,cloudcover,solar_azimuth,solar_altitude)
                self._states['weather/irradiancedirect'].value = round(float(I_direct_cloudy),2)
                self._states['weather/irradiancediffuse'].value = round(float(I_diffuse_cloudy),2)








class Ambienttemperaturesensor(components.Component):
    """
    a class implementing a temperature sensor
    
    """

    def initialize(self):
        self.states = {
            'value': {
                'default_config': {
                    'confidence': 0.5,
                },
                'fixed_config': {},
            },
        }
        self.config = {
        }


class Irradiancesensor(components.Component):
    """
    a class implementing a temperature sensor
    
    """

    def initialize(self):
        self.states = {
            'value': {
                'default_config': {
                    'orientation': 0,
                    'tilt': 0,
                    'confidence': 0.5,
                },
                'fixed_config': {},
            },
        }
        self.config = {
        }



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

class Weather(plugin.Plugin):
    """
    Class to control the HomeCon weather functions
    
    """

    def initialize(self):
        
        # create a thread pool executor for loading api data
        self.executor = concurrent.futures.ThreadPoolExecutor(7)

        # register components
        self.register_component(Temperaturesensor)
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
        self._states.add('weather/clouds',            config={'type': 'number', 'quantity':''           , 'unit':''    , 'label':'Clouds' , 'description':''})

        self._states.add('weather/sun/azimut',            config={'type': 'number', 'quantity':'angle' , 'unit':'°', 'label':'Azimut' , 'description':''})
        self._states.add('weather/sun/altitude',          config={'type': 'number', 'quantity':'angle' , 'unit':'°', 'label':'Azimut' , 'description':''})

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
            if self._states['weather/forecast/lastupdate'].value is None or self._states['weather/forecast/lastupdate'].value < timestamp_now-300:

                # load the forecast
                if self._states['settings/weather/service'].value == 'darksky':
                    await self.darksky_forecast()

                self._states['weather/forecast/lastupdate'].value = timestamp_now


            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)

            #when = self._loop.time() + timestamp_when - timestamp_now
            #self._loop.call_at(when,self.forecast)



    async def schedule_sunposition(self):
        """
        Schedule updating of the suns position

        """

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = dt_now + datetime.timedelta(minutes=1)

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )


            # calculate the suns position

            azimut,altitude = self.sunposition()
            self._states['weather/sun/azimut'].value = azimut
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
                            forecast['clouds'] = data['cloudCover']
                        except:
                            forecast['clouds'] = 0
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
                                forecast['clouds'] = data['cloudCover']
                            except:
                                forecast['clouds'] = 0
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

        except Exception as e:
            logging.error('Could not load data from Darksky.net: {}'.format(e))


    def sunposition(self,utcdatetime=None):
        """
        Returns the sun azimuth and altitude at a certain time at the current
        location
        
        Parameters
        ----------
        utcdatetime : datetime.datetime
            the datetime when to compute the sun position

        Returns
        -------
        azimut : number
            sun azimut in degrees
            0deg is N, 90deg is E, 180deg is S, 270deg is W

        altitude : number
            sun altitude in degrees
            0deg is the horizon, 90deg is vertical

        Notes
        -----
        See http://rhodesmill.org/pyephem/quick.html for an ephem introduction

        """

        if utcdatetime == None:
            utcdatetime = datetime.datetime.utcnow()

        # create an ephem observer
        obs = ephem.Observer()
        
        obs.lat = self._states['settings/location/latitude'].value*np.pi/180     #N+
        obs.lon =self._states['settings/location/longitude'].value*np.pi/180     #E+
        obs.elev = self._states['settings/location/elevation'].value
        obs.date = utcdatetime

        sun = ephem.Sun(obs)
        sun.compute(obs)
        
        azimut = sun.az*180/np.pi
        altitude = sun.alt*180/np.pi

        return azimut,altitude



    def clearskyirrradiance(self,utcdatetime=None):
        """
        Compute the clear sky theoretical direct and diffuse solar irradiance
        at a certain time at the current location according to [1]

        Parameters
        ----------
        utcdatetime : datetime.datetime
            the datetime when to compute the irradiance

        Notes
        -----
        [1] ASHRAE Fundamentals p. x.x

        """

        if utcdatetime == None:
            utcdatetime = datetime.datetime.utcnow()

        azimut,altitude = self.sunposition(utcdatetime)

        # air mass between the observer and the sun
        if 6.07995 + np.radians(altitude) > 0:
            m = 1/(np.sin(np.radians(altitude)) + 0.50572*(6.07995 + np.radians(altitude))**-1.6364);
        else:
            m = 0

        # day of the year
        n = float(utcdatetime.strftime('%j'))

        # extraterrestrial solar radiation
        Esc = 1367 # solar constant
        E0 = Esc*(1 + 0.033*np.cos(2*np.pi*(n-3)/365))

        # optical depths
        tau_b = np.interp(n,np.cumsum([-10,31,31,28,31,30,31,30,31,31,30,31,30,31]),[0.320,0.325,0.349,0.383,0.395,0.448,0.505,0.556,0.593,0.431,0.373,0.339,0.320,0.325]);
        tau_d = np.interp(n,np.cumsum([-10,31,31,28,31,30,31,30,31,31,30,31,30,31]),[2.514,2.461,2.316,2.176,2.175,2.028,1.892,1.779,1.679,2.151,2.317,2.422,2.514,2.461]);

        ab = 1.219 - 0.043*tau_b - 0.151*tau_d - 0.204*tau_b*tau_d; 
        ad = 0.202 + 0.852*tau_b - 0.007*tau_d -0.357*tau_b*tau_d;

        if altitude > 0:
            I_direct = E0*np.exp(-tau_b*m**ab);
        else:
            I_direct = 0

        if altitude > -2:
            I_diffuse = E0*np.exp(-tau_d*m**ad);
        else:
            I_diffuse = 0

        return I_direct,I_diffuse



    def listen_state_changed(self,event):
        if event.data['state'].path == 'weather/sun/altitude' or event.data['state'].path == 'weather/clouds':
            # update the irradiance
            I_direct,I_diffuse = self.clearskyirrradiance()

            self._states['weather/irradiancedirect'].value = I_direct#*(1-self._states['weather/clouds'].value)
            self._states['weather/irradiancediffuse'].value = I_diffuse#*(1-self._states['weather/clouds'].value)




class Temperaturesensor(components.Component):
    """
    a class implementing a temperature sensor
    
    """

    def initialize(self):
        self.states = {
            'value': {
                'default_config': {},
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
                },
                'fixed_config': {},
            },
        }
        self.config = {
        }



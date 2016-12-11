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

            azimuth,altitude = self.sunposition()
            self._states['weather/sun/azimuth'].value = round(azimuth,2)
            self._states['weather/sun/altitude'].value = round(altitude,2)

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
        azimuth : number
            sun azimuth in degrees
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

        lat = self._states['settings/location/latitude'].value    # N+
        lon = self._states['settings/location/longitude'].value   # E+
        elev = self._states['settings/location/elevation'].value

        if elev is None:
            elev = 0
            logging.warning('No elevation supplied, assuming 0 m')

        azimuth = None
        altitude = None

        if not lat is None and not lon is None:
            obs.lat = np.radians(lat)
            obs.lon = np.radians(lon)
            obs.elev = elev
            obs.date = utcdatetime

            sun = ephem.Sun(obs)
            sun.compute(obs)
            
            azimuth = sun.az*180/np.pi
            altitude = sun.alt*180/np.pi

        return azimuth,altitude



    def clearskyirrradiance(self,utcdatetime=None):
        """
        Compute the clear sky theoretical direct and diffuse solar irradiance
        at a certain time at the current location according to [1] results are
        similar to [2]

        Parameters
        ----------
        utcdatetime : datetime.datetime
            the datetime when to compute the irradiance

        Returns
        -------
        I_direct_normal : number
            direct normal irrradiance (W/m2)

        I_diffuse_horizontal : number
            diffuse horrizontal irrradiance (W/m2)

        Notes
        -----
        [1] ASHRAE 2009, H28, p9-11.
        [2] ASHRAE 2005, H31

        """

        if utcdatetime == None:
            utcdatetime = datetime.datetime.utcnow()

        azimuth,altitude = self.sunposition(utcdatetime)

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
            I_direct_normal = E0*np.exp(-tau_b*m**ab);
        else:
            I_direct_normal = 0

        if altitude > -2:
            I_diffuse_horizontal = E0*np.exp(-tau_d*m**ad);
        else:
            I_diffuse_horizontal = 0

        return I_direct_normal,I_diffuse_horizontal


    def incidentirradiance(self,I_direct_normal,I_diffuse_horizontal,solar_azimuth,solar_altitude,surface_azimuth,surface_tilt):
        """
        Method returns irradiation on a tilted surface according to ASHRAE

        Parameters
        ----------
        I_direct_normal : number
            local beam irradiation (W/m2)

        I_diffuse_horizontal : number
            local diffuse irradiation (W/m2)

        solar_azimuth : number
            solar azimuth angle from N in E direction (0=N, 90=E, 180=S, -270 = W) (deg)

        solar_altitude : number
            solar altitude angle (deg)

        surface_azimuth: number
            surface normal azimuth angle from N in E direction (0=N, 90=E, 180=S, 270 = W) (deg)

        surface_tilt: number
            surface tilt angle (0: facing up, pi/2: vertical, pi: facing down) (deg)

        output:
        I_tot : number
            total irradiance on tilted surface  (W/m2)

        I_direct: 
            Direct irradiance on tilted surface  (W/m2)

        I_diffuse: 
            Diffuse irradiance on tilted surface  (W/m2)

        I_ground: 
            Ground reflected radiation on tilted surface  (W/m2)

        """

        # surface solar azimuth (-pi/2< gamma < pi/2, else surface is in shade)
        gamma = solar_azimuth-surface_azimuth

        # incidence
        cos_theta = np.cos(np.radians(solar_altitude))*np.cos(np.radians(gamma))*np.sin(np.radians(surface_tilt)) + np.sin(np.radians(solar_altitude))*np.cos(np.radians(surface_tilt))

        # beam irradiation
        if cos_theta > 0:
            I_direct = I_direct_normal*cos_theta
        else:
            I_direct = 0

        # diffuse irradiation
        Y = max(0.45, 0.55 + 0.437*cos_theta+ 0.313*cos_theta**2)
        if surface_tilt < 90:
            I_diffuse = I_diffuse_horizontal*(Y*np.sin(np.radians(surface_tilt)) + np.cos(np.radians(surface_tilt)))
        else:
            I_diffuse = I_diffuse_horizontal*Y*np.sin(np.radians(surface_tilt))

        # ground reflected radiation
        rho_g = 0.2
        I_ground = (I_direct_normal*np.sin(np.radians(solar_altitude)) + I_diffuse_horizontal)*rho_g*(1-np.cos(np.radians(surface_tilt)))/2

        # total irradiation
        I_tot = (I_direct + I_diffuse + I_ground)

        return I_tot, I_direct, I_diffuse, I_ground



    def cloudyskyirrradiance(self,I_direct_clearsky,I_diffuse_clearsky,cloudcover,utcdatetime=None):
        """
        Correction of the direct normal and diffuse horizontal irradiance using
        the the cloudcover fraction in accordance with [3] and [4].
        Credits to Damien Picard for the literature and coding

        Parameters
        ----------
        I_direct_clearsky : number
            direct clearsky solar irradiance

        I_diffuse_clearsky : number
            diffuse clearsky solar irradiance

        cloudcover : number
            fraction of the sky covered by clouds

        utcdatetime : number
            the datetime when to compute the irradiance

        Returns
        -------
        I_direct_cloudy : number
            direct solar normal irradiance corrected by cloud coverage

        I_diffuse_cloudy : number
            diffuse solar horizontal irradiance corrected by cloud coverage

        Notes
        -----
        [3] K. Kimura and D. G. Stephenson, Solar radiation on cloudy days. Res.
            Paper 418, Division of Building Research, National Research Council,
            Ottawa (1969).
        [4] R. Brinsfield, M. Yaramanogly, F. Wheaton, Ground level solar
            radiation prediction model including cloud cover effects, Solar
            Energy, Volume 33, Issue 6, 1984, Pages 493-499

        """

        # irradiance on a horizontal surface
        solar_azimuth,solar_altitude = self.sunposition(utcdatetime=utcdatetime)
        I_tot, I_direct, I_diffuse, I_ground = self.incidentirradiance(I_direct_clearsky,I_diffuse_clearsky,solar_azimuth,solar_altitude,0,0)


        print(I_tot)
        print(I_direct)
        if I_tot > 0.1:

            if utcdatetime == None:
                utcdatetime = datetime.datetime.utcnow()

            # month of the year.
            n = float(utcdatetime.strftime('%m'))


            # Data from table 1 of [1]. Month of december and march are repeated for interpolation.
            P = np.interp(n, [-1., 3., 6., 9., 12., 15. ], [1.14, 1.06, 0.96, 0.95, 1.14, 1.06])
            Q = np.interp(n, [-1., 3., 6., 9., 12., 15. ], [0.003, 0.012, 0.033, 0.030, 0.003, 0.012])
            R = np.interp(n, [-1., 3., 6., 9., 12., 15. ], [-0.0082, -0.0084, -0.0106, -0.0108, -0.0082, -0.0084])

            # Cloud coverage and cloud coverage factor
            CC = cloudcover*10.
            CCF = P + Q*CC + R*CC**2

            # Correction for horizontal surface, according to [1]
            I_tot_cloudy = (I_tot - I_ground) * CCF                # equation 1, [1]: total radiation on horizontal surface, corrected with cloud coverage factor
                                                                   # Notice: CCF can be > 1 (higher radiation than average) and has a maximum at CC = 2-3 (see Fig.3, [1])
            I_direct_cloudy = I_direct_clearsky*(1-cloudcover)     # Direct radiation is proportional to cloud fraction (eq. 12, [1])
            I_diffuse_cloudy = I_tot_cloudy - I_direct_cloudy      # Diffuse radiation = total radiation - direct radiation (equivalent to eq. 13, [1])

        else:
            I_direct_cloudy = I_direct_clearsky
            I_diffuse_cloudy = I_diffuse_clearsky

        return I_direct_cloudy , I_diffuse



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
            # update the irradiance
            I_direct_clearsky,I_diffuse_clearsky = self.clearskyirrradiance()

            cloudcover = 0
            if not self._states['weather/cloudcover'].value is None:
                cloudcover = self._states['weather/cloudcover'].value

            I_direct_cloudy,I_diffuse_cloudy = self.cloudyskyirrradiance(I_direct_clearsky,I_diffuse_clearsky,self._states['weather/cloudcover'].value)

            self._states['weather/irradiancedirect'].value = round(I_direct_cloudy,2)
            self._states['weather/irradiancediffuse'].value = round(I_diffuse_cloudy,2)








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



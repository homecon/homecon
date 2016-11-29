#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import urllib.request
import json
import concurrent.futures

from .. import plugin

class Weather(plugin.Plugin):
    """
    Class to control the HomeCon weather functions
    
    """

    def initialize(self):

        # create a thread pool executor for loading api data
        self.executor = concurrent.futures.ThreadPoolExecutor(7)

        # add settings states
        self._states.add('settings/weather/service', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':''})
        self._states.add('settings/weather/apikey', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':''})
        self._states.add('weather/forecast/lastupdate', config={'type': 'number', 'quantity':'', 'unit':'','label':'', 'description':''})


        # add forecast states
        for i in range(7):
            self._states.add('weather/forecast/daily/{}'.format(i), config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})
        
        for i in range(24*7):
            self._states.add('weather/forecast/hourly/{}'.format(i), config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})


        # load the forecast
        self.forecast()

        logging.debug('Weather plugin Initialized')


    def load_url(self, url):
        """
        method for loading urls to be used in a thread pool executor

        """
        with urllib.request.urlopen(url, timeout=60) as conn:
            return conn.read()


    def forecast(self):
        """
        Loads a forecast from a webservice and schedules itself to run again an hour later

        """

        # schedule loading forecasts in an hour
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()

        dt_when = (dt_now + datetime.timedelta(hours=1)).replace(minute=1,second=0,microsecond=0)

        timestamp_now = int( (dt_now-dt_ref).total_seconds() )
        timestamp_when = int( (dt_when-dt_ref).total_seconds() )

        when = self._loop.time() + timestamp_when - timestamp_now

        self._loop.call_at(when,self.forecast)


        # check the last load time to avoid frequent loading upon restarts
        if self._states['weather/forecast/lastupdate'].value is None or self._states['weather/forecast/lastupdate'].value < timestamp_now-3599:

            # load the forecast
            if self._states['settings/weather/service'].value == 'darksky':
                self.darksky_forecast()

            self._states['weather/forecast/lastupdate'].value = timestamp_now

    def darksky_forecast(self):
        """
        Loads a forecast from darksky.net
        """

        # everything is wrapped in a try except statement as things to avoid errors throug api outages etc.
        try:
            # create a list of times to poll
            now = datetime.datetime.utcnow().replace( second=0, microsecond=0)
            timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

            timestamplist = [timestamp+i*24*3600 for i in range(7)]

            for i,timestamp in enumerate(timestamplist):
                url = 'https://api.darksky.net/forecast/{}/{},{},{}?units=si'.format(self._states['settings/weather/apikey'].value,self._states['settings/location/latitude'].value,self._states['settings/location/longitude'].value,timestamp)

                response = urllib.request.urlopen(url)
                response = json.loads(response.read().decode('utf-8'))

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

                # set the state
                self._states['weather/forecast/daily/{}'.format(i)].value = forecast


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

                    # set the states
                    self._states['weather/forecast/hourly/{}'.format(i*24+j)].value = forecast
            
            logging.debug('Weather forecast loaded from darksky.net')

        except Exception as e:
            logging.error('Could not load data from Darksky.net: {}'.format(e))

        



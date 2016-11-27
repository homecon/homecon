#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import urllib.request
import json

from .. import plugin

class Weather(plugin.Plugin):
    """
    Class to control the HomeCon weather functions
    
    """

    def initialize(self):

        # add settings states
        self._states.add('settings/weather/service', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':''})
        self._states.add('settings/weather/apikey', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':''})


        # add forecast states
        states = {
            'timestamp': 'number',
            'temperature': 'number',
            'pressure': 'number',
            'humidity': 'number',
            'icon': 'string',
            'clouds': 'number',
            'wind_speed': 'number',
            'wind_direction': 'number',
            'precipitation_intensity': 'number',
            'precipitation_probability': 'number',
        }

        for i in range(7):
            for state,statetype in states.items():
                self._states.add('weather/forecast/daily/{}/{}'.format(i,state), config={'type': statetype, 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})
        
        for i in range(24*7):
            for state,statetype in states.items():
                self._states.add('weather/forecast/hourly/{}/{}'.format(i,state), config={'type': statetype, 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})

        # load the forecast
        self.forecast()


    def forecast(self):
        """
        Loads a forecast from a webservice and schedules itself to run again an hour later

        """

        # schedule loading forecasts in an hour
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()

        dt_when = (dt_now + datetime.timedelta(hours=1)).replace(minute=1,second=0,microsecond=0)

        timestamp_now = (dt_now-dt_ref).total_seconds()
        timestamp_when = (dt_when-dt_ref).total_seconds()

        when = self._loop.time() + timestamp_when - timestamp_now

        self._loop.call_at(when,self.forecast)


        # load the forecast
        if self._states['settings/weather/service'].value == 'darksky':
            self.darksky_forecast()


    def darksky_forecast(self):
        """
        Loads a forecast from darksky.net
        """
        try:
            # create a list of times to poll
            now = datetime.datetime.utcnow().replace( second=0, microsecond=0)
            timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

            timestamplist = [timestamp+i*24*3600 for i in range(7)]
        
            hourlyweatherforecast = []
            dailyweatherforecast = []

            for timestamp in timestamplist:

                url = 'https://api.darksky.net/forecast/{}/{},{},{}?units=si'.format(self._states['settings/weather/apikey'].value,self._states['settings/location/latitude'].value,self._states['settings/location/longitude'].value,timestamp)

                response = urllib.request.urlopen(url)
                response = json.loads(response.read().decode('utf-8'))

                # hourly values
                for data in response['hourly']['data']:
                    currentforecast = {}
                    currentforecast['timestamp'] = data['time']
                    currentforecast['temperature'] = data['temperature']
                    currentforecast['pressure'] = data['pressure']
                    currentforecast['humidity'] = data['humidity']
                    currentforecast['icon'] = data['icon']
                    currentforecast['clouds'] = data['cloudCover']
                    currentforecast['wind_speed'] = data['windSpeed']
                    currentforecast['wind_direction'] = data['windBearing']
                    try:
                        currentforecast['precipitation_intensity'] = data['precipIntensity']
                        currentforecast['precipitation_probability'] = data['precipProbability']
                    except:
                        currentforecast['precipitation_intensity'] = 0
                        currentforecast['precipitation_probability'] = 0

                    hourlyweatherforecast.append(currentforecast)
            
                # daily values
                data = response['daily']['data'][0]
                currentforecast = {}
                currentforecast['timestamp'] = data['time']
                currentforecast['temperature_day'] = data['temperatureMax']
                currentforecast['temperature_night'] = data['temperatureMin']
                currentforecast['pressure'] = data['pressure']
                currentforecast['humidity'] = data['humidity']
                currentforecast['icon'] = data['icon']
                currentforecast['clouds'] = data['cloudCover']
                currentforecast['wind_speed'] = data['windSpeed']
                currentforecast['wind_directions'] = data['windBearing']
                try:
                    currentforecast['precipitation_intensity'] = data['precipIntensity']
                    currentforecast['precipitation_probability'] = data['precipProbability']
                except:
                    currentforecast['precipitation_intensity'] = 0
                    currentforecast['precipitation_probability'] = 0


                dailyweatherforecast.append(currentforecast)
        
            # set the states
            for i,forecast in enumerate(hourlyweatherforecast[:24*7]):
                for key,value in forecast.items():
                    self._states['weather/forecast/hourly/{}/{}'.format(i,key)].value = value

            for i,forecast in enumerate(dailyweatherforecast[:7]):
                for key,value in forecast.items():
                    self._states['weather/forecast/daily/{}/{}'.format(i,key)].value = value


            logging.info('Weather forecast loaded from darksky.net')
        except Exception as e:
            logging.error('Error loading weather forecast from darksky.net, {}'.format(e))



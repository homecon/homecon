#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import asyncio
import aiohttp
import json

from ... import core


class Darksky(core.plugin.Plugin):
    """
    Load forecasts from the darksky.net API

    """

    def initialize(self):

        core.states.add('darksky/settings/apikey', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':'', 'private':True})
        

        # schedule forecast loading
        self._loop.create_task(self.schedule_forecast())

        logging.debug('Darksky plugin Initialized')


    async def schedule_forecast(self):
        """
        Schedule forecast loading from a webservice and schedules itself to run again an hour later

        """

        while self.active:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = (dt_now + datetime.timedelta(hours=1)).replace(minute=1,second=0,microsecond=0)

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )

            # check the last load time to avoid frequent loading upon restarts
            if core.states['weather/forecast/lastupdate'].value is None or core.states['weather/forecast/lastupdate'].value < timestamp_now-600:

                # load the forecast
                self._loading = True
                success = await self.darksky_forecast()
                self._loading = False

                if success:
                    core.states['weather/forecast/lastupdate'].value = round(timestamp_now)

                    #core.states['weather/temperature'].value = round(self.ambienttemperature(),2)
                    #core.states['weather/cloudcover'].value = round(self.cloudcover(),3)
                    self.fire('forecast_updated',{})

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
                url = 'https://api.darksky.net/forecast/{}/{},{},{}?units=si'.format(self._states['darksky/settings/apikey'].value,self._states['settings/location/latitude'].value,self._states['settings/location/longitude'].value,timestamp)
                
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
                        await core.states['weather/forecast/daily/{}'.format(i)].set_async( forecast )


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
                            await core.states['weather/forecast/hourly/{}'.format(i*24+j)].set_async( forecast )

            logging.debug('Weather forecast loaded from darksky.net')

            return True

        except Exception as e:
            logging.error('Could not load data from Darksky.net: {}'.format(e))

            return False


    def listen_state_changed(self,event):
        if event.data['state'].path == 'darksky/settings/apikey':
            if not self._loading:
                #self._loop.create_task(self.darksky_forecast())
                task = asyncio.ensure_future(self.darksky_forecast())



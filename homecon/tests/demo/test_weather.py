#!/usr/bin/env python3
################################################################################
#    Copyright 2016 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
################################################################################


import asyncio
import numpy as np
import datetime

from .. import common

import homecon.core as core
import homecon.demo as demo

class WeatherTests(common.TestCase):

    def emulate_weater_extremes(self,month=1,cloudy=False):
        # add states
        core.states.add('settings/location/latitude',  value=51.0500)
        core.states.add('settings/location/longitude', value=5.5833)
        core.states.add('settings/location/elevation', value=74)
        core.states.add('settings/location/timezone',  value='Europe/Brussels')

        initialtimestamp = int( (datetime.datetime(2016,month,1)-datetime.datetime(1970,1,1)).total_seconds() )

        weatherdata = {
            'timestamp':[initialtimestamp],
            'cloudcover': [0.],
            'ambienttemperature': [15.],
        }
        if cloudy:
            weatherdata = demo.weather.emulate_weather(weatherdata,finaltimestamp=initialtimestamp+28*24*3600,mincloudcover=1)
        else:
            weatherdata = demo.weather.emulate_weather(weatherdata,finaltimestamp=initialtimestamp+28*24*3600,maxcloudcover=0)

        finaldayambienttemperature = weatherdata['ambienttemperature'][-int(24*3600/300):]

        #print([int(v*10)/10 for v in weatherdata['ambienttemperature'][::12]])
        #print([int(v*10)/10 for v in weatherdata['I_total_horizontal'][-int(24*3600/300)::12]])
        #print([int(v*10)/10 for v in weatherdata['ambienttemperature'][-int(24*3600/300)::12]])
        

        va = np.max(finaldayambienttemperature)
        vi = np.min(finaldayambienttemperature)
        ia = np.argmax(finaldayambienttemperature)
        ii = np.argmin(finaldayambienttemperature)
        
 
        print( 'mean: {:>5.1f} degC'.format(np.mean(finaldayambienttemperature) ) )
        print( 'min:  {:>5.1f} degC at time: {:>4.1f}h'.format(vi,ii*300/3600) )
        print( 'max:  {:>5.1f} degC at time: {:>4.1f}h'.format(va,ia*300/3600) )


    def test_emulate_weather_winter_clearsky(self):
        print('winter, clear sky:')
        self.emulate_weater_extremes(month=1,cloudy=False)
        print('')

    def test_emulate_weather_winter_cloudysky(self):
        print('winter, cloudy sky:')
        self.emulate_weater_extremes(month=1,cloudy=True)
        print('')

    def test_emulate_weather_spring_clearsky(self):
        print('spring, clear sky:')
        self.emulate_weater_extremes(month=4,cloudy=False)
        print('')

    def test_emulate_weather_spring_cloudysky(self):
        print('spring, cloudy sky:')
        self.emulate_weater_extremes(month=4,cloudy=True)
        print('')

    def test_emulate_weather_summer_clearsky(self):
        print('summer, clear sky:')
        self.emulate_weater_extremes(month=7,cloudy=False)
        print('')

    def test_emulate_weather_summer_cloudysky(self):
        print('summer, cloudy sky:')
        self.emulate_weater_extremes(month=7,cloudy=True)
        print('')

    def test_emulate_weather_fall_clearsky(self):
        print('fall, clear sky:')
        self.emulate_weater_extremes(month=10,cloudy=False)
        print('')

    def test_emulate_weather_fall_cloudysky(self):
        print('fall, cloudy sky:')
        self.emulate_weater_extremes(month=10,cloudy=True)
        print('')



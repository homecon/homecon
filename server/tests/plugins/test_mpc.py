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
import json
import importlib

from .. import common

import homecon.core as core
import homecon.demo as demo
import homecon.coreplugins.states
import homecon.coreplugins.weather
import homecon.coreplugins.building
import homecon.coreplugins.mpc



class MpcTests(common.TestCase):

    def test_mpc(self):
        # reload components
        importlib.reload(homecon.coreplugins.building.components.zone)
        importlib.reload(homecon.coreplugins.building.components.heating)

        # add components
        livingzone = core.components.add('livingzone', 'zone', config={})

        heatinggroup = core.components.add('heatinggroup', 'heatinggroup', config={})
        heatemissionsystem = core.components.add('heatemissionsystem', 'heatemissionsystem', config={'group':'heatinggroup'})
        heatgenerationsystem = core.components.add('heatgenerationsystem', 'heatgenerationsystem', config={'group':'heatinggroup'})
        

        states = homecon.coreplugins.states.States()

        # set location states
        core.states['settings/location/latitude'].set(51.0500,async=False)
        core.states['settings/location/longitude'].set(5.5833,async=False)
        core.states['settings/location/elevation'].set(74,async=False)
        core.states['settings/location/timezone'].set('Europe/Brussels',async=False)

        weather = homecon.coreplugins.weather.Weather()

        # add demo weather forecast
        dt_now = datetime.datetime.utcnow()
        dt_ref = datetime.datetime(1970,1,1)
        timestamp_now = int( (dt_now-dt_ref).total_seconds() )

        weatherdata = {'timestamp':[timestamp_now], 'cloudcover':[0], 'ambienttemperature':[5]}
        weatherdata = demo.weather.emulate_weather(weatherdata,finaltimestamp=timestamp_now+8*24*3600,maxcloudcover=0)
        demo.weatherdata = weatherdata

        demo.weatherforecast(async=False)

        building = homecon.coreplugins.building.Building()
        mpc = homecon.coreplugins.mpc.Mpc()

        
        mpc.optimization()


        #self.run_loop(seconds=2)

        print(heatgenerationsystem.Q_schedule)



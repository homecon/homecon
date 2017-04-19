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
import importlib

from .. import common

import homecon.core as core
import homecon.demo as demo
import homecon.coreplugins.building

class BuildingTests(common.TestCase):

    def test_emulate_building(self):
        importlib.reload(homecon.coreplugins.building.components.zone)
        importlib.reload(homecon.coreplugins.building.components.heating)
        importlib.reload(homecon.coreplugins.building.components.window)


        # add states
        core.states.add('settings/location/latitude',  value=51.0500)
        core.states.add('settings/location/longitude', value=5.5833)
        core.states.add('settings/location/elevation', value=74)
        core.states.add('settings/location/timezone',  value='Europe/Brussels')

        # add components
        core.components.add('dayzone'                    , 'zone'    ,{})
        core.components.add('heatinggroup1'              , 'heatinggroup'    ,{})
        core.components.add('floorheating_groundfloor'   , 'heatemissionsystem'       , {'type':'floorheating'    ,'zone':'dayzone', 'group':'heatinggroup1'})


        initialtimestamp = int( (datetime.datetime(2016,1,1)-datetime.datetime(1970,1,1)).total_seconds() )

        weatherdata = {
            'timestamp':[initialtimestamp],
            'cloudcover': [0.],
            'ambienttemperature': [15.],
        }
        weatherdata = demo.weather.emulate_weather(weatherdata,finaltimestamp=initialtimestamp+7*24*3600,maxcloudcover=0)


        buildingdata = {
            'timestamp':[initialtimestamp],
            'T_in': [21.],
            'T_em': [22.],
        }
        buildingdata = demo.building.emulate_building(buildingdata,weatherdata,finaltimestamp=initialtimestamp+7*24*3600,heatingcurve=True)

        print( 'T_amb (degC)  {}'.format([int(v*10)/10 for v in weatherdata['ambienttemperature'][-24*12::12]]) )
        print( 'T_in  (degC)  {}'.format([int(v*10)/10 for v in buildingdata['T_in'][-24*12::12]]) )
        print( 'T_em  (degC)  {}'.format([int(v*10)/10 for v in buildingdata['T_em'][-24*12::12]]) )
        print( 'Q_em    (kW)  {}'.format([int(v/100)/10 for v in buildingdata['Q_em'][-24*12::12]]) )





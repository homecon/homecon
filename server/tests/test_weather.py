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

import unittest
import time
import json
import sys
import os
import asyncio

from common import HomeConTestCase, Client

sys.path.append(os.path.abspath('..'))

from core.states import States
from core.components import Components
from core.plugins.weather import Weather


class WeatherTests(HomeConTestCase):
    
    def test_initialize(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        weather = Weather(queue,states,components)


    def test_darksky_forecast(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        weather = Weather(queue,states,components)
        
        states['settings/location/latitude'].value = 50.85
        states['settings/location/longitude'].value = 4.40
        states['settings/weather/apikey'].value = 'd6c9de5feab5ac6964521f05edf23757'

        weather.darksky_forecast()


if __name__ == '__main__':
    # run tests
    unittest.main()


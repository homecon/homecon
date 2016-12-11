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
import inspect
import copy
import datetime
import math

from common import HomeConTestCase, Client

sys.path.append(os.path.abspath('..'))

from core.states import States,State
from core.components import Components
from core.plugins.weather import Weather


class WeatherTests(HomeConTestCase):
    
    """
    def test_initialize(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = States(queue)
        components = Components(states)

        weather = Weather(queue,states,components)
    """

    def test_sunposition(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = DummyStates(queue)
        components = Components(states)


        states.add('settings/location/latitude')
        states['settings/location/latitude'].value = 51.053715
        states.add('settings/location/longitude')
        states['settings/location/longitude'].value = 5.6127946
        states.add('settings/location/elevation')
        states['settings/location/elevation'].value = 73

        weather = Weather(queue,states,components)

        dt_now = datetime.datetime.utcnow()
        utcdatetimes = [dt_now + datetime.timedelta(minutes=i) for i in range(60*24)]

        for utcdatetime in utcdatetimes:
            azi,alt = weather.sunposition(utcdatetime=utcdatetime)
            
            self.assertIsNotNaN(azi)
            self.assertIsNotNaN(alt)
            self.assertNotEqual(azi,None)
            self.assertNotEqual(alt,None)


    def test_clearskyirrradiance(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = DummyStates(queue)
        components = Components(states)


        states.add('settings/location/latitude')
        states['settings/location/latitude'].value = 51.053715
        states.add('settings/location/longitude')
        states['settings/location/longitude'].value = 5.6127946
        states.add('settings/location/elevation')
        states['settings/location/elevation'].value = 73

        weather = Weather(queue,states,components)

        dt_now = datetime.datetime.utcnow()
        utcdatetimes = [dt_now + datetime.timedelta(minutes=i) for i in range(60*24)]

        for utcdatetime in utcdatetimes:
            I_direct_normal,I_diffuse_horizontal = weather.clearskyirrradiance(utcdatetime=utcdatetime)
            
            self.assertIsNotNaN(I_direct_normal)
            self.assertIsNotNaN(I_diffuse_horizontal)


    def test_incidentirradiance(self):
        self.clear_database()
        queue = asyncio.Queue()
        states = DummyStates(queue)
        components = Components(states)


        states.add('settings/location/latitude')
        states['settings/location/latitude'].value = 51.053715
        states.add('settings/location/longitude')
        states['settings/location/longitude'].value = 5.6127946
        states.add('settings/location/elevation')
        states['settings/location/elevation'].value = 73

        weather = Weather(queue,states,components)

        dt_now = datetime.datetime.utcnow()
        utcdatetimes = [dt_now + datetime.timedelta(minutes=i) for i in range(60*24)]

        for utcdatetime in utcdatetimes:
            azi,alt = weather.sunposition(utcdatetime=utcdatetime)
            I_direct_normal,I_diffuse_horizontal = weather.clearskyirrradiance(utcdatetime=utcdatetime)
            I_tot, I_direct, I_diffuse, I_ground = weather.incidentirradiance(I_direct_normal,I_diffuse_horizontal,azi,alt,0,0)
            
            self.assertIsNotNaN(I_tot)
            self.assertIsNotNaN(I_direct)
            self.assertIsNotNaN(I_diffuse)
            self.assertIsNotNaN(I_ground)


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







class DummyStates(States):
    def add(self,path,config=None):
        """
        add a state

        """

        if not path in self._states:

            # check the config
            if config is None:
                config = {}

            if 'type' not in config:
                config['type'] = ''

            if 'quantity' not in config:
                config['quantity'] = ''

            if 'unit' not in config:
                config['unit'] = ''

            if 'label' not in config:
                config['label'] = ''

            if 'description' not in config:
                config['description'] = ''

            if 'readusers' not in config:
                config['readusers'] = []

            if 'writeusers' not in config:
                config['writeusers'] = []

            if 'readgroups' not in config:
                config['readgroups'] = [1]

            if 'writegroups' not in config:
                config['writegroups'] = [1]

            if 'log' not in config:
                config['log'] = True

            # check if the state is in the database and add it if not
            if len( self._db_states.GET(path=path) ) == 0:
                self._db_states.POST(path=path,config=json.dumps(config))

            # create the state
            state = DummyState(self,path,config=config)
            self._states[path] = state

            # update the value from the database
            try:
                state.get_value_from_db()
            except:
                pass

            return state
        else:
            return False


class DummyState(State):

    def set(self,value,source=None):
        oldvalue = copy.copy(self._value)

        if not value == oldvalue:
            self._value = value

            # update the value in the database
            self._states._db_states.PUT(value=json.dumps(value), where='path=\'{}\''.format(self._path))

            self._states.fire('state_changed',{'state':self,'value':self._value,'oldvalue':oldvalue},source)
    
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # get the source from inspection
        stack = inspect.stack()
        source = stack[1][0].f_locals["self"].__class__

        self.set(value,source=source)

if __name__ == '__main__':
    # run tests
    unittest.main()


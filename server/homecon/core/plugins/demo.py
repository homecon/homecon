#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import asyncio
import numpy as np

from .. import database
from .. import events
from ..plugin import Plugin
from ...util import weather

class Demo(Plugin):

    def initialize(self):

        ########################################################################
        # add components
        ########################################################################
        logging.debug('Adding demo components')
        
        self._components.add('living/light_dinnertable', 'light'       , {'type':'hallogen','power':35})
        self._components.add('living/light_tv'         , 'light'       , {'type':'led','power':10})
        self._components.add('living/light_couch'      , 'dimminglight', {'type':'led','power':15})
        self._components.add('kitchen/light'           , 'light'       , {'type':'led','power':5})
        self._components.add('bedroom/light'           , 'dimminglight', {'type':'led','power':20})


        self._components.add('living/window_west_1/screen'      ,'shading'       ,{})
        self._components.add('living/window_west_2/screen'      ,'shading'       ,{})
        self._components.add('kitchen/window_west/screen'       ,'shading'       ,{})
        self._components.add('kitchen/window_south/screen'      ,'shading'       ,{})

        self._components.add('bedroom/window_east/shutter'      ,'shading'       ,{})
        self._components.add('bedroom/window_north/shutter'     ,'shading'       ,{})




        ########################################################################
        # generate demo ambient conditions
        ########################################################################
        logging.debug('Adding demo measurements')
        latitude = 51.05
        longitude = 5.5833
        elevation = 74

        self.inputs = {}
        dt = 60
        time = np.arange(-14*24*3600,28*24*3600,dt,dtype=float)
        utcnow = datetime.datetime.utcnow()

        utcdatetime = np.array( [utcnow+datetime.timedelta(seconds=t) for t in time] )

        solar_azimuth = np.zeros_like(time)
        solar_altitude = np.zeros_like(time)
        I_direct_clearsky = np.zeros_like(time)
        I_diffuse_clearsky = np.zeros_like(time)
        I_direct_cloudy = np.zeros_like(time)
        I_diffuse_cloudy = np.zeros_like(time)
        cloudcover = np.zeros_like(time)
        ambienttemperature = np.zeros_like(time)
        I_total_horizontal = np.zeros_like(time)
        I_direct_horizontal = np.zeros_like(time)
        I_diffuse_horizontal = np.zeros_like(time)
        I_ground_horizontal = np.zeros_like(time)


        # create dummy weather data
        for i,t in enumerate(utcdatetime):

            solar_azimuth[i],solar_altitude[i] = weather.sunposition(latitude,longitude,elevation=elevation,utcdatetime=t)
            I_direct_clearsky[i],I_diffuse_clearsky[i] = weather.clearskyirrradiance(solar_azimuth[i],solar_altitude[i],utcdatetime=t)

            # random variation in cloud cover
            if i == 0:
                cloudcover[i] = 0
            else:
                cloudcover[i] = min(1.,max(0., cloudcover[i-1] + 0.0001*(2*np.random.random()-1)*dt ))

            I_direct_cloudy[i],I_diffuse_cloudy[i] = weather.cloudyskyirrradiance(I_direct_clearsky[i],I_diffuse_clearsky[i],cloudcover[i],solar_azimuth[i],solar_altitude[i],utcdatetime=t)
            
            I_total_horizontal[i], I_direct_horizontal[i], I_diffuse_horizontal[i], I_ground_horizontal[i] = weather.incidentirradiance(I_direct_cloudy[i],I_diffuse_cloudy[i],solar_azimuth[i],solar_altitude[i],0,0)

            # ambient temperature dependent on horizontal irradiance
            if i == 0:
                ambienttemperature[i] = 5
            else:
                ambienttemperature[i] = ambienttemperature[i-1] + 0.0000003*I_total_horizontal[i]*dt - 0.000001*(ambienttemperature[i-1]+10)*dt + 0.0002*(2*np.random.random()-1)*dt


        # store inputs locally
        self.data = {
            'time':time,
            'utcdatetime':utcdatetime,
            'solar_azimuth':solar_azimuth,
            'solar_altitude':solar_altitude,
            'I_direct_clearsky':I_direct_clearsky,
            'I_diffuse_clearsky':I_diffuse_clearsky,
            'I_direct_cloudy':I_direct_cloudy,
            'I_diffuse_cloudy':I_diffuse_cloudy,
            'cloudcover':cloudcover,
            'ambienttemperature':ambienttemperature,
            'I_total_horizontal':I_total_horizontal,
            'I_direct_horizontal':I_direct_horizontal,
            'I_diffuse_horizontal':I_diffuse_horizontal,
            'I_ground_horizontal':I_ground_horizontal,
        }



        # write data to homecon
        for 


        logging.debug('Demo plugin initialized')




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

    def __init__(self,homecon):
        self._homecon = homecon
        super(Demo,self).__init__()


    def initialize(self):

        ########################################################################
        # set settings
        ########################################################################
        self.latitude = 51.05
        self.longitude = 5.5833
        self.elevation = 74

        self._states['settings/location/latitude'].value = self.latitude
        self._states['settings/location/longitude'].value = self.longitude
        self._states['settings/location/elevation'].value = self.elevation
        self._states['settings/location/timezone'].value = 'Europe/Brussels'


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
        # add pages
        ########################################################################
        
        pages = self._homecon.coreplugins['pages']

        # delete all pages
        paths = [p for p in pages._widgets]
        for path in paths:
            pages.delete_widget(path)

        paths = [p for p in pages._sections]
        for path in paths:
            pages.delete_section(path)

        paths = [p for p in pages._pages]
        for path in paths:
            pages.delete_page(path)

        paths = [p for p in pages._groups]
        for path in paths:
            pages.delete_group(path)


        g = pages.add_group({'title':'Home'})
        p = pages.add_page(g['path'],{'title':'Home','icon':'blank'})

        g = pages.add_group({'title':'Central'})
        p = pages.add_page(g['path'],{'title':'Weather','icon':'weather_cloudy_light'})
        s = pages.add_section(p['path'],{'type':'transparent'})
        w = pages.add_widget(s['path'],'chart',config={'pathlist':['weather/temperature'],'title':'Temperature'})
        w = pages.add_widget(s['path'],'chart',config={'pathlist':['weather/sun/azimuth','weather/sun/altitude'],'title':'Sun'})
        w = pages.add_widget(s['path'],'chart',config={'pathlist':['weather/irradiancedirect','weather/irradiancediffuse'],'title':'Irradiance'})

        g = pages.add_group({'title':'Ground floor'})
        p = pages.add_page(g['path'],{'title':'Living','icon':'scene_livingroom'})
        s = pages.add_section(p['path'],{'type':'transparent'})
        w = pages.add_widget(s['path'],'switch',config={'path':'living/light_dinnertable','label':'Dinner table'})
        w = pages.add_widget(s['path'],'switch',config={'path':'living/light_tv','label':'TV'})


        ########################################################################
        # generate demo ambient conditions for the past 4 weeks
        ########################################################################
        logging.debug('Calculating demo weather conditions')
        self.timestep = 300


        utcnow = datetime.datetime.utcnow()
        startutcdatetime = (utcnow+datetime.timedelta(seconds=-14*24*3600-self.timestep)).replace(hour=0,minute=0,second=0,microsecond=0)
        weatherdata = self.emulate_weather({'utcdatetime':[startutcdatetime], 'cloudcover':[0], 'ambienttemperature':[5]},lookahead=int( (utcnow-startutcdatetime).total_seconds() ))


        ########################################################################
        # building simulation
        ########################################################################
        logging.debug('Calculating demo building simulation')


        buildingdata = {}

        ########################################################################
        # Add measurements to the database
        ########################################################################
        logging.debug('Adding demo measurements')

        # write data to homecon measurements database
        _db = database.Database(database=database.DB_MEASUREMENTS_NAME)

        connection,cursor = _db.create_cursor()

        for i,t in enumerate(weatherdata['timestamp']):
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/temperature\''      ,np.round(weatherdata['ambienttemperature'][i],2)))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/cloudcover\''       ,np.round(weatherdata['cloudcover'][i],2)        ))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/sun/azimuth\''      ,np.round(weatherdata['solar_azimuth'][i],2)     ))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/sun/altitude\''     ,np.round(weatherdata['solar_altitude'][i],2)    ))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/irradiancedirect\'' ,np.round(weatherdata['I_direct_cloudy'][i],2)   ))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/irradiancediffuse\'',np.round(weatherdata['I_diffuse_cloudy'][i],2)  ))


        connection.commit()

        logging.debug('Demo plugin initialized')



    def emulate_weather(self,initialdata,lookahead=3600):
        """

        Parameters
        ----------
        initialdata : dict
            
        lookahead : number
            number of seconds to look ahead from the final utcdatetime in initialdata

        """

        # generate new datetime vector
        time = np.arange(self.timestep,lookahead+self.timestep,self.timestep,dtype=float)
        utcdatetime = np.array( [initialdata['utcdatetime'][-1]+datetime.timedelta(seconds=t) for t in time] )


        timestamp = np.zeros(len(utcdatetime))
        solar_azimuth = np.zeros(len(utcdatetime))
        solar_altitude = np.zeros(len(utcdatetime))
        I_direct_clearsky = np.zeros(len(utcdatetime))
        I_diffuse_clearsky = np.zeros(len(utcdatetime))
        I_direct_cloudy = np.zeros(len(utcdatetime))
        I_diffuse_cloudy = np.zeros(len(utcdatetime))
        cloudcover = np.zeros(len(utcdatetime))
        ambienttemperature = np.zeros(len(utcdatetime))
        I_total_horizontal = np.zeros(len(utcdatetime))
        I_direct_horizontal = np.zeros(len(utcdatetime))
        I_diffuse_horizontal = np.zeros(len(utcdatetime))
        I_ground_horizontal = np.zeros(len(utcdatetime))

        for i,t in enumerate(utcdatetime):
            t_ref = datetime.datetime(1970, 1, 1)
            timestamp[i] = int( (t-t_ref).total_seconds() )

            solar_azimuth[i],solar_altitude[i] = weather.sunposition(self.latitude,self.longitude,elevation=self.elevation,utcdatetime=t)
            I_direct_clearsky[i],I_diffuse_clearsky[i] = weather.clearskyirrradiance(solar_azimuth[i],solar_altitude[i],utcdatetime=t)

            # random variation in cloud cover
            if i == 0:
                initial_cloudcover = initialdata['cloudcover'][-1]
            else:
                initial_cloudcover = cloudcover[i-1]
            cloudcover[i] = min(1.,max(0., initial_cloudcover + 0.0001*(2*np.random.random()-1)*self.timestep ))


            I_direct_cloudy[i],I_diffuse_cloudy[i] = weather.cloudyskyirrradiance(I_direct_clearsky[i],I_diffuse_clearsky[i],cloudcover[i],solar_azimuth[i],solar_altitude[i],utcdatetime=t)
            
            I_total_horizontal[i], I_direct_horizontal[i], I_diffuse_horizontal[i], I_ground_horizontal[i] = weather.incidentirradiance(I_direct_cloudy[i],I_diffuse_cloudy[i],solar_azimuth[i],solar_altitude[i],0,0)

            # ambient temperature dependent on horizontal irradiance
            if i == 0:
                initial_ambienttemperature = initialdata['ambienttemperature'][-1]
            else:
                initial_ambienttemperature = ambienttemperature[i-1]

            ambienttemperature[i] = initial_ambienttemperature + I_total_horizontal[i]*self.timestep/(30*24*3600) + (-10-initial_ambienttemperature)*self.timestep/(7*24*3600) + (2*np.random.random()-1)*self.timestep/(2*3600)


        utcdatetime_ref = datetime.datetime(1970, 1, 1)

        data = {
            'utcdatetime': utcdatetime,
            'timestamp': timestamp,
            'solar_azimuth': solar_azimuth,
            'solar_altitude': solar_altitude,
            'I_direct_clearsky': I_direct_clearsky,
            'I_diffuse_clearsky': I_diffuse_clearsky,
            'I_direct_cloudy': I_direct_cloudy,
            'I_diffuse_cloudy': I_diffuse_cloudy,
            'cloudcover': cloudcover,
            'ambienttemperature': ambienttemperature,
            'I_total_horizontal': I_total_horizontal,
            'I_direct_horizontal': I_direct_horizontal,
            'I_diffuse_horizontal': I_diffuse_horizontal,
            'I_ground_horizontal': I_ground_horizontal,
        }

        return data


    def emulate_building(self):
        pass



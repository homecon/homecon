#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import asyncio
import numpy as np

from .. import core
from .. import util


class Demo(core.plugin.Plugin):


    def initialize(self):

        ########################################################################
        # set settings
        ########################################################################
        self.latitude = 51.05
        self.longitude = 5.5833
        self.elevation = 74

        core.states['settings/location/latitude'].value = self.latitude
        core.states['settings/location/longitude'].value = self.longitude
        core.states['settings/location/elevation'].value = self.elevation
        core.states['settings/location/timezone'].value = 'Europe/Brussels'


        ########################################################################
        # add components
        ########################################################################
        logging.debug('Adding demo components')

        # outside sensors
        core.components.add('outside/temperature'      ,'ambienttemperaturesensor'    ,{'confidence':0.5})
        core.components.add('outside/irradiance'       ,'irradiancesensor'            ,{'confidence':0.8, 'azimuth':0.0, 'tilt':0.0})


        # dayzone
        core.components.add('dayzone'      ,'zone'    ,{})

        core.components.add('living/temperature_wall'      ,'zonetemperaturesensor'    ,{'zone':'dayzone','confidence':0.5})
        core.components.add('living/temperature_window'      ,'zonetemperaturesensor'    ,{'zone':'dayzone','confidence':0.8})

        core.components.add('living/window_west_1'    ,'window'       ,{'zone':'dayzone', 'area':7.2, 'azimuth':270})
        core.components.add('living/window_west_1'    ,'window'       ,{'zone':'dayzone', 'area':5.8, 'azimuth':270})
        core.components.add('kitchen/window_west'     ,'window'       ,{'zone':'dayzone', 'area':6.2, 'azimuth':270})
        core.components.add('kitchen/window_south'    ,'window'       ,{'zone':'dayzone', 'area':6.2, 'azimuth':180})

        core.components.add('living/window_west_1/screen'   ,'shading'       ,{'window':'living/window_west_1', 'closed_transmittance':0.4})
        core.components.add('living/window_west_2/screen'   ,'shading'       ,{'window':'living/window_west_2', 'closed_transmittance':0.4})
        core.components.add('kitchen/window_west/screen'    ,'shading'       ,{'window':'kitchen/window_west' , 'closed_transmittance':0.4})
        core.components.add('kitchen/window_south/screen'   ,'shading'       ,{'window':'kitchen/window_south', 'closed_transmittance':0.4})


        core.components.add('living/light_dinnertable', 'light'       , {'type':'hallogen','power':35   ,'zone':'dayzone'})
        core.components.add('living/light_tv'         , 'light'       , {'type':'led'     ,'power':10   ,'zone':'dayzone'})
        core.components.add('living/light_couch'      , 'dimminglight', {'type':'led'     ,'power':15   ,'zone':'dayzone'})
        core.components.add('kitchen/light'           , 'light'       , {'type':'led'     ,'power':5    ,'zone':'dayzone'})



        # nightzone
        core.components.add('nightzone'    ,'zone'    ,{})

        core.components.add('bedroom/temperature'      ,'zonetemperaturesensor'    ,{'zone':'nightzone','confidence':0.8})

        core.components.add('bedroom/window_east'       ,'window'       ,{'zone':'nightzone', 'area':1.2, 'azimuth':90})
        core.components.add('bedroom/window_north'      ,'window'       ,{'zone':'nightzone', 'area':0.8, 'azimuth':0})

        core.components.add('bedroom/window_east/shutter'      ,'shading'       ,{'window':'bedroom/window_east' , 'closed_transmittance':0.0})
        core.components.add('bedroom/window_north/shutter'     ,'shading'       ,{'window':'bedroom/window_north', 'closed_transmittance':0.0})

        core.components.add('bedroom/light'           , 'dimminglight', {'type':'led'     ,'power':20   ,'zone':'nightzone'})



        # bathroom
        core.components.add('bathroom'     ,'zone'    ,{})



        ########################################################################
        # add pages
        ########################################################################
        
        pages = core.plugins['pages']

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
        s = pages.add_section(p['path'],{'type':'raised'})
        w = pages.add_widget(s['path'],'chart',config={'pathlist':['weather/temperature'],'title':'Temperature'})
        w = pages.add_widget(s['path'],'chart',config={'pathlist':['weather/sun/azimuth','weather/sun/altitude'],'title':'Sun'})
        w = pages.add_widget(s['path'],'chart',config={'pathlist':['weather/irradiancedirect','weather/irradiancediffuse'],'title':'Irradiance'})

        p = pages.add_page(g['path'],{'title':'Shading','icon':'fts_sunblind'})
        s = pages.add_section(p['path'],{'type':'raised'})
        w = pages.add_widget(s['path'],'shading',config={'path':['living/window_west_1/screen'],'label':'Living west 1'})
        w = pages.add_widget(s['path'],'shading',config={'path':['living/window_west_2/screen'],'label':'Living west 2'})
        w = pages.add_widget(s['path'],'shading',config={'path':['kitchen/window_west/screen'],'label':'Kitchen west'})
        w = pages.add_widget(s['path'],'shading',config={'path':['kitchen/window_south/screen'],'label':'Kitchen south'})

        p = pages.add_page(g['path'],{'title':'Heating','icon':'sani_heating'})
        s = pages.add_section(p['path'],{'type':'raised'})
        w = pages.add_widget(s['path'],'chart',config={'pathlist':['living/temperature_wall/value','living/temperature_window/value'],'title':'Temperature'})



        g = pages.add_group({'title':'Ground floor'})
        p = pages.add_page(g['path'],{'title':'Living','icon':'scene_livingroom'})
        s = pages.add_section(p['path'],{'type':'raised'})
        w = pages.add_widget(s['path'],'switch',config={'path':'living/light_dinnertable','label':'Dinner table'})
        w = pages.add_widget(s['path'],'switch',config={'path':'living/light_tv','label':'TV'})


        ########################################################################
        # generate past demo data
        ########################################################################
        self.timestep = 300

        utcnow = datetime.datetime.utcnow()
        startutcdatetime = (utcnow+datetime.timedelta(seconds=-14*24*3600-self.timestep)).replace(hour=0,minute=0,second=0,microsecond=0)
        endutcdatetime = (utcnow+datetime.timedelta(seconds=10*24*3600-self.timestep)).replace(minute=0,second=0,microsecond=0)
        
        logging.debug('Calculating demo weather conditions')
        self.weatherdata = self.emulate_weather({'utcdatetime':[startutcdatetime], 'cloudcover':[0], 'ambienttemperature':[5]},lookahead=int( (endutcdatetime-startutcdatetime).total_seconds() ))


        logging.debug('Calculating demo building simulation')
        self.buildingdata = self.emulate_building({'utcdatetime':[startutcdatetime], 'T_in':[20.0]},lookahead=int( (utcnow-startutcdatetime).total_seconds() ),heatingcurve=True)


        ########################################################################
        # Add measurements to the database
        ########################################################################
        logging.debug('Adding demo measurements')

        # write data to homecon measurements database
        connection,cursor = core.measurements_db.create_cursor()

        utcnow = datetime.datetime.utcnow()
        utcref = datetime.datetime(1970,1,1)
        timestampnow = int( (utcnow-utcref).total_seconds() )
        for i,t in enumerate(self.weatherdata['timestamp']):
            if t<= timestampnow:
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/temperature\''      ,np.round(self.weatherdata['ambienttemperature'][i],2)))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/cloudcover\''       ,np.round(self.weatherdata['cloudcover'][i],2)        ))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/sun/azimuth\''      ,np.round(self.weatherdata['solar_azimuth'][i],2)     ))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/sun/altitude\''     ,np.round(self.weatherdata['solar_altitude'][i],2)    ))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/irradiancedirect\'' ,np.round(self.weatherdata['I_direct_cloudy'][i],2)   ))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/irradiancediffuse\'',np.round(self.weatherdata['I_diffuse_cloudy'][i],2)  ))
                
        for i,t in enumerate(self.buildingdata['timestamp']):
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.buildingdata['timestamp'][i],'\'living/temperature_wall/value\'',np.round(self.buildingdata['living/temperature_wall/value'][i],2)  ))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.buildingdata['timestamp'][i],'\'living/temperature_window/value\'',np.round(self.buildingdata['living/temperature_window/value'][i],2)  ))


        connection.commit()
        connection.close()


        ########################################################################
        # Schedule updates
        ########################################################################

        self._loop.create_task(self.schedule_emulate_weather())
        self._loop.create_task(self.schedule_sensor_updates())


        logging.debug('Demo plugin initialized')



    async def schedule_emulate_weather(self):

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = (dt_now + datetime.timedelta(hours=1)).replace(minute=5,second=0,microsecond=0)

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )

            # weather emulation
            newdata = self.emulate_weather(self.weatherdata,lookahead=3600)
            
            # append data and remove old data
            ind = np.where(self.weatherdata['timestamp'] >= timestamp_now-3600)

            for (key,val),(newkey,newval) in zip(self.weatherdata.items(),newdata.items()):
                self.weatherdata[key] = np.append(val[ind],newval)

            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)


    async def schedule_sensor_updates(self):

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = (dt_now + datetime.timedelta(minutes=1)).replace(second=0,microsecond=0)

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )

            # building emulation
            self.buildingdata = self.emulate_building(self.buildingdata ,lookahead=int( (self.buildingdata['utcdatetime'][-1]-dt_now).total_seconds() ),heatingcurve=True)

            # update states
            core.states['outside/temperature/value'].value = round(np.interp(timestamp_now,self.weatherdata['timestamp'],self.weatherdata['ambienttemperature']),2)
            core.states['outside/irradiance/value'].value = round(np.interp(timestamp_now,self.weatherdata['timestamp'],self.weatherdata['I_total_horizontal']),2)
            
            core.states['living/temperature_wall/value'].value = round(self.buildingdata['living/temperature_wall/value'][-1],2)
            core.states['living/temperature_window/value'].value = round(self.buildingdata['living/temperature_window/value'][-1],2)


            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)



    def emulate_weather(self,initialdata,lookahead=3600):
        """
        emulate weather conditions

        Parameters
        ----------
        initialdata : dict
            Dictionary with intial data.
            Must have a 'utcdatetime', 'cloudcover' and 'ambienttemperature' 
            keys with array like values

        lookahead : number
            Number of seconds to look ahead from the final utcdatetime in initialdata

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

            solar_azimuth[i],solar_altitude[i] = util.weather.sunposition(self.latitude,self.longitude,elevation=self.elevation,utcdatetime=t)
            I_direct_clearsky[i],I_diffuse_clearsky[i] = util.weather.clearskyirrradiance(solar_azimuth[i],solar_altitude[i],utcdatetime=t)

            # random variation in cloud cover
            if i == 0:
                initial_cloudcover = initialdata['cloudcover'][-1]
            else:
                initial_cloudcover = cloudcover[i-1]
            cloudcover[i] = min(1.,max(0., initial_cloudcover + 0.0001*(2*np.random.random()-1)*self.timestep ))


            I_direct_cloudy[i],I_diffuse_cloudy[i] = util.weather.cloudyskyirrradiance(I_direct_clearsky[i],I_diffuse_clearsky[i],cloudcover[i],solar_azimuth[i],solar_altitude[i],utcdatetime=t)
            
            I_total_horizontal[i], I_direct_horizontal[i], I_diffuse_horizontal[i], I_ground_horizontal[i] = util.weather.incidentirradiance(I_direct_cloudy[i],I_diffuse_cloudy[i],solar_azimuth[i],solar_altitude[i],0,0)

            # ambient temperature dependent on horizontal irradiance
            if i == 0:
                initial_ambienttemperature = initialdata['ambienttemperature'][-1]
            else:
                initial_ambienttemperature = ambienttemperature[i-1]

            ambienttemperature[i] = initial_ambienttemperature + I_total_horizontal[i]*self.timestep/(15*24*3600) + (-10-initial_ambienttemperature)*self.timestep/(5*24*3600) + (2*np.random.random()-1)*self.timestep/(2*3600)


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


    def emulate_building(self,initialdata,lookahead=300,heatingcurve=False):
        """
        emulate extremely simple building dynamics
        d(T_in)/dt = UA*(T_in-T_am) + Q_so + Q_in + Q_he 

        Parameters
        ----------
        initialdata : dict
            Dictionary with intial data.
            Must have a 'utcdatetime', 'T_in' keys with array like values

        lookahead : number
            Number of seconds to look ahead from the final utcdatetime in initialdata

        """

        # time
        time = np.arange(0,lookahead+self.timestep,self.timestep,dtype=float)
        utcdatetime = np.array( [initialdata['utcdatetime'][-1]+datetime.timedelta(seconds=t) for t in time] )
        
        t_ref = datetime.datetime(1970, 1, 1)
        timestamp = np.array( [int( (t-t_ref).total_seconds() ) for t in utcdatetime] )

        # parameters
        UA = 800
        C = 10e6
        T_set = 20
        K = 100


        # disturbances
        T_am = np.interp(timestamp,self.weatherdata['timestamp'],self.weatherdata['ambienttemperature'])
        Q_so = np.zeros_like(time)
        Q_in = np.zeros_like(time)
        Q_em = np.zeros_like(time)


        # initialization
        T_in = np.zeros_like(time)
        T_in[0] = initialdata['T_in'][-1]

        # solve discrete equation
        for i,t in enumerate(utcdatetime[:-1]):

            # emission heat flow
            if heatingcurve:
                Q_em[i] = (T_in[i]-T_am[i])*UA + (T_set-T_in[i])*K

            # solar gains
            Q = []
            for window in core.components.find(type='window'):
                Q.append( window.calculate_irradiation(utcdatetime=t) )

            Q_so[i] = 0

            # internal gains
            Q_in[i] = 0

            T_in[i+1] = T_in[i] + (T_am[i]-T_in[i])*self.timestep*UA/C + Q_so[i]*self.timestep/C + Q_in[i]*self.timestep/C + Q_em[i]*self.timestep/C


        # set the output data
        data = {
            'utcdatetime': utcdatetime[1:],
            'timestamp': timestamp[1:],
            'T_in': T_in[1:],
            'living/temperature_wall/value': T_in[1:] + 0.5,
            'living/temperature_window/value': T_in[1:] -0.2,
        }

        return data



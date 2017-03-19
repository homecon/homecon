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

        # systems
        core.components.add('heatpump'            , 'heatgenerationsystem'       , {'type':'heatpump'    ,'power':10000,})


        # outside sensors
        core.components.add('outside/temperature'      ,'ambienttemperaturesensor'    ,{'confidence':0.5})
        core.components.add('outside/irradiance'       ,'irradiancesensor'            ,{'confidence':0.8, 'azimuth':0.0, 'tilt':0.0})


        # dayzone
        core.components.add('dayzone'      ,'zone'    ,{})

        core.components.add('living/temperature_wall'        ,'zonetemperaturesensor'    ,{'zone':'dayzone','confidence':0.5})
        core.components.add('living/temperature_window'      ,'zonetemperaturesensor'    ,{'zone':'dayzone','confidence':0.8})

        core.components.add('living/window_west_1'    ,'window'       ,{'zone':'dayzone', 'area':7.2, 'azimuth':270})
        core.components.add('living/window_west_2'    ,'window'       ,{'zone':'dayzone', 'area':5.8, 'azimuth':270})
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
        

        core.components.add('floorheating_groundfloor'            , 'heatemissionsystem'       , {'type':'floorheating'    ,'zone':'dayzone', 'heatgenerationsystem':'heatpump'})



        # nightzone
        core.components.add('nightzone'    ,'zone'    ,{})

        core.components.add('bedroom/temperature'      ,'zonetemperaturesensor'    ,{'zone':'nightzone','confidence':0.8})

        core.components.add('bedroom/window_east'       ,'window'       ,{'zone':'nightzone', 'area':1.2, 'azimuth':90})
        core.components.add('bedroom/window_north'      ,'window'       ,{'zone':'nightzone', 'area':0.8, 'azimuth':0})

        core.components.add('bedroom/window_east/shutter'      ,'shading'       ,{'window':'bedroom/window_east' , 'closed_transmittance':0.0})
        core.components.add('bedroom/window_north/shutter'     ,'shading'       ,{'window':'bedroom/window_north', 'closed_transmittance':0.0})

        core.components.add('bedroom/light'           , 'dimminglight', {'type':'led'     ,'power':20   ,'zone':'nightzone'})



        # bathroom
        core.components.add('bathroomzone'     ,'zone'    ,{})



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

        dt_now = datetime.datetime.utcnow()
        dt_ref = datetime.datetime(1970,1,1)
        timestamp_now = int( (dt_now-dt_ref).total_seconds() )
        dt_start = (dt_now+datetime.timedelta(seconds=-14*24*3600-self.timestep)).replace(hour=0,minute=0,second=0,microsecond=0)

        logging.debug('Calculating demo weather data')
        self.weatherdata = self.emulate_weather({'utcdatetime':[dt_start], 'cloudcover':[0], 'ambienttemperature':[5]},lookahead=10*24*3600)


        # write data to homecon measurements database
        connection,cursor = core.measurements_db.create_cursor()
        for i,t in enumerate(self.weatherdata['timestamp']):
            if t<= timestamp_now:
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/temperature\''      ,np.round(self.weatherdata['ambienttemperature'][i],2)))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/cloudcover\''       ,np.round(self.weatherdata['cloudcover'][i],2)        ))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/sun/azimuth\''      ,np.round(self.weatherdata['solar_azimuth'][i],2)     ))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/sun/altitude\''     ,np.round(self.weatherdata['solar_altitude'][i],2)    ))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/irradiancedirect\'' ,np.round(self.weatherdata['I_direct_cloudy'][i],2)   ))
                cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.weatherdata['timestamp'][i],'\'weather/irradiancediffuse\'',np.round(self.weatherdata['I_diffuse_cloudy'][i],2)  ))
            else:
                break

        connection.commit()
        connection.close()

        # set the final values
        core.states['weather/temperature']._value = np.round(self.weatherdata['ambienttemperature'][i],2)
        core.states['weather/cloudcover']._value = np.round(self.weatherdata['cloudcover'][i],2)
        core.states['weather/sun/azimuth']._value = np.round(self.weatherdata['solar_azimuth'][i],2)
        core.states['weather/sun/altitude']._value = np.round(self.weatherdata['solar_altitude'][i],2)
        core.states['weather/irradiancedirect']._value = np.round(self.weatherdata['I_direct_cloudy'][i],2)
        core.states['weather/irradiancediffuse']._value = np.round(self.weatherdata['I_diffuse_cloudy'][i],2)



        logging.debug('Calculating demo building response')
        self.buildingdata = self.emulate_building({'utcdatetime':[dt_start], 'T_in':[20.0], 'T_em':[22.0]},heatingcurve=True)

        # write data to homecon measurements database
        connection,cursor = core.measurements_db.create_cursor()
        for i,t in enumerate(self.buildingdata['timestamp']):
            if t<= timestamp_now:
                for key,val in self.buildingdata.items():
                    if key in core.states:
                        cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(self.buildingdata['timestamp'][i],'\'{}\''.format(key),np.round(val[i],2)  ))

            else:
                break

        connection.commit()
        connection.close()

        # set the final values
        core.states['living/temperature_wall/value']._value = np.round(self.buildingdata['living/temperature_wall/value'][i],2)
        core.states['living/temperature_window/value']._value = np.round(self.buildingdata['living/temperature_window/value'][i],2)
        core.states['heatpump/power_setpoint']._value = np.round(self.buildingdata['Q_em'][i],1)
        core.states['heatpump/power']._value = np.round(self.buildingdata['Q_em'][i],1)
        core.states['floorheating_groundfloor/valve_position']._value = 1.0

#########

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
            logging.debug('Calculating demo weather data')
            newdata = self.emulate_weather(self.weatherdata,lookahead=10*24*3600)
            
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

            # update weather states
            core.states['outside/temperature/value'].value = round(np.interp(timestamp_now,self.weatherdata['timestamp'],self.weatherdata['ambienttemperature']),2)
            core.states['outside/irradiance/value'].value = round(np.interp(timestamp_now,self.weatherdata['timestamp'],self.weatherdata['I_total_horizontal']),2)
            

            # building emulation
            logging.debug('Calculating demo building response')
            self.buildingdata = self.emulate_building(self.buildingdata)


            # update building states
            core.states['living/temperature_wall/value'].value = round(self.buildingdata['living/temperature_wall/value'][-1],2)
            core.states['living/temperature_window/value'].value = round(self.buildingdata['living/temperature_window/value'][-1],2)

            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)






#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os
import datetime
import time
import threading
import numpy as np

from . import weather
from . import building

from .. import core
from .. import util


weatherdata = None
buildingdata = None


class DemoThread(threading.Thread):
    """
    A threading subclass used to run the threads required for demo mode
    
    """
    
    def __init__(self,callback,name='DemoThread',runevery=60):
        super().__init__()
        self.callback = callback
        self.name = name
        self.runevery = runevery

    def run(self):
        starttime = time.time()
        nextrun = starttime

        while True: # run forever
            self.callback()
    
            runtime = time.time()
            nextrun += self.runevery
            time.sleep(max(0,nextrun-runtime))


def prepare_database():
    """
    Add entries to the database as if HomeCon was already running for 2 weeks
    
    """
    global weatherdata
    global buildingdata

    logging.info('Starting Demo mode')

    ########################################################################
    # set settings
    ########################################################################
    latitude = 51.0500
    longitude = 5.5833
    elevation = 74


    core.states['settings/location/latitude'].set(latitude,async=False)
    core.states['settings/location/longitude'].set(longitude,async=False)
    core.states['settings/location/elevation'].set(elevation,async=False)
    core.states['settings/location/timezone'].set('Europe/Brussels',async=False)


    ########################################################################
    # add components
    ########################################################################
    logging.debug('Adding demo components')

    # outside sensors
    core.components.add('outside/temperature'      ,'ambienttemperaturesensor'    , config={'confidence':0.5})
    core.components.add('outside/irradiance'       ,'irradiancesensor'            , config={'confidence':0.8, 'azimuth':0.0, 'tilt':0.0})


    # dayzone
    core.components.add('dayzone'      ,'zone'    , config={})

    core.components.add('living/temperature_wall'        ,'zonetemperaturesensor'    , config={'zone':'dayzone','confidence':0.5})
    core.components.add('living/temperature_window'      ,'zonetemperaturesensor'    , config={'zone':'dayzone','confidence':0.8})

    core.components.add('living/window_west_1'    ,'window'       , config={'zone':'dayzone', 'area':7.2, 'azimuth':270})
    core.components.add('living/window_west_2'    ,'window'       , config={'zone':'dayzone', 'area':5.8, 'azimuth':270})
    core.components.add('kitchen/window_west'     ,'window'       , config={'zone':'dayzone', 'area':6.2, 'azimuth':270})
    core.components.add('kitchen/window_south'    ,'window'       , config={'zone':'dayzone', 'area':6.2, 'azimuth':180})

    core.components.add('living/window_west_1/screen'   ,'shading'       , config={'window':'living/window_west_1', 'transmittance_closed':0.4})
    core.components.add('living/window_west_2/screen'   ,'shading'       , config={'window':'living/window_west_2', 'transmittance_closed':0.4})
    core.components.add('kitchen/window_west/screen'    ,'shading'       , config={'window':'kitchen/window_west' , 'transmittance_closed':0.4})
    core.components.add('kitchen/window_south/screen'   ,'shading'       , config={'window':'kitchen/window_south', 'transmittance_closed':0.4})


    core.components.add('living/light_dinnertable', 'light'       , config={'type':'hallogen','power':35   ,'zone':'dayzone'})
    core.components.add('living/light_tv'         , 'light'       , config={'type':'led'     ,'power':10   ,'zone':'dayzone'})
    core.components.add('living/light_couch'      , 'dimminglight', config={'type':'led'     ,'power':15   ,'zone':'dayzone'})
    core.components.add('kitchen/light'           , 'light'       , config={'type':'led'     ,'power':5    ,'zone':'dayzone'})




    # nightzone
    core.components.add('nightzone'    ,'zone'    ,{})

    core.components.add('bedroom/temperature'      ,'zonetemperaturesensor'    , config={'zone':'nightzone','confidence':0.8})

    core.components.add('bedroom/window_east'       ,'window'       , config={'zone':'nightzone', 'area':1.2, 'azimuth':90})
    core.components.add('bedroom/window_north'      ,'window'       , config={'zone':'nightzone', 'area':0.8, 'azimuth':0})

    core.components.add('bedroom/window_east/shutter'      ,'shading'       , config={'window':'bedroom/window_east' , 'closed_transmittance':0.0})
    core.components.add('bedroom/window_north/shutter'     ,'shading'       , config={'window':'bedroom/window_north', 'closed_transmittance':0.0})

    core.components.add('bedroom/light'           , 'dimminglight', config={'type':'led'     ,'power':20   ,'zone':'nightzone'})



    # bathroom
    core.components.add('bathroomzone'     ,'zone'    ,{})


    # heatingsystem
    core.components.add('heatinggroup1'           , 'heatinggroup'        , config={})
    core.components.add('heatpump'                , 'heatgenerationsystem', config={'type':'heatpump'    , 'power':10000   , 'group':'heatinggroup1'})
    core.components.add('floorheating_groundfloor', 'heatemissionsystem'  , config={'type':'floorheating', 'zone':'dayzone', 'group':'heatinggroup1'})



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
    s = pages.add_section(p['path'],{'type':'hidden'})
    w = pages.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':0})
    w = pages.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':24})
    w = pages.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':48})
    w = pages.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':72})


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
    dt_now = datetime.datetime.utcnow()
    dt_ref = datetime.datetime(1970,1,1)
    timestamp_now = int( (dt_now-dt_ref).total_seconds() )
    timestamp_start = timestamp_now-14*24*3600


    logging.debug('Calculating past demo weather data')
    weatherdata = {'timestamp':[timestamp_start], 'cloudcover':[0], 'ambienttemperature':[5]}
    weatherdata = weather.emulate_weather(weatherdata,finaltimestamp=timestamp_now+10*24*3600)

    # write data to homecon measurements database
    connection,cursor = core.measurements_db.create_cursor()
    for i,t in enumerate(weatherdata['timestamp']):
        if t<= timestamp_now:
            
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/temperature\''      ,np.round(weatherdata['ambienttemperature'][i],2)))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/cloudcover\''       ,np.round(weatherdata['cloudcover'][i],2)        ))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/sun/azimuth\''      ,np.round(weatherdata['solar_azimuth'][i],2)     ))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/sun/altitude\''     ,np.round(weatherdata['solar_altitude'][i],2)    ))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/irradiancedirect\'' ,np.round(weatherdata['I_direct_cloudy'][i],2)   ))
            cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/irradiancediffuse\'',np.round(weatherdata['I_diffuse_cloudy'][i],2)  ))
        else:
            break

    connection.commit()
    connection.close()

    # set the final values
    core.states['weather/temperature']._value = np.round(weatherdata['ambienttemperature'][i],2)
    core.states['weather/cloudcover']._value = np.round(weatherdata['cloudcover'][i],2)
    core.states['weather/sun/azimuth']._value = np.round(weatherdata['solar_azimuth'][i],2)
    core.states['weather/sun/altitude']._value = np.round(weatherdata['solar_altitude'][i],2)
    core.states['weather/irradiancedirect']._value = np.round(weatherdata['I_direct_cloudy'][i],2)
    core.states['weather/irradiancediffuse']._value = np.round(weatherdata['I_diffuse_cloudy'][i],2)



    logging.debug('Calculating past demo building response')
    buildingdata = building.emulate_building({'timestamp':[timestamp_start], 'T_in':[20.0], 'T_em':[22.0]},weatherdata,finaltimestamp=timestamp_now,heatingcurve=True)


    # write data to homecon measurements database
    connection,cursor = core.measurements_db.create_cursor()
    for i,t in enumerate(buildingdata['timestamp']):
        if t<= timestamp_now:
            for key,val in buildingdata.items():
                if key in core.states:
                    cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(buildingdata['timestamp'][i],'\'{}\''.format(key),np.round(val[i],2)  ))


    connection.commit()
    connection.close()

    # set the final values
    core.states['living/temperature_wall/value']._value = np.round(buildingdata['living/temperature_wall/value'][i],2)
    core.states['living/temperature_window/value']._value = np.round(buildingdata['living/temperature_window/value'][i],2)
    core.states['heatpump/power_setpoint']._value = np.round(buildingdata['Q_em'][i],1)
    core.states['heatpump/power']._value = np.round(buildingdata['Q_em'][i],1)
    core.states['floorheating_groundfloor/valve_position']._value = 1.0

    

def emulate():
    """
    Set the system states
    
    """
    
    global weatherdata
    global buildingdata

    dt_ref = datetime.datetime(1970, 1, 1)
    dt_now = datetime.datetime.utcnow()

    timestamp_now = int( (dt_now-dt_ref).total_seconds() )

    
    if weatherdata['timestamp'][-1] < timestamp_now+7*24*3600:
        # weather emulation
        logging.debug('Calculating demo weather data')
        newdata = weather.emulate_weather(weatherdata,lookahead=10*24*3600)
        
        # append data and remove old data
        ind = np.where(weatherdata['timestamp'] >= timestamp_now-3600)

        for (key,val),(newkey,newval) in zip(weatherdata.items(),newdata.items()):
            weatherdata[key] = np.append(val[ind],newval)

    
    # update weather states
    core.states['outside/temperature/value'].value = round(np.interp(timestamp_now,weatherdata['timestamp'],weatherdata['ambienttemperature']),2)
    core.states['outside/irradiance/value'].value = round(np.interp(timestamp_now,weatherdata['timestamp'],weatherdata['I_total_horizontal']),2)

    # building emulation
    logging.debug('Calculating demo building response')
    buildingdata = building.emulate_building(buildingdata,weatherdata)


    # update building states
    core.states['living/temperature_wall/value'].value = round(buildingdata['living/temperature_wall/value'][-1],2)
    core.states['living/temperature_window/value'].value = round(buildingdata['living/temperature_window/value'][-1],2)




def weatherforecast():
    """
    Set the weather forecast states
    
    """
    
    global weatherdata

    # update weather forecast states
    now = datetime.datetime.utcnow().replace( hour=0, minute=0, second=0, microsecond=0)
    timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

    logging.debug('Setting demo weather forecast data')
    
    timestamplist = [timestamp+i*24*3600 for i in range(7)]
    for i,t in enumerate(timestamplist):
        forecast = {
            'timestamp': t,
            'temperature_day': np.interp(t+14*3600,weatherdata['timestamp'],weatherdata['ambienttemperature']),
            'temperature_night': np.interp(t+6*3600,weatherdata['timestamp'],weatherdata['ambienttemperature']),
            'pressure': 101325,
            'humidity': 0.6,
            'icon': '02d' if np.interp(t+14*3600,weatherdata['timestamp'],weatherdata['cloudcover']) < 0.5 else '09d',
            'cloudcover': np.interp(t+14*3600,weatherdata['timestamp'],weatherdata['cloudcover']),
            'wind_speed': 0,
            'wind_direction': 0,
            'precipitation_intensity': 0,
            'precipitation_probability': 0,
        }
        core.states['weather/forecast/daily/{}'.format(i)].value = forecast



    timestamplist = [timestamp+i*3600 for i in range(7*24)]
    for i,t in enumerate(timestamplist):

        forecast = {
            'timestamp': t,
            'temperature': np.interp(t,weatherdata['timestamp'],weatherdata['ambienttemperature']),
            'pressure': 101325,
            'humidity': 0.6,
            'icon': '02d' if np.interp(t,weatherdata['timestamp'],weatherdata['cloudcover']) < 0.5 else '09d',
            'cloudcover': np.interp(t,weatherdata['timestamp'],weatherdata['cloudcover']),
            'wind_speed': 0,
            'wind_direction': 0,
            'precipitation_intensity': 0,
            'precipitation_probability': 0,
        }
        core.states['weather/forecast/hourly/{}'.format(i)].value = forecast



emulatorthread = DemoThread(emulate,name='EmulatorThread')
forecastthread = DemoThread(weatherforecast,name='ForecastThread',runevery=3600)






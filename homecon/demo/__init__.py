#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import json
from shutil import rmtree
# import sys

# import datetime
# import time
# from threading import Thread
# import numpy as np

from uuid import uuid4

# from . import weather
# from . import building
#
#
# weatherdata = None
# buildingdata = None


from homecon.core.database import database_path, set_database_uri, set_measurements_database_uri
from homecon.core.state import State
from homecon.plugins.pages import deserialize, Section


logger = logging.getLogger(__name__)


def initialize():
    logger.info('initializing demo mode')
    set_databases()
    create_states()
    create_pages()


def set_databases():
    logger.info('creating the demo database')

    # clear the demo database
    try:
        rmtree(os.path.join(database_path, 'demo'))
    except:
        pass

    # initialize the database
    os.makedirs(os.path.join(database_path, 'demo'))
    set_database_uri('sqlite://{}'.format(os.path.join(database_path, 'demo', 'homecon.db')))
    set_measurements_database_uri('sqlite://{}'.format(os.path.join(database_path, 'demo', 'homecon_measurements.db')))


def create_states():
    logger.info('creating demo states')
    State.add('ground_floor')
    State.add('kitchen', parent='/ground_floor')
    State.add('some_value', parent='/ground_floor/kitchen', type='int', value=20)
    State.add('lights', parent='/ground_floor/kitchen')
    State.add('light', parent='/ground_floor/kitchen/lights',
              type='boolean', quantity='', unit='',
              label='Kitchen light', description='',
              config={'knx_ga_read': '1/1/31', 'knx_ga_write': '1/1/31', 'knx_dpt': '1'})
    State.add('spotlight', parent='/ground_floor/kitchen/lights',
              type='boolean', quantity='', unit='',
              label='Kitchen spotlights', description='',
              config={'knx_ga_read': '1/1/62', 'knx_ga_write': '1/1/62', 'knx_dpt': '1'})

    State.add('living', parent='/ground_floor')
    State.add('lights', parent='/ground_floor/living')
    State.add('light', parent='/ground_floor/living/lights',
              type='boolean', quantity='', unit='',
              label='Living room light', description='',
              config={'knx_ga_read': '1/1/41', 'knx_ga_write': '1/1/41', 'knx_dpt': '1'})

    State.add('windows', parent='/ground_floor/kitchen')
    State.add('south', parent='/ground_floor/kitchen/windows')
    State.add('shading', parent='/ground_floor/kitchen/windows/south')
    State.add('position', parent='/ground_floor/kitchen/windows/south/shading',
              type='float', quantity='', unit='',
              label='Position', description='',
              config={'knx_ga_read': '2/4/61', 'knx_ga_write': '2/3/61', 'knx_dpt': '5'})
    State.add('west', parent='/ground_floor/kitchen/windows')
    State.add('shading', parent='/ground_floor/kitchen/windows/west')
    State.add('position', parent='/ground_floor/kitchen/windows/west/shading',
              type='float', quantity='', unit='',
              label='Position', description='',
              config={'knx_ga_read': '2/4/62', 'knx_ga_write': '2/3/62', 'knx_dpt': '5'})

    State.add('myalarms')
    State.add('dummy', parent='/myalarms', type='action', value=[
        {'state': State.get('/ground_floor/kitchen/some_value').id, 'value': 10},
        {'state': State.get('/ground_floor/kitchen/some_value').id, 'value': 0, 'delay': 5}
    ], label='Dummy')
    State.add('1', parent='/myalarms', type='schedule',
              value={'trigger': {'day_of_week': '0,1,2,3,6', 'hour': '20', 'minute': '0'},
                     'action': State.get('/myalarms/dummy').id})


def create_pages():
    logger.info('creating demo pages')
    base_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_path, 'pages.json'), 'r') as f:
        pages = json.load(f)
    deserialize(pages)


# def prepare_database():
#     """
#     Add entries to the database as if HomeCon was already running for 2 weeks
#
#     """
#     global weatherdata
#     global buildingdata
#
#     logging.info('Starting Demo mode')
#
#     ########################################################################
#     # set settings
#     ########################################################################
#     latitude = 51.0500
#     longitude = 5.5833
#     elevation = 74
#
#
#     core.states['settings/location/latitude'].set(latitude,async=False)
#     core.states['settings/location/longitude'].set(longitude,async=False)
#     core.states['settings/location/elevation'].set(elevation,async=False)
#     core.states['settings/location/timezone'].set('Europe/Brussels',async=False)
#
#
#
#     ########################################################################
#     # add components
#     ########################################################################
#     logging.debug('Adding demo components')
#
#     # outside sensors
#     core.components.add('outside/temperature'      ,'ambienttemperaturesensor'    , config={'confidence':0.5})
#     core.components.add('outside/irradiance'       ,'irradiancesensor'            , config={'confidence':0.8, 'azimuth':0.0, 'tilt':0.0})
#
#
#     # dayzone
#     core.components.add('dayzone'      ,'zone'    , config={})
#
#     core.components.add('living/temperature_wall'        ,'zonetemperaturesensor'    , config={'zone':'dayzone','confidence':0.5})
#     core.components.add('living/temperature_window'      ,'zonetemperaturesensor'    , config={'zone':'dayzone','confidence':0.8})
#
#     core.components.add('living/window_west_1'    ,'window'       , config={'zone':'dayzone', 'area':5.8, 'azimuth':270})
#     core.components.add('living/window_west_2'    ,'window'       , config={'zone':'dayzone', 'area':4.2, 'azimuth':270})
#     core.components.add('kitchen/window_west'     ,'window'       , config={'zone':'dayzone', 'area':3.8, 'azimuth':270})
#     core.components.add('kitchen/window_south'    ,'window'       , config={'zone':'dayzone', 'area':4.4, 'azimuth':180})
#
#     core.components.add('living/window_west_1/screen'   ,'shading'       , config={'window':'living/window_west_1', 'transmittance_closed':0.2})
#     core.components.add('living/window_west_2/screen'   ,'shading'       , config={'window':'living/window_west_2', 'transmittance_closed':0.2})
#     core.components.add('kitchen/window_west/screen'    ,'shading'       , config={'window':'kitchen/window_west' , 'transmittance_closed':0.2})
#     core.components.add('kitchen/window_south/screen'   ,'shading'       , config={'window':'kitchen/window_south', 'transmittance_closed':0.2})
#
#
#     core.components.add('living/light_dinnertable', 'light'       , config={'type':'hallogen','power':35   ,'zone':'dayzone'})
#     core.components.add('living/light_tv'         , 'light'       , config={'type':'led'     ,'power':10   ,'zone':'dayzone'})
#     core.components.add('living/light_couch'      , 'dimminglight', config={'type':'led'     ,'power':15   ,'zone':'dayzone'})
#     core.components.add('kitchen/light'           , 'light'       , config={'type':'led'     ,'power':5    ,'zone':'dayzone'})
#
#
#     # nightzone
#     core.components.add('nightzone'    ,'zone'    ,{})
#
#     core.components.add('bedroom/temperature'      ,'zonetemperaturesensor'    , config={'zone':'nightzone','confidence':0.8})
#
#     core.components.add('bedroom/window_east'       ,'window'       , config={'zone':'nightzone', 'area':1.1, 'azimuth':90})
#     core.components.add('bedroom/window_north'      ,'window'       , config={'zone':'nightzone', 'area':0.8, 'azimuth':0})
#
#     core.components.add('bedroom/window_east/shutter'      ,'shading'       , config={'window':'bedroom/window_east' , 'transmittance_closed':0.0})
#     core.components.add('bedroom/window_north/shutter'     ,'shading'       , config={'window':'bedroom/window_north', 'transmittance_closed':0.0})
#
#     core.components.add('bedroom/light'           , 'dimminglight', config={'type':'led'     ,'power':20   ,'zone':'nightzone'})
#
#
#     # bathroom
#     core.components.add('bathroomzone'     ,'zone'    ,{})
#     core.components.add('bathroom/temperature'      ,'zonetemperaturesensor'    , config={'zone':'bathroomzone','confidence':0.8})
#
#     core.components.add('bathroom/light'           , 'light', config={'type':'led'     ,'power':50   ,'zone':'bathroomzone'})
#
#
#     # heatingsystem
#     core.components.add('heatinggroup1'           , 'heatinggroup'        , config={'heatingcurve':False,'controlzone':'dayzone'})
#     core.components.add('heatpump'                , 'heatpump'            , config={'type':'heatpump'    , 'power':10000   , 'group':'heatinggroup1', 'heatingcurve':False})
#     core.components.add('floorheating_groundfloor', 'heatemissionsystem'  , config={'type':'floorheating', 'zone':'dayzone', 'group':'heatinggroup1'})
#
#
#
#     ########################################################################
#     # Add actions
#     ########################################################################
#     actions.Action('Close shutters',config={},value=[{'event':'state', 'data':'{"path":"bedroom/window_east/shutter/position_min","value":1}','delay':0},{'event':'state', 'data':'{"path":"bedroom/window_north/shutter/position_min","value":1}','delay':0}])
#     actions.Action('Open shutters',config={},value=[{'event':'state', 'data':'{"path":"bedroom/window_east/shutter/position_min","value":0}','delay':0},{'event':'state', 'data':'{"path":"bedroom/window_north/shutter/position_min","value":0}','delay':0}])
#
#
#     ########################################################################
#     # Add schedules
#     ########################################################################
#     schedules.Schedule('_schedule1',config={'filter':'shading'},value={'hour':20,'minute':0,'mon':True,'tue':True,'wed':True,'thu':True,'fri':True,'sat':True,'sun':True,'action':'Close shutters'})
#     schedules.Schedule('_schedule2',config={'filter':'shading'},value={'hour':9,'minute':0,'mon':True,'tue':True,'wed':True,'thu':True,'fri':True,'sat':False,'sun':False,'action':'Open shutters'})
#     schedules.Schedule('_schedule3',config={'filter':'shading'},value={'hour':10,'minute':0,'mon':False,'tue':False,'wed':False,'thu':False,'fri':False,'sat':True,'sun':True,'action':'Open shutters'})
#
#
#     ########################################################################
#     # Set some initial states
#     ########################################################################
#     core.states['living/window_west_1/screen/auto'].value= True
#     core.states['living/window_west_2/screen/auto'].value= True
#     core.states['kitchen/window_west/screen/auto'].value= True
#     core.states['kitchen/window_south/screen/auto'].value= True
#     core.states['bedroom/window_east/shutter/auto'].value= True
#     core.states['bedroom/window_north/shutter/auto'].value= True
#
#
#
#
#     ########################################################################
#     # add pages
#     ########################################################################
#
#     pages = core.plugins['pages']
#
#     # delete all pages
#     paths = [p for p in pages._widgets]
#     for path in paths:
#         pages.delete_widget(path)
#
#     paths = [p for p in pages._sections]
#     for path in paths:
#         pages.delete_section(path)
#
#     paths = [p for p in pages._pages]
#     for path in paths:
#         pages.delete_page(path)
#
#     paths = [p for p in pages._groups]
#     for path in paths:
#         pages.delete_group(path)
#
#
#     g = pages.add_group({'title':'Home'})
#     p = pages.add_page(g['path'],{'title':'Home','icon':'blank'})
#
#     s = pages.add_section(p['path'],{'type':'underlined'})
#     w = pages.add_widget(s['path'],'clock',config={})
#     w = pages.add_widget(s['path'],'date',config={})
#
#     s = pages.add_section(p['path'],{'type':'underlined'})
#     w = pages.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':0})
#     w = pages.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':24})
#     w = pages.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':48})
#     w = pages.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':72})
#
#
#     g = pages.add_group({'title':'Central'})
#     p = pages.add_page(g['path'],{'title':'Weather','icon':'weather_cloudy_light'})
#     s = pages.add_section(p['path'],{'type':'raised'})
#     w = pages.add_widget(s['path'],'chart',config={'pathlist':['weather/temperature'],'title':'Temperature'})
#     w = pages.add_widget(s['path'],'chart',config={'pathlist':['weather/sun/azimuth','weather/sun/altitude'],'title':'Sun'})
#     w = pages.add_widget(s['path'],'chart',config={'pathlist':['weather/irradiancedirect','weather/irradiancediffuse'],'title':'Irradiance'})
#
#     p = pages.add_page(g['path'],{'title':'Shading','icon':'fts_sunblind'})
#     s = pages.add_section(p['path'],{'type':'raised'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['living/window_west_1/screen'],'label':'Living west 1'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['living/window_west_2/screen'],'label':'Living west 2'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['kitchen/window_west/screen'],'label':'Kitchen west'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['kitchen/window_south/screen'],'label':'Kitchen south'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['bedroom/window_east/shutter'],'label':'Bedroom east'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['bedroom/window_north/shutter'],'label':'Bedroom north'})
#
#     s = pages.add_section(p['path'],{'type':'raised'})
#     w = pages.add_widget(s['path'],'alarm',config={'label':'', 'filter':'shading'})
#
#     p = pages.add_page(g['path'],{'title':'Heating','icon':'sani_heating'})
#     s = pages.add_section(p['path'],{'type':'raised'})
#     w = pages.add_widget(s['path'],'chart',config={'pathlist':['living/temperature_wall/value','living/temperature_window/value'],'title':'Temperature'})
#
#
#     g = pages.add_group({'title':'Ground floor'})
#     p = pages.add_page(g['path'],{'title':'Living','icon':'scene_livingroom'})
#     s = pages.add_section(p['path'],{'type':'raised'})
#     w = pages.add_widget(s['path'],'switch',config={'path':'living/light_dinnertable','label':'Dinner table'})
#     w = pages.add_widget(s['path'],'switch',config={'path':'living/light_tv','label':'TV'})
#     s = pages.add_section(p['path'],{'type':'raised'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['living/window_west_1/screen'],'label':'Living west 1'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['living/window_west_2/screen'],'label':'Living west 2'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['kitchen/window_west/screen'],'label':'Kitchen west'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['kitchen/window_south/screen'],'label':'Kitchen south'})
#
#
#     g = pages.add_group({'title':'First floor'})
#     p = pages.add_page(g['path'],{'title':'Bedroom','icon':'scene_sleeping'})
#     s = pages.add_section(p['path'],{'type':'raised'})
#     w = pages.add_widget(s['path'],'dimmer',config={'path':'bedroom/light','label':'Light'})
#     s = pages.add_section(p['path'],{'type':'raised'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['bedroom/window_east/shutter'],'label':'Bedroom east'})
#     w = pages.add_widget(s['path'],'shading',config={'path':['bedroom/window_north/shutter'],'label':'Bedroom north'})
#
#     p = pages.add_page(g['path'],{'title':'Bathroom','icon':'scene_bath'})
#     s = pages.add_section(p['path'],{'type':'raised'})
#     w = pages.add_widget(s['path'],'switch',config={'path':'bathroom/light','label':'Light'})
#
#
#
#     ########################################################################
#     # generate past demo data
#     ########################################################################
#     dt_now = datetime.datetime.utcnow()
#     dt_ref = datetime.datetime(1970,1,1)
#     timestamp_now = int( (dt_now-dt_ref).total_seconds() )
#     timestamp_start = timestamp_now-14*24*3600
#
#
#     logging.debug('Calculating past demo weather data')
#     weatherdata = {'timestamp':[timestamp_start], 'cloudcover':[0], 'ambienttemperature':[5]}
#     weatherdata = weather.emulate_weather(weatherdata,finaltimestamp=timestamp_now+10*24*3600)
#
#     # write data to homecon measurements database
#     connection,cursor = core.measurements_db.create_cursor()
#     for i,t in enumerate(weatherdata['timestamp']):
#         if t<= timestamp_now:
#
#             cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/temperature\''      ,np.round(weatherdata['ambienttemperature'][i],2)))
#             cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/cloudcover\''       ,np.round(weatherdata['cloudcover'][i],2)        ))
#             cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/sun/azimuth\''      ,np.round(weatherdata['solar_azimuth'][i],2)     ))
#             cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/sun/altitude\''     ,np.round(weatherdata['solar_altitude'][i],2)    ))
#             cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/irradiancedirect\'' ,np.round(weatherdata['I_direct_cloudy'][i],2)   ))
#             cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(weatherdata['timestamp'][i],'\'weather/irradiancediffuse\'',np.round(weatherdata['I_diffuse_cloudy'][i],2)  ))
#         else:
#             break
#
#     connection.commit()
#     connection.close()
#
#     # set the final values
#     core.states['weather/temperature']._value = np.round(weatherdata['ambienttemperature'][i],2)
#     core.states['weather/cloudcover']._value = np.round(weatherdata['cloudcover'][i],2)
#     core.states['weather/sun/azimuth']._value = np.round(weatherdata['solar_azimuth'][i],2)
#     core.states['weather/sun/altitude']._value = np.round(weatherdata['solar_altitude'][i],2)
#     core.states['weather/irradiancedirect']._value = np.round(weatherdata['I_direct_cloudy'][i],2)
#     core.states['weather/irradiancediffuse']._value = np.round(weatherdata['I_diffuse_cloudy'][i],2)
#
#
#
#     logging.debug('Calculating past demo building response')
#     buildingdata = building.emulate_building({'timestamp':[timestamp_start], 'T_in':[20.0], 'T_em':[22.0]},weatherdata,finaltimestamp=timestamp_now,heatingcurve=True)
#
#
#     # write data to homecon measurements database
#     connection,cursor = core.measurements_db.create_cursor()
#     for i,t in enumerate(buildingdata['timestamp']):
#         if t<= timestamp_now:
#             for key,val in buildingdata.items():
#                 if key in core.states:
#                     cursor.execute('INSERT INTO measurements (`time`,`path`,`value`) VALUES ({},{},{})'.format(buildingdata['timestamp'][i],'\'{}\''.format(key),np.round(val[i],2)  ))
#
#
#     connection.commit()
#     connection.close()
#
#     # set the final values
#     core.states['living/temperature_wall/value']._value = np.round(buildingdata['living/temperature_wall/value'][i],2)
#     core.states['living/temperature_window/value']._value = np.round(buildingdata['living/temperature_window/value'][i],2)
#     core.states['bedroom/temperature/value']._value = np.round(buildingdata['bedroom/temperature/value'][i],2)
#     core.states['bathroom/temperature/value']._value = np.round(buildingdata['bathroom/temperature/value'][i],2)
#     core.states['heatpump/power_setpoint']._value = np.round(buildingdata['Q_em'][i],1)
#     core.states['heatpump/power']._value = np.round(buildingdata['Q_em'][i],1)
#     core.states['floorheating_groundfloor/valve_position']._value = 1.0

#
#
# class DemoThread(Thread):
#     """
#     A threading subclass used to run the threads required for demo mode
#
#     """
#
#     def __init__(self, callback, name='DemoThread', runevery=60):
#         super().__init__()
#         self.callback = callback
#         self.name = name
#         self.runevery = runevery
#
#     def run(self):
#         starttime = time.time()
#         nextrun = starttime
#
#         while True:  # run forever
#             self.callback()
#
#             runtime = time.time()
#             nextrun += self.runevery
#             time.sleep(max(0, nextrun - runtime))
#
# def emulate():
#     """
#     Set the system states
#
#     """
#
#     global weatherdata
#     global buildingdata
#
#     dt_ref = datetime.datetime(1970, 1, 1)
#     dt_now = datetime.datetime.utcnow()
#
#     timestamp_now = int( (dt_now-dt_ref).total_seconds() )
#
#
#     if weatherdata['timestamp'][-1] < timestamp_now+7*24*3600:
#         # weather emulation
#         logging.debug('Calculating demo weather data')
#         newdata = weather.emulate_weather(weatherdata,lookahead=10*24*3600)
#
#         # append data and remove old data
#         ind = np.where(weatherdata['timestamp'] >= timestamp_now-3600)
#
#         for (key,val),(newkey,newval) in zip(weatherdata.items(),newdata.items()):
#             weatherdata[key] = np.append(val[ind],newval)
#
#
#     # update weather states
#     core.states['outside/temperature/value'].value = round(np.interp(timestamp_now,weatherdata['timestamp'],weatherdata['ambienttemperature']),2)
#     core.states['outside/irradiance/value'].value = round(np.interp(timestamp_now,weatherdata['timestamp'],weatherdata['I_total_horizontal']),2)
#
#     # building emulation
#     logging.debug('Calculating demo building response')
#     buildingdata = building.emulate_building(buildingdata,weatherdata)
#
#
#     # update building states
#     core.states['living/temperature_wall/value'].value = round(buildingdata['living/temperature_wall/value'][-1],2)
#     core.states['living/temperature_window/value'].value = round(buildingdata['living/temperature_window/value'][-1],2)
#     core.states['bedroom/temperature/value'].value = round(buildingdata['bedroom/temperature/value'][-1],2)
#     core.states['bathroom/temperature/value'].value = round(buildingdata['bathroom/temperature/value'][-1],2)
#     #core.states['bedroom/temperature/value'].value = round(buildingdata['living/temperature_window/value'][-1],2)
#     #core.states['bathroom/temperature/value'].value = round(buildingdata['living/temperature_window/value'][-1],2)
#
#
# def weatherforecast(async=True):
#     """
#     Set the weather forecast states
#
#     """
#
#     global weatherdata
#
#     # update weather forecast states
#     now = datetime.datetime.utcnow().replace( hour=0, minute=0, second=0, microsecond=0)
#     timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )
#
#     logging.debug('Setting demo weather forecast data')
#
#     timestamplist = [timestamp+i*24*3600 for i in range(7)]
#     for i,t in enumerate(timestamplist):
#         forecast = {
#             'timestamp': t,
#             'temperature_day': np.interp(t+14*3600,weatherdata['timestamp'],weatherdata['ambienttemperature']),
#             'temperature_night': np.interp(t+6*3600,weatherdata['timestamp'],weatherdata['ambienttemperature']),
#             'pressure': 101325,
#             'humidity': 0.6,
#             'icon': '02d' if np.interp(t+14*3600,weatherdata['timestamp'],weatherdata['cloudcover']) < 0.5 else '09d',
#             'cloudcover': np.interp(t+14*3600,weatherdata['timestamp'],weatherdata['cloudcover']),
#             'wind_speed': 0,
#             'wind_direction': 0,
#             'precipitation_intensity': 0,
#             'precipitation_probability': 0,
#         }
#         core.states['weather/forecast/daily/{}'.format(i)].set(forecast,async=async)
#
#
#
#     timestamplist = [timestamp+i*3600 for i in range(7*24)]
#     for i,t in enumerate(timestamplist):
#
#         forecast = {
#             'timestamp': t,
#             'temperature': np.interp(t,weatherdata['timestamp'],weatherdata['ambienttemperature']),
#             'pressure': 101325,
#             'humidity': 0.6,
#             'icon': '02d' if np.interp(t,weatherdata['timestamp'],weatherdata['cloudcover']) < 0.5 else '09d',
#             'cloudcover': np.interp(t,weatherdata['timestamp'],weatherdata['cloudcover']),
#             'wind_speed': 0,
#             'wind_direction': 0,
#             'precipitation_intensity': 0,
#             'precipitation_probability': 0,
#         }
#         core.states['weather/forecast/hourly/{}'.format(i)].set(forecast,async=async)
#
# def building_response():
#
#     # update shading
#     for shading in core.components.find(type='shading'):
#         shading.states['position_status'].value = shading.states['position'].value
#
#     for dimminglight in core.components.find(type='dimminglight'):
#         dimminglight.states['value_status'].value = dimminglight.states['value'].value
#
#     logging.debug('updated building response')
#
#
#
# responsethread = DemoThread(building_response,name='ResponseThread',runevery=5)
# emulatorthread = DemoThread(emulate,name='EmulatorThread')
# forecastthread = DemoThread(weatherforecast,name='ForecastThread',runevery=3600)
#
#
#
#
#

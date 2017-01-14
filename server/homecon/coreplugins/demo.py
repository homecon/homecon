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



    def emulate_weather(self,initialdata,lookahead=0):
        """
        emulate weather conditions

        Parameters
        ----------
        initialdata : dict
            Dictionary with intial data.
            Must have a 'utcdatetime', 'cloudcover' and 'ambienttemperature' 
            keys with array like values

        lookahead : number
            Number of seconds to look ahead from now

        """

        # generate new datetime vector
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()

        utcdatetime = [initialdata['utcdatetime'][-1]+datetime.timedelta(seconds=t) for t in np.arange(0,(dt_now-initialdata['utcdatetime'][-1]).total_seconds()+lookahead,self.timestep)]
        if utcdatetime[-1] < dt_now:
            utcdatetime.append(dt_now)

        utcdatetime = np.array(utcdatetime)

        timestamp = np.array( [int( (dt-dt_ref).total_seconds() ) for dt in utcdatetime] )


        solar_azimuth = np.zeros(len(timestamp))
        solar_altitude = np.zeros(len(timestamp))
        I_direct_clearsky = np.zeros(len(timestamp))
        I_diffuse_clearsky = np.zeros(len(timestamp))
        I_direct_cloudy = np.zeros(len(timestamp))
        I_diffuse_cloudy = np.zeros(len(timestamp))
        cloudcover = np.zeros(len(timestamp))
        ambienttemperature = np.zeros(len(timestamp))
        I_total_horizontal = np.zeros(len(timestamp))
        I_direct_horizontal = np.zeros(len(timestamp))
        I_diffuse_horizontal = np.zeros(len(timestamp))
        I_ground_horizontal = np.zeros(len(timestamp))


        cloudcover[0] = initialdata['cloudcover'][-1]
        ambienttemperature[0] = initialdata['ambienttemperature'][-1]


        for i,t in enumerate(utcdatetime):

            solar_azimuth[i],solar_altitude[i] = util.weather.sunposition(self.latitude,self.longitude,elevation=self.elevation,utcdatetime=t)
            I_direct_clearsky[i],I_diffuse_clearsky[i] = util.weather.clearskyirrradiance(solar_azimuth[i],solar_altitude[i],utcdatetime=t)

            # random variation in cloud cover
            if i < len(timestamp)-1:
                delta_t = timestamp[i+1]-timestamp[i]
                cloudcover[i+1] = min(1.,max(0., cloudcover[i] + 0.0001*(2*np.random.random()-1)*delta_t ))

            I_direct_cloudy[i],I_diffuse_cloudy[i] = util.weather.cloudyskyirrradiance(I_direct_clearsky[i],I_diffuse_clearsky[i],cloudcover[i],solar_azimuth[i],solar_altitude[i],utcdatetime=t)
            
            I_total_horizontal[i], I_direct_horizontal[i], I_diffuse_horizontal[i], I_ground_horizontal[i] = util.weather.incidentirradiance(I_direct_cloudy[i],I_diffuse_cloudy[i],solar_azimuth[i],solar_altitude[i],0,0)

            # ambient temperature dependent on horizontal irradiance
            if i < len(timestamp)-1:
                delta_t = timestamp[i+1]-timestamp[i]
                ambienttemperature[i+1] = ambienttemperature[i] + I_total_horizontal[i]*delta_t/(15*24*3600) + (-10-ambienttemperature[i])*delta_t/(5*24*3600) + (2*np.random.random()-1)*delta_t/(2*3600)


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


    def emulate_building(self,initialdata,lookahead=0,heatingcurve=False):
        """
        emulate extremely simple building dynamics
        C_em*d(T_em)/dt = UA_em*(T_em-T_in) + Q_em 
        C_in*d(T_in)/dt = UA_in*(T_in-T_am) + UA_em*(T_in-T_em) + Q_so + Q_in

        Parameters
        ----------
        initialdata : dict
            Dictionary with intial data.
            Must have a 'utcdatetime', 'T_in', 'T_em' keys with array like values

        lookahead : number
            Number of seconds to look ahead from now

        """

        # time
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()

        utcdatetime = [initialdata['utcdatetime'][-1]+datetime.timedelta(seconds=t) for t in np.arange(0,(dt_now-initialdata['utcdatetime'][-1]).total_seconds()+lookahead,self.timestep)]
        if utcdatetime[-1] < dt_now:
            utcdatetime.append(dt_now)

        utcdatetime = np.array(utcdatetime)

        timestamp = np.array( [int( (dt-dt_ref).total_seconds() ) for dt in utcdatetime] )

        # parameters
        UA_in = 800
        C_in = 10e6

        UA_em = 600
        C_em = 8e6

        Q_em_max = 16000
        T_set = 20
        K_set = 5000
        K_am = 800


        # disturbances
        T_am = np.interp(timestamp,self.weatherdata['timestamp'],self.weatherdata['ambienttemperature'])

        Q_so = np.zeros(len(timestamp))
        for window in core.components.find(type='window'):
            Q_so = Q_so + window.calculate_solargain(
                I_direct=np.interp(timestamp,self.weatherdata['timestamp'],self.weatherdata['I_direct_cloudy']),
                I_diffuse=np.interp(timestamp,self.weatherdata['timestamp'],self.weatherdata['I_diffuse_cloudy']),
                solar_azimuth=np.interp(timestamp,self.weatherdata['timestamp'],self.weatherdata['solar_azimuth']),
                solar_altitude=np.interp(timestamp,self.weatherdata['timestamp'],self.weatherdata['solar_altitude']),
                shading_relativeposition=[np.zeros(len(timestamp)) for shading in core.components.find(type='shading',window=window.path) ])

        Q_in = np.zeros(len(timestamp))
        Q_em = np.zeros(len(timestamp))


        # initialization
        T_in = np.zeros(len(timestamp))
        T_in[0] = initialdata['T_in'][-1]

        T_em = np.zeros(len(timestamp))
        T_em[0] = initialdata['T_em'][-1]


        # solve discrete equation
        for i,t in enumerate(utcdatetime[:-1]):

            delta_t = timestamp[i+1]-timestamp[i]

            # emission heat flow
            if heatingcurve:
                Q_em[i] = min(Q_em_max,max(0, (T_in[i]-T_am[i])*K_am + (T_set-T_in[i])*K_set ))
            else:
                Q_em[i] = core.components['floorheating_groundfloor'].calculate_power()
    
            T_em[i+1] = T_em[i] + (T_in[i]-T_em[i])*delta_t*UA_em/C_em + Q_em[i]*delta_t/C_em
            T_in[i+1] = T_in[i] + (T_am[i]-T_in[i])*delta_t*UA_in/C_in + (T_em[i]-T_in[i])*delta_t*UA_em/C_in + Q_so[i]*delta_t/C_in + Q_in[i]*delta_t/C_in

        # set the output data
        data = {
            'utcdatetime': utcdatetime[1:],
            'timestamp': timestamp[1:],
            'T_in': T_in[1:],
            'T_em': T_em[1:],
            'Q_em': Q_em[1:],
            'Q_so': Q_so[1:],
            'dayzone/temperature': T_in[1:],
            'dayzone/solargain': 0.7*Q_so[1:],
            'dayzone/internalgain': 0*np.ones(len(utcdatetime[1:])),
            'nightzone/temperature': T_in[1:],
            'nightzone/solargain': 0.3*Q_so[1:],
            'nightzone/internalgain': 0*np.ones(len(utcdatetime[1:])),
            'bathroomzone/temperature': T_in[1:],
            'bathroomzone/solargain': 0.0*Q_so[1:],
            'bathroomzone/internalgain': 0*np.ones(len(utcdatetime[1:])),
            'living/temperature_wall/value': 0.90*T_in[1:] + 0.10*T_em[1:],
            'living/temperature_window/value': 0.98*T_in[1:] + 0.02*T_em[1:],
            'heatpump/power_setpoint': Q_em[1:],
            'heatpump/power': Q_em[1:],
            'floorheating_groundfloor/valve_position': 1.0*np.ones(len(utcdatetime[1:])),
            'living/window_west_1/screen/position': 0.0*np.ones(len(utcdatetime[1:])),
            'living/window_west_2/screen/position': 0.0*np.ones(len(utcdatetime[1:])),
            'kitchen/window_west/screen/position': 0.0*np.ones(len(utcdatetime[1:])),
            'kitchen/window_south/screen/position': 0.0*np.ones(len(utcdatetime[1:])),
            'bedroom/window_east/shutter/position': 0.0*np.ones(len(utcdatetime[1:])),
            'bedroom/window_north/shutter/position': 0.0*np.ones(len(utcdatetime[1:])),

        }
        return data



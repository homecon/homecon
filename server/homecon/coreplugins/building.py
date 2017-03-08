#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import pytz
import uuid
import numpy as np
import pyomo.environ as pyomo

from .. import core
from .. import util

class Building(core.plugin.Plugin):
    """
    Class to define the HomeCon building
    
    """

    def initialize(self):
        """
        Initialize

        """
        logging.debug('Building plugin initialized')


    def listen_state_changed(self,event):

        if 'component' in event.data['state'].config:
            component = core.components[event.data['state'].config['component']]

            if component.type == 'zonetemperaturesensor':
                print('zonetemperaturesensor changed')
                zone = core.components[component.config['zone']]
                zone.states['temperature'].value = np.round( zone.calculate_temperature(), 2)

            elif component.type == 'shading' and event.data['state'].path.split('/')[-1]=='position':
                window = core.components[component.config['window']]
                window.states['solargain'].value = np.round( window.calculate_solargain(), 1)

            elif component.type == 'window' and event.data['state'].path.split('/')[-1]=='solargain':
                zone = core.components[component.config['zone']]
                zone.states['solargain'].value = np.round( zone.calculate_solargain(), 1)

        if event.data['state'].path == 'weather/irradiancedirect' or event.data['state'].path == 'weather/irradiancediffuse':
            for window in core.components.find(type='window'):
                window.states['solargain'].value = np.round( window.calculate_solargain(), 1)




class Zone(core.component.Component):
    """
    a class implementing a building zone
    
    """
    default_config = {
        'type': '',
    }
    linked_states = {
        'temperature': {
            'default_config': {'datatype': 'number', 'quantity': 'temperature', 'unit': '°C'},
            'fixed_config': {},
        },
        'humidity': {
            'default_config': {'datatype': 'number', 'quantity': 'relative humidity', 'unit': '%'},
            'fixed_config': {},
        },
        'solargain': {
            'default_config': {'datatype': 'number', 'quantity': 'heat flow rate', 'unit': 'W', 'description':'Solar heat flow through all windows in the zone'},
            'fixed_config': {},
        },
        'internalgain': {
            'default_config': {'datatype': 'number', 'quantity': 'heat flow rate', 'unit': 'W', 'description':'Internal heat flows to the zone'},
            'fixed_config': {},
        },
    }

    def calculate_solargain(self,utcdatetime=None,I_direct=None,I_diffuse=None,solar_azimuth=None,solar_altitude=None,shading_relativeposition=None):
        """
        Parameters
        ----------

        shading_relativeposition : np.ndarray
            number of windows x  number of shadings x number of timesteps

        """

        windows = core.components.find(type='window', zone=self.path)

        if shading_relativeposition is None:
            shading_relativeposition = [None]*len(windows)


        solargain = sum([
            window.calculate_solargain(
                utcdatetime=utcdatetime,
                I_direct=I_direct,
                I_diffuse=I_diffuse,
                solar_azimuth=solar_azimuth,
                solar_altitude=solar_altitude,
                shading_relativeposition=position)
            for window,position in zip(windows,shading_relativeposition)
        ])

        return solargain

    def calculate_temperature(self,utcdatetime=None):
        """

        """

        temperature = []
        confidence = []
        for sensor in core.components.find(type='zonetemperaturesensor', zone=self.path):
            temp = sensor.states['value'].history(utcdatetime=utcdatetime)
            if not temp is None:
                temperature.append(temp)
                confidence.append(sensor.config['confidence'])


        if len(temperature)>0:
            return sum([c*t for c,t, in zip(temperature,confidence)])/sum(confidence)
        else:
            return None

core.components.register(Zone)



class Zonetemperaturesensor(core.component.Component):
    """
    a class implementing a temperature sensor
    
    """
    default_config = {
        'type': '',
        'zone': '',
        'confidence': 0.5,
    }
    linked_states = {
        'value': {
            'default_config': {'datatype': 'number', 'quantity': 'temperature', 'unit': '°C'},
            'fixed_config': {},
        },
    }

core.components.register(Zonetemperaturesensor)


class Window(core.component.Component):
    """
    a class implementing a window
    
    """

    default_config = {
        'type': '',
        'area': 1,
        'azimuth': 0,
        'tilt': 90,
        'transmittance': 0.8,

        'zone': '',
    }
    linked_states = {
        'solargain': {
            'default_config': {'datatype': 'number', 'quantity': 'heat flow rate', 'unit': 'W', 'description':'Solar heat flow through the window'},
            'fixed_config': {},
        },
    }

    def calculate_solargain(self,utcdatetime=None,I_direct=None,I_diffuse=None,solar_azimuth=None,solar_altitude=None,shading_relativeposition=None):
        """

        """

        # find shadings attached to this window
        shadings = core.components.find(type='shading', window=self.path)

        if shading_relativeposition is None:
            shading_relativeposition = [None]*len(shadings)

        shading_transmittance = 1.0
        for shading,position in zip(shadings,shading_relativeposition):
            shading_transmittance = shading_transmittance*shading.calculate_transmittance(utcdatetime=utcdatetime,relativeposition=position)





        # get inputs
        if I_direct is None:
            if utcdatetime is None:
                I_direct = core.states['weather/irradiancedirect'].value
            else:
                I_direct = core.states['weather/irradiancedirect'].history(utcdatetime)

        if I_diffuse is None:
            if utcdatetime is None:
                I_diffuse = core.states['weather/irradiancediffuse'].value
            else:
                I_diffuse = core.states['weather/irradiancediffuse'].history(utcdatetime)

        if solar_azimuth is None:
            if utcdatetime is None:
                solar_azimuth = core.states['weather/sun/azimuth'].value
            else:
                solar_azimuth = core.states['weather/sun/azimuth'].history(utcdatetime)

        if solar_altitude is None:
            if utcdatetime is None:
                solar_altitude = core.states['weather/sun/altitude'].value
            else:
                solar_altitude = core.states['weather/sun/altitude'].history(utcdatetime)


        surface_azimuth = self.config['azimuth']
        surface_tilt = self.config['tilt']
        surface_area = self.config['area']
        transmittance = self.config['transmittance']
        
        
        if not I_direct is None and not I_diffuse is None and not solar_azimuth is None and not solar_altitude is None:
            if hasattr(I_direct,'__len__'):
                I_total_surface = np.zeros(len(I_direct))
                for i in range(len(I_direct)):
                    I_total_surface[i], I_direct_surface, I_diffuse_surface, I_ground_surface = util.weather.incidentirradiance(I_direct[i],I_diffuse[i],solar_azimuth[i],solar_altitude[i],surface_azimuth,surface_tilt)
            
            else:
                I_total_surface, I_direct_surface, I_diffuse_surface, I_ground_surface = util.weather.incidentirradiance(I_direct,I_diffuse,solar_azimuth,solar_altitude,surface_azimuth,surface_tilt)

        else:
            I_total_surface = 0

        return I_total_surface*surface_area*transmittance*shading_transmittance


core.components.register(Window)


class Shading(core.component.Component):
    """
    a class implementing a window shading
    
    """
    default_config = {
        'type': '',
        'closed_transmittance': 0.3,
        'open_transmittance': 1.0,
        'closed_position': 1.0,
        'open_position': 0.0,
        'window': '',
    }
    linked_states = {
        'position': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
        'position_max': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
        'position_min': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
        'auto': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
    }


    def calculate_relative_position(self,utcdatetime=None,position=None):
        """
        """

        if position is None:
            position = self.states['position'].history(utcdatetime)

        if position is None:
            if utcdatetime is None:
                relativeposition = 0
            else:
                relativeposition = np.zeros(len(utcdatetime))
        else:
            relativeposition = (position-self.config['open_position'])/(self.config['closed_position']-self.config['open_position'])

        return relativeposition


    def calculate_transmittance(self,utcdatetime=None,relativeposition=None,position=None):
        """
        """

        if relativeposition is None:
            relativeposition = self.calculate_relative_position(utcdatetime=utcdatetime,position=position)

        return relativeposition*self.config['closed_transmittance'] + (1-relativeposition)*self.config['open_transmittance']


core.components.register(Shading)


class Light(core.component.Component):
    """
    a class implementing an on/off light
    
    """
    default_config = {
        'type': '',
        'power': '',
        'zone': '',
    }
    linked_states = {
        'value': {
            'default_config': {},
            'fixed_config': {},
        },
    }


core.components.register(Light)


class Dimminglight(Light):
    """
    a class implementing an dimmable light
    
    """
    pass

core.components.register(Dimminglight)



class Heatgenerationsystem(core.component.Component):
    """
    a class implementing a modulating heating system.
    
    """
    default_config = {
        'type': '',
        'power': 10000.,
    }
    linked_states = {
        'power': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
        'power_setpoint': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
    }


    def calculate_power(self,utcdatetime=None):

        if self.states['power'].value is None:
            return self.states['power_setpoint'].history(utcdatetime)
        else:
            return self.states['power'].history(utcdatetime)


core.components.register(Heatgenerationsystem)



class Heatpump(Heatgenerationsystem):
    """
    a class implementing a modulating heat pump.
    
    """

    def prepare_ocp_model(self,model):
        model.heatpump_P_el = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, initialize=0, bounds=(0,self.config['power']))
        model.heatpump_Q = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, initialize=0, bounds=(0,self.config['power']))
        model.heatpump_COP = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, initialize=0, bounds=(0,self.config['power']))
        
        model.heatpump_contraint_COP = pyomo.Constraint(model.i,rule=lambda model,i: model.heatpump_COP[i] == 3.0)
        model.heatpump_contraint_P_el = pyomo.Constraint(model.i,rule=lambda model,i: model.heatpump_P_el[i]*model.heatpump_COP[i] == model.heatpump_Q[i])


    def postprocess_ocp_model(self,model):
        self.Q_schedule = [(pyomo.value(model.timestamp[i]),pyomo.value(model.heatpump_Q[i])) for i in model.i]


    def maxpower(self,timestamp):
        return self.config['power']


core.components.register(Heatpump)




class Heatemissionsystem(core.component.Component):
    """
    a class implementing a heat emission system with a valve for controlling the
    energy flow to it.
    
    """

    default_config = {
        'type': '',
        'heatgenerationsystem': '',
        'zone': '',
        'closed_position': 0.0,
        'open_position': 1.0,
    }
    linked_states = {
        'power': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
        'valve_position': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
    }


    def calculate_power(self,utcdatetime=None):
        parallelsystems = core.components.find(type='heatemissionsystem',heatgenerationsystem=self.config['heatgenerationsystem'])

        valvepositions = np.array([(system.states['valve_position'].history(utcdatetime)-system.config['closed_position'])/(system.config['open_position']-system.config['closed_position']) for system in parallelsystems])

        relativepower = (self.states['valve_position'].history(utcdatetime)-self.config['closed_position'])/(self.config['open_position']-self.config['closed_position'])/sum(valvepositions)

        heatgenerationsystempower = core.components[self.config['heatgenerationsystem']].calculate_power(utcdatetime=utcdatetime)

        return relativepower*heatgenerationsystempower


core.components.register(Heatemissionsystem)



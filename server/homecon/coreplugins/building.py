#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import pytz
import uuid
import numpy as np

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
                window.states['irradiation'].value = np.round( window.calculate_irradiation(), 1)
                

        if event.data['state'].path == 'weather/irradiancedirect' or event.data['state'].path == 'weather/irradiancediffuse':
            for window in core.components.find(type='window'):
                window.states['irradiation'].value = np.round( window.calculate_irradiation(), 1)




class Zone(core.component.Component):
    """
    a class implementing a building zone
    
    """

    def initialize(self):
        self.states = {
            'temperature': {
                'default_config': {'type': 'number', 'quantity': 'temperature', 'unit': '°C'},
                'fixed_config': {},
            },
            'humidity': {
                'default_config': {'type': 'number', 'quantity': 'relative humidity', 'unit': '%'},
                'fixed_config': {},
            },
        }
        self.config = {
            'type': '',
        }

    def calculate_irradiation(self):
        """

        """
        irradiation = 0
        for window in core.components.find(type='window', zone=self.path):
            irradiation = window.calculate_irradiation()

        return irradiation

    def calculate_temperature(self):
        """

        """
        temperature = []
        confidence = []
        for sensor in core.components.find(type='zonetemperaturesensor', zone=self.path):
            temp = sensor.states['value'].value
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

    def initialize(self):
        self.states = {
            'value': {
                'default_config': {},
                'fixed_config': {},
            },
        }
        self.config = {
            'type': '',
            'zone': '',
            'confidence': 0.5,
        }

core.components.register(Zonetemperaturesensor)


class Window(core.component.Component):
    """
    a class implementing a window
    
    """

    def initialize(self):
        self.states = {
            'irradiation': {
                'default_config': {'type': 'number', 'quantity': 'irradiation', 'unit': 'W', 'description':'Solar heat flow through the window'},
                'fixed_config': {},
            },
        }
        self.config = {
            'type': '',
            'area': 1,
            'azimuth': 0,
            'tilt': 90,
            'transmittance': 0.8,
            'zone': '',
        }

    def calculate_irradiation(self,utcdatetime=None,I_direct=None,I_diffuse=None,solar_azimuth=None,solar_altitude=None,shading_relativeposition=None):
        """

        """

        # find shadings attached to this window
        shading_transmittance = 1.0
        for shading in core.components.find(type='shading', window=self.path):
            shading_transmittance = shading_transmittance*shading.calculate_transmittance(utcdatetime=utcdatetime,relativeposition=shading_relativeposition)

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
    
    def initialize(self):
        self.states = {
            'position': {
                'default_config': {},
                'fixed_config': {},
            },
            'move': {
                'default_config': {},
                'fixed_config': {},
            },
            'stop': {
                'default_config': {},
                'fixed_config': {},
            },
            'auto': {
                'default_config': {},
                'fixed_config': {},
            },
        }
        self.config = {
            'type': '',
            'closed_transmittance': 0.3,
            'open_transmittance': 1.0,
            'closed_position': 1.0,
            'open_position': 0.0,
            'window': '',
        }

    def calculate_transmittance(self,utcdatetime=None,relativeposition=None):
        """
        """

        if relativeposition is None:
            if utcdatetime is None:
                position = self.states['position'].value
            else:
                position = self.states['position'].history(utcdatetime)

            # relative position 1: closed, 0: open
            if position is None:
                relativeposition = 0
            else:
                relativeposition = (position-self.config['open_position'])/(self.config['closed_position']-self.config['open_position'])
        
        
        return relativeposition*self.config['closed_transmittance'] + (1-relativeposition)*self.config['open_transmittance']


core.components.register(Shading)


class Light(core.component.Component):
    """
    a class implementing an on/off light
    
    """

    def initialize(self):
        self.states = {
            'value': {
                'default_config': {},
                'fixed_config': {},
            },
        }
        self.config = {
            'type': '',
            'power': '',
            'zone': '',
        }

core.components.register(Light)


class Dimminglight(Light):
    """
    a class implementing an dimmable light
    
    """
    def initialize(self):
        super(Dimminglight,self).initialize()

core.components.register(Dimminglight)




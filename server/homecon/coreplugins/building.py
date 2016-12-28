#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import pytz
import uuid

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

        if not event.data['state'].component is None:
            component = core.components[event.data['state'].component]
            if component.type == 'zonetemperaturesensor':
                print('zonetemperaturesensor changed')

            elif component.type == 'shading' and event.data['state'].split('/')[-1]=='position':
                print('shading position changed')

        if event.data['state'].path == 'weather/irradiancedirect' or event.data['state'].path == 'weather/irradiancediffuse':
            print('irradiance changed')


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
            'orientation': 0,
            'tilt': 90,
            'zone': '',
        }

    def calculate_irradiation(self):
        """

        """

        # find shadings attached to this window
        shadingpath = self.path+'/shading'
        if shadingpath in self._components:
            shading = self._components[shadingpath]
            pos = shading.states['position'].state.value

        I_direct = self._states['weather/irradiancedirect'].value
        I_diffuse = self._states['weather/irradiancediffuse'].value
        solar_azimuth = self._states['weather/sun/azimuth'].value
        solar_altitude = self._states['weather/sun/altitude'].value
        surface_azimuth = self.config['azimuth']
        surface_tilt = self.config['tilt']
        surface_area = self.config['area']

        I = incidentirradiance(I_direct,I_diffuse,solar_azimuth,solar_altitude,surface_azimuth,surface_tilt)

        self.states['irradiation'].value = np.round(I*surface_area,1)

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
            'minimum_transmittance': 0.3,
            'maximum_transmittance': 1.0,
            'window': '',
        }

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




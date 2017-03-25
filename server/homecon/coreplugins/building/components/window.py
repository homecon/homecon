#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import numpy as np
import pyomo.environ as pyomo

from .... import core
from .... import util

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
        'cost_visibility': 1.0,
    }
    linked_states = {
        'solargain': {
            'default_config': {'datatype': 'number', 'quantity': 'heat flow rate', 'unit': 'W', 'description':'Solar heat flow through the window'},
            'fixed_config': {},
        },
    }

    def calculate_solargain(self,timestamp=None,I_direct=None,I_diffuse=None,solar_azimuth=None,solar_altitude=None,shading_relativeposition=None):
        """

        """

        shadings = core.components.find(type='shading', window=self.path)

        if shading_relativeposition is None:
            shading_relativeposition = [None]*len(shadings)

        shading_transmittance = 1.0
        for shading,position in zip(shadings,shading_relativeposition):
            shading_transmittance = shading_transmittance*shading.calculate_transmittance(timestamp=timestamp,relativeposition=position)



        # get inputs
        if I_direct is None:
            if timestamp is None:
                I_direct = core.states['weather/irradiancedirect'].value
            else:
                I_direct = core.states['weather/irradiancedirect'].history(timestamp)

        if I_diffuse is None:
            if timestamp is None:
                I_diffuse = core.states['weather/irradiancediffuse'].value
            else:
                I_diffuse = core.states['weather/irradiancediffuse'].history(timestamp)

        if solar_azimuth is None:
            if timestamp is None:
                solar_azimuth = core.states['weather/sun/azimuth'].value
            else:
                solar_azimuth = core.states['weather/sun/azimuth'].history(timestamp)

        if solar_altitude is None:
            if timestamp is None:
                solar_altitude = core.states['weather/sun/altitude'].value
            else:
                solar_altitude = core.states['weather/sun/altitude'].history(timestamp)


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
        'transmittance_closed': 0.3,
        'transmittance_open': 1.0,
        'position_closed': 1.0,
        'position_open': 0.0,
        'window': '',
        'override_duration': 180,
        'cost_movement': 1.0,
    }
    linked_states = {
        'position': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
        'position_status': {
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
        'override': {
            'default_config': {'datatype': 'number'},
            'fixed_config': {},
        },
    }


    def calculate_relative_position(self,timestamp=None,position=None):
        """
        The relative position is defined so that 0.0 is completely open and 1.0
        is completely closed.
        """

        if position is None:
            position = self.states['position'].history(timestamp)

        if position is None:
            if timestamp is None:
                relativeposition = 0
            else:
                relativeposition = np.zeros(len(timestamp))
        else:
            relativeposition = (position-self.config['position_open'])/(self.config['position_closed']-self.config['position_open'])

        return relativeposition


    def calculate_transmittance(self,timestamp=None,relativeposition=None,position=None):
        """
        """

        if relativeposition is None:
            relativeposition = self.calculate_relative_position(timestamp=timestamp,position=position)

        return relativeposition*self.config['transmittance_closed'] + (1-relativeposition)*self.config['transmittance_open']


core.components.register(Shading)


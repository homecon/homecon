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
        'transmittance': 0.5,
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
        'cost_visibility': 1.0,
        'open_if_rain': False,
        'max_wind_speed': 100,
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
            'default_config': {'datatype': 'boolean'},
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
            position = self.states['position_status'].history(timestamp)

        if position is None:
            if not hasattr(timestamp,'__len__'):
                relativeposition = 0.
            else:
                relativeposition = np.zeros(len(timestamp))

        else:
            relativeposition = np.maximum(0.,np.minimum(1., (position-self.config['position_open'])/(self.config['position_closed']-self.config['position_open']) ))

        return relativeposition


    def calculate_relative_position_bounds(self,timestamp=None,rain=False,wind=0):
        """
        Calculates the minimum relative position
        """
        if timestamp is None:

            if self.states['override'].value is None or self.states['override'].value<=0:
                if self.config['open_if_rain'] and rain:
                    position_min_temp = self.config['position_open']
                    position_max_temp = self.config['position_open']

                elif wind>self.config['max_wind_speed']:
                    position_min_temp = self.config['position_open']
                    position_max_temp = self.config['position_open']

                else:
                    if self.states['position_min'].value is None:
                        position_min_temp = self.config['position_open']
                    else:
                        position_min_temp = self.states['position_min'].value

                    if self.states['position_max'].value is None:
                        position_max_temp = self.config['position_closed']
                    else:
                        position_max_temp = self.states['position_max'].value

            else:
                position_min_temp = self.states['position_status'].value
                position_max_temp = self.states['position_status'].value

        else:
            if hasattr(timestamp,'__len__'):
                position_min_temp = self.config['position_open']*np.ones(len(timestamp))
                position_max_temp = self.config['position_closed']*np.ones(len(timestamp))
            else:
                position_min_temp = self.config['position_open']
                position_max_temp = self.config['position_closed']


        relativeposition_min_temp = self.calculate_relative_position( position=position_min_temp )
        relativeposition_max_temp = self.calculate_relative_position( position=position_max_temp )

        # it is not sure that min is closed and max is open
        # the relative position is defined so 0 is open and 1 is closed
        relativeposition_min = np.minimum(relativeposition_min_temp,relativeposition_max_temp)
        relativeposition_max = np.maximum(relativeposition_min_temp,relativeposition_max_temp)

        return (relativeposition_min,relativeposition_max)


    def calculate_transmittance(self,timestamp=None,relativeposition=None,position=None):
        """
        """

        if relativeposition is None:
            relativeposition = self.calculate_relative_position(timestamp=timestamp,position=position)

        return relativeposition*self.config['transmittance_closed'] + (1-relativeposition)*self.config['transmittance_open']


core.components.register(Shading)


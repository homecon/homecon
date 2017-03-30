#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pyomo.environ as pyomo
import numpy as np

from .... import core

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
        'solargain_setpoint': {
            'default_config': {'datatype': 'program', 'quantity': 'heat flow rate', 'unit': 'W', 'description':'Setpoint for solar heat flow through all windows in the zone'},
            'fixed_config': {},
        },
        'internalgain': {
            'default_config': {'datatype': 'number', 'quantity': 'heat flow rate', 'unit': 'W', 'description':'Internal heat flows to the zone'},
            'fixed_config': {},
        },
        'internalgain_setpoint': {
            'default_config': {'datatype': 'program', 'quantity': 'heat flow rate', 'unit': 'W', 'description':'Setpoint for internal heat flows to the zone'},
            'fixed_config': {},
        },
    }

    def calculate_solargain(self,timestamp=None,I_direct=None,I_diffuse=None,solar_azimuth=None,solar_altitude=None,shading_relativeposition=None):
        """
        Parameters
        ----------

        shading_relativeposition : np.ndarray
            number of windows x  number of shadings x number of timesteps

        """

        windows = core.components.find(type='window', zone=self.path)

        if shading_relativeposition is None:
            shading_relativeposition = [None]*len(windows)

        if len(windows)==0:
            if hasattr(timestamp,'__len__'):
                solargain = np.zeros( len(timestamp) )
            elif hasattr(I_direct,'__len__'):
                solargain = np.zeros( len(I_direct) )
            elif hasattr(I_diffuse,'__len__'):
                solargain = np.zeros( len(I_diffuse) )
            elif hasattr(solar_azimuth,'__len__'):
                solargain = np.zeros( len(solar_azimuth) )
            elif hasattr(solar_altitude,'__len__'):
                solargain = np.zeros( len(solar_altitude) )
            else:
                solargain = 0
        else:
            solargain = sum([
                window.calculate_solargain(
                    timestamp=timestamp,
                    I_direct=I_direct,
                    I_diffuse=I_diffuse,
                    solar_azimuth=solar_azimuth,
                    solar_altitude=solar_altitude,
                    shading_relativeposition=position)
                for window,position in zip(windows,shading_relativeposition)
            ])
        
            

        return solargain



    def calculate_temperature(self,timestamp=None):
        """

        """

        temperature = []
        confidence = []
        for sensor in core.components.find(type='zonetemperaturesensor', zone=self.path):
            temp = sensor.states['value'].history(timestamp=timestamp)
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





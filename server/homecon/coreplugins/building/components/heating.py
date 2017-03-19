#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import numpy as np
import pyomo.environ as pyomo

from .... import core

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

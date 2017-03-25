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

    def create_ocp_model_variables(self,model):

        self.ocp_variables['P_el'] = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, bounds=(0,self.config['power']), initialize=0.)
        self.ocp_variables['Q']    = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, bounds=(0,self.config['power']), initialize=0.)
        self.ocp_variables['COP']  = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, bounds=(0.,10.), initialize=3.)

        for key,val in self.ocp_variables:
            setattr(model,'{}_{}'.format(self.path.replace('/',''),key),val)

    def create_ocp_model_constraints(self,model):
        setattr(model,'constraint_{}_COP'.format(self.path.replace('/','')), pyomo.Constraint(model.i,rule=lambda model,i: self.ocp_variables['COP'][i] == 3.0))
        setattr(model,'constraint_{}_P_el'.format(self.path.replace('/','')),pyomo.Constraint(model.i,rule=lambda model,i: self.ocp_variables['P_el'][i]*self.ocp_variables['COP'][i] == self.ocp_variables['Q'][i]))


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
        'heatgenerationsystems': [],
        'zone': '',
        'valve_position_closed': 0.0,
        'valve_position_open': 1.0,
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

    def create_ocp_model_variables(self,model):
        self.ocp_variables['position'] = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, bounds=(0,1), initialize=0)
        self.ocp_variables['Q']        = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, initialize=0)

        for key,val in self.ocp_variables:
            setattr(model,'{}_{}'.format(self.path.replace('/',''),key),val)
       


    def create_ocp_model_constraints(self,model):

        # a list of all generation system heat flows connected to this heatemissionsystem
        Q_list = [core.components[heatgenerationsystem].ocp_variables['Q'] for heatgenerationsystem in self.config['heatgenerationsystems']]

        # FIXME use the valve position variable
        setattr(model,'constraint_{}_Q'.format(self.path.replace('/','')),pyomo.Constraint(model.i,rule=lambda model,i: self.ocp_variables['Q'][i] == sum(getattr(model,var)[i] for var in Q_list)))



    def calculate_power(self,utcdatetime=None):
        parallelsystems = core.components.find(type='heatemissionsystem',heatgenerationsystem=self.config['heatgenerationsystem'])

        valvepositions = np.array([(system.states['valve_position'].history(utcdatetime)-system.config['valve_position_closed'])/(system.config['valve_position_open']-system.config['valve_position_closed']) for system in parallelsystems])

        relativepower = (self.states['valve_position'].history(utcdatetime)-self.config['valve_position_closed'])/(self.config['valve_position_open']-self.config['valve_position_closed'])/sum(valvepositions)

        heatgenerationsystempower = core.components[self.config['heatgenerationsystem']].calculate_power(utcdatetime=utcdatetime)

        return relativepower*heatgenerationsystempower


core.components.register(Heatemissionsystem)

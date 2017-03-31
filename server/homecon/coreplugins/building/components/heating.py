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
        'group': '',
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

    def calculate_power(self,timestamp=None):

        if self.states['power'].value is None:
            return self.states['power_setpoint'].history(timestamp)
        else:
            return self.states['power'].history(timestamp)


    def create_ocp_variables(self,model):
        self.ocp_variables['Q'] = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, bounds=(0,self.config['power']), initialize=0.)
        
        for key,val in self.ocp_variables.items():
            setattr(model,'{}_{}'.format(self.path.replace('/',''),key),val)

    def postprocess_ocp(self,model):
        self.Q_schedule = [(pyomo.value(model.timestamp[i]),pyomo.value(self.ocp_variables['Q'][i])) for i in model.i]


core.components.register(Heatgenerationsystem)



class Heatpump(Heatgenerationsystem):
    """
    a class implementing a modulating heat pump.
    
    """

    def create_ocp_variables(self,model):
        self.ocp_variables['P_el'] = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, bounds=(0,self.config['power']), initialize=0.)
        self.ocp_variables['COP']  = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, bounds=(0.,10.), initialize=3.)

        super().create_ocp_variables(model)


    def create_ocp_constraints(self,model):
        setattr(model,'constraint_{}_COP'.format(self.path.replace('/','')), pyomo.Constraint(model.i,rule=lambda model,i: self.ocp_variables['COP'][i] == 3.0))
        setattr(model,'constraint_{}_P_el'.format(self.path.replace('/','')),pyomo.Constraint(model.i,rule=lambda model,i: self.ocp_variables['P_el'][i]*self.ocp_variables['COP'][i] == self.ocp_variables['Q'][i]))


    def postprocess_ocp(self,model):
        super().postprocess_ocp(model)
        self.P_el_schedule = [(pyomo.value(model.timestamp[i]),pyomo.value(self.ocp_variables['P_el'][i])) for i in model.i]


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
        'group': '',
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


    def create_ocp_variables(self,model):
        self.ocp_variables['Q']        = pyomo.Var(model.i, domain=pyomo.NonNegativeReals, initialize=0)

        for key,val in self.ocp_variables.items():
            setattr(model,'{}_{}'.format(self.path.replace('/',''),key),val)

    def postprocess_ocp_variables(self,model):

        grouppower = pyomo.value( core.components[self.config['group']].ocp_variables['Q'] )
        selfpower = pyomo.value(self.ocp_variables['Q'] )

        position = selfpower/grouppower if grouppower>0 else self.config['valve_position_open']   # FIXME check this, probably incorrect

        # set the valve position
        self.states['valve_position'].value = position


    def calculate_power(self,timestamp=None):
        emissionsystems = core.components.find(type='heatemissionsystem',group=self.config['group'])

        valveposition = self.states['valve_position'].history(timestamp)
        valvepositions = np.array([(system.states['valve_position'].history(timestamp)-system.config['valve_position_closed'])/(system.config['valve_position_open']-system.config['valve_position_closed']) for system in emissionsystems])
        
        if hasattr(timestamp,'__len__'):
            relativepower = np.array([(p-self.config['valve_position_closed'])/(self.config['valve_position_open']-self.config['valve_position_closed'])/s if s>0 else 0 for p,s in zip(valveposition,np.sum(valvepositions,axis=0))])
        else:
            relativepower = (valveposition-self.config['valve_position_closed'])/(self.config['valve_position_open']-self.config['valve_position_closed'])/sum(valvepositions) if sum(valvepositions)>0 else 0

        grouppower = core.components[self.config['group']].calculate_power(timestamp=timestamp)

        return relativepower*grouppower

core.components.register(Heatemissionsystem)



class Heatinggroup(core.component.Component):
    """
    a class implementing a group of connected heat generation systems and heat emission systems 
    
    """
    
    def calculate_power(self,timestamp=None):
        heatgenerationsystems = core.components.find(type='heatgenerationsystem',group=self.path)

        Q = sum([system.calculate_power(timestamp=timestamp) for system in heatgenerationsystems])

        if Q==0 and hasattr(timestamp,'__len__'):
            Q += np.zeros(len(timestamp))

        return Q


    def create_ocp_constraints(self,model):

        # a list of all generation system heat flows connected to this heatemissionsystem
        Q_generation_list = [system.ocp_variables['Q'] for system in core.components.find(type='heatgenerationsystem',group=self.path)]
        Q_emission_list = [system.ocp_variables['Q'] for system in core.components.find(type='heatemissionsystem',group=self.path)]


        setattr(model,'constraint_{}_Q'.format(self.path.replace('/','')),pyomo.Constraint(model.i,rule=lambda model,i: sum(var[i] for var in Q_generation_list) == sum(var[i] for var in Q_emission_list)))

core.components.register(Heatinggroup)


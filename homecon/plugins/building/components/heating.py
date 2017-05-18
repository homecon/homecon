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
        'heatingcurve': False,
        'Q_hc_nom': 7000.,
        'T_hc_sup_nom': 45.,
        'T_hc_amb_nom': -10.,
        'T_hc_sup_offset': -3.,
        'K_hc': 3.,
        'controlzone': '',
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
        super().create_ocp_variables(model)
        if self.config['heatingcurve']:
            self.add_ocp_Var(model,'Q', model.i, domain=pyomo.NonNegativeReals, initialize=0.)
        else:
            self.add_ocp_Var(model,'Q', model.i, domain=pyomo.NonNegativeReals, bounds=(0,self.config['power']), initialize=0.)

    def create_ocp_constraints(self,model):
        super().create_ocp_constraints(model)
        if self.config['heatingcurve']:
            UA_em_est = self.config['Q_hc_nom']/(self.config['T_hc_sup_nom']-20.)
            
            if self.config['controlzone'] in core.components:
                controlzone = core.components[self.config['controlzone']]
                T_in = controlzone.ocp_variables['T']
                T_in_set = controlzone.ocp_variables['T_min']
                
                self.add_ocp_Constraint(model,'Q_hc',model.i,rule=lambda model,i: self.ocp_variables['Q'][i] >= self.config['Q_hc_nom']*(model.T_amb[i]-20.)/(self.config['T_hc_amb_nom']-20.)-self.config['K_hc']*UA_em_est*(T_in[i]-T_in_set[i]) - UA_em_est*(T_in[i]-(20.+self.config['T_hc_sup_offset'])) )

            else:
                # no zone temperature feedback
                T_in = 20.
                T_in_set = 20.
                
                self.add_ocp_Constraint(model,'Q_hc',model.i,rule=lambda model,i: self.ocp_variables['Q'][i] == max(0.,min(self.config['power'] , self.config['Q_hc_nom']*(model.T_amb[i]-20.)/(self.config['T_hc_amb_nom']-20.)-self.config['K_hc']*UA_em_est*(T_in-T_in_set) - UA_em_est*(T_in-(20.+self.config['T_hc_sup_offset'])) )) )

    def postprocess_ocp(self,model):
        self.Q_schedule = [(pyomo.value(model.timestamp[i]),pyomo.value(self.ocp_variables['Q'][i])) for i in model.i]
        self.states['power_setpoint'].value = self.Q_schedule[0][1] # FIXME interpolate to future

core.components.register(Heatgenerationsystem)



class Gasboiler(Heatgenerationsystem):
    """
    a class implementing a modulating gas boiler.
    
    """

    def create_ocp_variables(self,model):
        super().create_ocp_variables(model)
        self.add_ocp_Var(model,'P_ng',model.i, domain=pyomo.NonNegativeReals, initialize=0.)

    def create_ocp_constraints(self,model):
        super().create_ocp_constraints(model)
        self.add_ocp_Constraint(model,'P_ng',model.i,rule=lambda model,i: self.ocp_variables['P_ng'][i] == self.ocp_variables['Q'][i]  )

core.components.register(Gasboiler)



class Heatpump(Heatgenerationsystem):
    """
    a class implementing a modulating heat pump.
    
    """

    def create_ocp_variables(self,model):
        super().create_ocp_variables(model)
        self.add_ocp_Var(model,'P_el',model.i, domain=pyomo.NonNegativeReals, initialize=0.)
        self.add_ocp_Param(model,'COP',model.i, initialize=lambda model,i: min(6.0,max(1.0,3.1+(model.T_amb[i]--2)/(7--2)*(4.2-3.1))) )

    def create_ocp_constraints(self,model):
        super().create_ocp_constraints(model)
        #self.add_ocp_Constraint(model,'COP',model.i,rule=lambda model,i: self.ocp_variables['COP'][i] == 3.0)
        self.add_ocp_Constraint(model,'P_el',model.i,rule=lambda model,i: self.ocp_variables['P_el'][i]*self.ocp_variables['COP'][i] == self.ocp_variables['Q'][i])

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
        super().create_ocp_variables(model)
        self.add_ocp_Var(model,'Q',model.i, domain=pyomo.NonNegativeReals, initialize=0.)

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
    default_config = {
        'heatingcurve': True,
        'Q_hc_nom': 7000.,
        'T_hc_sup_nom': 45.,
        'T_hc_amb_nom': -10.,
        'T_hc_sup_offset': -3.,
        'K_hc': 3.,
        'controlzone': '',
    }
    
    def calculate_power(self,timestamp=None):
        heatgenerationsystems = core.components.find(type='heatgenerationsystem',group=self.path)

        Q = sum([system.calculate_power(timestamp=timestamp) for system in heatgenerationsystems])

        if Q==0 and hasattr(timestamp,'__len__'):
            Q += np.zeros(len(timestamp))

        return Q

    def create_ocp_variables(self,model):
        super().create_ocp_variables(model)
        self.add_ocp_Var(model,'Q',model.i, domain=pyomo.NonNegativeReals, initialize=0.)

    def create_ocp_constraints(self,model):
        super().create_ocp_constraints(model)

        # a list of all generation system heat flows connected to this heatemissionsystem
        Q_gen_list = [system.ocp_variables['Q'] for system in core.components.find(type='heatgenerationsystem',group=self.path)]
        Q_emi_list = [system.ocp_variables['Q'] for system in core.components.find(type='heatemissionsystem',group=self.path)]


        self.add_ocp_Constraint(model,'Q_gen',model.i,rule=lambda model,i: self.ocp_variables['Q'][i] == sum(var[i] for var in Q_gen_list) )
        self.add_ocp_Constraint(model,'Q_emi',model.i,rule=lambda model,i: self.ocp_variables['Q'][i] == sum(var[i] for var in Q_emi_list) )

        if self.config['heatingcurve']:

            for system in core.components.find(type='heatgenerationsystem',group=self.path):
                all_systems_have_heatingcurve = True
                if not system.config['heatingcurve']:
                    all_systems_have_heatingcurve = False
                    break
            if all_systems_have_heatingcurve:
                logging.warning('All heat generation systems in the heating group are controlled by a heating curve. Heatinggroup {} heatingcurve is not applied.'.format(self.path))
            else:
                UA_em_est = self.config['Q_hc_nom']/(self.config['T_hc_sup_nom']-20.)
                
                if self.config['controlzone'] in core.components:
                    controlzone = core.components[self.config['controlzone']]
                    T_in = controlzone.ocp_variables['T']
                    T_in_set = controlzone.ocp_variables['T_min']
                    
                    self.add_ocp_Constraint(model,'Q_hc',model.i,rule=lambda model,i: self.ocp_variables['Q'][i] >= self.config['Q_hc_nom']*(model.T_amb[i]-20.)/(self.config['T_hc_amb_nom']-20.)-self.config['K_hc']*UA_em_est*(T_in[i]-T_in_set[i]) - UA_em_est*(T_in[i]-(20.+self.config['T_hc_sup_offset'])) )

                else:
                    # no zone temperature feedback
                    T_in = 20.
                    T_in_set = 20.
                    
                    self.add_ocp_Constraint(model,'Q_hc',model.i,rule=lambda model,i: self.ocp_variables['Q'][i] == max(0., self.config['Q_hc_nom']*(model.T_amb[i]-20.)/(self.config['T_hc_amb_nom']-20.)-self.config['K_hc']*UA_em_est*(T_in-T_in_set) - UA_em_est*(T_in-(20.+self.config['T_hc_sup_offset'])) ) )

core.components.register(Heatinggroup)


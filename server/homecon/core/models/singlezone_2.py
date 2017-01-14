#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pyomo.environ as pyomo

from . import model
from ... import core
#from ..component import components

"""
Notation constraints:

Q : Heat flow,
P : Electric power,
C : thermal heat capacity
UA : thermal UA value

T : temperature



_amb for ambient
_liv for living zone
_nig for night zone
_bat for bathroom

_est for estimated

_ini for initial

"""


class Singlezone_2(model.Buildingmodel):

    def __init__(self):
        self.timestep = 15*60           # timestep in seconds
        self.parameters = {'C_liv': 5e6, 'C_flr': 10e6, 'UA_liv_amb': 400, 'UA_flr_liv': 400} 


        # state constraints are used in both models
        def state_T_liv(model, i):
            if i < len(model.i)-1:
                return model.C_liv*(model.T_liv_est[i+1]-model.T_liv_est[i])/self.timestep == model.UA_liv_amb*(model.T_amb[i]-model.T_liv_est[i]) + model.UA_flr_liv*(model.T_flr_est[i]-model.T_liv_est[i]) + model.Q_sol[i] + model.Q_int[i]
            else:
                return pyomo.Constraint.Feasible

        def state_T_flr(model, i):
            if i < len(model.i)-1:
                return model.C_flr*(model.T_flr_est[i+1]-model.T_flr_est[i])/self.timestep == model.UA_flr_liv*(model.T_liv_est[i]-model.T_flr_est[i]) + model.Q_hea[i]
            else:
                return pyomo.Constraint.Feasible


        self.constraints = {
            'state_T_liv': state_T_liv,
            'state_T_flr': state_T_flr,
        }

        self.set_identification_model()
        self.set_validation_model()


    def set_identification_model(self):
        """
        """
        model = pyomo.AbstractModel()
        model.i = pyomo.Set(doc='time index')

        model.timestamp = pyomo.Param(model.i)
        model.T_amb = pyomo.Param(model.i)
        model.T_liv = pyomo.Param(model.i)

        model.Q_hea = pyomo.Param(model.i)
        model.Q_sol = pyomo.Param(model.i)
        model.Q_int = pyomo.Param(model.i)

        model.C_liv = pyomo.Var(domain=pyomo.NonNegativeReals, initialize=self.parameters['C_liv'], bounds=(1e3,100e9))
        model.UA_liv_amb = pyomo.Var(domain=pyomo.NonNegativeReals, initialize=self.parameters['UA_liv_amb'], bounds=(1,10000e3))

        model.C_flr = pyomo.Var(domain=pyomo.NonNegativeReals, initialize=self.parameters['C_flr'], bounds=(1e3,100e9))
        model.UA_flr_liv = pyomo.Var(domain=pyomo.NonNegativeReals, initialize=self.parameters['UA_flr_liv'], bounds=(1,10000e3))

        model.T_liv_est = pyomo.Var(model.i,domain=pyomo.Reals,initialize=lambda model,i: model.T_liv[i])
        model.T_flr_est = pyomo.Var(model.i,domain=pyomo.Reals)


        # contstraints
        model.state_liv = pyomo.Constraint(model.i,rule=self.constraints['state_T_liv'])
        model.state_liv_ini = pyomo.Constraint(rule=lambda model: model.T_liv_est[0] == model.T_liv[0])

        model.state_flr = pyomo.Constraint(model.i,rule=self.constraints['state_T_flr'])

        # objective
        model.objective = pyomo.Objective(rule=lambda model: sum( (model.T_liv[i]-model.T_liv_est[i])**2 for i in model.i ), sense=pyomo.minimize)

        self.identification_model = model


    def set_validation_model(self):
        """
        """
        model = pyomo.AbstractModel()
        model.i = pyomo.Set(doc='time index')

        model.timestamp = pyomo.Param(model.i)
        model.T_amb = pyomo.Param(model.i)
        model.T_liv = pyomo.Param(model.i)

        model.Q_hea = pyomo.Param(model.i)
        model.Q_sol = pyomo.Param(model.i)
        model.Q_int = pyomo.Param(model.i)

        model.C_liv = pyomo.Param(initialize=self.parameters['C_liv'])
        model.UA_liv_amb = pyomo.Param(initialize=self.parameters['UA_liv_amb'])

        model.C_flr = pyomo.Param(initialize=self.parameters['C_flr'])
        model.UA_flr_liv = pyomo.Param(initialize=self.parameters['UA_flr_liv'])

        model.T_liv_est = pyomo.Var(model.i,domain=pyomo.Reals,initialize=lambda model,i: model.T_liv[i])
        model.T_flr_est = pyomo.Var(model.i,domain=pyomo.Reals)

        # contstraints
        model.state_liv = pyomo.Constraint(model.i,rule=self.constraints['state_T_liv'])
        model.state_liv_ini = pyomo.Constraint(rule=lambda model: model.T_liv_est[0] == model.T_liv[0])

        model.state_flr = pyomo.Constraint(model.i,rule=self.constraints['state_T_flr'])

        # objective
        model.objective = pyomo.Objective(rule=lambda model: sum( (model.T_liv[i]-model.T_liv_est[i])**2 for i in model.i ), sense=pyomo.minimize)

        self.validation_model = model


    def get_data(self,utcdatetime):


        zones = [zone for zone in core.components.find(type='zone')]


        data = {}
        data['T_amb'] = core.states['weather/temperature'].history(utcdatetime)
        data['T_liv'] = np.mean( [zone.states['temperature'].history(utcdatetime) for zone in zones], axis=0)
        data['Q_hea'] = core.states['heatpump/power'].history(utcdatetime)
        data['Q_sol'] = np.sum( [zone.states['solargain'].history(utcdatetime) for zone in zones], axis=0 )
        data['Q_int'] = np.sum( [zone.states['internalgain'].history(utcdatetime) for zone in zones], axis=0 )


        return data


    def get_result(self,model):

        result = {
            'parameters': {},
            'inputs': {},
            'estimates': {},
            'observations': {},
            'fitquality': {},
        }

        result['parameters']['C_liv'] = pyomo.value(model.C_liv)
        result['parameters']['UA_liv_amb'] = pyomo.value(model.UA_liv_amb)
        result['parameters']['C_flr'] = pyomo.value(model.C_flr)
        result['parameters']['UA_flr_liv'] = pyomo.value(model.UA_flr_liv)

        result['inputs']['timestamp'] = [pyomo.value(model.timestamp[i]) for i in model.i]
        result['inputs']['T_amb'] = [pyomo.value(model.T_amb[i]) for i in model.i]
        result['inputs']['Q_hea'] = [pyomo.value(model.Q_hea[i]) for i in model.i]
        result['inputs']['Q_sol'] = [pyomo.value(model.Q_sol[i]) for i in model.i]
        result['inputs']['Q_int'] = [pyomo.value(model.Q_int[i]) for i in model.i]

        result['estimates']['T_liv'] = [pyomo.value(model.T_liv_est[i]) for i in model.i]

        result['observations']['T_liv'] = [pyomo.value(model.T_liv[i]) for i in model.i]

        error = np.array([pyomo.value(model.T_liv[i]-model.T_liv_est[i]) for i in model.i])
        rmse = np.mean( error**2 )**0.5

        result['fitquality']['rmse'] = rmse
        result['fitquality']['max_error'] = np.max(np.abs(error))
        result['fitquality']['success'] = False

        if rmse < 2.0 and np.max(np.abs(error)) < 2.0:
            result['fitquality']['success'] = True


        return result


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


class Singlezone_1(model.Buildingmodel):

    def __init__(self):
        self.timestep = 15*60           # timestep in seconds
        self.parameters = {'C_liv': 10e6, 'UA_liv_amb': 800} 


        # state constraints are used in both models
        def state_T_liv(model, i):
            if i < len(model.i)-1:
                return model.C_liv*(model.T_liv_est[i+1]-model.T_liv_est[i])/self.timestep == model.UA_liv_amb*(model.T_amb[i]-model.T_liv[i]) + model.Q_hea[i] + model.Q_sol[i] + model.Q_int[i]
            else:
                return pyomo.Constraint.Feasible

        self.constraints = {
            'state_T_liv': state_T_liv
        }

        self.set_identification_model()
        self.set_validation_model()


    def set_identification_model(self):
        """
        """
        model = pyomo.AbstractModel()
        model.i = pyomo.Set(doc='time index')

        model.T_amb = pyomo.Param(model.i)
        model.T_liv = pyomo.Param(model.i)

        model.Q_hea = pyomo.Param(model.i)
        model.Q_sol = pyomo.Param(model.i)
        model.Q_int = pyomo.Param(model.i)

        model.C_liv = pyomo.Var(domain=pyomo.NonNegativeReals, initialize=self.parameters['C_liv'], bounds=(1e3,100e9))
        model.UA_liv_amb = pyomo.Var(domain=pyomo.NonNegativeReals, initialize=self.parameters['UA_liv_amb'], bounds=(1,10000e3))
        model.T_liv_est = pyomo.Var(model.i,domain=pyomo.Reals,initialize=lambda model,i: model.T_liv[i])


        # contstraints
        model.state_liv = pyomo.Constraint(model.i,rule=self.constraints['state_T_liv'])
        model.state_liv_ini = pyomo.Constraint(rule=lambda model: model.T_liv_est[0] == model.T_liv[0])

        # objective
        model.objective = pyomo.Objective(rule=lambda model: sum( (model.T_liv[i]-model.T_liv_est[i])**2 for i in model.i ), sense=pyomo.minimize)

        self.identification_model = model


    def set_validation_model(self):
        """
        """
        model = pyomo.AbstractModel()
        model.i = pyomo.Set(doc='time index')

        model.T_amb = pyomo.Param(model.i)
        model.T_liv = pyomo.Param(model.i)

        model.Q_hea = pyomo.Param(model.i)
        model.Q_sol = pyomo.Param(model.i)
        model.Q_int = pyomo.Param(model.i)

        model.C_liv = pyomo.Param(initialize=self.parameters['C_liv'])
        model.UA_liv_amb = pyomo.Param(initialize=self.parameters['UA_liv_amb'])
        model.T_liv_est = pyomo.Var(model.i,domain=pyomo.Reals,initialize=lambda model,i: model.T_liv[i])

        # contstraints
        model.state_liv = pyomo.Constraint(model.i,rule=self.constraints['state_T_liv'])
        model.state_liv_ini = pyomo.Constraint(rule=lambda model: model.T_liv_est[0] == model.T_liv[0])

        # objective
        model.objective = pyomo.Objective(rule=lambda model: sum( (model.T_liv[i]-model.T_liv_est[i])**2 for i in model.i ), sense=pyomo.minimize)

        self.validation_model = model


    def get_data(self,utcdatetime):

        Q_sol = sum( [window.calculate_irradiation(
            I_direct=core.states['weather/irradiancedirect'].history(utcdatetime),
            I_diffuse=core.states['weather/irradiancediffuse'].history(utcdatetime),
            solar_azimuth=core.states['weather/sun/azimuth'].history(utcdatetime),
            solar_altitude=core.states['weather/sun/altitude'].history(utcdatetime),
            shading_relativeposition=np.zeros(len(utcdatetime))) for window in core.components.find(type='window')] )


        data = {}
        data['T_amb'] = core.states['weather/temperature'].history(utcdatetime)
        data['T_liv'] = core.states['living/temperature_wall/value'].history(utcdatetime)
        data['Q_hea'] = core.states['heatpump/power'].history(utcdatetime)
        data['Q_sol'] = Q_sol
        data['Q_int'] = np.zeros(len(utcdatetime))


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

        if rmse < 2.0 and np.max(np.abs(error)) < 1.0:
            result['fitquality']['success'] = True


        return result


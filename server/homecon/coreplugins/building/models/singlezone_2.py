#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pyomo.environ as pyomo

from . import model
from .... import core


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


    def get_identification_data(self,timestamp):


        zones = [zone for zone in core.components.find(type='zone')]


        data = {}
        data['T_amb'] = core.states['weather/temperature'].history(timestamp)
        data['T_liv'] = np.mean( [zone.states['temperature'].history(timestamp) for zone in zones], axis=0)
        data['Q_sol'] = np.sum( [zone.states['solargain'].history(timestamp) for zone in zones], axis=0 )
        data['Q_int'] = np.sum( [zone.states['internalgain'].history(timestamp) for zone in zones], axis=0 )
        data['Q_hea'] = np.sum( [heatemissionsystem.calculate_power(timestamp=timestamp) for zone in zones for heatemissionsystem in core.components.find(type='heatemissionsystem',zone=zone)], axis=0 )
        
        if data['Q_hea']==0 and hasattr(timestamp,'__len__'):
            data['Q_hea'] += np.zeros(len(timestamp))
        if not hasattr(data['Q_int'],'__len__'):
            data['Q_int'] += np.zeros(len(data['timestamp']))
        if not hasattr(data['Q_hea'],'__len__'):
            data['Q_hea'] += np.zeros(len(data['timestamp']))


        return data


    def get_identification_result(self,model):

        result = super().get_identification_result(model)

        result['parameters']['C_liv'] = pyomo.value(model.C_liv)
        result['parameters']['UA_liv_amb'] = pyomo.value(model.UA_liv_amb)
        result['parameters']['C_flr'] = pyomo.value(model.C_flr)
        result['parameters']['UA_flr_liv'] = pyomo.value(model.UA_flr_liv)

        result['inputs']['timestamp'] = [pyomo.value(model.timestamp[i]) for i in model.i]
        result['inputs']['T_amb'] = [np.round(pyomo.value(model.T_amb[i]),2) for i in model.i]
        result['inputs']['Q_hea'] = [np.round(pyomo.value(model.Q_hea[i]),2) for i in model.i]
        result['inputs']['Q_sol'] = [np.round(pyomo.value(model.Q_sol[i]),2) for i in model.i]
        result['inputs']['Q_int'] = [np.round(pyomo.value(model.Q_int[i]),2) for i in model.i]

        result['estimates']['T_liv'] = [np.round(pyomo.value(model.T_liv_est[i]),2) for i in model.i]

        result['observations']['T_liv'] = [np.round(pyomo.value(model.T_liv[i]),2) for i in model.i]

        error = np.array([pyomo.value(model.T_liv[i]-model.T_liv_est[i]) for i in model.i])
        rmse = np.mean( error**2 )**0.5

        result['fitquality']['rmse'] = rmse
        result['fitquality']['max_error'] = np.max(np.abs(error))
        result['fitquality']['success'] = False

        if rmse < 2.0 and np.max(np.abs(error)) < 2.0:
            result['fitquality']['success'] = True


        return result



    def create_ocp_constraints(self,model):
        # FIXME

        # state estimation?  # FIXME
        print(  [zone.states['temperature'].history(model.timestamp[0]) for zone in core.components.find(type='zone')] )
        T_liv_ini = np.nanmean( [zone.states['temperature'].history(model.timestamp[0]) for zone in core.components.find(type='zone')], axis=0)
        print(T_liv_ini)

        T_flr_ini = 20


        # constraints
        # states
        model.constraint_building_state_liv= pyomo.Constraint(model.i,
            rule=lambda model,i: self.parameters['C_liv']*(model.building_T_liv[i+1]-model.building_T_liv[i])/model.timestep[i] == self.parameters['UA_liv_amb']*(model.T_amb[i]-model.building_T_liv[i]) + model.building_Q_sol[i] + model.building_Q_int[i] if i < len(model.i)-1 else pyomo.Constraint.Feasible 
        )
        model.constraint_building_state_liv_ini = pyomo.Constraint(rule=lambda model: model.building_T_liv[0] == T_liv_ini)

        model.constraint_building_state_flr= pyomo.Constraint(model.i,
            rule=lambda model,i: self.parameters['C_flr']*(model.building_T_flr[i+1]-model.building_T_flr[i])/model.timestep[i] == self.parameters['UA_flr_liv']*(model.T_flr[i]-model.building_T_liv[i]) + model.building_Q_hea[i]  if i < len(model.i)-1 else pyomo.Constraint.Feasible 
        )
        model.constraint_building_state_flr_ini = pyomo.Constraint(rule=lambda model: model.building_T_flr[0] == T_flr_ini)



        # discomfort
        model.constraint_liv_D_tc = pyomo.Constraint(model.i,
            rule=lambda model,i: model.building_liv_D_tc[i] >= 20-(0.5*model.building_T_liv[i]+0.5*model.building_T_liv[i+1])  # FIXME minimum temperature bound must be defined through a state and the gui but different bounds can exist for other models
        )
        model.constraint_liv_D_th = pyomo.Constraint(model.i,
            rule=lambda model,i: model.building_liv_D_th[i] >= (0.5*model.building_T_liv[i]+0.5*model.building_T_liv[i+1])-24  # FIXME maximum temperature ...
        )
        model.constraint_liv_D_vi = pyomo.Constraint(model.i,
            rule=lambda model,i: model.building_liv_D_vi[i] >= model.building_Q_sol[i].bounds[1]-model.building_Q_sol[i]
        )


        # heatemissionsystems
        zones = core.components.find(type='zone')

        Q_list = []
        for zone in zones:
            heatemissionsystems = core.components.find(type='heatemissionsystem',zone=zone.path)
            Q_list += [heatemissionsystem.ocp_variables['Q'] for heatemissionsystem in heatemissionsystems]

        model.building_constraint_Q_hea = pyomo.Constraint(model.i,rule=lambda model,i: model.building_Q_hea[i] == sum(var[i] for var in Q_list))



    def postprocess_ocp(self,model):
        T_liv_program = [(int(pyomo.value(model.timestamp[i])),float(np.round(pyomo.value(model.building_T_liv[i]),2))) for i in model.ip]
        T_flr_program = [(int(pyomo.value(model.timestamp[i])),float(np.round(pyomo.value(model.building_T_flr[i]),2))) for i in model.ip]
        Q_hea_program = [(int(pyomo.value(model.timestamp[i])),float(np.round(pyomo.value(model.building_Q_hea[i]),2))) for i in model.i]
        Q_sol_program = [(int(pyomo.value(model.timestamp[i])),float(np.round(pyomo.value(model.building_Q_sol[i]),2))) for i in model.i]
        Q_int_program = [(int(pyomo.value(model.timestamp[i])),float(np.round(pyomo.value(model.building_Q_int[i]),2))) for i in model.i]

        zones = core.components.find(type='zone')
        for zone in zones:
            zone.states['temperature_program'].value = T_liv_program
            zone.states['solargain_program'].value = [(val[0], val[1]/len(zones) )for val in Q_sol_program]     # FIXME divide base on maximum solargain
            zone.states['internalgain_program'].value = [(val[0], val[1]/len(zones) )for val in Q_int_program] 


        result = {}
        result['timestamp'] = [int(pyomo.value(model.timestamp[i])) for i in model.i]
        result['T_liv'] = [float(np.round(pyomo.value(model.building_T_liv[i]),2)) for i in model.i]
        result['T_flr'] = [float(np.round(pyomo.value(model.building_T_flr[i]),2)) for i in model.i]
        result['T_amb'] = [float(np.round(pyomo.value(model.T_amb[i]),2)) for i in model.i]

        result['Q_hea'] = [float(np.round(pyomo.value(model.building_Q_hea[i]),2)) for i in model.i]

        result['Q_sol'] = [float(np.round(pyomo.value(model.building_Q_sol[i]),2)) for i in model.i]
        result['Q_sol_max'] = [float(np.round(pyomo.value(model.building_Q_sol[i].bounds[1]),2)) for i in model.i]
        result['Q_sol_min'] = [float(np.round(pyomo.value(model.building_Q_sol[i].bounds[0]),2)) for i in model.i]

        result['Q_int'] = [float(np.round(pyomo.value(model.building_Q_int[i]),2)) for i in model.i]

        core.states['mpc/building/program'].value = result


        # old
        result = {}
        result['timestamp'] = [int(pyomo.value(model.timestamp[i])) for i in model.i]
        result['T_liv_old'] = [float(np.round(pyomo.value(model.building_T_liv[i]),2)) for i in model.i]
        result['T_flr_old'] = [float(np.round(pyomo.value(model.building_T_flr[i]),2)) for i in model.i]
        result['Q_hea_old'] = [float(np.round(pyomo.value(model.building_Q_hea[i]),2)) for i in model.i]
        result['Q_sol_old'] = [float(np.round(pyomo.value(model.building_Q_sol[i]),2)) for i in model.i]
        result['Q_int_old'] = [float(np.round(pyomo.value(model.building_Q_int[i]),2)) for i in model.i]

        self.program_old.append(result)
        if len(self.program_old) == 24*4:
            result_old = self.program_old.pop(0)
        else:
            result_old = self.program_old[0]

        core.states['mpc/building/program_old'].value = result_old


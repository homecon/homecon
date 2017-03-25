#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import numpy as np
import pyomo.environ as pyomo

class Buildingmodel(object):
    """
    base class for building models

    """
    def __init__(self):

        self.timestep = 15*60
        self.parameters = {}
        self.constraints = {}
        self.identification_model = None
        self.validation_model = None


    def get_data(self,timestamp):
        """

        """

        return {}


    def get_result(self,model):
        """

        """

        results = {
            'success': False,
        }
        return results


    def _parse_data(self,timestamp,data):
        """
        Prepare a data dictionary of pyomo

        """

        # add the timestamp to data
        data['timestamp'] = timestamp

        pyomodata={None:{
            'i':{None: range(len(timestamp))},
        }}

        for key,val in data.items():
            pyomodata[None][key] = {(i,): val[i] for i in range(len(timestamp))}

        # add the parameters
        for key,val in self.parameters.items():
            pyomodata[None][key] = {None: val}

        return pyomodata


    def identify(self):
        # retrieve data
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_end = datetime.datetime.utcnow()
        dt_ini = dt_end - datetime.timedelta(days=7)

        timestamp_end = int( (dt_end-dt_ref).total_seconds() )
        timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

        timestamp = range(timestamp_ini,timestamp_end,self.timestep)

        data = self.get_data(timestamp)
        data = self._parse_data(timestamp,data)

        # create the instance
        instance = self.identification_model.create_instance(data)

        # set initial values
        for key,val in self.parameters.items():
            if hasattr(instance,key):
                setattr(instance,key,val)

        # solve
        solver = pyomo.SolverFactory('ipopt')
        results = solver.solve(instance, tee=True)

        result = self.get_result(instance)

        # set results
        for key in self.parameters:
            self.parameters[key] = result['parameters'][key]


        return result


    def validate(self):
        # retrieve data
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_end = datetime.datetime.utcnow()
        dt_ini = dt_end - datetime.timedelta(days=7)

        timestamp_end = int( (dt_end-dt_ref).total_seconds() )
        timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

        timestamp = range(timestamp_ini,timestamp_end,self.timestep)

        data = self.get_data(timestamp)
        data = self._parse_data(timestamp,data)


        # create the instance
        instance = self.validation_model.create_instance(data)


        # solve
        solver = pyomo.SolverFactory('ipopt')
        results = solver.solve(instance, tee=True)

        result = self.get_result(instance)

        return result


    def preprocess_ocp_model(self,model):
        pass


    def postprocess_ocp_model(self,model):
        pass
    

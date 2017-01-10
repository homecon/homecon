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
        print('Model')
        self.timestep = 15*60
        self.parameters = {}
        self.constraints = {}
        self.identification_model = None
        self.validation_model = None


    def get_data(self,utcdatetime):
        """

        """

        return {}


    def get_results(self,validationinstance):
        """

        """

        results = {
            'success': False,
        }
        return results


    def _parse_data(self,utcdatetime,data):
        """
        Prepare a data dictionary of pyomo

        """

        pyomodata={None:{
            'i':{None: range(len(utcdatetime))},
        }}

        for key,val in data.items():
            pyomodata[None][key] = {(i,): val[i] for i in range(len(utcdatetime))}

        return pyomodata


    def identify(self):
        # retrieve data
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_end = datetime.datetime.utcnow()
        dt_ini = dt_end - datetime.timedelta(days=1)

        timestamp_end = int( (dt_end-dt_ref).total_seconds() )
        timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

        utcdatetime = [datetime.datetime.utcfromtimestamp(ts) for ts in range(timestamp_ini,timestamp_end,self.timestep)]

        data = self.get_data(utcdatetime)
        data = self._parse_data(utcdatetime,data)

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
        dt_ini = dt_end - datetime.timedelta(days=1)

        timestamp_end = int( (dt_end-dt_ref).total_seconds() )
        timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

        utcdatetime = [datetime.datetime.utcfromtimestamp(ts) for ts in range(timestamp_ini,timestamp_end,self.timestep)]

        data = self.get_data(utcdatetime)
        data = self._parse_data(utcdatetime,data)


        # create the instance
        instance = self.validation_model.create_instance(data)

        # solve
        solver = pyomo.SolverFactory('ipopt')
        results = solver.solve(instance, tee=True)

        result = self.get_result(instance)

        return result




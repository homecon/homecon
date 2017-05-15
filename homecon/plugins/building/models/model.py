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
        """
        Notes
        -----
        redefine in a child class
        """

        self.parameters = {}

        self.identification_model = None
        self.validation_model = None


    def get_identification_data(self):
        """
        Redefine in child class

        Returns
        -------
        A dictionary with the data required for the identification model.
        'timestamp' must be a key
        """

        timestep = 15*60

        dt_ref = datetime.datetime(1970, 1, 1)
        dt_end = datetime.datetime.utcnow()
        dt_ini = dt_end - datetime.timedelta(days=2)

        timestamp_end = int( (dt_end-dt_ref).total_seconds() )
        timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

        timestamps = np.arange(timestamp_ini,timestamp_end,timestep)

        return {'timestamp':timestamps}


    def get_identification_result(self,model):
        """
        Redefine in child class
        """

        result = {
            'parameters': {},
            'inputs': {},
            'estimates': {},
            'observations': {},
            'fitquality': {},
        }

        return result

    def _check_data(self,data):

        for key,val in data.items():

            ind = np.where(np.isnan(val))[0]
            if len(ind) > 0.5*len(val):
                # more than half the values are nan, the data is not usable
                return False

        return True

    def _parse_data(self,data):
        """
        Prepare a data dictionary for pyomo

        Parameters
        ----------
        timestamp : list or numpy.array
            list of timestamps

        data : dict of lists or numpy.arrays
            dictionary with the data with keys corresponding to the pyomo model variables

        """

        pyomodata={None:{
            'i':{None: range(len(data['timestamp']))},
        }}

        for key,val in data.items():
            pyomodata[None][key] = {(i,): val[i] for i in range(len(data['timestamp']))}

        # add the parameters
        for key,val in self.parameters.items():
            pyomodata[None][key] = {None: val}

        return pyomodata



    def identify(self,verbose=0):
        """
        Retrieves data and performs the system identification

        """
        # retrieve data
        data = self.get_identification_data()

        if self._check_data(data):
            data = self._parse_data(data)

            # create the instance
            instance = self.identification_model.create_instance(data)

            # set initial values
            for key,val in self.parameters.items():
                if hasattr(instance,key):
                    setattr(instance,key,val)

            # solve
            solver = pyomo.SolverFactory('ipopt')
            results = solver.solve(instance, tee=True if verbose > 0 else False)

            result = self.get_identification_result(instance)

            # set parameters
            for key in self.parameters:
                self.parameters[key] = result['parameters'][key]

            return result

        else:
            # the data is insufficient to perform the identification
            return None

        

    def validate(self,verbose=0):
        """
        Retrieves data and performs the model validation

        """
        # retrieve data
        data = self.get_identification_data()
        if self._check_data(data):
            data = self._parse_data(data)
            
            # create the instance
            instance = self.validation_model.create_instance(data)

            # solve
            solver = pyomo.SolverFactory('ipopt')
            results = solver.solve(instance, tee=True if verbose > 0 else False)

            result = self.get_identification_result(instance)

            return result

        else:
            # the data is insufficient to perform the validation
            return None


    def create_ocp_variables(self,model):
        pass

    def create_ocp_constraints(self,model):
        pass

    def postprocess_ocp(self,model):
        pass
    

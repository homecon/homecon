#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import numpy as np
import pyomo.environ as pyomo
import asyncio

from .. import core
from .. import util


class Mpc(core.plugin.Plugin):
    """
    Class defining the model predictive control strategy
    
    """

    def initialize(self):
        

        self.horizon = 24*7*3600      # the prediction and control horizon in seconds
        self.timestep = 900           # the control timestep in seconds

        # schedule cross validation
        optimization_task = asyncio.ensure_future(self.schedule_optimization())

        logging.debug('MPC plugin Initialized')



    def optimization(self):

        # common data gathering
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_ini = datetime.datetime.utcnow()

        timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )
        timestamps = [ts for ts in range(timestamp_ini,timestamp_ini+self.horizon,self.timestep)]

        p_el = [0.250 for ts in timestamps]
        p_ng = [0.070 for ts in timestamps]
        

        weatherforecast_timestamps = []
        weatherforecast_T_amb = []
        for i in range(24*7):
            weatherforecast_timestamps.append( core.states['weather/forecast/hourly/{}'.format(i)].value['timestamp'] )
            weatherforecast_T_amb.append( core.states['weather/forecast/hourly/{}'.format(i)].value['temperature'] )

        print(weatherforecast_timestamps)
        print(weatherforecast_T_amb)
            
        T_amb = np.interp(timestamps,weatherforecast_timestamps,weatherforecast_T_amb)


        """
        Optimal control problem naming conventions

        T_xxx: Temperature
        Q_xxx: Heat flow
        V_xxx: Volume flow
        xxx_P_el: Electrical power
        xxx_P_ng: Natural gas power
        p_xx: price
       
        """

        # control optimization
        model = pyomo.ConcreteModel()
        model.i = pyomo.Set(initialize=range(len(timestamps)-1), doc='time index, the last timestamp is not included (-)')
        model.ip = pyomo.Set(initialize=range(len(timestamps)-1), doc='time index, the last timestamp is included (-)')

        model.timestamp = pyomo.Param(model.ip,initialize={i:timestamps[i] for i in model.ip}, doc='timestamp (s)')
        model.timestep = pyomo.Param(model.i,initialize={i:timestamps[i+1]-timestamps[i] for i in model.i}, doc='timestep of the interval [i,i+1] (s)')

        model.p_el = pyomo.Param(model.ip, initialize={i:p_el[i] for i in model.ip}, doc='electricity price (EUR/kWh)')
        model.p_ng = pyomo.Param(model.ip, initialize={i:p_el[i] for i in model.ip}, doc='natural gas price (EUR/kWh)')

        model.P_el_tot = pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0, doc='average electricity use in the interval [i,i+1] (W)')
        model.P_ng_tot = pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0, doc='average natural gas use in the interval [i,i+1] (W)')

        model.T_amb = pyomo.Param(model.ip, initialize={i:T_amb[i] for i in model.ip}, doc='ambient temperature at timestep i (degC)')



        # create variables from plugins and components in that order
        for plugin in core.plugins.values():
            plugin.create_ocp_variables(model)

        for component in core.components.values():
            component.create_ocp_variables(model)

        # create constraints from plugins and components in that order
        for plugin in core.plugins.values():
            plugin.create_ocp_constraints(model)

        for component in core.components.values():
            component.create_ocp_constraints(model)


        P_el_list = [attr for attr in dir(model) if attr.endswith('P_el')]
        P_ng_list = [attr for attr in dir(model) if attr.endswith('P_ng')]

        model.constraint_P_el_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.P_el_tot[i] == sum(getattr(model,var)[i] for var in P_el_list), doc='summing the total elctrical power demand')
        model.constraint_P_ng_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.P_ng_tot[i] == sum(getattr(model,var)[i] for var in P_ng_list), doc='summing the total natural gas power demand')


        # add an objective
        model.objective = pyomo.Objective(rule=lambda model: sum( model.p_el[i]*model.P_el_tot[i]*model.timestep[i] + model.p_ng[i]*model.P_ng_tot[i]*model.timestep[i] for i in model.i), sense=pyomo.minimize)


        # solve
        solver = pyomo.SolverFactory('ipopt')
        results = solver.solve(model, tee=True)  # FIXME should be done in a separate thread to not stop the event loop

        # pass control program to plugins
        for plugin in core.plugins.values():
            plugin.postprocess_ocp(model)


        # pass control program to components
        for component in core.components.values():
            component.postprocess_ocp(model)


        return True





    async def schedule_optimization(self):
        """
        Schedule cross validation running once a week

        """

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()

            nsecs = dt_now.minute*60 + dt_now.second + dt_now.microsecond*1e-6
            delta = np.round( nsecs/900 + 1 ) * 900 - nsecs
            dt_when = dt_now + datetime.timedelta(seconds=delta)

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )


            # optimize
            result = self.optimization()

            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)


    def listen_mpc_control_update(self,event):
        result = self.control_update()







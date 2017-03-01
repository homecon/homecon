#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import numpy as np
import pyomo.environ as pyomo

from .. import core
from .. import util


class Mpc(core.plugin.Plugin):
    """
    Class defining the model predictive control strategy
    
    """

    def initialize(self):
        

        # schedule cross validation
        self._loop.create_task(self.schedule_control_update())
        self.horizon = 24*7*3600      # the prediction and control horizon in seconds
        self.timestep = 900           # the control timestep in seconds

        logging.debug('MPC plugin Initialized')



    def control_update(self):

        # state estimation



        # predictions gathering
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_end = datetime.datetime.utcnow()
        dt_ini = dt_end - datetime.timedelta(seconds=self.horizon)

        timestamp_end = int( (dt_end-dt_ref).total_seconds() )
        timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

        utcdatetime = [datetime.datetime.utcfromtimestamp(ts) for ts in range(timestamp_ini,timestamp_end,self.timestep)]
        timestamps = [int((dt-dt_ref).total_seconds()) for dt in utcdatetime]

        p_el = [0.250 for dt in utcdatetime]
        p_ng = [0.070 for dt in utcdatetime]


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
        model.i = pyomo.Set(initialize=range(len(timestamps)-1),doc='time index')
        model.timestamp = pyomo.Param(model.i,initialize={i:timestamps[i] for i in model.i})
        model.timestep[i] = pyomo.Param(model.i,initialize={i:timestamps[i+1]-timestamps[i] for i in model.i})

        model.p_el = pyomo.Param(model.i, initialize={i:p_el[i] for i in model.i})
        model.p_ng = pyomo.Param(model.i, initialize={i:p_el[i] for i in model.i})

        model.P_el_tot= pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0)
        model.P_ng_tot= pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0)

        # load constraints and variables from components
        for component in core.components:
            component.prepare_ocp_model(model)

        P_el_list = [attr for attr in dir(model) if attr.endswith('P_el')]
        P_ng_list = [attr for attr in dir(model) if attr.endswith('P_ng')]

        model.constr_P_el_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.P_el_tot[i] == sum(getattr(model,P)[i] for P in P_el_list))
        model.constr_P_el_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.P_ng_tot[i] == sum(getattr(model,P)[i] for P in P_ng_list))


        model.objective = pyomo.Objective(rule=lambda model: sum( model.p_el[i]*model.P_el_tot[i]*model.timestep[i] + model.p_ng[i]*model.P_ng_tot[i]*model.timestep[i] for i in model.i), sense=pyomo.minimize)


        # objective
        solver = pyomo.SolverFactory('ipopt')
        results = solver.solve(model, tee=True)  # FIXME should be done in a separate thread to not stop the event loop


        # pass control schedules to components
        for component in core.components:
            component.postprocess_ocp_model(model)


        return True





    async def schedule_optimization(self):
        """
        Schedule cross validation running once a week

        """

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = (dt_now + datetime.timedelta(minutes=15)).replace(second=0,microsecond=0)  # FIXME perform optimization at 0min,15min,30min and 45min past the hour

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )


            # optimize
            result = self.control_update()


            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)


    def listen_mpc_control_update(self,event):
        result = self.control_update()







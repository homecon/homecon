#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import numpy as np
import pyomo.environ as pyomo
import asyncio
import traceback

from .. import core
from .. import util


class Mpc(core.plugin.Plugin):
    """
    Class defining the model predictive control strategy
    
    """

    def initialize(self):
        

        self.horizon = 24*7*3600      # the prediction and control horizon in seconds
        self.timestep = 900           # the control timestep in seconds
        self.program_old = []


        # add program
        core.states.add('mpc/power/program',       config={'datatype': 'dict', 'quantity':'', 'unit':''  , 'label':'', 'description':'', 'log': False})
        core.states.add('mpc/building/program',     config={'datatype': 'dict', 'quantity':'', 'unit':''  , 'label':'', 'description':'', 'log': False})

        core.states.add('mpc/power/program_old',       config={'datatype': 'dict', 'quantity':'', 'unit':''  , 'label':'', 'description':'', 'log': False})
        core.states.add('mpc/building/program_old',     config={'datatype': 'dict', 'quantity':'', 'unit':''  , 'label':'', 'description':'', 'log': False})

        core.states.add('mpc/priceprofiles/el', value=[(25200,0.25),(79200,0.22),(111600,0.25),(165600,0.22),(198000,0.25),(252000,0.22),(284400,0.25),(338400,0.22),(370800,0.25),(424800,0.22)],    config={'datatype': 'list', 'quantity':'', 'unit':''  , 'label':'', 'description':'', 'log': False})
        core.states.add('mpc/priceprofiles/ng', value=[(0,0.080)],    config={'datatype': 'list', 'quantity':'', 'unit':''  , 'label':'', 'description':'', 'log': False})
        

        core.states.add('mpc/energy_cost_scale'                     , value=0.2  , config={'datatype': 'number', 'quantity':'', 'unit':'EUR/h'      ,'label':'', 'description':'Average energy cost per hour', 'private':True})
        
        core.states.add('mpc/relative_cost_discomfort_too_hot'      , value=10.  , config={'datatype': 'number', 'quantity':'', 'unit':'1/K'      ,'label':'', 'description':'A value of 1 means a temperature of 1 K above the setpoint during 1 h costs as much as the energy cost scale', 'private':True})
        core.states.add('mpc/relative_cost_discomfort_too_cold'     , value=11.  , config={'datatype': 'number', 'quantity':'', 'unit':'1/K'      ,'label':'', 'description':'A value of 1 means a temperature of 1 K below the setpoint during 1 h costs as much as the energy cost scale', 'private':True})
        core.states.add('mpc/relative_cost_discomfort_air_quality'  , value=0.   , config={'datatype': 'number', 'quantity':'', 'unit':'1/m2'      ,'label':'', 'description':'A value of 1 means 1 m2 of lost visibility during 1 h costs as much as the energy cost scale', 'private':True})
        core.states.add('mpc/relative_cost_discomfort_visual'       , value=1e-6 , config={'datatype': 'number', 'quantity':'', 'unit':'1/m2'      ,'label':'', 'description':'A value of 1 means 1 m2 of lost visibility during 1 h costs as much as the energy cost scale', 'private':True})



        # schedule cross validation
        optimization_task = asyncio.ensure_future(self.schedule_optimization())

        logging.info('MPC plugin Initialized')



    def optimization(self):

        """
        Optimal control problem naming conventions

        T_xxx: Temperature
        Q_xxx: Heat flow
        V_xxx: Volume flow
        xxx_P_el: Electrical power                     (W)
        xxx_P_ng: Natural gas power                    (W)
        xxx_D_tc: Discomfort thermal too cold          (K)
        xxx_D_th: Discomfort thermal too hot           (K)
        xxx_D_aq: Discomfort air quality        (g CO2/m3)?
        xxx_D_vi: Discomfort visual                   (m2)

        xxxx_p: price                              (EUR/xxx)
       
        """

        try:
            logging.debug('Starting the control optimization')

            # common data gathering
            dt_ini = datetime.datetime.utcnow()

            # make the optimization timesteps coincide with 0min, 15min, 30min, 45min
            nsecs = dt_ini.minute*60 + dt_ini.second + dt_ini.microsecond*1e-6
            delta = int( np.round( nsecs/900 ) * 900 - nsecs )
            timestamp_ini = util.time.timestamp(dt_ini)+delta

            timestamps = [ts for ts in range(timestamp_ini,timestamp_ini+self.horizon,self.timestep)]


            weatherforecast_timestamps = []
            weatherforecast_T_amb = []
            for i in range(24*7):
                weatherforecast_timestamps.append( core.states['weather/forecast/hourly/{}'.format(i)].value['timestamp'] )
                weatherforecast_T_amb.append( core.states['weather/forecast/hourly/{}'.format(i)].value['temperature'] )
                
            T_amb = np.interp(timestamps,weatherforecast_timestamps,weatherforecast_T_amb)

            timestamps_of_the_week = [util.time.timestamp_of_the_week(ts) for ts in timestamps]

            P_el_p = util.interp.zoh(timestamps_of_the_week,[val[0] for val in core.states['mpc/priceprofiles/el'].value],[val[1] for val in core.states['mpc/priceprofiles/el'].value],period=7*24*3600)
            P_ng_p = util.interp.zoh(timestamps_of_the_week,[val[0] for val in core.states['mpc/priceprofiles/ng'].value],[val[1] for val in core.states['mpc/priceprofiles/ng'].value],period=7*24*3600)


            # Discomfort costs
            D_tc_p = [core.states['mpc/relative_cost_discomfort_too_cold'].value*core.states['mpc/energy_cost_scale'].value for ts in timestamps]
            D_th_p = [core.states['mpc/relative_cost_discomfort_too_hot'].value*core.states['mpc/energy_cost_scale'].value for ts in timestamps]

            D_aq_p = [core.states['mpc/relative_cost_discomfort_air_quality'].value*core.states['mpc/energy_cost_scale'].value for ts in timestamps]
            D_vi_p = [core.states['mpc/relative_cost_discomfort_visual'].value*core.states['mpc/energy_cost_scale'].value for ts in timestamps]


            # control optimization
            model = pyomo.ConcreteModel()
            model.i = pyomo.Set(initialize=range(len(timestamps)-1), doc='time index, the last timestamp is not included (-)')
            model.ip = pyomo.Set(initialize=range(len(timestamps)), doc='time index, the last timestamp is included (-)')

            model.timestamp = pyomo.Param(model.ip,initialize={i:timestamps[i] for i in model.ip}, doc='timestamp (s)')
            model.timestep = pyomo.Param(model.i,initialize={i:timestamps[i+1]-timestamps[i] for i in model.i}, doc='timestep of the interval [i,i+1] (s)')


            model.T_amb = pyomo.Param(model.ip, initialize={i:T_amb[i] for i in model.ip}, doc='ambient temperature at timestep i (degC)')



            model.P_el_p = pyomo.Param(model.i, initialize={i:P_el_p[i] for i in model.i}, doc='electricity price (EUR/kWh)')
            model.P_ng_p = pyomo.Param(model.i, initialize={i:P_ng_p[i] for i in model.i}, doc='natural gas price (EUR/kWh)')

            model.D_tc_p = pyomo.Param(model.i, initialize={i:D_tc_p[i] for i in model.i}, doc='thermal discomfort too cold price (EUR/Kh)')
            model.D_th_p = pyomo.Param(model.i, initialize={i:D_th_p[i] for i in model.i}, doc='thermal discomfort too cold price (EUR/Kh)')
            model.D_aq_p = pyomo.Param(model.i, initialize={i:D_aq_p[i] for i in model.i}, doc='air quality discomfort(EUR/xxx)')
            model.D_vi_p = pyomo.Param(model.i, initialize={i:D_vi_p[i] for i in model.i}, doc='visual discomfort(EUR/xxx)')

            model.P_el_tot = pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0, doc='average electricity use in the interval [i,i+1] (W)')
            model.P_ng_tot = pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0, doc='average natural gas use in the interval [i,i+1] (W)')

            model.D_tc_tot = pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0, doc='average thermal discomfort too cold in the interval [i,i+1] (K)')
            model.D_th_tot = pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0, doc='average thermal discomfort too hot in the interval [i,i+1] (K)')
            model.D_aq_tot = pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0, doc='average air quality discomfort in the interval [i,i+1] (xxx)')
            model.D_vi_tot = pyomo.Var(model.i,domain=pyomo.NonNegativeReals, initialize=0, doc='average visual discomfort in the interval [i,i+1] (m2)')



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

            P_el_list = [attr for attr in dir(model) if attr.endswith('P_el') and not attr.startswith('constraint')]
            P_ng_list = [attr for attr in dir(model) if attr.endswith('P_ng') and not attr.startswith('constraint')]
            D_tc_list = [attr for attr in dir(model) if attr.endswith('D_tc') and not attr.startswith('constraint')]
            D_th_list = [attr for attr in dir(model) if attr.endswith('D_th') and not attr.startswith('constraint')]
            D_aq_list = [attr for attr in dir(model) if attr.endswith('D_aq') and not attr.startswith('constraint')]
            D_vi_list = [attr for attr in dir(model) if attr.endswith('D_vi') and not attr.startswith('constraint')]


            model.constraint_P_el_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.P_el_tot[i] == sum(getattr(model,var)[i] for var in P_el_list), doc='summing the total elctrical power demand')
            model.constraint_P_ng_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.P_ng_tot[i] == sum(getattr(model,var)[i] for var in P_ng_list), doc='summing the total natural gas power demand')
            
            model.constraint_D_tc_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.D_tc_tot[i] == sum(getattr(model,var)[i] for var in D_tc_list), doc='summing the total thermal discomfort too cold')
            model.constraint_D_th_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.D_th_tot[i] == sum(getattr(model,var)[i] for var in D_th_list), doc='summing the total thermal discomfort too hot')
            model.constraint_D_aq_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.D_aq_tot[i] == sum(getattr(model,var)[i] for var in D_aq_list), doc='summing the total air quality discomfort')
            model.constraint_D_vi_tot = pyomo.Constraint(model.i,rule=lambda model,i: model.D_vi_tot[i] == sum(getattr(model,var)[i] for var in D_vi_list), doc='summing the total visual discomfort')


            # add an objective
            model.objective = pyomo.Objective(sense=pyomo.minimize, rule=lambda model:
                sum( model.P_el_p[i]/1000*model.P_el_tot[i]*model.timestep[i]/3600 for i in model.i) 
              + sum( model.P_ng_p[i]/1000*model.P_ng_tot[i]*model.timestep[i]/3600 for i in model.i)
              + sum( model.D_tc_p[i]*model.D_tc_tot[i]*model.timestep[i]/3600 for i in model.i)
              + sum( model.D_th_p[i]*model.D_th_tot[i]*model.timestep[i]/3600 for i in model.i)
              + sum( model.D_aq_p[i]*model.D_aq_tot[i]*model.timestep[i]/3600 for i in model.i)
              + sum( model.D_vi_p[i]*model.D_vi_tot[i]*model.timestep[i]/3600 for i in model.i)
            )


            # solve
            # the problem contains integers
            solver = pyomo.SolverFactory('bonmin')  # FIXME should be done in a separate thread to not stop the event loop
            #util.executor.run_in_executor(solver.solve,model,tee=True)
            results = solver.solve(model, tee=True)
            logging.debug('OCP solved using BONMIN')


            # pass control program to plugins
            for plugin in core.plugins.values():
                plugin.postprocess_ocp(model)


            # pass control program to components
            for component in core.components.values():
                component.postprocess_ocp(model)


            # set states
            result = {}
            result['timestamp'] = [int(pyomo.value(model.timestamp[i])) for i in model.i]
            result['P_el'] = [float(np.round(pyomo.value(model.P_el_tot[i]),2)) for i in model.i]
            result['P_ng'] = [float(np.round(pyomo.value(model.P_ng_tot[i]),2)) for i in model.i]
            
            core.states['mpc/power/program'].value = result


            # set the old result
            result = {}
            result['timestamp'] = [int(pyomo.value(model.timestamp[i])) for i in model.i]
            result['old_P_el'] = [float(np.round(pyomo.value(model.P_el_tot[i]),2)) for i in model.i]
            result['old_P_ng'] = [float(np.round(pyomo.value(model.P_ng_tot[i]),2)) for i in model.i]
            
            self.program_old.append(result)
            if len(self.program_old) == 24*4:
                result_old = self.program_old.pop(0)
            else:
                result_old = self.program_old[0]

            core.states['mpc/power/program_old'].value = result_old

            return True

        except:
            logging.error('the control optimization failed with error:\n{}'.format(traceback.format_exc()))




    async def schedule_optimization(self):
        """
        Schedule cross validation running once a week

        """

        while True:
            await asyncio.sleep(30)  # run the optimization 30 seconds after the quarterhour

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


    def listen_mpc_optimization(self,event):
        result = self.optimization()







#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import datetime
import numpy as np
import pyomo.environ as pyomo

from ... import core
from ... import util

class Shading(core.plugin.Plugin):
    """
    Shading control

    """

    def initialize(self):


        # create the optimization model
        model = pyomo.AbstractModel()

        # sets
        model.windows = pyomo.Set(doc='set of windows in a zone')
        model.shadings = pyomo.Set(dimen=2,doc='array of sets of all shadings')

        # parameters
        model.area = pyomo.Param(model.windows, doc='window area')
        model.solargain_max = pyomo.Param(model.windows, doc='window solargain without shading')
        model.solargain_set = pyomo.Param(doc='zone solargain setpoint')

        model.relativeposition_min = pyomo.Param(model.shadings, doc='minimum shading position, most open')
        model.relativeposition_max = pyomo.Param(model.shadings, doc='maximum shading position, most closed')
        model.relativeposition_old = pyomo.Param(model.shadings, doc='previous shading position')

        model.transmittance_open = pyomo.Param(model.shadings, doc='open shading transmittance')
        model.transmittance_closed = pyomo.Param(model.shadings, doc='closed shading transmittance')

        model.cost_solargain = pyomo.Param(doc='cost for deviation from the setpoint')
        model.cost_visibility = pyomo.Param(model.windows, doc='cost for degradation of visibility')
        model.cost_movement = pyomo.Param(model.shadings, doc='cost for movement')


        # variables
        model.relativeposition = pyomo.Var(model.shadings, domain=pyomo.NonNegativeReals, bounds=lambda model,w,s:(model.relativeposition_min[w,s],model.relativeposition_max[w,s]), doc='current shading position 0 is open 1 is closed')
        model.solargain = pyomo.Var(domain=pyomo.NonNegativeReals, doc='zone solargain')
        model.solargain_delta = pyomo.Var(domain=pyomo.NonNegativeReals, doc='absolute value of the difference from the setpoint')
        model.relativeposition_delta = pyomo.Var(model.shadings, domain=pyomo.NonNegativeReals, doc='absolute value of the difference from the current and old position')


        # constraints
        model.constraint_solargain = pyomo.Constraint(
            rule=lambda model: model.solargain == sum(model.solargain_max[w]*pyomo.prod((1-model.relativeposition[ww,s])*model.transmittance_open[ww,s] + (model.relativeposition[ww,s])*model.transmittance_closed[ww,s] for ww,s in model.shadings if w==ww) for w in model.windows)
        )

        model.constraint_solargain_delta_pos = pyomo.Constraint(
            rule=lambda model: model.solargain_delta >= model.solargain-model.solargain_set
        )
        model.constraint_solargain_delta_neg = pyomo.Constraint(
            rule=lambda model: model.solargain_delta >= model.solargain_set-model.solargain
        )

        model.constraint_position_delta_pos = pyomo.Constraint(model.shadings,
            rule=lambda model,w,s: model.relativeposition_delta[w,s] >= model.relativeposition[w,s]-model.relativeposition_old[w,s]
        )
        model.constraint_position_delta_neg = pyomo.Constraint(model.shadings,
            rule=lambda model,w,s: model.relativeposition_delta[w,s] >= model.relativeposition_old[w,s]-model.relativeposition[w,s]
        )

        # objective
        model.Objective = pyomo.Objective(
            rule=lambda model: model.solargain_delta*model.cost_solargain + sum(model.area[w]*pyomo.prod(model.relativeposition[ww,s] for ww,s in model.shadings if w == ww)*model.cost_visibility[w] for w in model.windows) + sum(model.relativeposition_delta[s]*model.cost_movement[s] for s in model.shadings)
        )

        self.model = model


        self._loop.create_task(self.schedule_auto_position())

        logging.info('Shading plugin Initialized')
    

    async def schedule_auto_position(self):
        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = dt_now + datetime.timedelta(minutes=1)

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )


            self.auto_position()
            await asyncio.sleep(timestamp_when-timestamp_now)


    def auto_position(self):
        """
        
        """

        # get all windows and zones
        zones = core.components.find(type='zone')
        windows = core.components.find(type='window')



        relativeposition_min = {}
        relativeposition_max = {}
        relativeposition_old = {}
        relativeposition_new = {}
        solargain_max = {}
        solargain_temp = {}


        for w in windows:

            shadings = core.components.find(type='shading', window=w.path)
            for s in shadings:

                position_min_temp = (s.config['position_open'] if s.states['position_min'].value is None else s.states['position_min'].value) if ( (s.states['override'].value is None or s.states['override'].value<=0) and s.states['auto'].value) else s.states['position_status'].value
                position_max_temp = (s.config['position_closed'] if s.states['position_max'].value is None else s.states['position_max'].value) if ( (s.states['override'].value is None or s.states['override'].value<=0) and s.states['auto'].value) else s.states['position_status'].value

                relativeposition_min_temp = s.calculate_relative_position( position=position_min_temp )
                relativeposition_max_temp = s.calculate_relative_position( position=position_max_temp )

                # it is not sure that min is closed and max is open
                # the relative position is defined so 0 is open and 1 is closed
                relativeposition_min[(w.path,s.path)] = min(relativeposition_min_temp,relativeposition_max_temp)
                relativeposition_max[(w.path,s.path)] = max(relativeposition_min_temp,relativeposition_max_temp)

                relativeposition_old[(w.path,s.path)] = s.calculate_relative_position( position=s.states['position_status'].value )
            
            solargain_max[w.path]  = w.calculate_solargain(shading_relativeposition=[0 for s in shadings])
            solargain_temp[w.path] = w.calculate_solargain(shading_relativeposition=[relativeposition_old[(w.path,s.path)] for s in shadings])

        print('')

        print(relativeposition_old)
        print(solargain_max)
        print(solargain_temp)

        # get the current timestamp
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        timestamp_now = int( (dt_now-dt_ref).total_seconds() )


        for zone in zones:

            windows = core.components.find(type='window', zone=zone.path)
            shadings = {w.path: core.components.find(type='shading', window=w.path) for w in windows}

            if len(windows)>0:

                solargain_max_zone = sum([solargain_max[w.path] for w in windows])
                solargain_temp_zone = sum([solargain_temp[w.path] for w in windows])

                solargain_program = zone.states['solargain_program'].value

                if solargain_program is None or timestamp_now > solargain_program[-1][0]:
                    logging.warning('No solargain setpoint')
                    solargain_set = solargain_max_zone
                else:
                    solargain_set = np.interp(timestamp_now, [val[0] for val in solargain_program], [val[1] for val in solargain_program])

                solargain_tol = np.maximum(200,0.1*solargain_set)



                print('')
                print(zone.path)
                print(sum([solargain_max[w.path] for w in windows]))
                print(solargain_set)
                print(solargain_tol)
                print(solargain_temp_zone)
                print('')

                # check if repositioning is required / allowed
                outsidetolerance = abs(solargain_temp_zone-solargain_set) > solargain_tol
                belowtolerance = (solargain_max_zone < solargain_tol and sum(relativeposition_old[(w.path,s.path)] if relativeposition_min[(w.path,s.path)]<relativeposition_max[(w.path,s.path)] else 0 for w in windows for s in shadings[w.path] )>1e-3)
                c3 = False

                if outsidetolerance or belowtolerance or c3:

                    # compute new shading positions through the optimization
                    data={None:{
                        'windows':{None: tuple([w.path for w in windows])},
                        'shadings': {None: tuple([(w.path,s.path) for w in windows for s in shadings[w.path]])},
                        'area':{(w.path,): w.config['area'] for w in windows},
                        'solargain_max':{(w.path,): solargain_max[w.path] for w in windows},
                        'solargain_set':{None: solargain_set},
                        'relativeposition_min':{(w.path,s.path): relativeposition_min[(w.path,s.path)] for w in windows for s in shadings[w.path]},
                        'relativeposition_max':{(w.path,s.path): relativeposition_max[(w.path,s.path)] for w in windows for s in shadings[w.path]},
                        'relativeposition_old':{(w.path,s.path): relativeposition_old[(w.path,s.path)] for w in windows for s in shadings[w.path]},
                        'transmittance_open':{(w.path,s.path): s.config['transmittance_open'] for w in windows for s in shadings[w.path]},
                        'transmittance_closed':{(w.path,s.path): s.config['transmittance_closed'] for w in windows for s in shadings[w.path]},
                        'cost_solargain':{None: 1.},
                        'cost_visibility':{(w.path,): 0.1*w.config['cost_visibility'] for w in windows},
                        'cost_movement':{(w.path,s.path): 1.0*s.config['cost_movement'] for w in windows for s in shadings[w.path]},
                    }}

                    # Create a problem instance and solve
                    instance = self.model.create_instance(data)
                    optimizer = pyomo.SolverFactory('ipopt')
                    results = optimizer.solve(instance,tee=True)
                    print(results)

                    logging.info('Recalculated shading positions for zone {}'.format(zone.path))


                    # Retrieve the results
                    for w in windows:
                        for s in shadings[w.path]:
                            if ((s.states['override'].value is None or not s.states['override'].value>0) and s.states['auto'].value):

                                if belowtolerance:
                                    relativeposition_new[(w.path,s.path)] = 0
                                else:                                
                                    relativeposition_new[(w.path,s.path)] = pyomo.value(instance.relativeposition[(w.path,s.path)])


        # set positions
        windows = core.components.find(type='window')
        for w in windows:

            shadings = core.components.find(type='shading', window=w.path)
            for s in shadings:

                if not (w.path,s.path) in relativeposition_new:
                    relativeposition_new[(w.path,s.path)] = min(relativeposition_max[(w.path,s.path)],max(relativeposition_min[(w.path,s.path)],relativeposition_old[(w.path,s.path)]))


                position = s.config['position_open']*(1-relativeposition_new[(w.path,s.path)]) + s.config['position_closed']*(relativeposition_new[(w.path,s.path)])
                s.states['position'].set(position,source=self)


        # update override
        for s in core.components.find(type='shading'):
            if s.states['override'].value is None:
                s.states['override'].value = 0

            if not s.states['override'].value is None and s.states['override'].value > 0:
                s.states['override'].value = s.states['override'].value-1



    def listen_state_changed(self,event):
        state = event.data['state']

        if 'component' in state.config:
            component = core.components[state.config['component']]
            if component.type == 'shading' and not event.source == self and state == component.states['position'] and component.states['auto']:
                component.states['override'].value = component.config['override_duration']
                logging.info('Enabled override for shading {}'.format(component.path))


            if component.type == 'shading' and ( state == component.states['auto'] or state == component.states['position_min'] or state == component.states['position_max'] or (state == component.states['override'] and state.value<=0) ):
                util.executor.debounce(5,self.auto_position)





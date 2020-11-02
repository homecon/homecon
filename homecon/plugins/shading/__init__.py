#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time
import datetime

import numpy as np
import pyomo.environ as pyomo

from homecon.core.plugins.plugin import Plugin
from homecon.core.states.state import State
from homecon.util.executor import debounce

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

logger = logging.getLogger(__name__)


class Shading(Plugin):
    """
    Shading control

    """

    ZONE_STATE_TYPE = 'zone'
    WINDOW_STATE_TYPE = 'window'
    SHUTTER_STATE_TYPES = ['shading', 'shutter', 'screen']
    BLIND_STATE_TYPES = ['blinds']

    SOLVER = 'cbc'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.solar_gain_tol_min = 200  # W

        # create the optimization model
        model = pyomo.AbstractModel()

        # sets
        model.windows = pyomo.Set(doc='set of windows in a zone')
        model.shadings = pyomo.Set(dimen=2, doc='array of sets of all shadings')

        # parameters
        model.area = pyomo.Param(model.windows, doc='window area')
        model.solar_gain_max = pyomo.Param(model.windows, doc='window solar_gain without shading')
        model.solar_gain_set = pyomo.Param(doc='zone solar_gain setpoint')

        model.relative_position_min = pyomo.Param(model.shadings, doc='minimum shading position, most open')
        model.relative_position_max = pyomo.Param(model.shadings, doc='maximum shading position, most closed')
        model.relative_position_old = pyomo.Param(model.shadings, doc='previous shading position')

        model.transmittance_open = pyomo.Param(model.shadings, doc='open shading transmittance')
        model.transmittance_closed = pyomo.Param(model.shadings, doc='closed shading transmittance')

        model.cost_solar_gain = pyomo.Param(doc='cost for difference from the solar_gain setpoint (EUR/W)')
        model.cost_visibility = pyomo.Param(model.windows, doc='cost for degradation of visibility (EUR/m2)')
        model.cost_movement = pyomo.Param(model.shadings, doc='cost for movement (EUR/relative position)')

        # variables
        model.relative_position = pyomo.Var(
            model.shadings, domain=pyomo.NonNegativeReals,
            bounds=lambda m, w, s: (m.relative_position_min[w, s], m.relative_position_max[w, s]),
            doc='current shading position 0 is open 1 is closed')
        model.solar_gain = pyomo.Var(domain=pyomo.NonNegativeReals, doc='zone solar_gain')
        model.solar_gain_delta = pyomo.Var(domain=pyomo.NonNegativeReals,
                                           doc='absolute value of the difference from the setpoint')
        model.relative_position_delta = pyomo.Var(
            model.shadings, domain=pyomo.NonNegativeReals,
            doc='absolute value of the difference from the current and old position')

        # constraints
        model.constraint_solar_gain = pyomo.Constraint(
            rule=lambda m: m.solar_gain ==
            sum([m.solar_gain_max[w]*pyomo.prod([(1-m.relative_position[ww, s])*m.transmittance_open[ww, s] +
                                                 (m.relative_position[ww, s])*m.transmittance_closed[ww, s]
                                                 for ww, s in m.shadings if w == ww]) for w in m.windows])
        )

        model.constraint_solar_gain_delta_pos = pyomo.Constraint(
            rule=lambda m: m.solar_gain_delta >= m.solar_gain - m.solar_gain_set
        )
        model.constraint_solar_gain_delta_neg = pyomo.Constraint(
            rule=lambda m: m.solar_gain_delta >= m.solar_gain_set - m.solar_gain
        )

        model.constraint_position_delta_pos = pyomo.Constraint(
            model.shadings,
            rule=lambda m, w, s: m.relative_position_delta[w, s] >=
            m.relative_position[w, s]-m.relative_position_old[w, s]
        )
        model.constraint_position_delta_neg = pyomo.Constraint(
            model.shadings,
            rule=lambda m, w, s: m.relative_position_delta[w, s] >=
            m.relative_position_old[w, s]-m.relative_position[w, s]
        )

        # objective
        model.Objective = pyomo.Objective(
            rule=lambda m: m.cost_solar_gain*m.solar_gain_delta +
            sum(m.area[w]*pyomo.prod(m.relative_position[ww, s]
                                     for ww, s in m.shadings if w == ww)*m.cost_visibility[w] for w in m.windows) +
            sum(m.relative_position_delta[s]*m.cost_movement[s] for s in m.shadings)
        )
        self.model = model
        self.scheduler = BackgroundScheduler()

    def initialize(self):
        self.scheduler.add_job(self.auto_position(), trigger='interval', seconds=60, id='auto_position')
        self.scheduler.start()
        logging.info('Shading plugin Initialized')

    @property
    def timezone(self):
        return State.get('/settings/location/timezone').value

    def get_override_state(self, shading):
        for s in shading.children:
            if s.name == 'override':
                return s

    def get_auto_state(self, shading):
        for s in shading.children:
            if s.name == 'auto':
                return s

    def get_position_state(self, shading):
        for s in shading.children:
            if s.name == 'position':
                return s

    def get_position_min_state(self, shading):
        for s in shading.children:
            if s.name == 'position_min':
                return s

    def get_position_max_state(self, shading):
        for s in shading.children:
            if s.name == 'position_max':
                return s

    def get_relative_position(self, shading):
        position = self.get_position_state(shading)
        if position is not None:
            return self.position_to_relative_position(shading, position.value or 0)
        else:
            return self.position_to_relative_position(shading, shading.config.get('position_open', 0))

    def get_relative_position_min(self, shading):
        position = self.get_position_min_state(shading)
        if position is not None:
            return self.position_to_relative_position(shading, position.value or 0)
        else:
            return self.position_to_relative_position(shading, shading.config.get('position_open', 0))

    def get_relative_position_max(self, shading):
        position = self.get_position_max_state(shading)
        if position is not None:
            return self.position_to_relative_position(shading, position.value or 0)
        else:
            return self.position_to_relative_position(shading, shading.config.get('position_closed', 1))

    def position_to_relative_position(self, shading, position):
        return (position - shading.config.get('position_open', 0)) / \
               (shading.config.get('position_closed', 1) - shading.config.get('position_open', 0))

    def relative_position_to_position(self, shading, relative_position):
        return shading.config.get('position_open', 0) * (1 - relative_position) + \
               shading.config.get('position_closed', 1) * (relative_position)

    def calculate_solar_gain(self, window, shading_relative_position):
        return 0

    def auto_position(self, force_recalculate=False):
        """
        
        """

        # get all windows and zones
        zones = [s for s in State.all() if s.type == self.ZONE_STATE_TYPE]
        shadings = [s for s in State.all() if s.type in self.SHUTTER_STATE_TYPES + self.BLIND_STATE_TYPES]
        windows = [s for s in State.all() if s.type in self.WINDOW_STATE_TYPE]
        window_shadings = {w.id:  [s for s in shadings if s.config.get('window') == w.id] for w in windows}

        relative_position_min = {}
        relative_position_max = {}
        relative_position_old = {}
        relative_position_new = {}
        solar_gain_max = {}
        solar_gain_min = {}
        solar_gain_old = {}

        for w in windows:
            for s in window_shadings[w.id]:
                relative_position_min[(w.id, s.id)] = self.get_relative_position_min(s)
                relative_position_max[(w.id, s.id)] = self.get_relative_position_max(s)
                relative_position_old[(w.id, s.id)] = self.get_relative_position(s)
            
            solar_gain_max[w.id] = self.calculate_solar_gain(w, shading_relative_position=[(s, 0) for s in shadings])
            solar_gain_min[w.id] = self.calculate_solar_gain(w, shading_relative_position=[(s, 1) for s in shadings])
            solar_gain_old[w.id] = self.calculate_solar_gain(
                w, shading_relative_position=[relative_position_old[(w.id, s.id)] for s in window_shadings[w.id]])

        # get the current timestamp
        timestamp_now = int(time.time())

        for zone in zones:
            zone_windows = [w for w in windows if w.config.get('zone') == zone.id]
            if len(zone_windows) == 0:
                continue

            zone_shadings = {w.id: window_shadings[w.id] for w in windows}

            solar_gain_max_zone = sum([solar_gain_max[w.id] for w in windows])
            solar_gain_min_zone = sum([solar_gain_min[w.id] for w in windows])
            solar_gain_old_zone = sum([solar_gain_old[w.id] for w in windows])

            # solar_gain_program = zone.states['solar_gain_program'].value
            solar_gain_program = None  # FIXME

            if solar_gain_program is None or timestamp_now > solar_gain_program[-1][0]:
                logger.warning('No solar_gain setpoint')
                solar_gain_set = solar_gain_max_zone
            else:
                solar_gain_set = np.interp(timestamp_now,
                                           [val[0] for val in solar_gain_program],
                                           [val[1] for val in solar_gain_program])

            solar_gain_set = 0.8*solar_gain_max_zone  # FIXME

            solar_gain_tol = max([self.solar_gain_tol_min, 0.1*solar_gain_set])

            logger.debug('Shading position quantities for zone {}: '
                         'max={:.0f} W, min={:.0f} W, set={:.0f} W, tol={:.0f} W, current={:.0f} W'
                         .format(zone.path, solar_gain_max_zone, solar_gain_min_zone,
                                 solar_gain_set, solar_gain_tol, solar_gain_old_zone))

            # check if repositioning is required / allowed
            outside_tolerance = abs(solar_gain_old_zone-solar_gain_set) > solar_gain_tol
            below_tolerance = (
                    solar_gain_max_zone < solar_gain_tol and
                    sum(relative_position_old[(w.id, s.id)]
                        if relative_position_min[(w.id, s.id)] < relative_position_max[(w.id, s.id)]
                        else 0 for w in zone_windows for s in zone_shadings[w.id]) > 1e-3)

            if outside_tolerance or below_tolerance or force_recalculate:

                # compute new shading positions through the optimization
                data = {None: {
                    'windows': {None: [w.id for w in zone_windows]},
                    'shadings': {None: [(w.id, s.id) for w in zone_windows for s in zone_shadings[w.id]]},
                    'area': {(w.id,): w.config.get('area', 1) for w in zone_windows},
                    'solar_gain_max': {(w.id,): solar_gain_max[w.id] for w in zone_windows},
                    'solar_gain_set': {None: solar_gain_set},
                    'relative_position_min': {(w.id, s.id): relative_position_min[(w.id, s.id)]
                                              for w in zone_windows for s in zone_shadings[w.id]},
                    'relative_position_max': {(w.id, s.id): relative_position_max[(w.id, s.id)]
                                              for w in zone_windows for s in zone_shadings[w.id]},
                    'relative_position_old': {(w.id, s.id): relative_position_old[(w.id, s.id)]
                                              for w in zone_windows for s in zone_shadings[w.id]},
                    'transmittance_open': {(w.id, s.id): s.config.get('transmittance_open', 1)
                                           for w in zone_windows for s in zone_shadings[w.id]},
                    'transmittance_closed': {(w.id, s.id): s.config.get('transmittance_closed', 0)
                                             for w in zone_windows for s in zone_shadings[w.id]},
                    'cost_solar_gain': {None: 1.},
                    'cost_visibility': {(w.id,): w.config.get('cost_visibility', 0.1) for w in zone_windows},
                    'cost_movement': {(w.id, s.id): s.config.get('cost_movement', 0.1)
                                      for w in zone_windows for s in zone_shadings[w.id]},
                }}

                # create a problem instance and solve
                instance = self.model.create_instance(data)
                optimizer = pyomo.SolverFactory(self.SOLVER)
                results = optimizer.solve(instance, tee=True)
                print(results)

                logger.info('Recalculated shading positions for zone {}'.format(zone.path))

                # retrieve the results
                for w in zone_windows:
                    for s in zone_shadings[w.id]:
                        override_state = self.get_override_state(s)
                        auto_state = self.get_auto_state(s)

                        if auto_state is not None and auto_state.value and \
                                (override_state is None or not override_state.value):
                            if below_tolerance:
                                relative_position_new[(w.id, s.id)] = 0
                            else:
                                relative_position_new[(w.id, s.id)] = np.round(
                                    pyomo.value(instance.relative_position[(w.id, s.id)]), 1)

        # set positions
        for w in windows:
            for s in window_shadings[w.id]:
                if not (w.id, s.id) in relative_position_new:
                    relative_position_new[(w.id, s.id)] = min(
                        relative_position_max[(w.id, s.id)],
                        max(relative_position_min[(w.id, s.id)], relative_position_old[(w.id, s.id)])
                    )

                position = self.relative_position_to_position(s, relative_position_new[(w.id, s.id)])
                position_state = self.get_position_state(s)
                position_state.set_value(position, source=str(self))

    def get_reset_override_job_id(self, state):
        return 'reset_override#{}'.format(state.id)

    def update_override(self, interval=60):
        shadings = [s for s in State.all() if s.type in self.SHUTTER_STATE_TYPES + self.BLIND_STATE_TYPES]
        for s in shadings:
            override_state = self.get_override_state(s)
            value = override_state.value
            if value > 0:
                override_state.set_value(max(0, value - interval), source=str(self))

    def listen_state_added(self, event):
        state = event.data['state']
        if state.type in self.SHUTTER_STATE_TYPES:
            # add additional states
            State.add('position', parent=state, type='float', config={'shading': state.id})
            State.add('position_min', parent=state, type='float', value=0, config={'shading': state.id})
            State.add('position_max', parent=state, type='float', value=1, config={'shading': state.id})
            State.add('auto', parent=state, type='bool', value=True, config={'shading': state.id})
            State.add('override', parent=state, type='bool', value=True, config={'shading': state.id,
                                                                                 'duration': 4*3600})

        elif state.type in self.BLIND_STATE_TYPES:
            State.add('override', parent=state, type='int', value=True, config={'shading': state.id,
                                                                                'duration': 4*3600})

    def set_reset_override_schedule(self, state):
        def reset_override():
            state.set_value(False, source=str(self))

        job = self.scheduler.get_job(self.get_reset_override_job_id(state))
        run_date = datetime.datetime.fromtimestamp(time.time() + state.config['duration'], tz=self.timezone)

        if job is None:
            self.scheduler.add_job(reset_override, trigger='date',
                                   run_date=run_date,
                                   timezone=self.timezone,
                                   id=self.get_reset_override_job_id(state))
            logger.debug('added reset override schedule for {} to reset at {}'
                         .format(state, run_date.strftime('%Y-%m-%d %H:%M:%S')))
        else:
            job.modify(func=reset_override, trigger=DateTrigger(
                run_date=datetime.datetime.fromtimestamp(time.time() + state.config['duration'])))
            logger.debug('added reset override schedule for {} to reset at {}'
                         .format(state, run_date.strftime('%Y-%m-%d %H:%M:%S')))

    def remove_reset_override_schedule(self, state):
        try:
            self.scheduler.remove_job(self.get_reset_override_job_id(state))
            logger.debug('removed reset override schedule for {}')
        except:
            logger.exception('job not found: {}'.format(self.get_reset_override_job_id(state)))

    def listen_state_value_changed(self, event):
        state = event.data['state']

        if event.source == str(self):
            return

        if state.name == 'position' and state.parent.type in self.SHUTTER_STATE_TYPES + self.BLIND_STATE_TYPES:
            override_state = self.get_override_state(state.parent)
            if override_state is not None:
                state.set_value(True, source=str(self))
                logger.debug('set override {} for shading {}'.format(override_state, state))
                self.set_reset_override_schedule(override_state)

        elif state.name == 'override' and state.parent.type in self.SHUTTER_STATE_TYPES + self.BLIND_STATE_TYPES:
            if state.value:
                self.set_reset_override_schedule(state)
            else:
                self.remove_reset_override_schedule(state)

        elif state.name in ['position_min', 'position_max', 'auto', 'override'] and \
                state.parent.type in self.SHUTTER_STATE_TYPES:
            debounce(5, self.auto_position)

    def listen_stop_plugin(self, event):
        super().listen_stop_plugin(event)
        self.scheduler.shutdown(wait=False)

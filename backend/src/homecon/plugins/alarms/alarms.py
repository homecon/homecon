#!/usr/bin/env python3

import logging
import time
from typing import List, Any
from uuid import uuid4
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger

from homecon.core.event import Event
from homecon.core.states.state import State, IStateManager
from homecon.core.plugins.plugin import BasePlugin


logger = logging.getLogger(__name__)


class StateAction:
    def __init__(self, states: List[State], value: Any, delay: int = 0):
        self.states = states
        self.value = value
        self.delay = delay

    def execute(self, source=''):

        def func(delay=0):
            time.sleep(delay)
            for s in self.states:
                logger.debug(f'setting {s} to {self.value} from {source}')
                s.set_value(self.value)

        if self.delay > 0:
            Thread(target=func, kwargs={'delay': self.delay}).start()
        else:
            func()


class Action:
    STATE_TYPE = 'action'

    def __init__(self, state_actions: List[StateAction]):
        self._state_actions = state_actions

    def execute(self, source=''):
        logger.debug('executing action')
        for action in self._state_actions:
            action.execute(source=source)

    @classmethod
    def from_state(cls, state: State, state_manager: IStateManager):
        assert state.type == cls.STATE_TYPE

        state_actions = []
        for v in state.value:

            if isinstance(v['state'], int):
                states = [state_manager.get(id=v['state'])]
            else:
                states = state_manager.find(v['state'])

            delay = v.get('delay', 0)
            value = v['value']
            state_actions.append(StateAction(states, value, delay=delay))
        return cls(state_actions)


class Alarms(BasePlugin):
    """
    Class to control the HomeCon scheduler

    """

    ALARM_STATE_TYPE = 'alarm'
    ACTION_STATE_TYPE = Action.STATE_TYPE

    DEFAULT_TIMEZONE = 'utc'
    TIMEZONE_STATE_PATH = '/settings/location/timezone'

    def __init__(self, *args, timezone=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.scheduler = None
        self._timezone = timezone

    def start(self):
        executors = {
            'default': ThreadPoolExecutor(5),
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 3,
            'misfire_grace_time': 3600
        }
        self.scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)

        # add existing jobs
        for state in self._state_manager.all():
            if state.type == self.ALARM_STATE_TYPE:
                self.update_job(state)

        self.scheduler.start()
        logger.debug('Scheduler plugin Initialized')

    def stop(self):
        super().stop()
        self.scheduler.shutdown(wait=False)

    @property
    def timezone(self):
        if self._timezone is not None:
            return self._timezone
        state = self._state_manager.get(self.TIMEZONE_STATE_PATH)
        if state is None:
            return self.DEFAULT_TIMEZONE
        return state.value or self.DEFAULT_TIMEZONE

    @staticmethod
    def get_job_id(state: State):
        return 'state#{}'.format(state.id)

    def update_job(self, state):
        if 'trigger' not in state.value or 'action' not in state.value:
            logger.exception('trigger and action must be included in the state value')
            return

        if state.value['action'] is not None:
            def func():
                logger.debug('executing scheduler {}'.format(state))
                action_state = self._state_manager.get(id=state.value['action'])
                action = Action.from_state(action_state, self._state_manager)
                action.execute(source=f'schedule {state}')

            job = self.scheduler.get_job(self.get_job_id(state))
            if job is None:
                logger.debug('adding scheduler job for {}'.format(state))
                self.scheduler.add_job(func, trigger='cron', **state.value['trigger'], timezone=self.timezone,
                                       id=self.get_job_id(state))
            else:
                logger.debug('updating scheduler job for {}'.format(state))
                job.modify(func=func)
                job.reschedule(CronTrigger(**state.value['trigger']))
        else:
            job = self.scheduler.get_job(self.get_job_id(state))
            if job is not None:
                self.scheduler.remove_job(self.get_job_id(state))

    def delete_job(self, state: State):
        if state.type == self.ALARM_STATE_TYPE:
            job_id = self.get_job_id(state)
            job = self.scheduler.get_job(job_id)
            if job is not None:
                self.scheduler.remove_job(job_id)
        else:
            logger.warning('state {} is not a schedule'.format(state))

    def listen_state_value_changed(self, event: Event):
        state = event.data['state']
        if state.type == self.ALARM_STATE_TYPE:
            self.update_job(state)

    def listen_state_added(self, event: Event):
        state = event.data['state']
        if state.type == self.ALARM_STATE_TYPE:
            self.update_job(state)

    def listen_state_deleted(self, event: Event):
        state = event.data['state']
        if state.type == self.ALARM_STATE_TYPE:
            self.delete_job(state)

    def listen_add_schedule(self, event: Event):
        if 'id' in event.data:
            state = self._state_manager.get(id=event.data['id'])
            if state is not None:
                default_schedule_value = {
                    'trigger': {'hour': '0', 'minute': '0', 'day_of_week': '0,1,2,3,4'},
                    'action': None
                }
                self._state_manager.add(name=str(uuid4()), parent=state,
                                        type=self.ALARM_STATE_TYPE, value=default_schedule_value)

    def listen_delete_schedule(self, event: Event):
        if 'id' in event.data:
            state = self._state_manager.get(id=event.data['id'])
            if state is not None:
                if state.type == self.ALARM_STATE_TYPE:
                    self._state_manager.delete(state)
                else:
                    logger.error(f'state {state} is not an alarm')
            else:
                logger.error('no state')

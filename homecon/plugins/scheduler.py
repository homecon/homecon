#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from uuid import uuid4
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger

from homecon.core.event import Event
from homecon.core.state import State
from homecon.core.plugin import Plugin


logger = logging.getLogger(__name__)


class Scheduler(Plugin):
    """
    Class to control the HomeCon scheduler

    """

    SCHEDULE_STATE_TYPE = 'schedule'
    ACTION_STATE_TYPE = 'action'

    def __init__(self):
        super().__init__()
        self.scheduler = None

    def initialize(self):
        executors = {
            'default': ThreadPoolExecutor(20),
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        self.scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)

        # add existing jobs
        for state in State.all():
            if state.type == self.SCHEDULE_STATE_TYPE:
                self.update_job(state)

        # start the scheduler
        self.scheduler.start()

        logger.debug('Scheduler plugin Initialized')

    @property
    def timezone(self):
        return State.get('/settings/location/timezone').value

    @staticmethod
    def get_job_id(state):
        return 'state#{}'.format(state.id)

    def update_job(self, state):
        if 'trigger' not in state.value or 'action' not in state.value:
            logger.exception('trigger and action must be included in the state value')
            return

        if state.value['action'] is not None:
            def func():
                logger.debug('executing scheduler {}'.format(state))
                action = State.get(id=state.value['action'])
                assert action.type == self.ACTION_STATE_TYPE

                for v in action.value:
                    d = v.get('delay', 0)
                    if d > 0:
                        def e():
                            s = State.get(id=v['state'])
                            time.sleep(d)
                            logger.debug('setting {} to {} from schedule {}'.format(s, v['value'], state))
                            s.set_value(v['value'], source='Scheduler')

                        Thread(target=e).start()
                    else:
                        s = State.get(id=v['state'])
                        logger.debug('setting {} to {} from schedule {}'.format(s, v['value'], state))
                        s.set_value(v['value'], source='Scheduler')

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

    def delete_job(self, state):
        if state.type == self.SCHEDULE_STATE_TYPE:
            parent = state.parent
            job_id = self.get_job_id(state)
            job = self.scheduler.get_job(job_id)
            if job is not None:
                self.scheduler.remove_job(job_id)
            self.broadcast_list_schedules(parent)
        else:
            logger.warning('state {} is not a schedule'.format(state))

    def broadcast_list_schedules(self, state):
        logger.debug(state)
        if state is not None:
            Event.fire('websocket_send', {
                'event': 'list_schedules',
                'data': {
                    'id': state.id,
                    'value': [s.serialize() for s in state.children if s.type == self.SCHEDULE_STATE_TYPE]
                }
            })

    def broadcast_list_actions(self, state):
        logger.debug(state)
        if state is not None:
            Event.fire('websocket_send', {
                'event': 'list_actions',
                'data': {
                    'id': state.id,
                    'value': [s.serialize() for s in state.children if s.type == self.ACTION_STATE_TYPE]
                }
            })

    def listen_state_value_changed(self, event):
        state = event.data['state']
        if state.type == self.SCHEDULE_STATE_TYPE:
            self.update_job(state)

    def listen_state_added(self, event):
        state = event.data['state']
        if state.type == self.SCHEDULE_STATE_TYPE:
            self.update_job(state)
            parent = state.parent
            self.broadcast_list_schedules(parent)

    def listen_state_deleted(self, event):
        state = event.data['state']
        if state.type == self.SCHEDULE_STATE_TYPE:
            self.delete_job(state)

    def listen_list_schedules(self, event):
        if 'id' in event.data:
            state = State.get(id=event.data['id'])
            event.reply({'id': event.data['id'],
                         'value': [s.serialize() for s in state.children if s.type == self.SCHEDULE_STATE_TYPE]})

    def listen_add_schedule(self, event):
        if 'id' in event.data:
            state = State.get(id=event.data['id'])
            if state is not None:
                default_schedule_value = {
                    'trigger': {'hour': '0', 'minute': '0', 'day_of_week': '0,1,2,3,4'},
                    'action': None
                }
                State.add(name=str(uuid4()), parent=state, type=self.SCHEDULE_STATE_TYPE, value=default_schedule_value)

    def listen_delete_schedule(self, event):
        if 'id' in event.data:
            # FIXME use the State api here instead of an event as events might require permissions
            # state = State.get(id=event.data['id'])
            # self.delete_job(state)
            Event.fire('state_delete', event.data, source=event.source)

    def listen_list_actions(self, event):
        if 'id' in event.data:
            state = State.get(id=event.data['id'])
            if state is not None:
                actions = [s.serialize() for s in state.children if s.type == self.ACTION_STATE_TYPE]
            else:
                actions = []
            event.reply({'id': event.data['id'], 'value': actions})

    def listen_add_action(self, event):
        if 'id' in event.data:
            state = State.get(id=event.data['id'])
            if state is not None:
                State.add(name=event.data.get('name', str(uuid4())), parent=state, type=self.ACTION_STATE_TYPE,
                          value=event.data.get('value') or [], label=event.data.get('label') or 'New action')
                self.broadcast_list_actions(state)

    def listen_update_action(self, event):
        if 'id' in event.data:
            state = State.get(id=event.data['id'])
            if state is not None:
                state.set_value(event.data['value'])
                if 'label' in event.data:
                    state.update(label=event.data['label'])
                    self.broadcast_list_actions(state.parent)

    def listen_delete_action(self, event):
        if 'id' in event.data:
            # FIXME use the State api here instead of an event as events might require permissions
            Event.fire('state_delete', event.data, source=event.source)

    def listen_stop_plugin(self, event):
        super().listen_stop_plugin(event)
        self.scheduler.shutdown(wait=False)

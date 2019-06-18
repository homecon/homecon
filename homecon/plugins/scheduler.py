#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import pytz
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger

from homecon.core.state import State
from homecon.core.event import Event
from homecon.core.plugin import Plugin


logger = logging.getLogger(__name__)


class Scheduler(Plugin):
    """
    Class to control the HomeCon scheduler

    """

    def __init__(self):
        super().__init__()
        self.scheduler = None

    def initialize(self):
        State.add('scheduler', type=None)
        State.add('action', type=None)

        jobstores = {
        }
        executors = {
            'default': ThreadPoolExecutor(20),
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        self.scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)

        # add existing jobs
        for state in self.base_state.children:
            self.update_job(state)

        # start the scheduler
        self.scheduler.start()

        logger.debug('Scheduler plugin Initialized')

    @property
    def base_state(self):
        return State.get('/scheduler')

    @property
    def timezone(self):
        return State.get('/settings/location/timezone').value

    def update_job(self, state):
        if 'trigger' not in state.value or 'action' not in state.value:
            logger.exception('trigger and action must be included in the state value')
            return

        def func():
            logger.debug('executing scheduler {}'.format(state))
            for v in State.get(state.value['action']).value:
                d = v.get('delay', 0)
                if d > 0:
                    def e():
                        s = State.get(v['path'])
                        time.sleep(d)
                        logger.debug('setting {} to {} from schedule {}'.format(s, v['value'], state))
                        s.set_value(v['value'], source='Scheduler')

                    Thread(target=e).start()
                else:
                    s = State.get(v['path'])
                    logger.debug('setting {} to {} from schedule {}'.format(s, v['value'], state))
                    s.set_value(v['value'], source='Scheduler')

        job = self.scheduler.get_job(state.path)
        if job is None:
            logger.debug('adding scheduler job for {}'.format(state))
            self.scheduler.add_job(func, trigger='cron', **state.value['trigger'], timezone=self.timezone,
                                   id=state.path)
        else:
            logger.debug('updating scheduler job for {}'.format(state))
            job.modify(func=func, trigger=CronTrigger(**state.value['trigger']))

    def listen_state_value_changed(self, event):
        state = event.data['state']
        if state.parent == self.base_state:
            self.update_job(state)

    def listen_state_deleted(self, event):
        state_path = event.data['path']
        if state_path.startswith(self.base_state.path):
            try:
                self.scheduler.remove_job(state_path)
            except:
                logger.exception('job not found: {}'.format(state_path))

    def listen_stop_plugin(self, event):
        super().listen_stop_plugin(event)
        self.scheduler.shutdown(wait=False)

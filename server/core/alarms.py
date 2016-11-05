#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import pytz
import asyncio

from . import database
from .plugin import Plugin

class Alarms(Plugin):
    """
    Class to control the HomeCon alarms
    
    
    """

    def initialize(self):
        self._loop = asyncio.get_event_loop()

        self._schedule = {}

        # look for states with an action type
        for state in self.states.values():
            if state.config['type'] == 'action':
                self._actions[state.path] = Action(state)

        # look for states with an alarm type
        for state in self.states.values():
            if state.config['type'] == 'alarm':
                self.schedule_alarm(state)


    def schedule_alarm(self,state):
        """
        Schedule or reschedule an alarm for execution

        """

        # cancel the old scheduling
        if state.path in self._schedule:
            self._schedule[state.path].cancel()
            del self._schedule[state.path]


        if not self.states['settings/timezone'].value is None:
            timezone = pytz.timezone(self.states['settings/timezone'].value)
        else:
            timezone = pytz.utc

        # schedule the alarm
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()


        timestamp_now = (dt_now-dt_ref).total_seconds()


        # no match found for the next time, reschedule?
        never_matches = False

        if state.value['mon']==False and state.value['tue']==False and state.value['wed']==False and state.value['thu']==False and state.value['fri']==False and state.value['sat']==False and state.value['sun']==False:
            never_matches = True

        if not state.value['year'] is None and not state.value['month'] is None and not state.value['day'] is None and not state.value['hour'] is None and not state.value['minute'] is None:
            dt_when = timezone.localize( datetime.datetime(state.value['year'],state.value['month'],state.value['day'],state.value['hour'],state.value['minute']) )
            timestamp_when = (dt_when-dt_ref).total_seconds()
            if timestamp_when > timestamp_now:
                never_matches = True


        if never_matches:
            logging.debug('Could not schedule {}, alarm never occurs'.format(state.path))
        
        else:
            # get the next execution time
            timesdelta = 60

            dt_when = dt_now.replace(second=0,microsecond=0)
            timestamp_when = (dt_when-dt_ref).total_seconds()


            for i in range(1441):
                
                timestamp_when += timesdelta
                dt_when = pytz.utc.localize( datetime.datetime.utcfromtimestamp(timestamp_when) ).astimezone(timezone)
                
                match = True
                if timestamp_when < timestamp_now + 5:  # 5 seconds extra
                    match = False
                elif not state.value['year'] is None and not state.value['year']==dt_when.year:
                    match = False
                elif not state.value['month'] is None and not state.value['month']==dt_when.month:
                    match = False
                elif not state.value['day'] is None and not state.value['day']==dt_when.day:
                    match = False
                elif not state.value['hour'] is None and not state.value['hour']==dt_when.hour:
                    match = False
                elif not state.value['minute'] is None and not state.value['minute']==dt_when.minute:
                    match = False
                elif not state.value['sun'] is None and not state.value['sun'] and dt_when.weekday()==0:
                    match = False
                elif not state.value['mon'] is None and not state.value['mon'] and dt_when.weekday()==1:
                    match = False
                elif not state.value['tue'] is None and not state.value['tue'] and dt_when.weekday()==2:
                    match = False
                elif not state.value['wed'] is None and not state.value['wed'] and dt_when.weekday()==3:
                    match = False
                elif not state.value['thu'] is None and not state.value['thu'] and dt_when.weekday()==4:
                    match = False
                elif not state.value['fri'] is None and not state.value['fri'] and dt_when.weekday()==5:
                    match = False
                elif not state.value['sat'] is None and not state.value['sat'] and dt_when.weekday()==6:
                    match = False

                if match:
                    break


            if not match:
                logging.debug('Could not schedule {}, retry at {}'.format(state.path,dt_when))

                when = self._loop.time() + timestamp_when - timestamp_now
                self._loop.call_at(when,self.schedule_alarm,state)


            else:
                # call at
                when = self._loop.time() + timestamp_when - timestamp_now
                handle = self._loop.call_at(when,self.run_alarm,state)
                self._schedule[state.path] = Scheduled(timestamp_when,handle)

                logging.debug('Scheduled {} to run at {}'.format(state.path,dt_when))


    def run_alarm(self,state):
        """
        Run alarm actions and reschedule the alarm
        
        Parameters
        ----------
        state : homecon.core.states.State
            a state object with type alarm

        """

        logging.debug('Running {} action'.format(state.path))

        # remove from the schedule
        if state.path in self._schedule:
            del self._schedule[state.path]

        # run the actions
        if state.value['action'] in self.states:
            self.run_action(self.states[state.value['action']])

        # schedule the next execution
        self.schedule_alarm(state)


    def run_action(self,state):
        """
        Runs an action defined in a state

        Parameters
        ----------
        state : homecon.core.states.State
            a state object with type action, the value must be a list of tuples
            containing a path, value and delay

        """

        for action in state.value:
            path = action[0]
            value = action[1]
            delay = action[2]

            self._loop.call_later(delay,functools.partial(self.fire, 'state', {'path':path, 'value':value}, source=self))


    def listen(self,event):
        """
        Listen for events

        """

        if event.type == 'state_changed':
            if event.data['state'].config['type'] == 'alarm':
                # schedule
                self.schedule_alarm(event.data['state'])


        elif event.type == 'state_added':
            if event.data['state'].config['type'] == 'alarm':
                # schedule
                self.schedule_alarm(event.data['state'])


        elif event.type == 'alarm_snooze':
            logging.warning('alarm snooze is not implemented yet')



class Scheduled(object):
    def __init__(self,timestamp,handle):
        self.timestamp = timestamp
        self.handle = handle

    def cancel(self):
        self.handle.cancel()




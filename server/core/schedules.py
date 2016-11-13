#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import pytz
import uuid

from . import database
from .plugin import BasePlugin

class Schedules(BasePlugin):
    """
    Class to control the HomeCon scheduling
    
    """

    def initialize(self):
        """
        Initialize

        """
        self._schedules = {}
        self._scheduled = {}

        self.timezone = pytz.utc

        self._db = database.Database(database='homecon.db')
        self._db_schedules = database.Table(self._db,'schedules',[
            {'name':'path',   'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'config', 'type':'char(511)',  'null': '',  'default':'',  'unique':''},
            {'name':'value',  'type':'char(255)',  'null': '',  'default':'',  'unique':''},
        ])

        # get all schedules from the database
        result = self._db_schedules.GET()
        for schedule in result:
            self.add_local( schedule['path'],json.loads(schedule['config']),json.loads(schedule['value']) )


    def add_local(self,path,config,value):
        """
        Adds a schedule but does not add it to the database

        """

        schedule = Schedule(self,path,config,value)
        self._schedules[path] = schedule
        self.schedule(schedule)

        return schedule


    def add(self,path,config,value):
        """
        Add a schedule to the plugin and the database

        """
        self._db_schedules.POST(path=path,config=json.dumps(config),value=json.dumps(value))

        schedule = self.add_local(path,config,value)

        return schedule

    def schedule(self,schedule):
        """
        Schedule or reschedule an alarm for execution

        """

        # cancel the old scheduling
        if schedule.path in self._scheduled:
            self._scheduled[schedule.path].cancel()
            del self._scheduled[schedule.path]


        # schedule the alarm
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()


        timestamp_now = (dt_now-dt_ref).total_seconds()


        # no match found for the next time, reschedule?
        never_matches = False

        if schedule.value['mon']==False and schedule.value['tue']==False and schedule.value['wed']==False and schedule.value['thu']==False and schedule.value['fri']==False and schedule.value['sat']==False and schedule.value['sun']==False:
            never_matches = True

        if not schedule.value['year'] is None and not schedule.value['month'] is None and not schedule.value['day'] is None and not schedule.value['hour'] is None and not schedule.value['minute'] is None:
            dt_when = self.timezone.localize( datetime.datetime(schedule.value['year'],schedule.value['month'],schedule.value['day'],schedule.value['hour'],schedule.value['minute']) )
            timestamp_when = (dt_when-dt_ref).total_seconds()
            if timestamp_when > timestamp_now:
                never_matches = True


        if never_matches:
            logging.debug('Could not schedule {}, event never occurs'.format(schedule.path))
        
        else:
            # get the next execution time
            timesdelta = 60

            dt_when = dt_now.replace(second=0,microsecond=0)
            timestamp_when = (dt_when-dt_ref).total_seconds()


            for i in range(1441):
                
                timestamp_when += timesdelta
                dt_when = pytz.utc.localize( datetime.datetime.utcfromtimestamp(timestamp_when) ).astimezone(self.timezone)
                
                match = True
                if timestamp_when < timestamp_now + 5:  # 5 seconds extra
                    match = False
                elif not schedule.value['year'] is None and not schedule.value['year']==dt_when.year:
                    match = False
                elif not schedule.value['month'] is None and not schedule.value['month']==dt_when.month:
                    match = False
                elif not schedule.value['day'] is None and not schedule.value['day']==dt_when.day:
                    match = False
                elif not schedule.value['hour'] is None and not schedule.value['hour']==dt_when.hour:
                    match = False
                elif not schedule.value['minute'] is None and not schedule.value['minute']==dt_when.minute:
                    match = False
                elif not schedule.value['sun'] is None and not schedule.value['sun'] and dt_when.weekday()==0:
                    match = False
                elif not schedule.value['mon'] is None and not schedule.value['mon'] and dt_when.weekday()==1:
                    match = False
                elif not schedule.value['tue'] is None and not schedule.value['tue'] and dt_when.weekday()==2:
                    match = False
                elif not schedule.value['wed'] is None and not schedule.value['wed'] and dt_when.weekday()==3:
                    match = False
                elif not schedule.value['thu'] is None and not schedule.value['thu'] and dt_when.weekday()==4:
                    match = False
                elif not schedule.value['fri'] is None and not schedule.value['fri'] and dt_when.weekday()==5:
                    match = False
                elif not schedule.value['sat'] is None and not schedule.value['sat'] and dt_when.weekday()==6:
                    match = False

                if match:
                    break


            if not match:
                logging.debug('Could not schedule {}, retry at {}'.format(schedule.path,dt_when))

                when = self._loop.time() + timestamp_when - timestamp_now
                self._loop.call_at(when,self.schedule,schedule)


            else:
                # call at
                when = self._loop.time() + timestamp_when - timestamp_now
                handle = self._loop.call_at(when,self.schedule,schedule)
                self._scheduled[schedule.path] = Scheduled(timestamp_when,handle)

                logging.debug('Scheduled {} to run at {}'.format(schedule.path,dt_when))



    def get_schedules_list(self):
        unsortedlist =  [s.serialize() for s in self._schedules]
        sortedlist = sorted(unsortedlist, key=lambda k: k['id'])
        return sortedlist


    def listen_add_schedule(self,event):

        path = str(uuid.uuid4())
        schedule = self.add(path,event.data['config'],event.data['value'])

        if state:
            self.fire('schedule_added',{'schedule':schedule})
            self.fire('send_to',{'event':'list_schedules', 'path':'', 'value':self.get_schedules_list(), 'clients':[event.client]})
    

    def listen_schedule(self,event):
        logging.warning('schedule is not implemented yet')


    def listen_delete_schedule(self,event):
        logging.warning('delete schedule is not implemented yet')


    def listen_snooze_schedule(self,event):
        logging.warning('snooze schedule is not implemented yet')


    def listen_state_changed(self,event):
        if event.data['state'].path == 'settings/timezone':
            try:
                self.timezone = pytz.timezone(event.data['value'])
            except:
                logging.error('timezone {} is not available in pytz'.format(event.data['value']))



class Schedule(object):
    """
    """
    def __init__(self,schedules,path,config,value):

        self._schedules = schedules

        self.path = path
        self.config = config
        self.value = value


    def run(self):
        """
        Run alarm actions and reschedule the alarm
        
        Parameters
        ----------
        state : homecon.core.states.State
            a state object with type alarm

        """

        logging.debug('Running {} scheduled actions'.format(self.path))

        # remove from the schedule
        if self.path in self._schedules._scheduled:
            del self._schedules._scheduled[self.path]

        # run the actions
        self._schedules.fire('run_action',{'path':self.value['action']})

        # schedule the next execution
        self._schedules.schedule(schedule)


    def serialize(self):
        """
        return a dict representation of the instance

        """

        data = {
            'path': self.path,
            'config': json.dumps(self.config),
            'value': json.dumps(self.value),
        }
        return data


class Scheduled(object):
    """
    """
    def __init__(self,timestamp,handle):
        self.timestamp = timestamp
        self.handle = handle

    def cancel(self):
        self.handle.cancel()




class Actions(BasePlugin):
    def initialize(self):

        self._actions = {}

        self._db = database.Database(database='homecon.db')
        self._db_actions = database.Table(self._db,'actions',[
            {'name':'path',   'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'config', 'type':'char(511)',  'null': '',  'default':'',  'unique':''},
            {'name':'value',  'type':'char(255)',  'null': '',  'default':'',  'unique':''},
        ])

        # get all actions from the database
        result = self._db_actions.GET()
        for action in result:
            self.add_local(action['path'],json.loads(action['config']),json.loads(action['value']))


    def add_local(self,path,config,value):
        """
        Add a schedule to the plugin but not to the database

        """

        action = Action(self._loop,path,config,value)
        self._actions[action.path] = action

        return action


    def add(self,path,config,value):
        """
        Add a schedule to the plugin and the database

        """

        self._db_actions.POST(path=path,config=json.dumps(config),value=json.dumps(value))

        action = self.add_local(path,config,value)

        return action


    def listen_run_action(self,event):
        if event.data['path'] in self._actions:
            self._actions[event.data['path']].run(source=event.source)



class Action(object):
    """
    """
    def __init__(self,loop,path,config,value):

        self._loop = loop

        self.path = path
        self.config = config
        self.value = value


    def run(self,source=None):
        """
        Runs an action defined in a state

        Parameters
        ----------
        action : Action instance
            an Action instance defining the action to be run

        """

        if source is None:
            source = self

        for a in self.value:
            path = a[0]
            value = a[1]
            delay = a[2]

            self._loop.call_later(delay,functools.partial(self.fire, 'state', {'path':path, 'value':value}, source=source))


    def serialize(self):
        """
        return a dict representation of the instance

        """

        data = {
            'path': self.path,
            'config': json.dumps(self.config),
            'value': json.dumps(self.value),
        }
        return data




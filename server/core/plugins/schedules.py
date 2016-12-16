#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import pytz
import uuid
import asyncio

from .. import database
from ..plugin import Plugin

class Schedules(Plugin):
    """
    Class to control the HomeCon scheduling
    
    """

    def initialize(self):
        """
        Initialize

        """
        self._schedules = {}

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
            self.add( schedule['path'], config=json.loads(schedule['config']), value=json.loads(schedule['value']), id=schedule['id'])


        # schedule schedule running
        self._loop.create_task(self.schedule_schedules())


        logging.debug('Schedules plugin Initialized')


    def add(self,path,config=None,value=None,id=None):
        """
        Add a schedule to the plugin and the database

        """
        # check the config
        if config is None:
            config = {}
        if not 'filter' in config:
            config['filter'] = ''
 
        # check value
        if value is None:
            value = {}
        if not 'year' in value:
            value['year'] = None
        if not 'month' in value:
            value['month'] = None
        if not 'day' in value:
            value['day'] = None
        if not 'hour' in value:
            value['hour'] = 0
        if not 'minute' in value:
            value['minute'] = 0
        if not 'sun' in value:
            value['sun'] = True
        if not 'mon' in value:
            value['mon'] = True
        if not 'tue' in value:
            value['tue'] = True
        if not 'wed' in value:
            value['wed'] = True
        if not 'thu' in value:
            value['thu'] = True
        if not 'fri' in value:
            value['fri'] = True
        if not 'sat' in value:
            value['sat'] = True

        if not 'actions' in value:
            value['actions'] = []


        # check if the schedule is in the database and add it if not
        if len( self._db_schedules.GET(path=path) ) == 0:
            self._db_schedules.POST(path=path,config=json.dumps(config),value=json.dumps(value))

        if id is None:
            result = self._db_schedules.GET(path=path)
            id = result[0]['id']

        schedule = Schedule(self,path,config,value,id)
        self._schedules[path] = schedule

        return schedule

    def delete(self,path):

        # remove the schedule from the database
        self._db_schedules.DELETE(path=path)
        # remove the schedule from the local reference
        del self._schedules[path]


    def update(self,path,value):
        """
        Updated the values of a schedule

        Parameters
        ----------
        path : str
            the schedule path

        value : dict
            a dicionary with values for the schedule

        """

        if path in self._schedules:
            schedule = self._schedules[path]

            for key,val in value.items():
                if key in schedule.value:
                    if key in ['hour','minute']:
                        val = int(val)

                    schedule.value[key] = val

            # update the database
            self._db_schedules.PUT(value=json.dumps(schedule.value), where='path=\'{}\''.format(schedule.path))

            return schedule

        else:
            return False



    async def schedule_schedules(self):
        """
        Schedule schedule checking

        """

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = (dt_now + datetime.timedelta(minutes=1)).replace(second=0,microsecond=0)

            timestamp_when = int( (dt_when-dt_ref).total_seconds() )

            dt = pytz.utc.localize( dt_now ).astimezone(self.timezone)
            for path,schedule in self._schedules.items():
                if schedule.match(dt):
                    self._loop.call_soon_threadsafe(schedule.run)


            # sleep until the next call
            timestamp_now = int( (datetime.datetime.utcnow()-dt_ref).total_seconds() )
            if timestamp_when-timestamp_now > 0:
                await asyncio.sleep(timestamp_when-timestamp_now)


    def get_schedules_list(self,filter=None):

        unsortedlist =  [s.serialize() for s in self._schedules.values() if (filter is None or filter=='' or not 'filter' in s.config or s.config['filter'] == filter)]
        sortedlist = sorted(unsortedlist, key=lambda k: k['id'])
        return sortedlist


    def listen_list_schedules(self,event):

        if 'path' in event.data:
            filter = event.data['path']
        else:
            filter = None

        self.fire('send_to',{'event':'list_schedules', 'path':event.data['path'], 'value':self.get_schedules_list(filter=filter), 'clients':[event.client]})


    def listen_add_schedule(self,event):

        path = str(uuid.uuid4())
        schedule = self.add(path,event.data['config'],event.data['value'])

        if schedule:
            self.fire('schedule_added',{'schedule':schedule})
            filter = schedule.config['filter']
            self.fire('send_to',{'event':'list_schedules', 'path':filter, 'value':self.get_schedules_list(filter=filter), 'clients':[event.client]})


    def listen_schedule(self,event):
        if 'path' in event.data:
            schedule = self.update(event.data['path'],event.data['value'])

            if schedule:
                filter = schedule.config['filter']
                self.fire('send_to',{'event':'list_schedules', 'path':filter, 'value':self.get_schedules_list(filter=filter), 'clients':[event.client]})
            else:
                logging.error('Schedule does not exist {}'.format(event.data['path']))


    def listen_delete_schedule(self,event):
        filter = self._schedules[event.data['path']].config['filter']

        self.delete(event.data['path'])
        logging.debug('deleted schedule {}'.format(event.data['path']))
        self.fire('send_to',{'event':'list_schedules', 'path':filter, 'value':self.get_schedules_list(filter=filter), 'clients':[event.client]})


    def listen_snooze_schedule(self,event):
        logging.warning('snooze schedule is not implemented yet')


    def listen_state_changed(self,event):
        if event.data['state'].path == 'settings/location/timezone':
            try:
                self.timezone = pytz.timezone(event.data['value'])
            except:
                logging.error('timezone {} is not available in pytz'.format(event.data['value']))



class Schedule(object):
    """
    """
    def __init__(self,schedules,path,config,value,id):

        self._schedules = schedules

        self.path = path
        self.config = config
        self.value = value
        self.id = id

    def match(self,dt):
        """
        Check if the schedule should be run at a certain datetime

        Parameters
        ----------
        dt : datetime.datetime
            a localized datetime object

        """

        match = True
        if not self.value['year'] is None and not self.value['year']==dt.year:
            match = False
        elif not self.value['month'] is None and not self.value['month']==dt.month:
            match = False
        elif not self.value['day'] is None and not self.value['day']==dt.day:
            match = False
        elif not self.value['hour'] is None and not self.value['hour']==dt.hour:
            match = False
        if not self.value['minute'] is None and not self.value['minute']==dt.minute:
            match = False
        elif not self.value['sun'] is None and not self.value['sun'] and dt.weekday()==0:
            match = False
        elif not self.value['mon'] is None and not self.value['mon'] and dt.weekday()==1:
            match = False
        elif not self.value['tue'] is None and not self.value['tue'] and dt.weekday()==2:
            match = False
        elif not self.value['wed'] is None and not self.value['wed'] and dt.weekday()==3:
            match = False
        elif not self.value['thu'] is None and not self.value['thu'] and dt.weekday()==4:
            match = False
        elif not self.value['fri'] is None and not self.value['fri'] and dt.weekday()==5:
            match = False
        elif not self.value['sat'] is None and not self.value['sat'] and dt.weekday()==6:
            match = False

        return match



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
            'id': self.id,
            'path': self.path,
            'config': json.dumps(self.config),
            'value': json.dumps(self.value),
        }
        return data




class Actions(Plugin):
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
            self.add(action['path'],json.loads(action['config']),json.loads(action['value']))


    def add(self,path,config,value):
        """
        Add a schedule to the plugin and the database

        """
        if len( self._db_actions.GET(path=path) ) == 0:
            self._db_actions.POST(path=path,config=json.dumps(config),value=json.dumps(value))

        action = Action(self._loop,path,config,value)
        self._actions[action.path] = action

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




#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import pytz
import uuid
import asyncio

from .. import core


class Schedule(core.state.BaseState):
    """
    """

    def fire_changed(self,value,oldvalue,source=None):
        """
        """
        core.event.fire('schedule_changed',{'schedule':self,'value':value,'oldvalue':oldvalue},source=source)


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
        Run schedule actions

        """

        logging.debug('Running {} scheduled actions'.format(self.path))

        # run the actions
        core.event.fire('run_action',{'path':self.value['action']},source=self)


    def _check_config(self,config):

        config= super(Schedule,self)._check_config(config)

        if not 'filter' in config:
            config['filter'] = ''

        return config


    def _check_value(self,value):

        value = super(Schedule,self)._check_value(value)

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

        if not 'action' in value:
            value['action'] = ''


        value['hour'] = int(value['hour'])
        value['minute'] = int(value['minute'])


        return value





class Schedules(core.plugin.ObjectPlugin):
    """
    Class to control the HomeCon scheduling
    
    """

    objectclass = Schedule
    objectname = 'schedule'

    def initialize(self):
        """
        Initialize

        """

        # define the default timezone
        try:
            self.timezone = pytz.timezone(core.states['settings/location/timezone'].value)
        except:
            self.timezone = pytz.utc
        

        # schedule schedule running
        self._loop.create_task(self.run_schedules())

        logging.debug('Schedules plugin Initialized')
        

    async def run_schedules(self):
        """
        run schedule checking

        """

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = (dt_now + datetime.timedelta(minutes=1)).replace(second=0,microsecond=0)

            timestamp_when = int( (dt_when-dt_ref).total_seconds() )

            dt = pytz.utc.localize( dt_now ).astimezone(self.timezone)

            for path,schedule in self.items():
                if schedule.match(dt):
                    self._loop.call_soon_threadsafe(schedule.run)


            # sleep until the next call
            timestamp_now = int( (datetime.datetime.utcnow()-dt_ref).total_seconds() )
            if timestamp_when-timestamp_now > 0:
                await asyncio.sleep(timestamp_when-timestamp_now)


    def list(self,filter=None):

        unsortedlist =  [obj.serialize() for obj in self.values() if (filter is None or filter=='' or not 'filter' in obj.config or obj.config['filter'] == filter)]
        sortedlist = sorted(unsortedlist, key=lambda obj: obj['id'])
        pathlist = [obj['path'] for obj in sortedlist]

        return pathlist


    def listen_add_schedule(self,event):

        path = str(uuid.uuid4())
        obj = self.objectclass(self._objectdict,self._db_objects,path,config=event.data['config'])

        if obj:
            core.event.fire('schedule_added',{'schedule':obj})
            filter = obj.config['filter']
            core.event.fire('send_to',{'event':'list_schedules', 'path':filter, 'value':self.list(filter=filter), 'clients':[event.client]})


    def listen_delete_schedule(self,event):

        if 'path' in event.data:
            if event.data['path'] in self:

                obj = self[event.data['path']]
                filter = obj.config['filter']
                obj.delete()

                logging.debug('deleted {} {}'.format(self.objectname.capitalize(), event.data['path']))

                core.event.fire('send',{'event':'list_{}s'.format(self.objectname), 'path':filter, 'value':self.list(filter=filter)})

            else:
                logging.error('{} does not exist {}'.format(self.objectname.capitalize(),event.data['path']))



    def listen_schedule_changed(self,event):
        core.event.fire('send',{'event':'schedule', 'path':event.data['schedule'].path, 'value':event.data['schedule'].value, 'readusers':event.data['schedule'].config['readusers'], 'readgroups':event.data['schedule'].config['readgroups']})


    def listen_snooze_schedule(self,event):
        logging.warning('snooze schedule is not implemented yet')


    def listen_state_changed(self,event):
        if event.data['state'].path == 'settings/location/timezone':
            try:
                self.timezone = pytz.timezone(event.data['value'])
            except:
                logging.error('timezone {} is not available in pytz'.format(event.data['value']))





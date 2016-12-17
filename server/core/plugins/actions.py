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
from ..states import BaseState
from ..plugin import Plugin


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
        for db_entry in result:
            Action(self._actions,self._db_actions,db_entry['path'],db_entry=db_entry)


    def listen_run_action(self,event):
        if event.data['path'] in self._actions:
            self._actions[event.data['path']].run(source=event.source)


    def listen_add_action(self,event):
        
        action = Action(self._actions,self._db_actions,event.data['path'],config=event.data['config'])

        if schedule:
            self.fire('schedule_added',{'schedule':schedule})
            filter = schedule.config['filter']
            self.fire('send_to',{'event':'list_schedules', 'path':filter, 'value':self.get_schedules_list(filter=filter), 'clients':[event.client]})

    def listen_action(self,event)

        if 'path' in event.data:
            # get or set an action
            if 'value' in event.data:
                # set
                if event.data['path'] in self._actions:
                    action = self._actions[event.data['path']]

                    value = dict(action.value)
                    for key,val in event.data['value'].items():
                        value[key] = val

                    action.set(value,source=event.source)

            else:
                # get
                if event.data['path'] in self._actions:
                    action = self._actions[event.data['path']]
                    self.fire('send_to',{'event':'action', 'path':event.data['path'], 'value':action.value, 'clients':[event.client]})
        else:
            logging.error('Action does not exist {}'.format(event.data['path']))


    def __getitem__(self,path):
        return self._actions[path]

    def __iter__(self):
        return iter(self._actions)

    def __contains__(self,path):
        return path in self._actions

    def keys(self):
        return self._actions.keys()

    def items(self):
        return self._actions.items()

    def values(self):
        return self._actions.values()



class Action(BaseState):
    """
    """

    def fire_changed(self,value,oldvalue,source):
        """
        """
        self._plugin.fire('action_changed',{'action':self,'value':value,'oldvalue':oldvalue},source)


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


    def _check_value(self,config):

        value= super(Schedule,self)._check_value(value)

        if not 'filter' in value:
            value['filter'] = ''

        return value


    def __repr__(self):
        return '<action {} value={}>'.format(self._path,self._value)




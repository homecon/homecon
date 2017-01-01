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
from .authentication import servertoken
from .authentication import jwt_decode

class Action(core.state.BaseState):
    """
    an action is a collection of events which are fired when the action is run

    """

    db_table = core.database.Table(core.database.db,'actions',[
        {'name':'path',   'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
        {'name':'config', 'type':'char(511)',  'null': '',  'default':'',  'unique':''},
        {'name':'value',  'type':'char(255)',  'null': '',  'default':'',  'unique':''},
    ])
    container = {}

    def initialize(self):
        logging.debug('Actions initialized')


    def fire_changed(self,value,oldvalue,source):
        """
        """

        client=None

        core.event.fire('action_changed',{'action':self,'value':value,'oldvalue':oldvalue},source,client)


    def run(self,source=None):
        """
        Runs an action defined in a state

        Parameters
        ----------
        source : 
            the action caller

        """

        if source is None:
            source = self

        client = None

        for action in self.value:
            data = json.loads(action['data'])

            # add the server token to the data, this token has the highest permission so every event will be processed
            data['token'] = servertoken

            self._loop.call_later(float(action['delay']),functools.partial(core.event.fire, action['event'], data, source, client))


    def _check_value(self,value):

        if value is None:
            value = []

        return value


    def __repr__(self):
        return '<action {} value={}>'.format(self._path,self._value)




class Actions(core.plugin.ObjectPlugin):

    objectclass = Action
    objectname = 'action'


    def listen_run_action(self,event):
        if event.data['path'] in self:
            self[event.data['path']].run(source=event.source)




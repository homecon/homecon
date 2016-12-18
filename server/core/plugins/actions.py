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
from .. import events
from ..states import BaseState
from ..plugin import ObjectPlugin



class Action(BaseState):
    """
    an action is a collection of events which are fired when the action is run

    """
    def initialize(self):
        logging.debug('Actions initialized')


    def fire_changed(self,value,oldvalue,source):
        """
        """

        client=None

        events.fire('action_changed',{'action':self,'value':value,'oldvalue':oldvalue},source,client)


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

        for a in self.value:
            event = a[0]
            data  = a[1]
            delay = a[2]

            self._loop.call_later(delay,functools.partial(events.fire, event, data, source, client))


    def _check_value(self,value):

        if value is None:
            value = []

        return value


    def __repr__(self):
        return '<action {} value={}>'.format(self._path,self._value)




class Actions(ObjectPlugin):

    objectclass = Action
    objectname = 'action'


    def listen_run_action(self,event):
        if event.data['path'] in self:
            self[event.data['path']].run(source=event.source)




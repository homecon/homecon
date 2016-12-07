#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import os
import sys

from concurrent.futures import ThreadPoolExecutor

from . import database

sys.path.append(os.path.abspath('..'))

# the worker thread pool
executor = ThreadPoolExecutor(10)

class Event(object):
    def __init__(self,event_type,data,source,client):
        self.type = event_type
        self.data = data
        self.source = source
        self.client = client

    def __str__(self):
        newdata = dict(self.data)
        for key in ['password','token']:
            if key in newdata:
                newdata[key] = '***'

        return 'Event: {}, data: {}, source: {}, client: {}'.format(self.type,newdata.__repr__(),self.source.__class__.__name__,self.client.__repr__())


class BasePlugin(object):
    """
    A class defining a base plugin
    """
    def __init__(self,queue):
        """
        Initialize a plugin instance
        
        Parameters
        ---------
        queue : event queue
            the main homecon event queue
            
        """

        self._queue = queue
        self._loop = asyncio.get_event_loop()


    def fire(self,event_type,data,source=None,client=None):
        """
        Add the event to the que
        
        Parameters
        ----------
        event_type : string
            the event type

        data : dict
            the data describing the event
        
        source : string
            the source of the event
            
        """
        
        if source==None:
            source = self

        event = Event(event_type,data,source,client)

        async def do_fire(event):
            await self._queue.put(event)


        def do_create_task():
            self._loop.create_task(do_fire(event))

        self._loop.call_soon_threadsafe(do_create_task)




class Plugin(BasePlugin):
    """
    A class for defining plugins with listener methods

    Notes
    -----
    A plugin can not send events to itself through the fire / listen methods

    Examples
    --------
    .. code-block::
        def listen_someevent(self,event):
            self.do_something(event)

        def listen_someotherevent(self,event):
            self.do_somethingelse(event)

    """

    def __init__(self,queue,states,components):
        """
        Initialize a plugin instance
        
        Parameters
        ---------
        queue : event queue
            the main homecon event queue
            
        states : homecon.core.states.States
            the main homecon states object
            
        components : homecon.core.components.Components
            the main homecon components object
            
        """

        self._queue = queue
        self._states = states
        self._components = components

        self._loop = asyncio.get_event_loop()
        self.config_keys = []

        self.get_listeners()

        self.initialize()

    def get_listeners(self):
        self.listeners = {}
        for method in dir(self):
            if method.startswith('listen_'):
                event = '_'.join(method.split('_')[1:])
                self.listeners[event] = getattr(self,method)


    def initialize(self):
        """
        Base method runs when the plugin is instantiated
        
        redefine this method in a child class
        """
        pass

    def register_component(self,componentclass):
        self._components.register(componentclass)

    def components(self):
        """
        Redefinable method which should return a list of components defined by the plugin and enables the app to edit the component

        Examples
        --------
        [{
            'name': 'light',
            'properties': ['power'],
            'states': [
                {
                    'path': 'value',    # the final path of a state is prefixed with the component path ex. living/light1/value
                    'defaultconfig': {         # values listed here will be defaults
                        'label': 'light',
                        'quantity': 'boolean',
                        'unit' : ''
                    },
                    'fixedconfig': {         # values listed here will not be changeable
                        'type': bool
                    },
                },
            ]
        },]

        """

        return []


    def _listen(self,event):
        """
        Base listener method called when an event is taken from the que
        
        checks whether this plugin is the target or if there is no target and
        then calls the code:`listen` method if so
        
        Parameters
        ----------
        event : Event
            an Event instance
            
        Notes
        -----
        Source checking to avoid infinite loops needs to be done in the plugin
        listener method

        """

        if event.type in self.listeners:
            #executor.submit(self.listeners[event.type], event)
            #asyncio.ensure_future(self._loop.run_in_executor(executor, self.listeners[event.type], event))
            self.listeners[event.type](event)





#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import os
import sys
import uuid

from concurrent.futures import ThreadPoolExecutor

from . import events
from . import states
from . import components
from . import database

sys.path.append(os.path.abspath('..'))

# the worker thread pool
executor = ThreadPoolExecutor(10)



class Plugin(object):
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


    def __init__(self):
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

        self._queue = events.queue
        self._states = states.states
        self._components = components.components

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
        """
        if source==None:

            source = self



        event = events.Event(event_type,data,source,client)



        async def do_fire(event):

            await self._queue.put(event)





        def do_create_task():

            self._loop.create_task(do_fire(event))



        self._loop.call_soon_threadsafe(do_create_task)


        """
        if source==None:
            source = self


        events.fire(event_type,data,source,client)


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


    def __getitem__(self,path):
        return None

    def __iter__(self):
        return iter([])

    def __contains__(self,path):
        return False

    def keys(self):
        return []

    def items(self):
        return []

    def values(self):
        return []




class ObjectPlugin(Plugin):
    """
    A plugin including an object list and usefull listeners
    
    objectclass and objectname must be defined in a child class

    """

    objectclass = states.State
    objectname = 'state'

    def __init__(self):


        self._objectdict = {}

        self._db = database.Database(database='homecon.db')
        self._db_objects = database.Table(self._db,self.objectname,[
            {'name':'path',   'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'config', 'type':'char(511)',  'null': '',  'default':'',  'unique':''},
            {'name':'value',  'type':'char(255)',  'null': '',  'default':'',  'unique':''},
        ])

        # get all objects from the database
        result = self._db_objects.GET()
        for db_entry in result:
            self.objectclass(self._objectdict,self._db_objects,db_entry['path'],db_entry=db_entry)



        # add listener methods
        def listen_add_object(cls, event):
            """
            add
            """
            if 'path' in event.data:
                path = event.data['path']
            else:
                path = str(uuid.uuid4())

            if 'config' in event.data:
                config = event.data['config']
            else:
                config = None

            if 'value' in event.data:
                value = event.data['value']
            else:
                value = None

            obj = self.objectclass(self._objectdict,self._db_objects,path,config=config,value=value)

            if obj:
                self.fire('{}_added'.format(self.objectname),{self.objectname: obj})
                self.fire('send',{'event':'list_{}s'.format(self.objectname), 'path':'', 'value':self.list()})


        def listen_delete_object(cls,event):
            """
            delete
            """
            if 'path' in event.data:
                if event.data['path'] in self:

                    obj = self[event.data['path']]
                    obj.delete()

                    logging.debug('deleted {} {}'.format(self.objectname.capitalize(), event.data['path']))

                    self.fire('send',{'event':'list_{}s'.format(self.objectname), 'path':'', 'value':self.list()})

                else:
                    logging.error('{} does not exist {}'.format(self.objectname.capitalize(),event.data['path']))


        def listen_list_objects(cls,event):
            """
            list
            """
            if 'path' in event.data:
                filter = event.data['path']
            else:
                filter = None

            self.fire('send_to',{'event':'list_{}s'.format(self.objectname), 'path':event.data['path'], 'value':self.list(filter=filter), 'clients':[event.client]})


        def listen_object(cls,event):
            """
            get or set
            """
            if 'path' in event.data:
                if event.data['path'] in self:
                    # get or set
                    obj = self[event.data['path']]

                    if 'value' in event.data:
                        # set
                        if isinstance(event.data['value'], dict):
                            value = dict(obj.value)
                            for key,val in event.data['value'].items():
                                value[key] = val
                        else:
                            value = event.data['value']

                        obj.set(value,source=event.source)

                    else:
                        # get
                        self.fire('send_to',{'event':self.objectname, 'path':event.data['path'], 'value':obj.value, 'clients':[event.client]})

                else:
                    logging.error('{} does not exist {}'.format(self.objectname.capitalize(), event.data['path']))


        setattr(ObjectPlugin, 'listen_add_{}'.format(self.objectname), classmethod(listen_add_object))
        setattr(ObjectPlugin, 'listen_delete_{}'.format(self.objectname), classmethod(listen_delete_object))
        setattr(ObjectPlugin, 'listen_list_{}s'.format(self.objectname), classmethod(listen_list_objects))
        setattr(ObjectPlugin, 'listen_{}'.format(self.objectname), classmethod(listen_object))


        # run the parent init
        super(ObjectPlugin,self).__init__()



    def list(self,filter=None):
        """
        redefine if necessary
        """
        unsortedlist = [obj.serialize() for obj in self.values() if (filter is None or filter=='' or not 'filter' in obj.value or obj.value['filter'] == filter)]
        sortedlist = sorted(unsortedlist, key=lambda obj: obj['path'])
        pathlist = [obj['path'] for obj in sortedlist]

        return pathlist


    def __getitem__(self,path):
        return self._objectdict[path]

    def __iter__(self):
        return iter(self._objectdict)

    def __contains__(self,path):
        return path in self._objectdict

    def keys(self):
        return self._objectdict.keys()

    def items(self):
        return self._objectdict.items()

    def values(self):
        return self._objectdict.values()




#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
import sys

from . import database

sys.path.append(os.path.abspath('..'))

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
    def __init__(self,queue):
        """
        Initialize a plugin instance
        
        Parameters
        ---------
        homecon : Homecon object
            the main homecon object
            
        """

        self._queue = queue
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


    def listen(self,event):
        """
        Base method to listen for events and perform actions
        
        redefine this method in a child class
        
        Parameters
        ----------
        event : Event
            an Event instance
            
        Notes
        -----
        A plugin can not send events to itself through the fire / listen methods

        Examples
        --------
        .. code-block::
            def listen(self,event):

                if event.type == 'do_something':
                    self.do_something(event)

                elif event.type == 'do_something_else':
                    self.do_something_else(event)

        """
        pass


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


        #self.homecon.fire( Event(event_type,data,source,client) )


    def _listen(self,event):
        """
        Base listener method called when an event is taken from the que
        
        checks whether this plugin is the target or if there is no target and
        then calls the code:`listen` method if so
        
        Parameters
        ----------
        event : Event
            an Event instance
            
        """

        # check if this plugin is the source and stop execution if so
        if not event.source == self:
            #self.listen(event)
            #getattr(self,'listen')(event)
            if event.type in self.listeners:
                self.listeners[event.type](event)


class Plugin(BasePlugin):
    def __init__(self,queue,states):
        """
        Initialize a plugin instance
        
        Parameters
        ---------
        states : States object
            the main states object
            
        """

        self._queue = queue
        self._loop = asyncio.get_event_loop()
        self.get_listeners()

        self.states = states

        self.initialize()


class Plugins(Plugin):
    """
    A class to manage plugins dynamically
    """
    def initialize(self):

        self.pluginfolder = 'plugins'
        self._plugins = {}

        self._db = database.Database(database='homecon.db')
        self._db_plugins = database.Table(self._db,'plugins',[
            {'name':'name', 'type':'char(255)', 'null': '', 'default':'', 'unique':'UNIQUE'},
        ])
        
        # list all plugins in the pluginfolder
        path = os.path.join( os.path.dirname(os.path.realpath(__file__)) ,'..',self.pluginfolder)
        self._availableplugins = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path,name)) and not name=='__pycache__' ]
        

        # start  plugins
        result = self._db_plugins.GET(columns=['id','name'])
        
        for p in result:
            self._start_plugin(p['name'])


    def get_plugins_list(self):
        """
        Generate a list of all available plugins and those that are active
        
        """

        pluginslist = []
        for name in self._availableplugins:

            if name in self._plugins:
                active = True
            else:
                active = False

            pluginslist.append({'name':name,'active':active})

        return pluginslist


    def get_state_config_keys(self):

        keyslist = []

        keyslist.append({'name':'states', 'keys':['type','quantity','unit','label','description']})
        keyslist.append({'name':'permissions', 'keys':['readusers','writeusers','readgroups','writegroups']})
        
        for name,plugin in self._plugins.items():
            keys = plugin.config_keys
            if len(config)>0: 
                keyslist.append({'name':name, 'keys':keys})

        return keyslist


    def activate(self,name):
        """
        Activate an available plugin by name

        """

        if name in self._availableplugins and not name in self._plugins:
            self._db_plugins.POST(name=name)
            self._start_plugin(name)

            return True
        else:
            return False


    def deactivate(self,name):
        """
        Deactivate an available plugin by name

        """
        return False


    def download(self,url):
        """
        Download a plugin from a url

        """
        return False


    def listen_list_plugins(self,event):
        self.fire('send_to',{'event':'list_plugins', 'path':'', 'value':self.get_plugins_list(), 'clients':[event.client]})
        

    def listen_list_state_config_keys(self,event):
        self.fire('send_to',{'event':'list_state_config_keys', 'path':'', 'value':self.get_state_config_keys(), 'clients':[event.client]})


    def listen_activate_plugin(self,event):
        if self.activate(event.data['plugin']):
            self.fire('send_to',{'event':'list_plugins', 'path':'', 'value':self.get_plugins_list(), 'clients':[event.client]})


    def listen_deactivate_plugin(self,event):
        if self.deactivate(event.data['plugin']):
            self.fire('send_to',{'event':'list_plugins', 'path':'', 'value':self.get_plugins_list(), 'clients':[event.client]})


    def listen_download_plugin(self,event):
        if self.download(event.data['url']):
            self.fire('send_to',{'event':'list_plugins', 'path':'', 'value':self.get_plugins_list(), 'clients':[event.client]})


    def _start_plugin(self,name,package=None):
        """
        Starts a plugin

        this attempts to load the plugin with the correct format by name from
        the plugins folder

        Parameters
        ----------
        name : string
            the filename of the plugin
    
        package : string
            package where to find the plugin, defaults to the default pluginfolder

        """

        if package is None:
            package = self.pluginfolder

        pluginmodule = __import__('{}.{}'.format(package,name), fromlist=[name])
        pluginclass = getattr(pluginmodule, name.capitalize())
        
        plugininstance = pluginclass(self._queue,self.states)
        self._plugins[name] = plugininstance


    def __getitem__(self,path):
        return self.get(path)


    def __iter__(self):
        return iter(self._plugins)


    def keys(self):
        return self._plugins.keys()


    def items(self):
        return self._plugins.items()


    def values(self):
        return self._plugins.values()




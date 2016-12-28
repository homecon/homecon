#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import os
import sys

from .. import core

class Plugins(core.plugin.Plugin):
    """
    A class to manage plugins dynamically
    """
    def initialize(self):

        self.pluginfolder = 'plugins'
        self._plugins = {}

        self._db_plugins = core.database.Table(core.db,'plugins',[
            {'name':'name', 'type':'char(255)', 'null': '', 'default':'', 'unique':'UNIQUE'},
        ])
        
        # list all plugins in the pluginfolder
        path = os.path.join( os.path.dirname(os.path.realpath(__file__)) ,'..',self.pluginfolder)
        self._availableplugins = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path,name)) and not name=='__pycache__' ]
        

        # start  plugins
        result = self._db_plugins.GET(columns=['id','name'])
        
        for p in result:
            self._start_plugin(p['name'])

        logging.debug('Plugins plugin Initialized')

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

    def get_components(self):
        
        keyslist = []

        keyslist.append({'name':'building', 'components':[
            {
                'name': 'relay',
                'states': [
                    'value',
                ]
            },
        ]})
        
        #for name,plugin in self._plugins.items():
        #    keys = plugin.components()
        #    if len(config)>0: 
        #        keyslist.append({'name':name, 'keys':keys})

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
        core.event.fire('send_to',{'event':'list_plugins', 'path':'', 'value':self.get_plugins_list(), 'clients':[event.client]})
        

    def listen_list_state_config_keys(self,event):
        core.event.fire('send_to',{'event':'list_state_config_keys', 'path':'', 'value':self.get_state_config_keys(), 'clients':[event.client]})


    def listen_activate_plugin(self,event):
        if self.activate(event.data['plugin']):
            core.event.fire('send_to',{'event':'list_plugins', 'path':'', 'value':self.get_plugins_list(), 'clients':[event.client]})


    def listen_deactivate_plugin(self,event):
        if self.deactivate(event.data['plugin']):
            core.event.fire('send_to',{'event':'list_plugins', 'path':'', 'value':self.get_plugins_list(), 'clients':[event.client]})


    def listen_download_plugin(self,event):
        if self.download(event.data['url']):
            core.event.fire('send_to',{'event':'list_plugins', 'path':'', 'value':self.get_plugins_list(), 'clients':[event.client]})


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
        
        plugininstance = pluginclass(self._queue,self._states,self._components)
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




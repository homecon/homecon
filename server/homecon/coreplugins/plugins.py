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

        logging.debug('Plugins plugin Initialized')


    def get_optionalplugins_list(self):
        """
        Generate a list of all available optional plugins and those that are active
        
        """

        pluginslist = []
        for name in core.plugins.availableplugins:

            if name in core.plugins:
                active = True
            else:
                active = False

            pluginslist.append({'name':name,'active':active})

        return pluginslist


    def get_activeplugins_list(self):
        """
        Generate a list of all active plugins, excluding core plugins
        
        """
        pluginslist = []
        for name in core.plugins.optionalplugins:

            if name in core.plugins:
                pluginslist.append(name)

        pluginslist = sorted(pluginslist)
        return pluginslist


    def get_state_config_keys(self):

        keyslist = []

        keyslist.append({'name':'states', 'keys':['type','quantity','unit','label','description']})
        keyslist.append({'name':'permissions', 'keys':['readusers','writeusers','readgroups','writegroups']})
        
        for name,plugin in core.plugins.items():
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

        if name in core.plugins.availableplugins and not name in core.plugins:
            core.plugins.activate(name)

            return True
        else:
            return False

    def deactivate(self,name):
        if name in core.plugins and name in core.plugins.optionalplugins:

            core.plugins.deactivate(name)

            return True
        else:
            return False

    

    def listen_list_optionalplugins(self,event):
        core.websocket.send({'event':'list_optionalplugins', 'path':'', 'value':self.get_optionalplugins_list()}, clients=[event.client])

    def listen_list_activeplugins(self,event):
        core.websocket.send({'event':'list_activeplugins', 'path':'', 'value':self.get_activeplugins_list()}, clients=[event.client])

    def listen_list_state_config_keys(self,event):
        core.websocket.send({'event':'list_state_config_keys', 'path':'', 'value':self.get_state_config_keys()}, clients=[event.client])

    def listen_activate_plugin(self,event):
        self.activate(event.data['plugin'])
        core.websocket.send({'event':'list_optionalplugins', 'path':'', 'value':self.get_optionalplugins_list()}, clients=[event.client])
        core.websocket.send({'event':'list_activeplugins', 'path':'', 'value':self.get_activeplugins_list()}, clients=[event.client])

    def listen_deactivate_plugin(self,event):
        self.deactivate(event.data['plugin'])
        core.websocket.send({'event':'list_optionalplugins', 'path':'', 'value':self.get_optionalplugins_list()}, clients=[event.client])
        core.websocket.send({'event':'list_activeplugins', 'path':'', 'value':self.get_activeplugins_list()}, clients=[event.client])

    def listen_download_plugin(self,event):
        if self.download(event.data['url']):
            core.websocket.send({'event':'list_optionalplugins', 'path':'', 'value':self.get_optionalplugins_list()}, clients=[event.client])



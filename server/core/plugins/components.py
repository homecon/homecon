#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import copy
import json
import inspect


from .. import plugin
from .. import components

class Components(plugin.Plugin):
    """
    Class to control the HomeCon states
    
    Each 'state' in the building should be reflected by a HomeCon state. This 
    can be the status of a light (on/off), the temperature in a room, the solar 
    irradiation, ...
    
    A state is identified by a string, its path. The predefined HomeCon States are 
    structured as if they were actual paths to folders on a unix system, using
    slashes (:code`/`). e.g. :code`settings/latitude`.
    
    Unlike a folder structure, the paths remain simple strings so 
    'parent folders' do not need to exists.
    
    The format is not manatory, any characters can be used. However, when using
    this format, parent or child states can be retrieved are available and for 
    dependent expressions some regular expression syntax can be used.
    
    """

    def list(self):
        """
        Returns a list of components
        """

        componentslist = []
        for component in self._components.values():
            componentslist.append({'path':component.path,'type':component.type,'config':component.config,'states':[states['state'].path for states in component.states.values()]})

        sortedlist = sorted(componentslist, key=lambda k: k['path'])

        return sortedlist


    def listen_list_components(self,event):
        if event.type == 'list_states':

            self.fire('send_to',{'event':'list_components', 'path':'', 'value':self.list(), 'clients':[event.client]})


    def listen_add_component(self,event):
        if event.data['type']=='value':
            component = self._components.add(event.data['path'],Value,event.data['config'])
        elif event.data['type']=='light':
            component = self._components.add(event.data['path'],Light,event.data['config'])
        elif event.data['type']=='dimminglight':
            component = self._components.add(event.data['path'],Dimminglight,event.data['config'])
        elif event.data['type']=='shading':
            component = self._components.add(event.data['path'],Shading,event.data['config'])

        if component:
            self.fire('component_added',{'component':component})
            self.fire('send_to',{'event':'list_components', 'path':'', 'value':self.list(), 'clients':[event.client]})


    def listen_edit_component(self,event):
        if event.data['path'] in self._components:

            component = self._components[event.data['path']]

            config = dict(component.config)
            for key,val in event.data['config'].items():
                config[key] = val

            self._component._db_component.PUT(config=json.dumps(config), where='path=\'{}\''.format(event.data['path']))
            component.config = config

            self.fire('send_to',{'event':'list_components', 'path':'', 'value':self.list(), 'clients':[event.client]})





class Value(components.Component):
    """
    a class implementing an basic single value
    
    """

    def initialize(self):
        self.states = {
            'value': {
                'default_config': {},
                'fixed_config': {},
            },
        }
        self.config = {
        }


class Light(components.Component):
    """
    a class implementing an on/off light
    
    """

    def initialize(self):
        self.states = {
            'value': {
                'default_config': {},
                'fixed_config': {},
            },
        }
        self.config = {
            'type': '',
            'power': '',
        }


class Dimminglight(Light):
    """
    a class implementing an dimmable light
    
    """
    def initialize(self):
        super(self).initialize()

class Shading(components.Component):
    """
    a class implementing a window shading
    
    """
    
    def initialize(self):
        self.states = {
            'position': {
                'default_config': {},
                'fixed_config': {},
            },
            'move': {
                'default_config': {},
                'fixed_config': {},
            },
            'stop': {
                'default_config': {},
                'fixed_config': {},
            },
            'auto': {
                'default_config': {},
                'fixed_config': {},
            },
        }
        self.config = {
            'type': '',
            'power': '',
        }



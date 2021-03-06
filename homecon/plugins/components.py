#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import copy
import json
import inspect


from .. import core

class Components(core.plugin.Plugin):
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

    def initialize(self):

        logging.debug('Components plugin Initialized')

    def list(self):
        """
        Returns a list of components
        """

        componentslist = []
        for component in self._components.values():
            componentslist.append({'path':component.path,'type':component.type,'config':component.config,'states':sorted([state.path for state in component.states.values()])})

        sortedlist = sorted(componentslist, key=lambda k: k['path'])

        return sortedlist

    def list_types(self):
        typeslist = []
        for key,val in self._components.types():
            typeslist.append({'type':key})


        sortedlist = sorted(typeslist, key=lambda k: k['type'])

        return sortedlist


    def listen_component_types(self,event):
            core.websocket.send({'event':'component_types', 'path':'', 'value':self.list_types()}, clients=[event.client])

    def listen_list_components(self,event):
            core.websocket.send({'event':'list_components', 'path':'', 'value':self.list()}, clients=[event.client])

    def listen_add_component(self,event):

        component = self._components.add(event.data['path'],event.data['type'],event.data['config'])
        
        if component:
            self.fire('component_added',{'component':component})
            core.websocket.send({'event':'list_components', 'path':'', 'value':self.list()}, clients=[event.client])
            self.fire('list_states',{},client=event.client)

    def listen_delete_component(self,event):

        if core.components.delete(event.data['path']):
            core.websocket.send({'event':'list_components', 'path':'', 'value':self.list()}, clients=[event.client])


    def listen_edit_component(self,event):
        if event.data['path'] in self._components:

            component = self._components[event.data['path']]

            config = dict(component.config)
            for key,val in event.data['config'].items():
                config[key] = val

            component.config = config

            core.websocket.send({'event':'list_components', 'path':'', 'value':self.list()}, clients=[event.client])




class Value(core.component.Component):
    """
    a class implementing an basic single value
    
    """
    default_config = {
    }
    linked_states = {
        'value': {
            'default_config': {},
            'fixed_config': {},
        },
    }

core.components.register(Value)



#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from homecon.core.plugin import Plugin
from homecon.core.state import State
from homecon.core.database import get_database

from .. import util
from .authentication import jwt_decode


logger = logging.getLogger(__name__)


class States(Plugin):
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
    def __init__(self):
        super().__init__()
        self.triggers = {}

    def initialize(self):
        # add settings states
        State.add('settings')
        State.add('location', parent='/settings')
        State.add('latitude', parent='/settings/location',
                  config={'type': 'number', 'quantity': 'angle',  'unit': 'deg',
                          'label': 'Latitude',  'description': 'HomeCon latitude',
                          'private': True}, value=51.05)
        State.add('longitude', parent='/settings/location',
                  config={'type': 'number', 'quantity': 'angle',  'unit': 'deg',
                          'label': 'Longitude', 'description': 'HomeCon longitude',
                          'private': True}, value=5.5833)
        State.add('elevation', parent='/settings/location',
                  config={'type': 'number', 'quantity': 'height', 'unit': 'm',
                          'label': 'Elevation', 'description': 'HomeCon elevation',
                          'private': True}, value=74.0)
        State.add('timezone', parent='/settings/location',
                  config={'type': 'string', 'quantity': '',       'unit': '',
                          'label': 'Time zone', 'description': 'HomeCon time zone',
                          'private': True}, value='Europe/Brussels')

        State.add('ground_floor')
        State.add('kitchen', parent='/ground_floor')
        State.add('lights', parent='/ground_floor/kitchen')
        State.add('light', parent='/ground_floor/kitchen/lights',
                  config={'type': 'boolean', 'quantity': '', 'unit': '',
                          'label': 'Kitchen light', 'description': ''})
        logger.debug('States plugin Initialized')

    def parse_triggers(self):
        for path in State.all_paths():
            self.triggers[path] = {}
            state = State.get(path=path)
            for path in state.triggers:
                if path in self._states and state not in self._states[path].trigger:
                    self._states[path].trigger.append(state)

    # def list(self):
    #     """
    #     Returns a list of states which can be edited
    #     """
    #
    #     stateslist = []
    #     for state in core.states.values():
    #         if not 'private' in state.config or not state.config['private']:
    #             stateslist.append({'path': state.path, 'config': state.config})
    #
    #     newlist = sorted(stateslist, key=lambda k: k['path'])
    #
    #     return newlist

    # def listen_list_states(self, event):
    #     if event.type == 'list_states':
    #         core.websocket.send({'event': 'list_states', 'path': '', 'value': self.list()}, clients=[event.client])
    #
    # def listen_add_state(self, event):
    #     state = core.states.add(event.data['path'], config=event.data['config'])
    #
    #     if state:
    #         core.event.fire('state_added', {'state': state})
    #         core.websocket.send({'event': 'list_states', 'path': '', 'value': self.list()}, clients=[event.client])
    #
    # def listen_edit_state(self,event):
    #     if event.data['path'] in core.states:
    #
    #         state = core.states[event.data['path']]
    #
    #         config = dict(state.config)
    #         for key,val in event.data['config'].items():
    #             config[key] = val
    #
    #         state.config = config
    #         core.states.parse_triggers()
    #
    #         core.websocket.send({'event':'list_states', 'path':'', 'value':self.list()}, clients=[event.client])
    #
    # def listen_state_config(self,event):
    #     if event.data['path'] in core.states:
    #
    #         state = core.states[event.data['path']]
    #
    #         if not 'value' in event.data:
    #             core.websocket.send({'event':'state_config', 'path':state.path, 'value':state.config}, clients=[event.client])
    #
    #         else:
    #             logger.warning('listen_state_config, edit state config :' + state.path)
    #             #config = dict(state.config)
    #             #for key,val in event.data['config'].items():
    #             #    config[key] = val
    #
    #             #state.config = config
    #             #core.websocket.send({'event':'state_config', 'path':state.path, 'value':state.config}, clients=[event.client])
    #             #core.websocket.send({'event':'list_states', 'path':'', 'value':self.list()}, clients=[event.client])

    def listen_state_changed(self,event):
        #core.event.fire('send',{'event':'state', 'path':event.data['state'].path, 'value':event.data['state'].value, 'readusers':event.data['state'].config['readusers'], 'readgroups':event.data['state'].config['readgroups']},source=self)
        # core.websocket.send({'event':'state', 'path':event.data['state'].path, 'value':event.data['state'].value}, readusers=event.data['state'].config['readusers'], readgroups=event.data['state'].config['readgroups'])
        #
        # if event.data['state'].path == 'settings/location/timezone':
        #     util.time.set_timezone(event.data['value'])
        pass

    def listen_state_value(self, event):
        if 'id' in event.data and 'value' not in event.data:
            state = State.get(id=event.data['id'])
            if state is not None:
                event.reply('websocket_reply', {'event': 'state_value', 'data': {'id': event.data['id'],
                                                                                  'value': state.value}})
        elif 'path' in event.data and 'value' not in event.data:
            state = State.get(path=event.data['path'])
            if state is not None:
                event.reply('websocket_reply', {'event': 'state_value',
                                                'data': {'path': event.data['path'], 'value': state.value}})

        elif 'id' in event.data and 'value' in event.data:
            state = State.get(id=event.data['id'])
            if state is not None:
                state.value = event.data['value']

        elif 'path' in event.data and 'value' in event.data:
            state = State.get(path=event.data['path'])
            if state is not None:
                state.value = event.data['value']

    #
    # def listen_state(self, event):
    #     if 'path' in event.data:
    #         if event.data['path'] in State.all_paths():
    #             state = State.get(event.data['path'])
    #             tokenpayload = jwt_decode(event.data['token'])
    #
    #             if 'value' in event.data:
    #                 # set
    #                 permitted = False
    #                 if tokenpayload and tokenpayload['userid'] in state.config['writeusers']:
    #                     permitted = True
    #                 else:
    #                     for g in tokenpayload['groupids']:
    #                         if g in state.config['writegroups']:
    #                             permitted = True
    #                             break
    #
    #                 if permitted:
    #                     value = event.data['value']
    #                     if 'type' in state.config and state.config['type'] == 'number':
    #                         value = float(value)
    #
    #                     state.set(value,source=event.source)
    #
    #                 else:
    #                     logging.warning('User {} on client {} attempted to change the value of {} but is not permitted'.format(tokenpayload['userid'],event.client.address,state.path))
    #
    #             else:
    #                 # get
    #                 permitted = False
    #                 if tokenpayload and tokenpayload['userid'] in state.config['readusers']:
    #                     permitted = True
    #                 elif tokenpayload:
    #                     for g in tokenpayload['groupids']:
    #                         if g in state.config['readgroups']:
    #                             permitted = True
    #                             break
    #
    #                 if permitted:
    #                     core.websocket.send({'event':'state', 'path':state.path, 'value':state.value}, clients=[event.client], readusers=state.config['readusers'] ,readgroups=state.config['readgroups'])
    #                 else:
    #                     logging.warning('User {} attempted to change the value of {} but is not permitted'.format(tokenpayload['userid'],state.path))
    #
    #
    # def listen_send_states_to(self, event):
    #
    #     for state in core.states.values():
    #         core.websocket.send({'event':'state', 'path':state.path, 'value':state.value}, clients=event.data['clients'], readusers=state.config['readusers'] ,readgroups=state.config['readgroups'])
    #

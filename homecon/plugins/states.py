#!/usr/bin/env python3
import logging
import time
import json

from homecon.core.event import Event
from homecon.core.plugins.plugin import BasePlugin


logger = logging.getLogger(__name__)


class States(BasePlugin):
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
    def __init__(self, *args, now=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_update_timestamp = now or time.time()

        self.triggers = {}
        # add settings states
        s = self._state_manager.add('settings', type=None)
        sl = self._state_manager.add('location', type=None, parent=s)
        self._state_manager.add('latitude', parent=sl,
                                type='float', quantity='angle', unit='deg',
                                label='Latitude', description='HomeCon latitude', value=51.05)
        self._state_manager.add('longitude', parent=sl,
                                type='float', quantity='angle', unit='deg',
                                label='Longitude', description='HomeCon longitude', value=5.58)
        self._state_manager.add('elevation', parent=sl,
                                type='float', quantity='height', unit='m',
                                label='Elevation', description='HomeCon elevation', value=74.0)
        self._state_manager.add('timezone', parent=sl,
                                type='str', quantity='', unit='',
                                label='Time zone', description='HomeCon time zone', value='Europe/Brussels')

    def start(self):
        logger.debug('States plugin Initialized')

    #
    # def parse_triggers(self):
    #     for path in State.all_paths():
    #         self.triggers[path] = {}
    #         state = State.get(path=path)
    #         for path in state.triggers:
    #             if path in self._states and state not in self._states[path].trigger:
    #                 self._states[path].trigger.append(state)

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

    def listen_state(self, event: Event):
        if 'id' in event.data:
            state = self._state_manager.get(id=event.data['id'])
            event.reply({'id': event.data['id'], 'value': state.serialize()})

    def listen_state_value(self, event: Event):
        logger.info(event)
        if 'id' in event.data and 'value' not in event.data:
            state = self._state_manager.get(id=event.data['id'])
            if state is not None:
                event.reply({'id': event.data['id'], 'value': state.value})
        elif 'path' in event.data and 'value' not in event.data:
            state = self._state_manager.get(path=event.data['path'])
            if state is not None:
                event.reply({'path': event.data['path'], 'value': state.value})

        elif 'id' in event.data and 'value' in event.data:
            state = self._state_manager.get(id=event.data['id'])
            if state is not None:
                state.value = event.data['value']

        elif 'path' in event.data and 'value' in event.data:
            state = self._state_manager.get(path=event.data['path'])
            if state is not None:
                state.value = event.data['value']

    # def listen_state_children(self, event):
    #     if 'id' in event.data:
    #         if event.data['id'] is None or int(event.data['id']) == 0:
    #             states = [s.serialize() for s in State.all() if s.parent is None]
    #         else:
    #             parent = State.get(id=int(event.data['id']))
    #             if parent is not None:
    #                 states = [s.serialize() for s in parent.children]
    #             else:
    #                 raise Exception('parent does not exist')
    #         event.reply('websocket_reply', {'event': 'state_children',
    #                                         'data': {'id': event.data['id'],
    #                                                  'value': states}})

    def listen_state_list(self, event: Event):
        states = [s.serialize() for s in self._state_manager.all()]
        event.reply({'id': '', 'value': states})

    def listen_state_add(self, event):
        kwargs = dict(event.data)
        name = kwargs.pop('name')
        self._state_manager.add(name, **kwargs)

    def listen_state_update(self, event):
        if 'id' in event.data:
            kwargs = dict(event.data)
            id = kwargs.pop('id')
            state = self._state_manager.get(id=id)

            if state is not None:
                state.update(**kwargs)
            else:
                logger.error('cannot update state, state not found')

        else:
            logger.error('cannot update state, no id supplied')

    def listen_state_delete(self, event):
        if 'id' in event.data:
            state = self._state_manager.get(id=event.data['id'])
            state.delete()

    def listen_export_states(self, event):
        event.reply({'id': '', 'value': json.dumps(self._state_manager.export_states(), indent=2)})

    def listen_import_states(self, event):
        self._state_manager.import_states(json.loads(event.data['value']))

    @property
    def settings_sections(self):
        sections = [{
            'config': {
                'title': 'Location'
            },
            'widgets': [{
                'type': 'value-input',
                'config': {
                    'state': self._state_manager.get(path='/settings/location/timezone').id,
                    'label': 'Timezone',
                }
            }, {
                'type': 'value-input',
                'config': {
                    'state': self._state_manager.get(path='/settings/location/longitude').id,
                    'label': 'Longitude',
                }
            }, {
                'type': 'value-input',
                'config': {
                    'state': self._state_manager.get(path='/settings/location/latitude').id,
                    'label': 'Latitude',
                }
            }, {
                'type': 'value-input',
                'config': {
                    'state': self._state_manager.get(path='/settings/location/elevation').id,
                    'label': 'Elevation',
                }
            }]
        }]
        return sections


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

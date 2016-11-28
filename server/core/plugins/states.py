#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from .. import plugin

class States(plugin.Plugin):
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
        logging.debug('States plugin Initialized')

    def get(self,path):
        """
        gets a state given its path
        
        Parameters
        ----------
        path : string
            the state path

        Returns
        -------
        state : State
            the state or :code`None`if the state is unknown

        """

        if path in self._states:
            return self._states[path]
        else:
            logging.error('State {} is not defined'.format(path))
            return None

    def list(self):
        """
        Returns a list of states which can be edited
        """

        stateslist = []
        for state in self._states.values():
            stateslist.append({'path':state.path,'config':sorted([{'key':key,'value':val} for key,val in state.config.items()],key=lambda x:x['key'])})

        newlist = sorted(stateslist, key=lambda k: k['path'])

        return newlist


    def listen_list_states(self,event):
        if event.type == 'list_states':

            self.fire('send_to',{'event':'list_states', 'path':'', 'value':self.list(), 'clients':[event.client]})


    def listen_add_state(self,event):
        state = self._states.add(event.data['path'],event.data['config'])

        if state:
            self.fire('state_added',{'state':state})
            self.fire('send_to',{'event':'list_states', 'path':'', 'value':self.list(), 'clients':[event.client]})


    def listen_edit_state(self,event):
        if event.data['path'] in self._states:

            state = self._states[event.data['path']]

            config = dict(state.config)
            for key,val in event.data['config'].items():
                config[key] = val

            state.config = config

            self.fire('send_to',{'event':'list_states', 'path':'', 'value':self.list(), 'clients':[event.client]})


    def listen_state_changed(self,event):
        self.fire('send',{'event':'state', 'path':event.data['state'].path, 'value':event.data['state'].value, 'readusers':event.data['state'].config['readusers'], 'readgroups':event.data['state'].config['readgroups']},source=self)


    def listen_state(self,event):
        # get or set a state
        if 'path' in event.data:
            state = self.get(event.data['path'])

            if not state is None:
                tokenpayload = event.client.tokenpayload  # event.data['token']  fixme, retrieve the payload from the token

                
                if 'value' in event.data:
                    # set
                    permitted = False
                    if tokenpayload['userid'] in state.config['writeusers']:
                        permitted = True
                    else:
                        for g in tokenpayload['groupids']:
                            if g in state.config['writegroups']:
                                permitted = True
                                break

                    if permitted:
                        state.set(event.data['value'],event.source)
                    else:
                        logging.warning('User {} on client {} attempted to change the value of {} but is not permitted'.format(tokenpayload['userid'],event.client.address,state.path))

                else:
                    # get
                    permitted = False
                    if tokenpayload['userid'] in state.config['readusers']:
                        permitted = True
                    else:
                        for g in tokenpayload['groupids']:
                            if g in state.config['readgroups']:
                                permitted = True
                                break

                    if permitted:
                        self.fire('send_to',{'event':'state', 'path':state.path, 'value':state.value, 'clients':[event.client]})
                    else:
                        logging.warning('User {} attempted to change the value of {} but is not permitted'.format(tokenpayload['userid'],state.path))


    def listen_send_states_to(self,event):
        for client in event.data['clients']:
            tokenpayload = client.tokenpayload  # event.data['token']  fixme, retrieve the payload from the token

            for state in self._states.values():
                permitted = False
                if tokenpayload['userid'] in state.config['readusers']:

                    permitted = True
                else:
                    for g in tokenpayload['groupids']:
                        if g in state.config['readgroups']:
                            permitted = True
                            break

                if permitted:
                    self.fire('send_to',{'event':'state', 'path':state.path, 'value':state.value, 'clients':[client]})






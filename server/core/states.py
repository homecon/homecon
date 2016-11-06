#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import copy
import json
import inspect

from . import database
from .plugin import BasePlugin

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

    def initialize(self):
        self._states = {}
        self._db = database.Database(database='homecon.db')
        self._db_states = database.Table(self._db,'states',[
            {'name':'path',   'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'config', 'type':'char(511)',  'null': '',  'default':'',  'unique':''},
            {'name':'value',  'type':'char(255)',  'null': '',  'default':'',  'unique':''},
        ])

        # get all states from the database
        result = self._db_states.GET()
        for s in result:
            state = State(self,s['path'],config=json.loads(s['config']))
            state.get_value_from_db()
            self._states[s['path']] = state

        # add settings states
        self.add('settings/latitude', config={'type': 'number', 'quantity':'angle', 'unit':'deg','label':'latitude', 'description':'HomeCon latitude'})
        self.add('settings/longitude',config={'type': 'number', 'quantity':'angle', 'unit':'deg','label':'longitude','description':'HomeCon longitude'})
        self.add('settings/elevation',config={'type': 'number', 'quantity':'height','unit':'m',  'label':'elevation','description':'HomeCon elevation'})
        self.add('settings/timezone', config={'type': 'string', 'quantity':'',      'unit':'',   'label':'time zone','description':'HomeCon time zone'})


    def add(self,path,config=None):
        """
        add a state

        Parameters
        ----------
        path : string
            the state path
        
        config : dict
            state configuration dictionary

        """

        if not path in self._states:

            # check the config
            if config is None:
                config = {}

            if 'type' not in config:
                config['type'] = ''

            if 'quantity' not in config:
                config['quantity'] = ''

            if 'unit' not in config:
                config['unit'] = ''

            if 'label' not in config:
                config['label'] = ''

            if 'description' not in config:
                config['description'] = ''

            if 'readusers' not in config:
                config['readusers'] = []

            if 'writeusers' not in config:
                config['writeusers'] = []

            if 'readgroups' not in config:
                config['readgroups'] = [1]

            if 'writegroups' not in config:
                config['writegroups'] = [1]


            state = State(self,path,config=config)
            self._db_states.POST(path=path,config=json.dumps(config))
            self._states[path] = state

            # update the value from the database
            state.get_value_from_db()

            return state
        else:
            return False

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

    def get_states_list(self):
        """
        Returns a list of states which can be edited
        """

        stateslist = []
        for state in self._states.values():
            if not state.path.split('/')[0] in ['settings','plugins']:
                stateslist.append({'path':state.path,'config':state.config})

        newlist = sorted(stateslist, key=lambda k: k['path'])

        return newlist


    def listen(self,event):
        """
        Listen for events

        """
        if event.type == 'list_states':

            self.fire('send_to',{'event':'list_states', 'path':'', 'value':self.get_states_list(), 'clients':[event.client]})


        if event.type == 'add_state':
            state = self.add(event.data['path'],event.data['config'])

            if state:
                self.fire('state_added',{'state':state})
                self.fire('send_to',{'event':'list_states', 'path':'', 'value':self.get_states_list(), 'clients':[event.client]})
        

        if event.type == 'edit_state':
            if event.data['path'] in self._states:

                state = self._states[event.data['path']]
                for key,val in event.data['config'].items():
                    state.config[key] = val

                self.fire('send_to',{'event':'list_states', 'path':'', 'value':self.get_states_list(), 'clients':[event.client]})


        if event.type == 'state_changed':
            self.fire('send',{'event':'state', 'path':event.data['state'].path, 'value':event.data['state'].value, 'readusers':event.data['state'].config['readusers'], 'readgroups':event.data['state'].config['readgroups']},source=event.source)


        if event.type == 'state':

            # get or set a state
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
                    


    def __getitem__(self,path):
        return self.get(path)


    def __iter__(self):
        return iter(self._states)


    def keys(self):
        return self._states.keys()


    def items(self):
        return self._states.items()


    def values(self):
        return self._states.values()




class State(object):
    """
    A class representing a single state

    """

    def __init__(self,states,path,config=None):
        """
        Parameters
        ----------
        states : States object
            the states object
        
        path : string
            the item identifier relations between states (parent - child) can be
            indicated with dots

        config : dict
            dictionary configuring the state
        
        """
        self._states = states
        self._path = path

        if config == None:
            self.config = {}
        else:
            self.config = config 

        self._value = None


    def set(self,value,source=None):
        oldvalue = copy.copy(self._value)
        self._value = value

        # update the value in the database
        self._states._db_states.PUT(value=json.dumps(value), where='path=\'{}\''.format(self.path))

        self._states.fire('state_changed',{'state':self,'value':self._value,'oldvalue':oldvalue},source)


    def get(self):
        return self._value

    def get_value_from_db(self):
        result = self._states._db_states.GET(path=self.path,columns=['value'])
        value = result[0]['value']
        if not value is None:
            self._value = json.loads(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # get the source from inspection
        
        self.set(value,source=self)

    @property
    def path(self):
        return self._path


    @property
    def parent(self):
        """
        returns the parent of the current state when the paths follow the slash
        syntax according to :code`parent/child`

        Example
        -------
        >>> p = states.add('parent')
        >>> c = states.add('parent/child')
        >>> c.return_parent()
        
        """

        if '/' in self._path:
            parentpath = '/'.join(self._path.split('/')[:-1])
            parent = self._states.get(parentpath)
            return parent
        else:
            return None


    @property
    def children(self):
        """
        returns a list of children of the current state when the paths follow 
        the slash syntax according to :code`parent/child`

        Example
        -------
        >>> p = states.add('parent')
        >>> c0 = states.add('parent/child0')
        >>> c1 = states.add('parent/child1')
        >>> cc = states.add('parent/child0/child')
        >>> p.return_children()
        
        """

        children = []
        for path,state in self._states.items():
            if self._path in path:
                if len(self._path.split('/')) == len(path.split('/'))-1:
                    children.append(state)

        return children


    def __call__(self):
        return self._value


    def __str__(self):
        return self._path


    def __repr__(self):
        return '<state {} value={}>'.format(self._path,self._value)


        

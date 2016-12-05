#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import copy
import inspect

from . import database
from . import plugin

class States(plugin.BasePlugin):
    """
    a container class for states with access to the database

    """

    def __init__(self,queue):
        super(States,self).__init__(queue)

        self._states = {}
        self._db = database.Database(database='homecon.db')
        self._db_states = database.Table(self._db,'states',[
            {'name':'path',   'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'config', 'type':'char(511)',  'null': '',  'default':'',  'unique':''},
            {'name':'value',  'type':'char(255)',  'null': '',  'default':'',  'unique':''},
        ])

        # get all states from the database
        result = self._db_states.GET()
        for state in result:
            self.add(state['path'],config=json.loads(state['config']))


        # add settings states
        self.add('settings/location/latitude', config={'type': 'number', 'quantity':'angle', 'unit':'deg','label':'latitude', 'description':'HomeCon latitude'})
        self.add('settings/location/longitude',config={'type': 'number', 'quantity':'angle', 'unit':'deg','label':'longitude','description':'HomeCon longitude'})
        self.add('settings/location/elevation',config={'type': 'number', 'quantity':'height','unit':'m',  'label':'elevation','description':'HomeCon elevation'})
        self.add('settings/location/timezone', config={'type': 'string', 'quantity':'',      'unit':'',   'label':'time zone','description':'HomeCon time zone'})


    def add(self,path,config=None):
        """
        add a state

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

            if 'log' not in config:
                config['log'] = True

            # check if the state is in the database and add it if not
            if len( self._db_states.GET(path=path) ) == 0:
                self._db_states.POST(path=path,config=json.dumps(config))

            # create the state
            state = State(self,path,config=config)
            self._states[path] = state

            # update the value from the database
            try:
                state.get_value_from_db()
            except:
                pass

            return state
        else:
            return False


    def __getitem__(self,path):
        return self._states[path]


    def __iter__(self):
        return iter(self._states)


    def __contains__(self,path):
        return path in self._states


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
            self._config = {}
        else:
            self._config = config 

        self._value = None


    def set(self,value,source=None):
        oldvalue = copy.copy(self._value)
        self._value = value

        # update the value in the database
        self._states._db_states.PUT(value=json.dumps(value), where='path=\'{}\''.format(self._path))

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
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._states._db_states.PUT(config=json.dumps(config), where='path=\'{}\''.format(self._path))
        self._config=config

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
            parent = self._states[parentpath]
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


        

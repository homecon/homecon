#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import copy
import inspect
import asyncio
import math

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
        for db_entry in result:
            self.add(db_entry['path'],db_entry=db_entry)


    def add(self,path,config=None,db_entry=None):
        """
        add a state

        """

        if not path in self._states:

            state = State(self,self._db_states,path,config=config,db_entry=db_entry)
            self._states[path] = state

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


class BaseState(object):
    """
    A base class for objects identified by a path with a config and a value
    attribute which are backed by the database

    """

    def __init__(self,plugin,db_table,path,config=None,value=None,db_entry=None):
        """
        Parameters
        ----------
        plugin : homecon.plugin.BasePlugin
            A base plugin or plugin
        
        db_table: homecon.database.table
            a database table where things are stored
            the database table must have a path, config and value column

        path : string
            the item identifier relations between states (parent - child) can be
            indicated with dots

        db_entry : dict
            if the state was loaded from the database, the database entry must
            be supplied as a dictionary with `config` and `value` keys

        config : dict
            dictionary configuring the state
        
        """

        self._plugin = plugin
        self._loop = asyncio.get_event_loop()
        self._db_table = db_table
        self._path = path


        if db_entry is None:
            self._config = self._check_config(config)
            self._value = self._check_value(value)

            # post to the database
            self._db_table.POST(path=self._path,config=json.dumps(self._config))

        else:
            # update the config from the database
            jsonconfig = db_entry['config']
            if not jsonconfig is None:
                config = json.loads(jsonconfig)
            else:
                config = None

            self._config = self._check_config(config)

            # update the value from the database
            jsonvalue = db_entry['value']
            if not jsonvalue is None:
                value = json.loads(jsonvalue)

                if 'type' in self._config and self._config['type']=='number':
                    value = float(value)

                    if math.isnan(value):
                        value = None
            else:
                value = None

            self._value = self._check_value(value)


    def fire_changed(self,value,oldvalue,source):
        """
        """
        pass


    async def set(self,value,source=None):
        oldvalue = copy.copy(self._value)

        if not value == oldvalue:
            self._value = value

            # update the value in the database
            self._db_table.PUT(value=json.dumps(value), where='path=\'{}\''.format(self._path))

            self.fire_changed(self._value,oldvalue,source)
            await asyncio.sleep(0.01) # avoid flooding asyncio

    def get(self):
        return self._value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # get the source from inspection
        stack = inspect.stack()
        source = stack[1][0].f_locals["self"].__class__

        self._loop.create_task(self.set(value,source=source))
        

    @property
    def path(self):
        return self._path

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._db_table.PUT(config=json.dumps(config), where='path=\'{}\''.format(self._path))
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

            if parentpath in self._plugin:
                return self._plugin[parentpath]

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
        for path,state in self._plugin.items():
            if self._path in path:
                if len(self._path.split('/')) == len(path.split('/'))-1:
                    children.append(state)

        return children


    def _check_config(self,config):
        """
        Checks the config for required keys

        """

        if config is None:
            config = {}
        if 'readusers' not in config:
            config['readusers'] = []
        if 'writeusers' not in config:
            config['writeusers'] = []
        if 'readgroups' not in config:
            config['readgroups'] = [1]
        if 'writegroups' not in config:
            config['writegroups'] = [1]

        return config

    def _check_value(self,value):
        """
        Checks the value for required keys

        """

        return value

    def __call__(self):
        return self._value


    def __str__(self):
        return self._path


    def __repr__(self):
        return '<BaseState {} value={}>'.format(self._path,self._value)


class State(BaseState):
    """
    A class representing a single state

    """

    def fire_changed(self,value,oldvalue,source):
        """
        """
        self._plugin.fire('state_changed',{'state':self,'value':value,'oldvalue':oldvalue},source)

    def _check_config(self,config):

        config = super(State,self)._check_config(config)

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
        if 'log' not in config:
            config['log'] = True

        return config

    def __repr__(self):
        return '<State {} value={}>'.format(self._path,self._value)



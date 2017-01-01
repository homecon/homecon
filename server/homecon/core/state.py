#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import copy
import inspect
import asyncio
import math
import datetime

from . import database
from . import event


class BaseState(object):
    """
    A base class for objects identified by a path with a config and a value
    attribute which are backed by the database



    Redefinable attributes
    ----------------------
    db_table : homecon.database.table
        A database table where things are stored.
        The database table must have a path, config and value column

    container : dict
        Must be redefined with an empty dictionary in a subclass.
        This is a bit hacky but otherwise the BaseState container is used to
        reference objects
    """

    db_table = database.Table(database.db,'states',[
        {'name':'path',   'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
        {'name':'config', 'type':'char(511)',  'null': '',  'default':'',  'unique':''},
        {'name':'value',  'type':'char(255)',  'null': '',  'default':'',  'unique':''},
    ])

    container = {}

    def __new__(cls,path,config=None,value=None,db_entry=None):
        if path in cls.container:
            return None
        else:
            return super(BaseState, cls).__new__(cls)


    def __init__(self,path,config=None,value=None,db_entry=None):
        """
        Parameters
        ----------
        path : string
            the item identifier relations between states (parent - child) can be
            indicated with dots

        db_entry : dict
            if the state was loaded from the database, the database entry must
            be supplied as a dictionary with `config` and `value` keys

        config : dict
            dictionary configuring the state
        
        component : str
            if the state belongs to a component, the path of the components can 
            be passes
        """

        self._loop = asyncio.get_event_loop()
        self._path = path

        if db_entry is None:

            # check if the path allready exists in the database
            result = self.db_table.GET(path=self._path)
            if len(result) == 0:
                self._config = self._check_config(config)
                self._value = self._check_value(value)

                # post to the database
                self.db_table.POST(path=self._path,config=json.dumps(self._config),value=json.dumps(self._value))

                # get the id
                result = self.db_table.GET(path=self._path)
                self._id = result[0]['id']
            else:
                # create the db_entry
                db_entry = result[0]


        if not db_entry is None:
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

                if 'type' in self._config and self._config['type']=='number' and not value is None:
                    value = float(value)

                    if math.isnan(value):
                        value = None
            else:
                value = None

            self._value = self._check_value(value)

            # add an id value
            self._id = db_entry['id']


        # add self to _sice
        self.container[self._path] = self

    def fire_changed(self,value,oldvalue,source):
        """
        """
        pass


    def set(self,value,source=None):
        """
        Sets the value by creating a task to set the value

        Parameters
        ----------
        value : 
            the new value

        source : class
            a class, the source setting the value, if not supplied it is 
            determined by ispection

        """

        if source is None:
            # get the source from inspection
            stack = inspect.stack()
            source = stack[1][0].f_locals["self"].__class__

        self._loop.create_task(self.set_async(value,source=source))


    async def set_async(self,value,source=None):
        """
        Sets the value async, should be awaited for

        Parameters
        ----------
        value : 
            the new value

        source : class
            a class, the source setting the value, if not supplied it is 
            determined by ispection

        Example
        -------
        state = states['somepath']
        await state.set_async(10)

        """

        oldvalue = copy.copy(self._value)

        # make sure value is valid
        value = self._check_value(value)

        # if the new and old value are different update and put in the database
        if not value == oldvalue:
            self._value = value

            # update the value in the database
            self.db_table.PUT(value=json.dumps(value), where='path=\'{}\''.format(self._path))

            # check the source
            if source is None:
                # get the source from inspection
                stack = inspect.stack()
                source = stack[1][0].f_locals["self"].__class__

            self.fire_changed(self._value,oldvalue,source)
            await asyncio.sleep(0.01) # avoid flooding asyncio


    def get(self):
        """
        Returns the current value

        """
        return self._value

    def delete(self):

        self.db_table.DELETE(path=self._path)

        # remove the object from the local reference
        del self.container[self._path]



    def serialize(self):
        """
        return a dict representation of the instance

        """

        data = {
            'id': self.id,
            'path': self.path,
            'config': json.dumps(self.config),
            'value': json.dumps(self.value),
        }
        return data




    @property
    def id(self):
        return self._id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.set(value)

    @property
    def path(self):
        return self._path

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        config = self._check_config(config)
        self.db_table.PUT(config=json.dumps(config), where='path=\'{}\''.format(self._path))
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

            if parentpath in self.container:
                return self.container[parentpath]

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
        for path,state in self.container.items():
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
        elif not 1 in config['readgroups']:
            config['readgroups'].append(1)
        if 'writegroups' not in config:
            config['writegroups'] = [1]
        elif not 1 in config['writegroups']:
            config['writegroups'].append(1)

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

    db_table = database.Table(database.db,'states',[
        {'name':'path',   'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
        {'name':'config', 'type':'char(511)',  'null': '',  'default':'',  'unique':''},
        {'name':'value',  'type':'char(255)',  'null': '',  'default':'',  'unique':''},
    ])
    db_history = database.Table(database.measurements_db,'measurements',[
        {'name':'time',   'type':'INT',   'null': '',  'default':'',  'unique':''},
        {'name':'path',   'type':'TEXT',  'null': '',  'default':'',  'unique':''},
        {'name':'value',  'type':'TEXT',  'null': '',  'default':'',  'unique':''},
    ])
    container = {}

    def fire_changed(self,value,oldvalue,source):
        """
        """
        event.fire('state_changed',{'state':self,'value':value,'oldvalue':oldvalue},source,None)


    def _check_config(self,config):
        """
        """
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


    @property
    def component(self):
        return self._component

    def history(self,datetime,interpolation='linear'):
        """
        return the history of a state

        Parameters
        ----------
        datetime : datetime.datetime or list of datetime.datetimes
            time to return the history

        """

        datetime_ref = datetime.datetime(1970,1,1)

        if hasattr(datetime, "__len__"):
            timestamps = [int( (t-datetime_ref).total_seconds() ) for t in datetime]
        else:
            timestamps = [int( (datetime-datetime_ref).total_seconds() )]


        # retrieve data from the database
        result = self.db_history.GET(path=self.path,time__ge=timestamps[0]-3600,time__le=timestamps[-1]+3600)
        if len(result)>0:
            db_timestamps = [res['time'] for res in result]
            db_values = [res['value'] for res in result]

        else:
            # did not find any value, expand the horizon
            db_timestamps = [res['time'] for res in result]
            db_values = [res['value'] for res in result]

        return 0

        if hasattr(datetime, "__len__"):
            return values
        else:
            return values[0]



    def __repr__(self):
        formattedvalue = '{}'.format(self._value)
        if len(formattedvalue) > 10:
            formattedvalue = formattedvalue[:9] + ' ... ' + formattedvalue[-1]

        return '<State {} value={}>'.format(self._path,formattedvalue)



class States(object):
    """
    a container class for states with access to the database

    """

    def __init__(self):

        self._states = State.container
        self._db_states = State.db_table

        # get all states from the database
        result = self._db_states.GET()
        for db_entry in result:
            self.add(db_entry['path'],db_entry=db_entry)


    def add(self,path,config=None,db_entry=None):
        """
        add a state

        """

        return State(path,config=config,db_entry=db_entry)



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



# create the components container
states = States()

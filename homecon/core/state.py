#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import copy
import inspect
import math
import numpy as np
import threading
from scipy.interpolate import interp1d

from homecon.core.database import get_database, get_measurements_database, Field, DatabaseObject
from homecon.core.event import Event


logger = logging.getLogger(__name__)


class State(DatabaseObject):

    def __init__(self, id=None, path=None, config=None, value=None):
        super().__init__(id=id)
        self._path = path
        self._config = json.loads(config) or {}
        self._value = json.loads(value)

    @staticmethod
    def get_table():
        db = get_database()
        if 'states' in db:
            table = db.states
        else:
            table = db.define_table(
                'states',
                Field('path', type='string', default='', unique=True),
                Field('config', type='string', default='{}'),
                Field('value', type='string'),
            )
        return db, table

    @classmethod
    def get(cls, path=None, id=None):
        if id is not None:
            db, table = cls.get_table()
            entry = table(id)
            db.close()
        elif path is not None:
            db, table = cls.get_table()
            entry = table(path=path)
            db.close()
        else:
            raise Exception('id or path must be supplied')

        if entry is not None:
            return cls(**entry.as_dict())
        else:
            return None

    @classmethod
    def add(cls, path, config=None, value=None):
        """
        Add a state to the database
        """
        # check if it already exists
        db, table = cls.get_table()
        entry = table(path=path)
        if entry is None:
            id = table.insert(path=path, config=json.dumps(config or '{}'), value=json.dumps(value))
            db.close()
            # get the state FIXME error checking
            obj = cls.get(id=id)
            logger.debug('added state')
            Event.fire('state_added', {'state': obj}, 'State')
        else:
            obj = cls(**entry.as_dict())
        return obj

    @property
    def path(self):
        self._path = self.get_property('path')
        return self._path

    @property
    def config(self):
        self._config = json.loads(self.get_property('config'))
        return self._config

    @property
    def value(self):
        self._value = json.loads(self.get_property('value'))
        return self._value

    @value.setter
    def value(self, value):
        if not self._value == value:
            db, table = self.get_table()
            entry = table(id=self.id)
            entry.update_record(value=json.dumps(value))
            db.close()
            self._value = value
            Event.fire('state_changed', {'state': self}, source='State')

    @property
    def triggers(self):
        """
        Evaluates the value of triggers
        """
        triggers = self.config.get('triggers', None)
        if triggers is not None:
            try:
                paths = eval(triggers.replace('`', '\''), {'State': State, 'np': np})

                if isinstance(paths, list):
                    return paths
                elif isinstance(paths, str):
                    return [paths]

            except:
                logging.exception('Triggers for state {} could not be parsed'.format(self.path))

        return []

    @property
    def computed(self):
        """
        Evaluates the value of computed
        """
        computed = self.config.get('computed', None)
        if computed is not None:
            try:
                value = eval(computed.replace('`', '\''), {'State': State, 'np': np})
                return value
            except Exception as e:
                logging.error('Could not compute value for state {}: {}'.format(self.path, e))
        return None

    @property
    def parent(self):
        """
        returns the parent of the current state when the paths follow the slash
        syntax according to :code`parent/child`

        Example
        -------
        >>> p = State.add('parent')
        >>> c = State.add('parent/child')
        >>> c.return_parent()
        """
        path = self.path
        if '/' in path:
            parentpath = '/'.join(path.split('/')[:-1])
            return State.get(path=parentpath)
        return None

    @property
    def children(self):
        """
        returns a list of children of the current state when the paths follow
        the slash syntax according to :code`parent/child`

        Example
        -------
        >>> p = State.add('parent')
        >>> c0 = State.add('parent/child0')
        >>> c1 = State.add('parent/child1')
        >>> cc = State.add('parent/child0/child')
        >>> p.return_children()
        """
        children = []
        path = self.path
        for s in State.all():
            if '/'.join(s.path.split('/')[:-1]) == path:
                children.append(s)
        return children

    def __call__(self):
        return self.value

    def __repr__(self):
        return '<State: {}, path: {}, value: {}>'.format(self.id, self._path, self._value)

#
#
#
# class BaseObject(object):
#     """
#     A base class for objects identified by a path with a config attribute which
#     are backed by the database
#
#     """
#     # db_table = Table(db, 'objects', [
#     #     {'name': 'path',   'type': 'char(255)',  'null': '',  'default': '',  'unique': 'UNIQUE'},
#     #     {'name': 'config', 'type': 'char(511)',  'null': '',  'default': '',  'unique': ''},
#     # ])
#
#     container = {}
#
#     def __new__(cls, path, **kwargs):
#         if path in cls.container:
#             return None
#         else:
#             return super().__new__(cls)  # super(BaseObject, cls).__new__(cls)
#
#     def __init__(self, path, config=None, db_entry=None):
#         """
#         Parameters
#         ----------
#         path : str
#             The item identifier relations between states (parent - child) can be
#             indicated with dots
#         config : dict
#             Dictionary configuring the state
#         db_entry : dict
#             If the state was loaded from the database, the database entry must
#             be supplied as a dictionary with `config` and `value` keys
#
#         """
#         self._path = path
#         self._thread = threading.current_thread()
#
#         if db_entry is None:
#             # check if the path already exists in the database
#             result = self._table.get(path=self._path)
#             if len(result) == 0:
#                 self.config = self._check_config(config)
#
#                 # post to the database
#                 self._table.post(path=self._path, config=json.dumps(self._config))
#
#                 # get the id
#                 result = self._table.get(path=self._path)
#                 self._id = result[0]['id']
#             else:
#                 # create the db_entry
#                 db_entry = result[0]
#
#         if db_entry is not None:
#             # update the config from the database
#             json_config = db_entry['config']
#             if json_config is not None:
#                 config = json.loads(json_config)
#             else:
#                 config = None
#
#             new_config = self._check_config(config)
#             if new_config == config:
#                 self._config = new_config  # without changing it in the database
#             else:
#                 self.config = new_config  # update the database
#
#             # add an id value
#             self._id = db_entry['id']
#
#         # add self to container
#         self.container[self._path] = self
#
#     def delete(self):
#         self._table.delete(path=self._path)
#         # remove the object from the local reference
#         del self.container[self._path]
#
#     @property
#     def id(self):
#         return self._id
#
#     @property
#     def path(self):
#         return self._path
#
#     @property
#     def config(self):
#         return self._config
#
#     @config.setter
#     def config(self, config):
#         config = self._check_config(config)
#         self._table.put(config=json.dumps(config), where='path=\'{}\''.format(self._path))
#         self._config = config
#
#     def set_config(self, key, value):
#         """
#         sets a single key, value pair to the config dictionary and update the database
#
#         """
#         config = self._config
#         config[key] = value
#         config = self._check_config(config)
#         self.config = config
#
#     def _check_config(self, config):
#         """
#         Checks the config for required keys
#
#         """
#         if config is None:
#             config = {}
#         return config
#
#     def __repr__(self):
#         return '<{} {}>'.format(self.__class__.__name__, self._path)
#
#
# _states_table = None
# _measurements_table = None
#
#
#
#
#
# def get_measurements_table():
#     global _measurements_table
#     if _measurements_table is None:
#         _measurements_table = Table(get_measurements_database(), 'measurements', [
#             {'name': 'time',   'type': 'INT',   'null': '',  'default': '',  'unique': ''},
#             {'name': 'path',   'type': 'TEXT',  'null': '',  'default': '',  'unique': ''},
#             {'name': 'value',  'type': 'TEXT',  'null': '',  'default': '',  'unique': ''},
#         ])
#     return _measurements_table
#
#
# class State(BaseObject):
#     """
#     A base class for objects identified by a path with a config and a value
#     attribute which are backed by the database
#
#     Re-definable attributes
#     -----------------------
#     db_table : homecon.database.table
#         A database table where things are stored.
#         The database table must have a path, config and value column
#     container : dict
#         Must be redefined with an empty dictionary in a subclass.
#         This is a bit hacky but otherwise the BaseState container is used to
#         reference objects
#     """
#
#     container = {}
#
#     def __new__(cls, path, **kwargs):
#         if path in cls.container:
#             return None
#         else:
#             return super(State, cls).__new__(cls, path)
#
#     def __init__(self, path, config=None, value=None, db_entry=None):
#         """
#         Parameters
#         ----------
#         path : string
#             the item identifier relations between states (parent - child) can be
#             indicated with dots
#
#         db_entry : dict
#             if the state was loaded from the database, the database entry must
#             be supplied as a dictionary with `config` and `value` keys
#
#         config : dict
#             dictionary configuring the state
#
#         """
#         self._table = get_states_table()
#         self.trigger = []
#         super().__init__(path, config=config, db_entry=db_entry)
#
#         if db_entry is not None:
#             json_value = None
#             # set the value from the db_entry
#             if 'value' in db_entry:
#                 json_value = db_entry['value']
#
#             if json_value is not None:
#                 value = json.loads(json_value)
#
#                 if 'datatype' in self._config and self._config['datatype'] == 'number' and value is not None:
#                     try:
#                         value = float(value)
#                         if math.isnan(value):
#                             value = None
#                     except Exception as e:
#                         logging.error('Could not convert database entry to value for state {}: {}'.format(self.path, e))
#             else:
#                 value = None
#
#         self._value = self._check_value(value)
#
#         if db_entry is None and self._value is not None:
#             # update the value in the database
#             self._table.put(value=json.dumps(self._value), where='path=\'{}\''.format(self._path))
#
#     def set(self, value, source=None):
#         """
#         Sets the value by creating a future to set the value
#
#         Parameters
#         ----------
#         value :
#             The new value
#         source : class
#             A class, the source setting the value, if not supplied it is
#             determined by ispection
#         """
#         if source is None:
#             # get the source from inspection
#             stack = inspect.stack()
#             try:
#                 source = stack[1][0].f_locals['self'].__class__
#             except:
#                 source = 'unknown'  # FIXME if the source is not an instance
#
#         if self.config['datatype'] == 'number':
#             try:
#                 value = value*self.config['scale'] + self.config['offset']
#             except:
#                 pass
#
#         old_value = copy.copy(self._value)
#         # make sure value is valid
#         value = self._check_value(value)
#
#         # if the new and old value are different update and put in the database
#         if not value == old_value:
#             self._value = value
#             # update the value in the database
#             json_value = json.dumps(value)
#             self._table.put(value=json_value, where='path=\'{}\''.format(self._path))
#
#         # fire a state changed event
#         event.fire('state_changed', {'state': self, 'value': value, 'old_value': old_value}, source)
#
#         # computed states
#         for state in self.trigger:
#             if not state.config['computed'] == '':
#                 state.set(state.computed, source='computed')
#
#     def get(self):
#         """
#         Returns the current value
#
#         """
#         return self._value
#
#     def serialize(self):
#         """
#         return a dict representation of the instance
#
#         """
#
#         data = {
#             'id': self.id,
#             'path': self.path,
#             'config': json.dumps(self.config),
#             'value': json.dumps(self.value),
#         }
#         return data
#
#     @property
#     def value(self):
#         return self._value
#
#     @value.setter
#     def value(self, value):
#         self.set(value)
#
#     @property
#     def parent(self):
#         """
#         returns the parent of the current state when the paths follow the slash
#         syntax according to :code`parent/child`
#
#         Example
#         -------
#         >>> p = states.add('parent')
#         >>> c = states.add('parent/child')
#         >>> c.return_parent()
#
#         """
#
#         if '/' in self._path:
#             parentpath = '/'.join(self._path.split('/')[:-1])
#
#             if parentpath in self.container:
#                 return self.container[parentpath]
#
#         return None
#
#
#     @property
#     def children(self):
#         """
#         returns a list of children of the current state when the paths follow
#         the slash syntax according to :code`parent/child`
#
#         Example
#         -------
#         >>> p = states.add('parent')
#         >>> c0 = states.add('parent/child0')
#         >>> c1 = states.add('parent/child1')
#         >>> cc = states.add('parent/child0/child')
#         >>> p.return_children()
#
#         """
#
#         children = []
#         for path,state in self.container.items():
#             if self._path in path:
#                 if len(self._path.split('/')) == len(path.split('/'))-1:
#                     children.append(state)
#
#         return children
#
#     @property
#     def triggers(self):
#         """
#         Evaluates the value of triggers
#
#         """
#
#         triggers = self.config['triggers']
#         if not triggers == '':
#             try:
#                 paths = eval(triggers.replace('`', '\''), {'states': self.container, 'np': np})
#
#                 if isinstance(paths,list):
#                     return paths
#                 elif isinstance(paths,str):
#                     return [paths]
#
#             except Exception as e:
#                 logging.error('Triggers for state {} could not be parsed: {}'.format(self.path, e))
#
#         return []
#
#     @property
#     def computed(self):
#         """
#         Evaluates the value of computed
#
#         """
#         computed = self.config['computed']
#         if not computed == '':
#             try:
#                 value = eval(computed.replace('`', '\''), {'states': self.container, 'np': np})
#                 return value
#             except Exception as e:
#                 logging.error('Could not compute value for state {}: {}'.format(self.path, e))
#
#         return None
#
#     @property
#     def component(self):
#         return self._component
#
#     def history(self, timestamp=None, interpolation='linear'):
#         """
#         return the history of a state
#
#         Parameters
#         ----------
#         timestamp : None or int or list of ints
#             Unix timestamp to return the history
#         interpolation : string
#             Type of interpolation, `linear` results in linear interpolation (default)
#             anything else results in zero order hold interpolation
#
#         """
#
#         if timestamp is None:
#             return self.value
#
#         else:
#
#             if hasattr(timestamp, "__len__"):
#                 timestamps = timestamp
#             else:
#                 timestamps = [timestamp]
#
#             # retrieve data from the database
#             result = get_measurements_table().get(path=self.path, time__ge=timestamps[0] - 3600, time__le=timestamps[-1] + 3600)
#
#             if len(result) > 0:
#                 db_timestamps = [res['time'] for res in result]
#                 db_values = [res['value'] for res in result]
#             else:
#                 # did not find any value, expand the horizon
#                 # FIXME find the 1st value before the 1st timestamp
#                 db_timestamps = [res['time'] for res in result]
#                 db_values = [res['value'] for res in result]
#
#             # interpolate to the correct timestamps
#             if self.config['datatype'] == 'number':
#                 if len(db_timestamps) > 0:
#                     f = interp1d(db_timestamps, db_values, kind=interpolation, bounds_error=False, fill_value=np.nan)
#                     values = f(timestamps)
#                 else:
#                     values = np.nan*np.ones(len(timestamps))
#
#             # return an array or scalar depending on the input
#             if hasattr(timestamp, "__len__") or values is None:
#                 return values
#             else:
#                 return values[0]
#
#     def _check_config(self, config):
#         """
#         Checks the config for required keys
#
#         """
#         if config is None:
#             config = {}
#         if 'readusers' not in config:
#             config['readusers'] = []
#         if 'writeusers' not in config:
#             config['writeusers'] = []
#         if 'readgroups' not in config:
#             config['readgroups'] = [1]
#         elif not 1 in config['readgroups']:
#             config['readgroups'].append(1)
#         if 'writegroups' not in config:
#             config['writegroups'] = [1]
#         elif not 1 in config['writegroups']:
#             config['writegroups'].append(1)
#
#         if 'datatype' not in config:
#             config['datatype'] = ''
#         if 'quantity' not in config:
#             config['quantity'] = ''
#         if 'unit' not in config:
#             config['unit'] = ''
#         if 'label' not in config:
#             config['label'] = ''
#         if 'description' not in config:
#             config['description'] = ''
#         if 'log' not in config:
#             config['log'] = True
#         if 'timestampdelta' not in config:
#             config['timestampdelta'] = 0
#         if 'triggers' not in config:
#             config['triggers'] = ''
#         if 'computed' not in config:
#             config['computed'] = ''
#         if 'scale' not in config:
#             config['scale'] = 1
#         if 'offset' not in config:
#             config['offset'] = 0
#         return config
#
#     def _check_value(self, value):
#         """
#         Checks the value for required keys
#
#         """
#
#         return value
#
#     def __call__(self):
#         return self._value
#
#     def __str__(self):
#         return self._path
#
#     def __repr__(self):
#         formattedvalue = '{}'.format(self._value)
#         if len(formattedvalue) > 10:
#             formattedvalue = formattedvalue[:9] + ' ... ' + formattedvalue[-1]
#
#         return '<{} {} value={}>'.format(self.__class__.__name__, self._path, formattedvalue)
#
#
# class States(object):
#     """
#     a container class for states with access to the database
#
#     """
#
#     def __init__(self):
#         self._states = State.container
#         self.load()
#         self.parse_triggers()
#
#     def load(self):
#         """
#         Loads all states from the database
#
#         """
#         print(get_states_table())
#         result = get_states_table().get()
#         for db_entry in result:
#             self.add(db_entry['path'], db_entry=db_entry, parse_triggers=False)
#
#     def add(self, path, value=None, config=None, db_entry=None, parse_triggers=True):
#         """
#         add a state
#
#         """
#         state = State(path, value=value, config=config, db_entry=db_entry)
#         if parse_triggers:
#             self.parse_triggers()
#         return state
#
#     def parse_triggers(self):
#         for state in self._states.values():
#             state.trigger = []
#
#         for state in self._states.values():
#             for path in state.triggers:
#                 if path in self._states and state not in self._states[path].trigger:
#                     self._states[path].trigger.append(state)
#
#     def delete(self, path):
#         try:
#             self._states[path].delete()
#             self.parse_triggers()
#         except:
#             logger.error('Attempt to delete state {} but it is not found'.format(path))
#
#     def __getitem__(self, path):
#         try:
#             return self._states[path]
#         except:
#             logging.error('Attempt to access state {} but it is not found'.format(path))
#
#     def __iter__(self):
#         return iter(self._states)
#
#     def __contains__(self,path):
#         return path in self._states
#
#     def keys(self):
#         return self._states.keys()
#
#     def items(self):
#         return self._states.items()
#
#     def values(self):
#         return self._states.values()
#
# # create the states container
# # states = States()
#

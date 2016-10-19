#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import copy

from . import database
from .plugin import BasePlugin

class States(BasePlugin):
 
    def initialize(self):
        self._states = {}
        self._db = database.Database(database='homecon.db')
        con = self._db
        self._db_states = database.Table(self._db,'states',[
            {'name':'path',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'config',      'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'quantity',    'type':'char(63)',   'null': '',  'default':'',  'unique':''},
            {'name':'unit',        'type':'char(15)',   'null': '',  'default':'',  'unique':''},
            {'name':'label',       'type':'char(63)',   'null': '',  'default':'',  'unique':''},
            {'name':'description', 'type':'char(255)',  'null': '',  'default':'',  'unique':''},
        ])

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
            state = State(self,path,config=config)
            self._states[path] = state
        else:
            logging.error('State {} allready exists'.format(path))


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

    def listen(self,event):
        if event.type == 'state_add':
            self.add_state(event.data['path'],event.data['config'])


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
        self._states.fire('state_changed',{'state':self,'value':self._value,'oldvalue':oldvalue},source)


    def get(self):
        return self._value


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
    def parent(self):
        """
        returns the parent of the current state when the paths follow the dot
        syntax according to :code`parent.child`

        Example
        -------
        >>> p = states.add('parent')
        >>> c = states.add('parent.child')
        >>> c.return_parent()
        
        """

        if '.' in self._path:
            parentpath = '.'.join(self._path.split('.')[:-1])
            parent = self._states.get(parentpath)
            return parent
        else:
            return None


    @property
    def children(self):
        """
        returns a list of children of the current state when the paths follow the dot
        syntax according to :code`parent.child`

        Example
        -------
        >>> p = states.add('parent')
        >>> c0 = states.add('parent.child0')
        >>> c1 = states.add('parent.child1')
        >>> cc = states.add('parent.child0.child')
        >>> p.return_children()
        
        """

        children = []
        for path,state in self._states.items():
            if self._path in path:
                if len(self._path.split('.')) == len(path.split('.'))-1:
                    children.append(state)

        return children


    def __call__(self):
        return self._value


    def __str__(self):
        return self._path


    def __repr__(self):
        return '<state {} value={}>'.format(self._path,self._value)


        

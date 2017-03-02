#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from . import database
from . import event
from . import state

class Components(object):
    """
    a container class for components with access to the database

    """

    def __init__(self):
        #super(Components,self).__init__(queue)

        self._component_types = {}
        self._components = {}

        self._db_components = database.Table(database.db,'components',[
            {'name':'path',    'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'type',    'type':'char(127)',  'null': '',  'default':'',  'unique':''},
            {'name':'config',  'type':'char(511)',  'null': '',  'default':'',  'unique':''},
        ])


    def load(self):
        """
        Loads all components from the database

        """
        
        # get all components from the database
        result = self._db_components.GET()
        for component in result:
            self.add(component['path'],component['type'],config=json.loads(component['config']))


    def register(self,componentclass):
        """
        Register a component type

        """
        self._component_types[componentclass.__name__.lower()] = componentclass


    def types(self):
        return self._component_types.items()


    def add(self,path,type,config=None):
        """
        add a component

        """

        if not path in self._components and type in self._component_types:
            
            # check if the component is in the database and add it if not
            if len( self._db_components.GET(path=path) ) == 0:
                self._db_components.POST( path=path,type=type,config=json.dumps(config) )

            # create the component
            component = self._component_types[type](self,path,config=config)
            self._components[path] = component

            return component

        else:
            return False


    def find(self,**kwargs):
        """
        finds components with certain config attributes
        """
        
        components = []
        for component in self._components.values():
            add = True
            for key,val in kwargs.items():
                if key == 'type':
                    if not component.type == val:
                        add = False
                        break
                else:
                    if not key in component.config:
                        add = False
                        break
                    elif not component.config[key] == val:
                        add = False
                        break

            if add:
                components.append(component)

        return components


    def __getitem__(self,path):
        return self._components[path]


    def __iter__(self):
        return iter(self._components)


    def __contains__(self,path):
        return path in self._components


    def keys(self):
        return self._components.keys()


    def items(self):
        return self._components.items()


    def values(self):
        return self._components.values()




class Component(object):
    """
    base class for defining a HomeCon component
    
    """
    
    def __init__(self,components,path,config=None):
        """
        Create a component
    
        Parameters
        ----------
        path : str
            the component identifier

        """
        self._path = path
        self.states = {}
        self.config = {}

        self.initialize()

        if not config is None:
            for key,val in config.items():
                self.config[key] = val


        # try to find the corresponding states and create them if required
        for path in self.states:
            fullpath = self._path + '/' + path

            if fullpath in state.states:
                tempstate = state.states[fullpath]
                config = tempstate.config
                config['component'] = self._path

                tempstate.config = config
                self.states[path] = tempstate
            else:
                config = {}
                for key,val in self.states[path]['default_config'].items():
                    config[key] = val
                for key,val in self.states[path]['fixed_config'].items():
                    config[key] = val
                config['component'] = self._path

                # replace the initialized dictionary with the state
                self.states[path] = state.states.add(fullpath,config=config)


    def initialize(self):
        """
        Redefine this method to alter the component

        """
        self.config = {}
        self.states = {}

    def prepare_ocp_model(self,model):
        """
        Redefine this method to alter the optimal control pyomo model
        
        Parameters
        ----------
        model : pyomo.ConcreteModel
            The pyomo optimal control model
 
        """
        pass

    def postprocess_ocp_model(self,model):
        """
        Redefine this method to use values from the optimal control problem solution
        
        Parameters
        ----------
        model : pyomo.ConcreteModel
            The pyomo optimal control model
 
        """
        pass

    @property
    def type(self):
        return self.__class__.__name__.lower()

    @property
    def path(self):
        return self._path

    @classmethod
    def properties(cls):
        repr = {
            'name': cls.__name__,
            'config': cls.config.keys(),
            'states': [{'path':key, 'default_config':val['default_config'], 'fixed_config':val['fixed_config']} for key,val in cls.states.items()],
        }
        return json.dumps(repr)

# create the components container
components = Components()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from . import database
from . import event
from . import state


class Component(state.BaseObject):
    """
    base class for defining a HomeCon component
    
    """

    db_table = database.Table(database.db,'components',[
        {'name':'path',    'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
        {'name':'type',    'type':'char(127)',  'null': '',  'default':'',  'unique':''},
        {'name':'config',  'type':'char(511)',  'null': '',  'default':'',  'unique':''},
    ])

    container = {}

    default_config = {}
    linked_states = {}

    def __init__(self,path,config=None,db_entry=None):
        """
        Create a component
    
        Parameters
        ----------
        path : str
            the component identifier

        """

        super().__init__(path,config=config,db_entry=db_entry)
        self.states = {}
        self.ocp_variables = {}

        # update the type in the database
        self.db_table.PUT(type=self.type, where='path=\'{}\''.format(self._path))


        # set the default config if the keys are not defined yet
        for key,val in self.default_config.items():
            if not key in self.config:
                self.set_config(key,val)


        # try to find the corresponding states and create them if required
        for path in self.linked_states:
            fullpath = self._path + '/' + path

            if fullpath in state.states:
                tempstate = state.states[fullpath]
                config = tempstate.config
                config['component'] = self._path

                tempstate.config = config
                self.states[path] = tempstate
            else:
                config = {}
                for key,val in self.linked_states[path]['default_config'].items():
                    config[key] = val
                for key,val in self.linked_states[path]['fixed_config'].items():
                    config[key] = val
                config['component'] = self._path

                # replace the initialized dictionary with the state
                self.states[path] = state.states.add(fullpath,config=config)

        # initialize
        self.initialize()



    def initialize(self):
        """
        This method is run when the component and associated states are created

        """
        pass


    def create_ocp_variables(self,model):
        """
        Redefine this method to add variables to the optimal control pyomo model
        
        Parameters
        ----------
        model : pyomo.ConcreteModel
            The pyomo optimal control model
 
        """
        pass


    def create_ocp_constraints(self,model):
        """
        Redefine this method to add constraints to the optimal control pyomo
        model
        
        Parameters
        ----------
        model : pyomo.ConcreteModel
            The pyomo optimal control model
 
        """
        pass


    def postprocess_ocp(self,model):
        """
        Redefine this method to use values from the optimal control problem solution
        
        Parameters
        ----------
        model : pyomo.ConcreteModel
            The pyomo optimal control model
 
        """
        pass

    def set(self):
        pass


    async def set_async(self):
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

    def delete(self):

        # delete all associated states
        for s in self.states.values():
            s.delete()

        # remove component properties from states and components
        componenttype = self.type
        for component in self.container.values():
            if self.type in component.config and component.config[self.type] == self.path:
                component.config[self.type] = '';

        super().delete()


class Components(object):
    """
    a container class for components

    """

    def __init__(self):

        self._component_types = {}
        self._components = Component.container
        self._db_components = Component.db_table

    def load(self):
        """
        Loads all components from the database

        """
        
        # get all components from the database
        result = self._db_components.GET()
        for db_entry in result:
            self.add(db_entry['path'],db_entry['type'],db_entry=db_entry)


    def register(self,componentclass):
        """
        Register a component type

        """
        self._component_types[componentclass.__name__.lower()] = componentclass


    def types(self):
        return self._component_types.items()

        
    def add(self,path,type,config=None,db_entry=None):
        """
        add a component

        """

        if not path in self._components and type in self._component_types:
            component = self._component_types[type](path,config=config,db_entry=db_entry)
            return component

            """
            # check if the component is in the database and add it if not
            if len( self._db_components.GET(path=path) ) == 0:
                self._db_components.POST( path=path,type=type,config=json.dumps(config) )

            # create the component
            component = self._component_types[type](self,path,config=config)
            self._components[path] = component

            return component
            """
        else:
            return False
            

    def delete(self,path):
        """
        Delete a component
        """
        if path in self._components:
            self._components[path].delete()
            return True


    def find(self,**kwargs):
        """
        finds components with certain config attributes
        """
        
        components = []
        for component in self._components.values():
            add = True
            for key,val in kwargs.items():
                if key == 'type':
                    if not val in self._component_types:
                        add = False
                        break
                    elif not isinstance(component,self._component_types[val]):
                        add = False
                        break
                elif key == 'type_strict':
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





# create the components container
components = None


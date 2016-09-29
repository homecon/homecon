#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random

from .plugin import Plugin

class States(Plugin):
 
    def initialize(self):
        self.states = {}
        


    def add(self,path,config=None):
        """
        add a state
        """
        if not path in self.items:
            state = State(path,config=config)
            self.states[path] = state
        else:
            print('item allready exists')


    def set(self,path,value):
        if path in self.states:
            state = self.states[path]
            state.value = value
            self.fire('command',{'cmd':'state_changed','state':state})

        else:
            print('unknown item')


    def get(self,path):
        if path in self.states:
            value = self.states[path].value
            self.fire('command',{'cmd':'state_value','path':path,'value':value})
        else:
            self.homecon.logger.warning('unknown state')


    def listen(self,event):
        
        if event.data['cmd'] == 'state_set':
            self.set(event.data['path'],event.data['value'])

        if event.data['cmd'] == 'item_get':
            self.get(event.data['path'])




class State(object):
    def __init__(self,path,config=None):

        self.path = path

        if config == None:
            self.config = {}
        else:
            self.config = config 

        self.value = None




        

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Event(object):
    def __init__(self,event_type,data,source,client):
        self.type = event_type
        self.data = data
        self.source = source
        self.client = client

    def __str__(self):
        return 'Event: {}, data: {}, source: {}, client: {}'.format(self.type,self.data.__repr__(),self.source.__class__.__name__,self.client.__repr__())




class BasePlugin(object):
    def __init__(self,homecon):
        """
        Initialize a plugin instance
        
        Parameters
        ---------
        homecon : Homecon object
            the main homecon object
            
        """

        self.homecon = homecon

        self.initialize()


    def initialize(self):
        """
        Base method runs when the plugin is instantiated
        
        redefine this method in a child class
        """
        pass


    def listen(self,event):
        """
        Base method to listen for events and perform actions
        
        redefine this method in a child class
        
        Parameters
        ----------
        event : Event
            an Event instance
            
        Notes
        -----
        A plugin can not send events to itself through the fire / listen methods

        Examples
        --------
        .. code-block::
            def listen(self,event):

                if event.type == 'do_something':
                    self.do_something(event)

                elif event.type == 'do_something_else':
                    self.do_something_else(event)

        """
        pass


    def fire(self,event_type,data,source=None,client=None):
        """
        Add the event to the que
        
        Parameters
        ----------
        event_type : string
            the event type

        data : dict
            the data describing the event
        
        source : string
            the source of the event
            
        """

        if source==None:
            source = self

        self.homecon.fire( Event(event_type,data,source,client) )


    def _listen(self,event):
        """
        Base listener method called when an event is taken from the que
        
        checks whether this plugin is the target or if there is no target and
        then calls the code:`listen` method if so
        
        Parameters
        ----------
        event : Event
            an Event instance
            
        """

        # check if this plugin is the source and stop execution if so
        if not event.source == self:
            self.listen(event)


class Plugin(BasePlugin):
    def __init__(self,homecon):
        """
        Initialize a plugin instance
        
        Parameters
        ---------
        homecon : Homecon object
            the main homecon object
            
        """

        self.homecon = homecon

        self.states = self.homecon.states
        self.websocket = self.homecon.websocket

        self.initialize()





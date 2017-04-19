#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

# create the main event loop
loop = asyncio.get_event_loop()
if loop.is_closed():
    loop = asyncio.new_event_loop()

asyncio.set_event_loop(loop)

# create a queue for events
queue = asyncio.Queue(loop=loop)


class Event(object):
    """
    """
    def __init__(self,event_type,data,source,client):
        self.type = event_type
        self.data = data
        self.source = source
        self.client = client

    def __str__(self):
        newdata = dict(self.data)
        for key in ['password','token']:
            if key in newdata:
                newdata[key] = '***'

        printdata = newdata.__repr__()
        if len(printdata) > 405:
            printdata = printdata[:200] + ' ... ' +printdata[-200:]

        return 'Event: {}, data: {}, source: {}, client: {}'.format(self.type,printdata,self.source.__class__.__name__,self.client.__repr__())



def fire(event_type,data,source=None,client=None):
    """
    Add the event to the queue
    
    Parameters
    ----------
    event_type : string
        the event type

    data : dict
        the data describing the event
    
    source : object
        the source of the event
        
    """
    
    event = Event(event_type,data,source,client)

    async def do_fire(event):
        await queue.put(event)


    def do_create_task():
        loop.create_task(do_fire(event))

    loop.call_soon_threadsafe(do_create_task)



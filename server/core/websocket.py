#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import asyncio


import asyncws



from .plugin import BasePlugin


class Websocket(BasePlugin):
    def initialize(self):

        self.clients = []
        self.server = None

        clients_lock = asyncio.Lock()


        def connect_client(websocket):
            """
            connect a client and listen for messages
            """

            client = Client(websocket)
            with (yield from clients_lock):
                
                self.clients.append(client)

            address = client.address

            logging.debug('Incomming connection from {}'.format(address))

            try:
                while True:
                    message = yield from websocket.recv()
                    if message is None:
                        break

                    # parse the message and fire an event if the data is in the correct format
                    try:
                        data = json.loads(message)
                        self.log_data(address,data)
                        
                        if 'event' in data:
                            self.fire(data['event'],data,client=client)

                        elif 'echo' in data:
                            yield from client.send(data)

                    except:
                        logging.debug('A message was recieved but could not be handled')
                    

            finally:
                with (yield from clients_lock):
                    self.clients.remove(client)

                logging.debug('Disconnected {}'.format(address))


        # create a server and run it in the event loop
        servergenerator = asyncws.start_server(connect_client, host='127.0.0.1', port=9024, loop=self._loop)
        self.server = self._loop.run_until_complete( servergenerator )


        logging.info('Websocket started')


    def log_data(self,address,data):
        """
        removes sensitive data before logging

        Parameters
        ----------
        address : string
            identifies the client

        data : dict
            a dictionary with the sent data

        """

        newdata = dict(data)
        for key in ['password','token']:
            if key in newdata:
                newdata[key] = '***'

        logging.debug('Client on {} sent {}'.format(address,newdata))


    def listen(self,event):

        if event.type == 'broadcast':
            # send the event to all connected clients
            for client in self.clients:
                asyncio.ensure_future( client.send(event.data) )


        if event.type == 'send':
            # send the event to permitted clients
            senddata = {key:val for key,val in event.data.items() if not (key=='readusers' or key=='readgroups')}

            for client in self.clients:
                permitted = False
                if client.tokenpayload['userid'] in event.data['readusers']:
                    permitted = True
                else:
                    for g in client.tokenpayload['groupids']:
                        if g in event.data['readgroups']:
                            permitted = True
                            break

                if permitted:
                    asyncio.ensure_future( client.send(senddata) )


        elif event.type == 'send_to':
            # send the event to some clients
            clients = event.data['clients']
            senddata = {key:val for key,val in event.data.items() if not key=='clients'}

            for client in clients:
                asyncio.ensure_future( client.send(senddata) )


    def stop(self):
        if self.server is not None:
            # send a shutting down message to all clients
            
            # close the server
            self.server.close()
            self.server = None
            logging.info('Websocket stopped')


class Client(object):
    def __init__(self,websocket):
        self.websocket = websocket
        self.tokenpayload = False

        address = websocket.writer.get_extra_info('peername')
        self.address = '{}:{}'.format(address[0],address[1])

    @asyncio.coroutine
    def send(self,message):
        yield from self.websocket.send(json.dumps(message))


class DummyAdminClient(object):
    def __init__(self,websocket=None):
        self.websocket = websocket
        self.address = '1.1.1.1'
        self.tokenpayload = {'userid':1, 'groupids':[1,2], 'username':'admin','permission':9}

    def send(self,message):
        pass




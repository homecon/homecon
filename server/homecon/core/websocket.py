#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import asyncio

import asyncws

from . import event

class Websocket(object):
    """
    A class for managing the websocket connections

    """

    def __init__(self):

        self._loop = asyncio.get_event_loop()
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
                            event.fire(data['event'],data,source=self,client=client)

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


    def send(self,data, clients=None,readusers=None,readgroups=None):
        """
        Send data to clients

        Parameters
        ----------
        data: dict
            Data to send to the clients

        clients: list of Client or single Client, optional
            Clients to send the data to

        readusers: list, optional
            List of user id's which are allowed to read the data

        readgroups: list, optional
            List of group id's which are allowed to read the data
    
        """

        if clients is None:
            clients = self.clients

        if not hasattr(clients,'__len__'):
            clients = [clients]


        for client in clients:
            if self.check_readpermission(client,readusers=readusers,readgroups=readgroups) or data['event'] == 'request_token':
                asyncio.ensure_future( client.send(data) )


    def check_readpermission(self,client,readusers=None,readgroups=None):
        """
        Check if a client has the permission to read based on the readusers and
        readgroups lists

        """

        permitted = False
        if client.tokenpayload:


            if readusers is None and readgroups is None:
                permitted = True
            else:
                if readusers is None:
                    readusers = []

                if readgroups is None:
                    readgroups = []


                if client.tokenpayload['userid'] in readusers:
                    permitted = True
                else:
                    for g in client.tokenpayload['groupids']:
                        if g in readgroups:
                            permitted = True
                            break

        return permitted



class Client(object):
    def __init__(self,websocket):
        self.websocket = websocket
        self.tokenpayload = False

        address = websocket.writer.get_extra_info('peername')
        self.address = '{}:{}'.format(address[0],address[1])

    @asyncio.coroutine
    def send(self,message):

        printmessage = message.__repr__()
        if len(printmessage) > 405:
            printmessage = printmessage[:200] + ' ... ' +printmessage[-200:]
        logging.debug('send {} to {}'.format(printmessage,self))

        yield from self.websocket.send(json.dumps(message))

    def __repr__(self):
        return self.address



class DummyAdminClient(object):
    def __init__(self,websocket=None):
        self.websocket = websocket
        self.address = '1.1.1.1'
        self.tokenpayload = {'userid':1, 'groupids':[1,2], 'username':'admin','permission':9}

    def send(self,message):
        pass


websocket = Websocket()


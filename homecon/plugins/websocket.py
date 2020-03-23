#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import logging
import json
import asyncio
from threading import Thread

from uuid import uuid4

import asyncws

from homecon.core.plugin import Plugin
from homecon.core.event import Event


class Logger(logging.Logger):
    """
    Custom logger which blanks out passwords and tokens.
    """

# logger = Logger(__name__)


logger = logging.getLogger(__name__)


class Websocket(Plugin):
    """
    Class to control the HomeCon websocket

    """
    def __init__(self, host='0.0.0.0', port=9099):
        super().__init__()
        self.clients = {}
        self.host = host
        self.port = port
        self.server = None
        self._loop = asyncio.get_event_loop()

    def initialize(self):
        # FIXME this is very ugly with an asyncio loop inside a thread
        logger.info(f'starting websocket at ws://{self.host}:{self.port}')
        clients_lock = asyncio.Lock()

        def connect_client(websocket):
            """
            connect a client and listen for messages
            """
            client = Client(websocket)
            with (yield from clients_lock):
                self.clients[client.id] = client

            address = client.address
            logger.debug('Incomming connection from {}'.format(address))

            try:
                while True:
                    message = yield from websocket.recv()
                    if message is None:
                        break
                    # parse the message and fire an event if the data is in the correct format
                    try:
                        data = json.loads(message)
                        self.log_data(address, data)
                        if 'event' in data:
                            if data['event'] == 'echo':
                                yield from client.send(data)
                            else:
                                Event.fire(data['event'], data['data'], source=self.__class__.__name__,
                                           reply_to='Websocket/{}'.format(client.id))
                    except Exception as e:
                        logger.debug('A message was received but could not be handled, {}'.format(e))
            finally:
                with (yield from clients_lock):
                    del self.clients[client.id]
                logger.debug('Disconnected {}'.format(address))

        def run_server(loop):
            # create a server and run it in the event loop
            asyncio.set_event_loop(loop)
            server_generator = asyncws.start_server(connect_client, host=self.host, port=self.port, loop=self._loop)
            self.server = self._loop.run_until_complete(server_generator)
            loop.run_forever()

        server_thread = Thread(target=run_server, args=(asyncio.get_event_loop(),))
        server_thread.start()
        logger.debug('Websocket plugin initialized')

    def log_data(self, address, data):
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
        for key in ['password', 'token']:
            if key in newdata:
                newdata[key] = '***'

        logger.debug('Client on {} sent {}'.format(address, newdata))

    def send(self, data, clients=None, readusers=None, readgroups=None):
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

        if not hasattr(clients, '__len__'):
            clients = {'temp': clients}
        for client in clients.values():
            if (self.check_readpermission(client, readusers=readusers, readgroups=readgroups)
                    or data['event'] == 'request_token'):
                asyncio.run_coroutine_threadsafe(client.send(data), loop=self._loop)

    def check_readpermission(self, client, readusers=None, readgroups=None):
        """
        Check if a client has the permission to read based on the readusers and
        readgroups lists

        """
        return True
        # FIXME
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

    def listen_websocket_send(self, event):
        self.send(event.data)

    def listen_websocket_reply(self, event):
        self.send(event.data)

    def listen_reply(self, event):
        self.send(event.data)

    def listen_state_value_changed(self, event):
        self.send({
            'event': 'state_value',
            'data': {
                'path': event.data['state'].path,
                'id': event.data['state'].id,
                'value': event.data['state'].value
            }
        })

    def listen_state_list_changed(self, event):
        self.send({
            'event': 'state_list',
            'data': {
                'id': '',
                'value': [s.serialize() for s in event.data['state_list']]
            }
        })

    def listen_state_changed(self, event):
        self.send({
            'event': 'state',
            'data': {
                'path': event.data['state'].path,
                'id': event.data['state'].id,
                'value': event.data['state'].serialize()
            }
        })

    def listen_stop_plugin(self, event):
        super().listen_stop_plugin(event)
        self.server.close()
        asyncio.get_event_loop().stop()


class Client(object):
    def __init__(self, websocket):
        self.websocket = websocket
        self.tokenpayload = False
        self.id = uuid4()

        address = websocket.writer.get_extra_info('peername')
        self.address = '{}:{}'.format(address[0], address[1])

    @asyncio.coroutine
    def send(self, message):
        printmessage = message.__repr__()
        if len(printmessage) > 405:
            printmessage = printmessage[:200] + ' ... ' +printmessage[-200:]
        logger.debug('send {} to {}'.format(printmessage, self))

        yield from self.websocket.send(json.dumps(message))

    def __repr__(self):
        return self.address


class DummyAdminClient(object):
    def __init__(self, websocket=None):
        self.websocket = websocket
        self.address = '1.1.1.1'
        self.tokenpayload = {'userid': 1, 'groupids': [1, 2], 'username': 'admin', 'permission': 9}

    def send(self, message):
        pass


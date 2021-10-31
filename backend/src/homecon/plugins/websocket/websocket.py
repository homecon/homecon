#!/usr/bin/env python3
import logging
import json
import asyncio
from threading import Thread

from uuid import uuid4

import websockets

from homecon.core.states.state import IStateManager
from homecon.core.event import Event
from homecon.core.auth import IAuthManager

from homecon.core.plugins.plugin import IPlugin, BasePlugin


class Logger(logging.Logger):
    """
    Custom logger which blanks out passwords and tokens.
    """
    pass


logger = logging.getLogger(__name__)


class Websocket(IPlugin):
    """
    Class to control the HomeCon websocket

    """
    def __init__(self, state_manager: IStateManager, auth_manager: IAuthManager, host='0.0.0.0', port=9099):
        self._state_manager = state_manager
        self._auth_manager = auth_manager
        self.clients = {}
        self.host = host
        self.port = port
        self.server = None
        self._loop = asyncio.get_event_loop()
        self._server_thread = None

    @property
    def name(self):
        return 'websocket'

    def start(self):
        # FIXME this is very ugly with an asyncio loop inside a thread
        logger.info(f'starting websocket at ws://{self.host}:{self.port}')
        clients_lock = asyncio.Lock()

        async def connect_client(websocket, path):
            """
            connect a client and listen for messages
            """
            client = Client(websocket)
            with (await clients_lock):
                self.clients[client.id] = client

            address = client.address
            logger.debug('incomming connection from {}'.format(address))

            try:
                while True:
                    message = await websocket.recv()
                    logger.debug(f'recieved message, {message}')
                    if message is None:
                        break
                    # parse the message and fire an event if the data is in the correct format
                    try:
                        data = json.loads(message)
                        self.log_data(address, data)
                        if 'event' in data:
                            if self._auth_manager.is_authorized(data['event'], data.get('data', {}), data.get('token', '')):
                                if data['event'] == 'echo':
                                    await client.send(data)
                                else:
                                    self.fire(data['event'], data['data'], reply_to=f'{self.name}/{client.id}')
                            else:
                                logger.info(f'unauthorized message received from {address}: {data}')
                        else:
                            logger.info(f'a message was received but contained no event, {data}')
                    except Exception:
                        logger.exception('a message was received but could not be handled')
            finally:
                with (await clients_lock):
                    del self.clients[client.id]
                logger.debug('disconnected {}'.format(address))

        def run_server(loop):
            # create a server and run it in the event loop
            asyncio.set_event_loop(loop)
            server_generator = websockets.serve(connect_client, host=self.host, port=self.port, loop=loop)
            self.server = loop.run_until_complete(server_generator)
            loop.run_forever()

        self._server_thread = Thread(target=run_server, args=(asyncio.get_event_loop(),))
        self._server_thread.start()
        logger.debug('Websocket plugin initialized')

    def stop(self):
        self.server.close()
        self._loop.call_soon_threadsafe(self._loop.stop)

        if self._server_thread is not None:
            self._server_thread.join()

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
            if True or data['event'] == 'request_token':
                asyncio.run_coroutine_threadsafe(client.send(data), loop=self._loop)

    def handle_event(self, event: Event):
        if event.type == 'websocket_send':
            self.listen_websocket_send(event)
        if event.type == 'websocket_reply':
            self.listen_websocket_reply(event)
        if event.type == 'reply':
            self.listen_reply(event)
        if event.type == 'state_value_changed':
            self.listen_state_value_changed(event)
        if event.type == 'state_updated':
            self.listen_state_updated(event)
        if event.type == 'state_added':
            self.listen_state_added(event)
        if event.type == 'state_deleted':
            self.listen_state_deleted(event)

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

    def listen_state_updated(self, event):
        self.send({
            'event': 'state',
            'data': {
                'path': event.data['state'].path,
                'id': event.data['state'].id,
                'value': event.data['state'].serialize()
            }
        })
        self.send({
            'event': 'state_list',
            'data': {
                'id': '',
                'value': [s.serialize() for s in self._state_manager.all()]
            }
        })

    def listen_state_added(self, _):
        self.send({
            'event': 'state_list',
            'data': {
                'id': '',
                'value': [s.serialize() for s in self._state_manager.all()]
            }
        })

    def listen_state_deleted(self, _):
        self.send({
            'event': 'state_list',
            'data': {
                'id': '',
                'value': [s.serialize() for s in self._state_manager.all()]
            }
        })


class Client(object):
    def __init__(self, websocket):
        self.websocket = websocket
        self.tokenpayload = False
        self.id = uuid4()

    @property
    def address(self):
        address = self.websocket.remote_address
        if address is not None:
            return '{}:{}'.format(address[0], address[1])
        else:
            return '/'

    @asyncio.coroutine
    def send(self, message):
        printmessage = message.__repr__()
        if len(printmessage) > 405:
            printmessage = printmessage[:200] + ' ... ' +printmessage[-200:]

        yield from self.websocket.send(json.dumps(message))
        logger.debug(f'sent {printmessage} to {self}')

    def __repr__(self):
        return self.address


class DummyAdminClient(object):
    def __init__(self, websocket=None):
        self.websocket = websocket
        self.address = '1.1.1.1'
        self.tokenpayload = {'userid': 1, 'groupids': [1, 2], 'username': 'admin', 'permission': 9}

    def send(self, message):
        pass


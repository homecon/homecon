#!/usr/bin/env python3
import logging
import json
import asyncio

from threading import Thread
from uuid import uuid4
from http import HTTPStatus

import websockets

from homecon.core.event import Event
from homecon.core.plugins.plugin import BasePlugin


class Logger(logging.Logger):
    """
    Custom logger which blanks out passwords and tokens.
    """
    pass


logger = logging.getLogger(__name__)


class WebsocketEvents:
    WEBSOCKET_SEND = 'websocket_send'
    WEBSOCKET_REPLY = 'websocket_reply'


class Websocket(BasePlugin):
    """
    Class to control the HomeCon websocket

    """
    def __init__(self, *args, host: str = '0.0.0.0', port: int = 9099, token: str = '', **kwargs):
        super().__init__(*args, **kwargs)
        self._host = host
        self._port = port
        self._token = token

        self._clients = {}
        self.server = None
        self._loop = asyncio.get_event_loop()
        self._server_thread = None

    def start(self):
        # FIXME this is very ugly with an asyncio loop inside a thread
        logger.info(f'starting websocket at ws://{self._host}:{self._port}')
        clients_lock = asyncio.Lock()

        async def connect_client(websocket, path):
            """
            connect a client and listen for messages
            """

            client = Client(websocket)
            with (await clients_lock):
                self._clients[client.id] = client

            address = client.address
            logger.debug('incoming connection from {}'.format(address))

            try:
                while True:
                    message = await websocket.recv()
                    logger.debug(f'received message, {message}')
                    if message is None:
                        break
                    # parse the message and fire an event if the data is in the correct format
                    try:
                        data = json.loads(message)
                        self.log_data(address, data)
                        if 'event' in data:
                            if data['event'] == 'echo':
                                await client.send(data)
                            else:
                                self.fire(data['event'], data['data'], reply_to=f'{self.name}/{client.id}')
                        else:
                            logger.debug(f'a message was received but contained no event, {data}')
                    except Exception:
                        logger.exception('a message was received but could not be handled')
            finally:
                with (await clients_lock):
                    del self._clients[client.id]
                logger.debug('disconnected {}'.format(address))

        async def process_request(path, headers):
            token = path[1:]
            if token != self._token:
                logger.warning(f'client tried to connect with an invalid token')
                return HTTPStatus.UNAUTHORIZED, [], b'incorrect token'

        def run_server(loop):
            # create a server and run it in the event loop
            asyncio.set_event_loop(loop)
            server_generator = websockets.serve(connect_client, process_request=process_request,
                                                host=self._host, port=self._port, loop=loop)
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

    def send(self, data, clients=None):
        """
        Send data to clients

        Parameters
        ----------
        data: dict
            Data to send to the clients

        clients: list of Client or single Client, optional
            Clients to send the data to
        """

        if clients is None:
            clients = self._clients

        if not hasattr(clients, '__len__'):
            clients = {'temp': clients}
        for client in clients.values():
            if self.check_readpermission(client):
                asyncio.run_coroutine_threadsafe(client.send(data), loop=self._loop)

    def check_readpermission(self, client):
        """
        Check if a client has the permission to read based on the readusers and
        readgroups lists

        """
        return True

    def listen_websocket_send(self, event: Event):
        self.send(event.data)

    def listen_websocket_reply(self, event: Event):
        self.send(event.data)

    def listen_reply(self, event):
        self.send(event.data)

    def listen_state_value_changed(self, event: Event):
        self.send({
            'event': 'state_value',
            'data': {
                'path': event.data['state'].path,
                'id': event.data['state'].id,
                'value': event.data['state'].value
            }
        })

    def listen_state_updated(self, event: Event):
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


import asyncio
import websockets
import json

from homecon.tests import common
from homecon.core.event import queue
from homecon.plugins.websocket import Websocket


class Client(object):
    """
    A convienient wrapper for creating a websocket connection
    """

    async def connect(self, address):
        """
        connect to a websocket server
        """
        self.websocket = await websockets.connect(address)

    async def send(self, message):
        """
        recieve a websocket message in json format
        """
        await self.websocket.send(json.dumps(message))

    async def recv(self):
        """
        recieve a websocket message in json format
        """
        message = await self.websocket.recv()
        return json.loads(message)

    def close(self):
        self.websocket.close()


class TestWebsocket(common.TestCase):
    def test_websocket_recieve(self):

        plugin = Websocket()
        plugin.start()

        client = Client()
        async def async_actions():
            await client.connect('ws://localhost:9024')
            await client.send({'event': 'myevent', 'key1': 'val1', 'key2': 'val2'})
            client.close()
            event = queue.get(timeout=2)
            self.assertEqual(event.type, 'myevent')
            self.assertEqual(event.data, {'event': 'myevent', 'key1': 'val1', 'key2': 'val2'})

        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_actions())

        plugin.stop()
        plugin.join()

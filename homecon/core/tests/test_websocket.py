#!/usr/bin/env python3
################################################################################
#    Copyright 2016 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import asyncio


from homecon.tests import common

from homecon.core.websocket import Websocket


class WebsocketTests(common.TestCase):

    def test_recv(self):
        
        websocket = homecon.core.websocket
        client = common.Client()

        async def asyncactions():
            await client.connect('ws://127.0.0.1:9024')
            await client.send({'event':'myevent','key1':'val1','key2':'val2'})

            event = await homecon.core.event.queue.get()

            self.assertEqual(event.type,'myevent')
            self.assertEqual(event.data,{'event':'myevent','key1':'val1','key2':'val2'})
            self.assertEqual(event.source,websocket)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncactions())


    def test_client_echo(self):

        websocket = homecon.core.websocket
        client = common.Client()

        async def asyncactions():
            await client.connect('ws://127.0.0.1:9024')
            await client.send({'echo':'somevalue'})
            response = await client.recv()
    
            self.assertEqual(response,{'echo':'somevalue'})

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncactions())


    def test_send(self):

        websocket = homecon.core.websocket
        client = common.Client()

        async def asyncactions():
            await client.connect('ws://127.0.0.1:9024')
            websocket.send({'event':'request_token','token':'test'}) # only a request token event is passed without an authenticated client
    
            done,pending = await asyncio.wait([client.recv()],timeout=1)
            
            for d in done:
                self.assertEqual(d.result(),{'event':'request_token','token':'test'})

            self.assertEqual(len(pending),0)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncactions())


    def test_send_not_authenticated(self):

        websocket = homecon.core.websocket
        client = common.Client()

        async def asyncactions():
            await client.connect('ws://127.0.0.1:9024')
            websocket.send({'event':'myevent','key1':'val1'}) # only a request token event is passed without an authenticated client
    
            done,pending = await asyncio.wait([client.recv()],timeout=1)
            
            self.assertEqual(len(done),0)
            self.assertEqual(len(pending),1)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncactions())




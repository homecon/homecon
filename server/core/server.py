#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import asyncio
import asyncws



from .plugin import Plugin,Event

class Server(Plugin):
    def initialize(self):

        self.clients = []
        clients_lock = asyncio.Lock()

        def connect_client(websocket):
            """
            connect a client and listen for messages
            """
            self.logger.debug( 'Connecting new client' )

            with (yield from clients_lock):
                self.clients.append(websocket)

            address = websocket.writer.get_extra_info('peername')
            address = '{}:{}'.format(address[0],address[1])

            self.logger.debug('Incomming connection from {}'.format(address))

            try:
                while True:
                    message = yield from websocket.recv()
                    if message is None:
                        break

                    # parse the message and fire an event to homecon if the data is in the correct format
                    try:
                        data = json.loads(message)
                        self.log_data(address,data)
                        
                        if 'event' in data:
                            self.fire(data['event'],data)

                    except:
                        self.logger.debug('A message was recieved but could not be handled')
                    

            finally:
                with (yield from clients_lock):
                    self.clients.remove(websocket)

                self.logger.debug('Disconnected {}'.format(address))


        # create a server and run it in the event loop
        server = asyncws.start_server(connect_client, '127.0.0.1', 9024)
        self.homecon._loop.run_until_complete( server )



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
            if key in data:
                data[key] = '***'

        self.logger.debug('Client on {} sent {}'.format(address,data))


    def listen(self,event):
        
        if event.type == 'send':
            # send the event to all connected clients
            for client in self.clients:
                client.send(event.data)





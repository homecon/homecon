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
            logging.debug( 'Connecting new client' )

            with (yield from clients_lock):
                self.clients.append(websocket)

            address = websocket.writer.get_extra_info('peername')
            address = '{}:{}'.format(address[0],address[1])

            logging.debug('Incomming connection from {}'.format(address))

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
                        logging.debug('A message was recieved but could not be handled')
                    

            finally:
                with (yield from clients_lock):
                    self.clients.remove(websocket)

                logging.debug('Disconnected {}'.format(address))


        # create a server and run it in the event loop
        servergenerator = asyncws.start_server(connect_client, host='127.0.0.1', port=9024, loop=self.homecon._loop)
        self.server = self.homecon._loop.run_until_complete( servergenerator )

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
            if key in data:
                data[key] = '***'

        logging.debug('Client on {} sent {}'.format(address,data))


    def listen(self,event):
        
        if event.type == 'send':
            # send the event to all connected clients
            for client in self.clients:
                client.send(event.data)


    def stop(self):
        if self.server is not None:
            self.server.close()
            self.server = None
            logging.info('Websocket stopped')



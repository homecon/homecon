#!/usr/bin/env python3
######################################################################################
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
######################################################################################

import unittest
import os
import sqlite3
import json
import asyncio
import asyncws
import time

dbname='test_homecon'

import homecon.core

# initialize the core components once
homecon.core.initialize(dbname=dbname)
homecon.core.websocket.close()
loop = asyncio.get_event_loop()
loop.close()



class TestCase(unittest.TestCase):
    
    

    def clear_database(self):
        try:
            os.remove('{}.db'.format(dbname))
        except:
            pass
        try:
            os.remove('{}_measurements.db'.format(dbname))
        except:
            pass


    def setUp(self):
        """
        Executed before every test
        """

        self.clear_database()
        homecon.core.initialize(dbname=dbname)


    def tearDown(self):
        """
        Executed after every test
        """

        loop = asyncio.get_event_loop()

        # close the websocket connection
        homecon.core.websocket.close()

        # cancel all tasks
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()

        # run the event loop for a small time
        self.run_loop()
        loop.close()

        self.clear_database()

    def run_loop(self,seconds=0.01):
        
        async def test():
            await asyncio.sleep(seconds)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test())



class Client(object):
    """
    A convienient wrapper for creating a websocket connection
    """

    async def connect(self,address):
        """
        connect to a websocket server
        """
        self.websocket = await asyncws.connect(address)

    async def send(self,message):
        """
        recieve a websocket message in json format
        """
        await self.websocket.send(json.dumps(message))

    async def recv(self):
        """
        recieve a websocket message in json format
        """
        message = await self.websocket.recv()
        return json.loads( message )

    def close(self):
        self.websocket.close()


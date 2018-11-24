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

from unittest import TestCase
from unittest.mock import patch
import os
import sqlite3
import json
import asyncws
import time

from threading import Thread

# from homecon.homecon import HomeCon
from homecon.core.database import Database

# from homecon.core import plugin
from homecon.core import state

# create test databases
# database.db = database.Database(database='test_homecon.db')
# database.measurements_db = database.Database(database='test_measurements.db')


class TestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_get_database_patcher = patch('homecon.core.plugin.get_database',
                                                 new=lambda: Database(database='test_homecon.db'))
        self.state_get_database_patcher = patch('homecon.core.state.get_database',
                                                new=lambda: Database(database='test_homecon.db'))
        self.state_get_measurements_database_patcher = patch('homecon.core.state.get_measurements_database',
                                                             new=lambda: Database(database='test_measurements.db'))

    def clear_database(self):
        if os.path.exists('test_homecon.db'):
            os.remove('test_homecon.db')

        if os.path.exists('test_measurements.db'):
            os.remove('test_measurements.db')

        state._states_table = None

    def setUp(self):
        """
        Executed before every test
        """

        self.clear_database()
        self.plugin_get_database_patcher.start()
        self.state_get_database_patcher.start()
        self.state_get_measurements_database_patcher.start()

    def tearDown(self):
        """
        Executed after every test
        """
        self.clear_database()
        self.plugin_get_database_patcher.stop()
        self.state_get_database_patcher.stop()
        self.state_get_measurements_database_patcher.stop()

    # def run_homecon(self, sleep=0.01):
    #     self.homecon_thread = Thread(target=self.homecon.start)
    #     self.homecon_thread.start()
    #     time.sleep(sleep)
    #     self.homecon.stop()
    #     self.homecon_thread.join()


class Client(object):
    """
    A convienient wrapper for creating a websocket connection
    """

    async def connect(self, address):
        """
        connect to a websocket server
        """
        self.websocket = await asyncws.connect(address)

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


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
from shutil import rmtree

from threading import Thread

# from homecon.homecon import HomeCon
from pydal import DAL

# from homecon.core import plugin
from homecon.core import state

# create test databases
# database.db = database.Database(database='test_homecon.db')
# database.measurements_db = database.Database(database='test_measurements.db')
from homecon.core.database import base_path


test_database_path = os.path.join(base_path, 'db_test')


class TestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database_path_patcher = patch('homecon.core.database.database_path', new=test_database_path)

    def clear_database(self):
        if os.path.exists(test_database_path):
            rmtree(test_database_path)

    def setUp(self):
        """
        Executed before every test
        """

        self.clear_database()
        self.database_path_patcher.start()

    def tearDown(self):
        """
        Executed after every test
        """
        self.clear_database()
        self.database_path_patcher.stop()

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


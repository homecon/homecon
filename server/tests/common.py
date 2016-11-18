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
import subprocess
import threading
import time
import os
import sys
import shutil
import sqlite3
import json
import asyncio

from websocket import create_connection

sys.path.append(os.path.abspath('..'))
#from homecon import HomeCon

class HomeConTestCase(unittest.TestCase):
    
    homecondir = '..'
    logfile = os.path.join(homecondir,'log/homecon.log')

    if not os.path.exists('log'):
        os.mkdir('log')


    def create_database_connection(self):
        connection = sqlite3.connect('homecon')
    #    con = pymysql.connect('localhost', 'homecon_test', 'passwordusedfortesting', 'homecon_test')
    #    cur = con.cursor()
    #
        return connection


    def clear_database(self):
        try:
            os.remove('homecon.db')
        except:
            pass

    def start_homecon(self,sleep=1,clear_log=True,print_log=False):
        """
        starts homecon
        """

        temp = {}
        def target():
            temp['hc'] = HomeCon(loglevel='debug',printlog=print_log)
            temp['hc'].main()

        hc_thread = threading.Thread(target=target)
        hc_thread.start()

        while not 'hc' in temp:
            time.sleep(0.1) # starting homecon takes some time

        hc = temp['hc']


        return hc

    def stop_homecon(self,hc,sleep=1):
        """
        stop homecon
        """
        hc._loop.call_soon_threadsafe( hc.stop() )

        while hc._loop and hc._loop.is_running():
            time.sleep(0.1) # stopping homecon takes some time

    # run the loop to fire fire events
    def run_event_loop(self,loop,sleep=0.1):

        async def spam():
            asyncio.sleep(sleep)

        loop.run_until_complete(spam())


    def save_homecon_log(self,append=''):
        """
        save the homecon log into the tests direcory
        """

        shutil.copyfile(self.logfile, 'log/{}_{}{}_homecon.log'.format(self.__class__.__name__,self._testMethodName,append))

        # check if there are errors in the log file
        with open(self.logfile) as f:
            errors = []
            for l in f:
                if ' ERROR ' in l:
                    errors.append(l)

            self.assertEqual(len(errors),0,msg='\n' + '\n'.join(errors))

    def setUp(self):
        """
        Executed before every test

        clear the smarthome log file
        start smarthome
        """

        # clear the log file
        open(self.logfile, 'w').close()

        # clear the database
        self.clear_database()

    def tearDown(self):
        """
        Executed after every test

        stop smarthome
        copy the smarthome log file
        check the log file for errors
        """
        
        # stop smarthome if it is still running
        try:
            self.stop_smarthome()
        except:
            pass

        # clear the database
        self.clear_database()


class Client(object):
    """
    A convienient wrapper for creating a websocket connection
    """
    def __init__(self,address):

        self.address = address
        self.client = create_connection(self.address)

    def send(self,message):
        """
        recieve a websocket message in json format
        """
        self.client.send(json.dumps(message))

    def recv(self):
        """
        recieve a websocket message in json format
        """
        return json.loads( self.client.recv() )

    def close(self):
        self.client.close()

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
from homecon import HomeCon

class HomeConTestCase(unittest.TestCase):
    
    homecondir = '..'
    logfile = os.path.join(homecondir,'log/homecon.log')

    if not os.path.exists('log'):
        os.mkdir('log')


    @classmethod
    def setUpClass(cls):
        """
        Executed before the tests
        Set up smarthome and homecon
        """
        print('\nSetting up test environment')

        # copy the homecon plugin to the smarthome plugins folder
        #if os.path.exists(os.path.join(cls.smarthomedir,'plugins','homecon')):
        #    shutil.rmtree(os.path.join(cls.smarthomedir,'plugins','homecon'))

        #shutil.copytree(cls.homecondir, os.path.join(cls.smarthomedir,'plugins','homecon') )

        # setup the config files for testing
        #f = open(os.path.join(cls.smarthomedir,'etc/smarthome.conf'), 'w')
        #f.write('lat = 50.894914\nlon = 4.341551\nelev = 100\ntz = \'Europe/Brussels\'')
        #f.close()

        #f = open(os.path.join(cls.smarthomedir,'etc/plugin.conf'), 'w')
        #f.write('[homecon]\n    class_name = HomeCon\n    class_path = plugins.homecon\n    db_name = homecon_test\n    db_user=homecon_test\n    db_pass=passwordusedfortesting')
        #f.close()

        #f = open(os.path.join(cls.smarthomedir,'etc/logic.conf'), 'w').close()


    @classmethod
    def tearDownClass(cls):
        """
        Executed after the tests
        Return smarthome to its original state
        """
        print('\nTearing down test environment')

        # undo changes to the smarthome repo
        #os.remove(os.path.join(cls.smarthomedir,'etc/smarthome.conf'))
        #os.remove(os.path.join(cls.smarthomedir,'etc/plugin.conf'))
        #os.remove(os.path.join(cls.smarthomedir,'etc/logic.conf'))

        #shutil.rmtree(os.path.join(cls.smarthomedir,'plugins','homecon'))


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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import inspect
import time
import asyncio
import logging

from . import util
from . import core
from . import plugins



################################################################################
# create the logger
################################################################################

logFormatter = logging.Formatter('%(asctime)s    %(threadName)-15.15s %(levelname)-8.8s    %(message)s')
logger = logging.getLogger()

basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if not os.path.exists( os.path.join(basedir,'log')):
    os.makedirs(os.path.join(basedir,'log'))

if not 'homecon.fileHandler' in [lh.name for lh in logger.handlers]:
    fileHandler = logging.FileHandler(os.path.join(basedir,'log/homecon.log'))
    fileHandler.setFormatter(logFormatter)
    fileHandler.set_name('homecon.fileHandler')
    logger.addHandler(fileHandler)



################################################################################
# HomeCon object
################################################################################
class HomeCon(object): 
    def __init__(self,loglevel='info',printlog=False,demo=False):
        """
        Create a new HomeCon object

        Parameters
        ----------
        loglevel : str
            'info', 'debug', ...

        printlog : boolean
            print the log to the console or not

        """

        self.loglevel = loglevel
        self.printlog = printlog
        self.demo = demo

        ########################################################################
        # set logging properties
        ########################################################################
        if self.printlog:
            if not 'homecon.consoleHandler' in [lh.name for lh in logger.handlers]:
                consoleHandler = logging.StreamHandler()
                consoleHandler.setFormatter(logFormatter)
                consoleHandler.set_name('homecon.consoleHandler')
                logger.addHandler(consoleHandler)

        if self.loglevel=='info':
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)

        logging.info('Creating HomeCon object')


        ########################################################################
        # demo mode
        ########################################################################
        if self.demo:
            logging.info('Demo mode')
            # clear the databases
            core.database.DB_NAME = 'homecon_demo.db'
            core.database.DB_MEASUREMENTS_NAME = 'homecon_measurements_demo.db'

            try:
                os.remove(core.database.DB_NAME)
            except:
                pass

            try:
                os.remove(core.database.DB_MEASUREMENTS_NAME)
            except:
                pass

            # update the references to the states and components database
            core.states.states = core.states.States()
            core.states.components = core.components.Components()


        ########################################################################
        # get the event loop and queue
        ########################################################################
        self._loop = asyncio.get_event_loop()

        if self.loglevel == 'debug':
            self._loop.set_debug(True)

        self._queue = core.events.queue #asyncio.Queue(loop=self._loop)


        ########################################################################
        # load core components
        ########################################################################
        self.states = core.states.states
        self.components = core.components.components

        # load plugins
        self.coreplugins = {
            'states': core.plugins.states.States(),                # load states 1st
            'components': core.plugins.components.Components(),    # load components 2nd
            'plugins': core.plugins.plugins.Plugins(),
            'authentication': core.plugins.authentication.Authentication(),
            'pages': core.plugins.pages.Pages(),
            'schedules': core.plugins.schedules.Schedules(),
            'actions': core.plugins.actions.Actions(),
            'measurements': core.plugins.measurements.Measurements(),
            'weather': core.plugins.weather.Weather(),
            'building': core.plugins.building.Building(),
        }

        # load components
        self.components.load()

        # load the websocket
        self.coreplugins['websocket'] = core.plugins.websocket.Websocket()

        # demo mode
        if self.demo:
            self.coreplugins['demo'] = core.plugins.demo.Demo(self)


        logging.info('HomeCon object Initialized')



    def fire(self,event):
        """
        fire an event, mainly used for testing

        """

        async def do_fire(event):
            await self._queue.put(event)

        def do_create_task():
            self._loop.create_task(do_fire(event))

        self._loop.call_soon_threadsafe(do_create_task)



    async def listen(self):
        """
        listen for events in all plugins

        """

        while True:
            event = await self._queue.get()
            logging.debug(event)

            for plugin in self.coreplugins.values():
                self._loop.call_soon_threadsafe(plugin._listen, event)

            for plugin in self.coreplugins['plugins'].values():
                self._loop.call_soon_threadsafe(plugin._listen, event)



    def main(self):

        # Start the event loop
        logging.debug('Starting event loop')

        self._loop.create_task(self.listen())

        self._loop.run_forever()

        logging.info('Homecon stopped\n\n')



    def stop(self):
        logging.info('Stopping HomeCon')

        # cancel all tasks
        for task in asyncio.Task.all_tasks():
            task.cancel()

        # stop the websocket
        self._loop.call_soon_threadsafe(self.coreplugins['websocket'].stop)

        # stop the event loop
        self._loop.stop()
        time.sleep(0.1)





#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import inspect
import time
import asyncio
import logging

import core
import plugins



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
    def __init__(self,loglevel='info',printlog=False):
        """
        initialize a homecon object
        """

        ########################################################################
        # set logging properties
        ########################################################################
        if printlog:
            if not 'homecon.consoleHandler' in [lh.name for lh in logger.handlers]:
                consoleHandler = logging.StreamHandler()
                consoleHandler.setFormatter(logFormatter)
                consoleHandler.set_name('homecon.consoleHandler')
                logger.addHandler(consoleHandler)

        if loglevel=='info':
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)

        logging.info('HomeCon started')


        ########################################################################
        # get the event loop and queue
        ########################################################################
        self._loop = asyncio.get_event_loop()

        if loglevel == 'debug':
            self._loop.set_debug(True)

        self._queue = core.events.queue #asyncio.Queue(loop=self._loop)


        ########################################################################
        # start core components
        ########################################################################
        self.states = core.states.states
        self.components = core.components.components

        # start plugins
        self.coreplugins = {
            'states': core.plugins.states.States(),                # load states 1st
            'components': core.plugins.components.Components(),    # load components 2nd
            'plugins': core.plugins.plugins.Plugins(),
            'authentication': core.plugins.authentication.Authentication(),
            'pages': core.plugins.pages.Pages(),
            'schedules': core.plugins.schedules.Schedules(),
            'measurements': core.plugins.measurements.Measurements(),
            'weather': core.plugins.weather.Weather(),
        }

        # load components
        self.components.load()

        # load the websocket
        self.coreplugins['websocket'] = core.plugins.websocket.Websocket()

        logging.info('HomeCon Initialized')


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
        self._loop.call_soon_threadsafe(self.websocket.stop)

        # stop the event loop
        self._loop.stop()
        time.sleep(0.1)


if __name__ == '__main__':

    kwargs = {}
    if 'debug' in sys.argv:
        kwargs = {
            'loglevel': 'debug',
            'printlog': True,
        }

    # start homecon
    print('Starting HomeCon')
    print('Press Ctrl + C to stop')
    print('')
    hc = HomeCon(**kwargs)
    try:
        hc.main()
    except KeyboardInterrupt:
        hc.stop()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import inspect
import time
import logging

from queue import Empty

from homecon.__version__ import version as __version__
from homecon.core.event import queue
from homecon.plugins.plugins import Plugins

# from . import core
# from . import util


# configure logging
# logFormatter = logging.Formatter('%(asctime)s [%(levelname)s]  %(threadName)-15.15s  %(name)s: %(message)s',
#                                  datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# if not os.path.exists(os.path.join(basedir, 'log')):
#     os.makedirs(os.path.join(basedir, 'log'))
#
# if 'homecon.fileHandler' not in [lh.name for lh in logger.handlers]:
#     fileHandler = logging.FileHandler(os.path.join(sys.prefix, 'log/homecon/homecon.log'))
#     fileHandler.setFormatter(logFormatter)
#     fileHandler.set_name('homecon.fileHandler')
#     logger.addHandler(fileHandler)


# HomeCon object
class HomeCon(object): 
    def __init__(self):
        """
        Create a new HomeCon object
        """
        # set logging properties
        # if self.printlog:
        #     if 'homecon.consoleHandler' not in [lh.name for lh in logger.handlers]:
        #         consoleHandler = logging.StreamHandler()
        #         consoleHandler.setFormatter(logFormatter)
        #         consoleHandler.set_name('homecon.consoleHandler')
        #         logger.addHandler(consoleHandler)
        #
        # if self.loglevel == 'debug':
        #     logger.setLevel(logging.DEBUG)
        # elif self.loglevel == 'debugdb':
        #     logger.setLevel(9)
        # else:
        #     logger.setLevel(logging.INFO)
        logger.info('Creating HomeCon object')

        # create the main event queue
        self._queue = queue
        self._running = False

        # initialize core components
        # kwargs = {}
        # if demo:
        #     kwargs['dbname'] = 'demo_homecon'
        # core.initialize(**kwargs)

        # start plugins
        self.plugins = Plugins()

        logger.info('HomeCon object Initialized')

    def listen(self):
        """
        Listen for events in all plugins
        """
        while self._running:
            try:
                event = self._queue.get(timeout=1)
                logger.debug(event)
            except Empty:
                pass
            else:
                for plugin in self.plugins.values():
                    if event.target is None or event.target == plugin.name:
                        plugin.listen(event)

    def start(self):
        # start all plugins
        logger.debug('Starting plugins')
        for plugin in self.plugins.values():
            plugin.start()

        time.sleep(1)
        # Start the event loop
        logger.debug('Starting the event loop')
        self._running = True
        self.listen()

    def stop(self):
        logger.info('Stopping HomeCon')

        # stop plugins
        for plugin in self.plugins.values():
            plugin.stop()
            plugin.join()

        self._running = False
        logger.info('HomeCon stopped')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import logging

from queue import Empty

from homecon.__version__ import version as __version__
from homecon.core.event import queue
from homecon.plugins.plugins import Plugins


logger = logging.getLogger(__name__)


class HomeCon(object): 
    def __init__(self):
        """
        Create a new HomeCon object
        """
        logger.info('Creating HomeCon object')

        # create properties
        self.running = False
        self._queue = queue
        self.__version__ = __version__

        # start plugins
        self.plugins = Plugins()
        logger.info('HomeCon object Initialized')

    def listen(self):
        """
        Listen for events in all plugins
        """
        while self.running:
            try:
                event = self._queue.get(timeout=1)
                logger.debug(event)
            except Empty:
                pass
            else:
                for plugin in self.plugins.values():
                    if event.target is None or event.target.split('/')[0] == plugin.name:
                        plugin.listen(event)

    def start(self):
        # start all plugins
        self.running = True
        logger.info('Starting HomeCon')
        logger.debug('Starting plugins')
        for plugin in self.plugins.values():
            plugin.start()

        time.sleep(1)
        # Start the event loop
        logger.debug('Starting the event loop')
        self.listen()

    def stop(self):
        logger.info('Stopping HomeCon')

        # stop plugins
        for plugin in self.plugins.values():
            plugin.stop()
            plugin.join()

        self.running = False
        logger.info('HomeCon stopped')

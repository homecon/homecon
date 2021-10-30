#!/usr/bin/env python3
import time
import logging


from homecon.__version__ import version as __version__
from homecon.core.event import Event, IEventManager, NoEventError
from homecon.core.plugins.plugin import IPluginManager


logger = logging.getLogger(__name__)


class IExecutor:
    def submit(self, fn, *args, **kwargs):
        raise NotImplementedError


class HomeCon:
    def __init__(self, event_manager: IEventManager, plugin_manager: IPluginManager, executor: IExecutor):
        """
        Create a new HomeCon object
        """
        logger.info('Creating HomeCon object')

        # create properties
        self._running = False
        self._event_manager = event_manager
        self._plugin_manager = plugin_manager
        self._executor = executor

        self.__version__ = __version__
        logger.info('HomeCon object Initialized')

    @property
    def running(self):
        return self._running

    def handle_event(self, event: Event):
        target_plugin = event.target.split('/')[0] if event.target is not None else None
        for plugin in self._plugin_manager.values():
            if event.target is None or target_plugin == plugin.name:
                self._executor.submit(plugin.handle_event, event)

    def get_and_handle_event(self):
        try:
            event = self._event_manager.get()
            logger.debug(event)
        except NoEventError:
            pass
        else:
            self.handle_event(event)

    def run(self):
        """
        Listen for events in all plugins
        """
        while self._running:
            self.get_and_handle_event()

    def start(self):
        self._running = True
        logger.info('Starting HomeCon')
        logger.debug('Starting plugins')
        self._plugin_manager.start()

        time.sleep(1)
        logger.debug('Starting event handling')
        self.run()

    def stop(self):
        logger.info('Stopping HomeCon')

        self._plugin_manager.stop()
        self._running = False
        logger.info('HomeCon stopped')

#!/usr/bin/env python3
import logging

from typing import Iterable, Tuple, Dict
from homecon.core.event import Event, IEventManager
from homecon.core.states.state import IStateManager
from homecon.core.pages.pages import IPagesManager

logger = logging.getLogger(__name__)


class IPlugin:
    @property
    def name(self):
        raise NotImplementedError

    def start(self):
        pass

    def stop(self):
        pass

    def join(self):
        pass

    def handle_event(self, event: Event):
        raise NotImplementedError

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class BasePlugin(IPlugin):
    def __init__(self, name: str, event_manager: IEventManager, state_manager: IStateManager, pages_manager: IPagesManager):
        self._name = name
        self._event_manager = event_manager
        self._state_manager = state_manager
        self._pages_manager = pages_manager

        self.listeners = self._get_listeners()

    @property
    def name(self):
        return self._name

    def fire(self, type_: str, data: dict, target: str = None, reply_to: str = None):
        source = self.name
        self._event_manager.fire(type_, data, target=target, reply_to=reply_to, source=source)

    def handle_event(self, event: Event):
        """
        Base event handler method called when an event is taken from the queue.

        Parameters
        ----------
        event : Event
            An Event instance.

        Notes
        -----
        Source checking to avoid infinite loops needs to be done in the plugin listener method.
        """
        listener = self.listeners.get(event.type, None)
        if listener is not None:
            # noinspection PyBroadException
            try:
                listener(event)
            except Exception:
                logger.exception(f'error in event listener {event.type}')

    def _get_listeners(self):
        """
        Gets listener methods and adds them to the listeners dictionary.
        """
        listeners = {}
        for method in dir(self):
            if method.startswith('listen_'):
                event_type = '_'.join(method.split('_')[1:])
                listeners[event_type] = getattr(self, method)
        return listeners


class IPluginManager:
    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def __getitem__(self, key: str) -> IPlugin:
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __contains__(self, key: str):
        raise NotImplementedError

    def keys(self) -> Iterable[str]:
        raise NotImplementedError

    def items(self) -> Iterable[Tuple[str, IPlugin]]:
        raise NotImplementedError

    def values(self) -> Iterable[IPlugin]:
        raise NotImplementedError


class MemoryPluginManager(IPluginManager):
    def __init__(self, plugins: Dict[str, IPlugin], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plugins = plugins

    def start(self):
        for plugin in self._plugins.values():
            plugin.start()

    def stop(self):
        for plugin in self._plugins.values():
            plugin.stop()

        for plugin in self._plugins.values():
            plugin.join()

    def __getitem__(self, key: str) -> IPlugin:
        return self._plugins.__getitem__(key)

    def __iter__(self):
        return self._plugins.__iter__()

    def __contains__(self, key: str):
        return self._plugins.__contains__(key)

    def keys(self) -> Iterable[str]:
        return self._plugins.keys()

    def items(self):
        return self._plugins.items()

    def values(self) -> Iterable[IPlugin]:
        return self._plugins.values()

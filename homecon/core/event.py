#!/usr/bin/env python3
import logging

from queue import Queue, Empty


logger = logging.getLogger(__name__)


class Event:
    """

    Parameters
    ----------
    type_ :
        The event type.
    data :
        The data describing the event.
    source :
        The source of the event.
    target :
        The target of the event.
    reply_to :
        ???
    """
    def __init__(self, event_manager: 'IEventManager', type_: str, data: dict, source: str = None, target: str = None, reply_to: str = None):
        self.event_manager = event_manager
        self.type = type_
        self.data = data
        self.source = source
        self.target = target
        self.reply_to = reply_to

    def reply(self, data, **kwargs):
        full_data = {'event': self.type, 'data': data}
        self.event_manager.fire('reply', full_data, target=self.reply_to, **kwargs)

    def __repr__(self):
        new_data = dict(self.data)
        for key in ['password', 'token']:
            if key in new_data:
                new_data[key] = '***',

        print_data = new_data.__repr__()
        if len(print_data) > 405:
            print_data = print_data[:200] + ' ... ' + print_data[-200:]

        return f'<Event: {self.type}, data: {print_data}, source: {self.source}, target: {self.target}, reply_to: {self.reply_to}>'


class NoEventError(Exception):
    pass


class IEventManager:
    def fire(self, *args, **kwargs) -> Event:
        raise NotImplementedError

    def get(self) -> Event:
        raise NotImplementedError


class EventManager(IEventManager):
    def __init__(self):
        self._queue = Queue()

    def fire(self, *args, **kwargs) -> Event:
        event = Event(self, *args, **kwargs)
        logger.debug(f'putting {event} on queue')
        self._queue.put(event)
        return event

    def get(self) -> Event:
        try:
            event = self._queue.get(timeout=1)
            logger.debug(f'got {event} from queue')
        except Empty:
            raise NoEventError
        else:
            return event

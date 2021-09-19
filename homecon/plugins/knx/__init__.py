#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time
from typing import Callable, Any

from knxpy.knxd import KNXD
from knxpy.util import decode_dpt

from homecon.core.plugins.plugin import BasePlugin

logger = logging.getLogger(__name__)


class ListMapping:
    def __init__(self):
        self._map = {}

    def add(self, key, val):
        if key not in self._map:
            self._map[key] = []
        if val not in self._map[key]:
            self._map[key].append(val)

    def remove(self, val):
        for values in self._map.values():
            try:
                values.pop(values.index(val))
            except ValueError:
                pass

    def get(self, key) -> list:
        return self._map.get(key, [])

    def keys(self):
        return self._map.keys()


class IKNXDConnection:
    def connect(self, address: str, port: int) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    def listen(self, callback: Callable):
        raise NotImplementedError

    def group_read(self, key: str):
        raise NotImplementedError

    def group_write(self, ga: str, value: Any, dpt: str):
        raise NotImplementedError


class Message:
    def __init__(self, dst, val):
        self.dst = dst
        self.val = val


class KNXDConnection(IKNXDConnection):
    def __init__(self):
        self.knxd = None

    def connect(self, address: str, port: int) -> None:
        if self.knxd is not None:
            self.knxd.close()
        self.knxd = KNXD(address, port)
        self.knxd.connect()

    def close(self) -> None:
        self.knxd.close()

    def listen(self, callback: Callable[[Message], None]):
        return self.knxd.listen(callback)

    def group_read(self, key: str):
        return self.knxd.group_read(key)

    def group_write(self, ga: str, value: Any, dpt: str):
        self.knxd.group_write(ga, value, dpt)


class Knx(BasePlugin):
    """
    Communicate with an EIB-KNX home automation system through knxd

    """
    DEFAULT_DPT = '1'
    KNX_GA_READ = 'knx_ga_read'
    KNX_GA_WRITE = 'knx_ga_write'
    KNX_DPT = 'knx_dpt'
    KNX_EVAL_READ = 'knx_eval_read'
    KNX_EVAL_WRITE = 'knx_eval_write'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ga_read_mapping = ListMapping()
        self.connection = KNXDConnection()
        self.address_state = None
        self.port_state = None

        # add settings states
        self._state_manager.add('settings', type=None)
        self._state_manager.add('knxd', type=None, parent_path='/settings')
        self._state_manager.add('address', parent_path='/settings/knxd',
                                type='str', quantity='', unit='',
                                label='', description='knxd address', value='localhost')
        self._state_manager.add('port', parent_path='/settings/knxd',
                                type='int', quantity='', unit='',
                                label='', description='knxd port', value=6720)

    def start(self):
        # build the ga_read_mapping
        for state in self._state_manager.all():
            knx_ga_read = state.config.get(self.KNX_GA_READ)
            if knx_ga_read is not None:
                self.ga_read_mapping.add(knx_ga_read, state.id)

        self.connect()
        logger.debug('KNX plugin Initialized')

    def connect(self):
        try:
            address = self._state_manager.get('/settings/knxd/address').value
            port = self._state_manager.get('/settings/knxd/port').value

            if address is not None and port is not None:
                self.connection.connect(address, port)
                self.connection.listen(self.callback)

                time.sleep(1)
                for key in self.ga_read_mapping.keys():
                    logger.debug('reading {}'.format(key))
                    self.connection.group_read(key)
        except ConnectionRefusedError:
            logger.exception('KNXD connection refused')

    def callback(self, message):
        if message is not None:
            logger.debug('received message {}'.format(message))
            try:
                # find a state with the dst address
                for state_id in self.ga_read_mapping.get(message.dst):
                    state = self._state_manager.get(id=state_id)
                    logger.debug('found state {} corresponding to message {}'.format(state, message))
                    dpt = state.config.get(self.KNX_DPT, self.DEFAULT_DPT)
                    eval_read = state.config.get(self.KNX_EVAL_READ)
                    if eval_read is not None:
                        value = eval(eval_read, {'value': decode_dpt(message.val, dpt)})
                    else:
                        value = decode_dpt(message.val, dpt)
                    state.set_value(value, source=self.name)

            except:  # noqa
                logger.exception('error while parsing message {}'.format(message))

    def listen_state_value_changed(self, event):
        state = event.data['state']

        if state.path == 'settings/knxd/address' or state.path == 'settings/knxd/port':
            self.connect()

        elif self.KNX_GA_WRITE in state.config and self.KNX_DPT in state.config:
            if not event.source == self.name:
                eval_write = state.config.get(self.KNX_EVAL_WRITE)
                if eval_write is not None:
                    value = eval(eval_write, {'value': state.value})
                else:
                    value = state.value
                logger.debug('{} changed, writing {} to knx group address: {}'
                             .format(state, value, state.config[self.KNX_GA_WRITE]))
                self.connection.group_write(
                    str(state.config[self.KNX_GA_WRITE]), value, str(state.config[self.KNX_DPT])
                )

    def listen_state_added(self, event):
        state = event.data['state']
        if self.KNX_GA_READ in state.config:
            self.ga_read_mapping.add(state.config[self.KNX_GA_READ], state.id)

    def listen_state_changed(self, event):
        state = event.data['state']
        if self.KNX_GA_READ in state.config:
            self.ga_read_mapping.add(state.config[self.KNX_GA_READ], state.id)
        else:
            self.ga_read_mapping.remove(state)

    def listen_state_deleted(self, event):
        state = event.data['state']
        self.ga_read_mapping.remove(state.id)

    @property
    def settings_sections(self):
        sections = [{
            'config': {
                'title': 'knxd'
            },
            'widgets': [{
                'type': 'value-input',
                'config': {
                    'state': self._state_manager.get(path='/settings/knxd/address').id,
                    'label': 'Address',
                }
            }, {
                'type': 'value-input',
                'config': {
                    'state': self._state_manager.get(path='/settings/knxd/port').id,
                    'label': 'Port',
                }
            }

            ]
        }]
        return sections

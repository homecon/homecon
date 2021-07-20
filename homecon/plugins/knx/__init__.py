#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time

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


class Knx(BasePlugin):
    """
    Communicate with an EIB-KNX home automation system through knxd

    """
    DEFAULT_DPT = '1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ga_read_mapping = ListMapping()
        self.connection = None
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
            knx_ga_read = state.config.get('knx_ga_read')
            if knx_ga_read is not None:
                self.ga_read_mapping.add(knx_ga_read, state.id)

        self.connect()
        logger.debug('KNX plugin Initialized')

    def connect(self):
        try:
            if self.connection is not None:
                self.connection.close()

            address = self._state_manager.get('/settings/knxd/address').value
            port = self._state_manager.get('/settings/knxd/port').value

            if address is not None and port is not None:
                self.connection = KNXD(address, port)
                self.connection.connect()
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
                    dpt = state.config.get('knx_dpt', self.DEFAULT_DPT)
                    state.set_value(decode_dpt(message.val, dpt), source=self.name)

            except:  # noqa
                logger.exception('error while parsing message {}'.format(message))

    def listen_state_value_changed(self, event):
        state = event.data['state']

        if state.path == 'settings/knxd/address' or state.path == 'settings/knxd/port':
            self.connect()

        elif 'knx_ga_write' in state.config and 'knx_dpt' in state.config:
            if not event.source == self.name:
                logger.debug('{} changed, writing {} to knx group address: {}'
                             .format(state, state.value, state.config['knx_ga_write']))
                self.connection.group_write(
                    str(state.config['knx_ga_write']), state.value, str(state.config['knx_dpt'])
                )

    def listen_state_added(self, event):
        state = event.data['state']
        if 'knx_ga_read' in state.config:
            self.ga_read_mapping.add(state.config['knx_ga_read'], state.id)

    def listen_state_changed(self, event):
        state = event.data['state']
        if 'knx_ga_read' in state.config:
            self.ga_read_mapping.add(state.config['knx_ga_read'], state.id)
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import time

from knxpy.knxd import KNXD
from knxpy.util import decode_dpt

from homecon.core.plugin import Plugin
from homecon.core.state import State

logger = logging.getLogger(__name__)


class Knx(Plugin):
    """
    Communicate with an EIB-KNX home automation system through knxd

    """
    DEFAULT_DPT = '1'

    def __init__(self):
        super().__init__()
        self.ga_read_mapping = {}
        self.connection = None
        self.address_state = None
        self.port_state = None

    def initialize(self):
        State.add('settings', type=None)
        State.add('knxd', type=None, parent='/settings')
        State.add('address', parent='/settings/knxd',
                  type='string', quantity='', unit='',
                  label='', description='knxd address', value='localhost')
        State.add('port', parent='/settings/knxd',
                  type='number', quantity='', unit='',
                  label='', description='knxd port', value=6720)

        # build the ga_read_mapping
        for state in State.all():
            knx_ga_read = state.config.get('knx_ga_read')
            if knx_ga_read is not None:
                self.ga_read_mapping[knx_ga_read] = state.id

        self.connect()
        logger.debug('KNX plugin Initialized')

    def connect(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = KNXD(State.get('/settings/knxd/address').value, int(State.get('/settings/knxd/port').value))
        self.connection.connect()
        self.connection.listen(self.callback)

        time.sleep(1)
        for key in self.ga_read_mapping.keys():
            logger.debug('reading {}'.format(key))
            self.connection.group_read(key)

    def callback(self, message):
        if message is not None:
            logger.debug('received message {}'.format(message))
            try:
                # find a state with the dst address
                state_id = self.ga_read_mapping.get(message.dst)
                if state_id is not None:
                    state = State.get(id=state_id)
                    logger.debug('found state {} corresponding to message {}'.format(state, message))
                    dpt = state.config.get('knx_dpt', self.DEFAULT_DPT)
                    state.set_value(decode_dpt(message.val, dpt), source=self.name)
                else:
                    logger.debug('no state corresponding to ga {}'.format(message.dst))
            except:
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
            self.ga_read_mapping[state.config['knx_ga_read']] = state.id

    @property
    def settings_sections(self):
        sections = [{
            'config': {
                'title': 'knxd'
            },
            'widgets': [{
                'type': 'value-input',
                'config': {
                    'state': State.get(path='/settings/knxd/address').id,
                    'label': 'Address',
                }
            }, {
                'type': 'value-input',
                'config': {
                    'state': State.get(path='/settings/knxd/port').id,
                    'label': 'Port',
                }
            }

            ]
        }]
        return sections

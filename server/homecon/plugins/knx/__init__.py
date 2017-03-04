#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from ... import core

class Knx(core.plugin.Plugin):

    def initialize(self):

        logging.debug('KNX plugin Initialized')


    def listen_state_changed(self,event):
        state = event.data['state']
        if 'knx_ga' in state.config:
            logging.debug('{} changed, write {} to knx group address: {}'.format(state.path,state.value,state.config['knx_ga']))
        






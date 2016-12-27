#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from .. import Plugin

class Knx(Plugin):


    def listen(self,event):

        if event.type == 'state_changed':
            # what is the group address of the item
            state = event.data['state']
            if 'knx_ga' in state.config:
                logging.debug('{} changed, write {} to knx ga: {}'.format(state.path,state.value,state.config['knx_ga']))
        






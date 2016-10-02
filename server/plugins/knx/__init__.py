#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from .. import Plugin

class Knx(Plugin):


    def listen(self,event):

        if event.data['cmd'] == 'item_changed':
            # what is the group address of the item
            item = event.data['item']
            if 'knx_ga' in item.config:
                logging.debug('{} changed, write {} to knx ga: {}'.format(item.path,item.value,item.config['knx_ga']))
        






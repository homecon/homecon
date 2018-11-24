#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from homecon.core.plugin import Plugin
from homecon.core.event import Event

from homecon.core.websocket import Websocket

logger = logging.getLogger(__name__)


class Websocket(Plugin):
    """
    Class to control the HomeCon websocket

    """
    def __init__(self):
        super().__init__()
        self.websocket = None

    def initialize(self):
        logger.debug('Websocket plugin Initialized')
        self.websocket = Websocket()

    def listen_websocket_send(self, event):
        self.websocket.send(event['data'])

    def listen_websocket_reply(self, event):
        pass

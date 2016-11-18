#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import functools
import json
import datetime
import pytz
import uuid

from .. import database
from ..plugin import Plugin

class Schedules(Plugin):
    """
    Class to control the HomeCon scheduling
    
    """

    def initialize(self):
        """
        Initialize

        """
        self._schedules = {}
        self._scheduled = {}

        self.timezone = pytz.utc

        self._db = database.Database(database='homecon.db')
        

        # get all schedules from the database
        result = self._db_schedules.GET()
        for schedule in result:
            self.add_local( schedule['path'],json.loads(schedule['config']),json.loads(schedule['value']) )




    def listen_add_component():


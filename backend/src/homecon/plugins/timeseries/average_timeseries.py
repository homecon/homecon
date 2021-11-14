#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import pytz
from datetime import datetime, timedelta

from dataclasses import dataclass
from typing import List, Any

from pydal import DAL, Field

from homecon.core.plugins.plugin import IPlugin
from homecon.core.states.state import IStateManager, State, StateEventsTypes, TimestampedValue
from homecon.core.event import IEventManager, Event


class Aggregation:
    HOUR = '1h'
    DAY = '1d'
    WEEK = '1w'
    MONTH = '1M'
    YEAR = '1Y'


@dataclass
class AverageValue:
    aggregation: str
    from_: int
    to: int
    period: str
    value: Any


class AverageTimeseries(IPlugin):
    DEFAULT_TIMEZONE = 'utc'
    TIMEZONE_STATE_PATH = '/settings/location/timezone'

    def __init__(self, event_manager: IEventManager, state_manager: IStateManager, db_folder: str, db_uri: str,):
        self._event_manager = event_manager
        self._state_manager = state_manager
        self._subscriptions = []

        self._db = DAL(db_uri, folder=db_folder)

        self._table_values_aggregation = self._db.define_table(
            'state_values_log',
            Field('state_key', type='string'),
            Field('aggregation', type='string'),
            Field('from', type='integer'),
            Field('to', type='integer'),
            Field('period', type='string'),
            Field('value', type='string'),
        )

    @property
    def name(self):
        return 'average_timeseries'

    @property
    def timezone(self):
        state = self._state_manager.get(self.TIMEZONE_STATE_PATH)
        if state is None:
            return self.DEFAULT_TIMEZONE
        return state.value or self.DEFAULT_TIMEZONE

    def handle_event(self, event: Event):
        if event.type == StateEventsTypes.STATE_VALUE_CHANGED:
            self._handle_state_value_changed_event(event)

    def _handle_state_value_changed_event(self, event: Event):
        state = event.data['state']
        if state.log_key != state.NO_LOGGING_KEY:
            self.aggregate(state)

    def aggregate(self, state: State):
        timestamp = int(time.time())
        last_hour_value = self.aggregate_hour(state, timestamp - 3600)
        hour_value = self.aggregate_hour(state, timestamp)

    def aggregate_hour(self, state: State, timestamp: int) -> AverageValue:
        tz = pytz.timezone(self.timezone)
        from_ = datetime.fromtimestamp(timestamp, tz=tz).replace(minute=0, second=0, microsecond=0)
        to = from_ + timedelta(hours=1)
        period = from_.strftime('DD-MM-YYYY HH:mm')
        timeseries = state.get_values_log(from_.timestamp(), to.timestamp())


    @staticmethod
    def _calculate_average(timeseries: List[TimestampedValue], since: int, until: int):
        moment = 0
        last_value = 0
        last_timestamp = since

        for val in timeseries:
            if val.timestamp >= until:
                moment += last_value * (until - last_timestamp)
                break
            elif val.timestamp > since:
                moment += last_value * (val.timestamp - last_timestamp)
                last_value = val.value
                last_timestamp = val.timestamp
            else:
                last_timestamp = since

        return moment / (until - since)

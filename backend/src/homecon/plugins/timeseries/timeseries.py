#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time

from dataclasses import dataclass, asdict
from typing import List

from pydal import DAL, Field

from homecon.core.plugins.plugin import IPlugin
from homecon.core.states.state import IStateManager, StateEventsTypes
from homecon.core.event import IEventManager, Event


logger = logging.getLogger(__name__)


@dataclass
class StateValueTimeseries:
    state_id: int
    timestamps: List[float]
    values: List[float]


class IStateValueRepository:
    def store(self, state_id: int, timestamp: float, value: float) -> None:
        raise NotImplementedError

    def get(self, state_id: int, since: float, until: float) -> StateValueTimeseries:
        raise NotImplementedError


class PyDalStateValueRepository(IStateValueRepository):
    def __init__(self, folder: str, uri: str):
        self._db = DAL(uri, folder=folder)
        self._table = self._db.define_table(
            'state_timeseries',
            Field('state_id', type='integer'),
            Field('timestamp', type='float'),
            Field('value', type='float'),
        )

    def store(self, state_id: int, timestamp: float, value: float) -> None:
        try:
            # noinspection PyProtectedMember
            self._db._adapter.reconnect()
            self._db.state_timeseries.insert(state_id=state_id, timestamp=timestamp, value=value)
            self._db.commit()
            # noinspection PyProtectedMember
            self._db._adapter.close()
        except Exception:
            logger.exception('could not store state value timeseries')

    def get(self, state_id: int, since: float, until: float) -> StateValueTimeseries:
        for row in self._db().select(self._db.state_timeseries.ALL):
            pass
        timestamps = []
        values = []
        return StateValueTimeseries(state_id, timestamps, values)


class TimeseriesEventTypes:
    TIMESERIES = 'timeseries'


class TimeSeries(IPlugin):
    """
    Store state history.
    """

    SUPPORTED_TYPES = ['int', 'float', 'bool']

    def __init__(self, event_manager: IEventManager, state_manager: IStateManager, value_repository: IStateValueRepository):
        self._event_manager = event_manager
        self._state_manager = state_manager
        self._value_repository = value_repository

    @property
    def name(self):
        return 'timeseries'

    def handle_event(self, event: Event):
        if event.type == StateEventsTypes.STATE_UPDATED:
            self._handle_state_value_changed_event(event)

        elif event.type == StateEventsTypes.STATE_VALUE_CHANGED:
            self._handle_state_value_changed_event(event)

        elif event.type == TimeseriesEventTypes.TIMESERIES:
            pass

    def _handle_state_value_changed_event(self, event: Event):
        state = event.data['state']
        if state.type in self.SUPPORTED_TYPES:
            self._value_repository.store(state.id, time.time(), float(state.value))

    def _handle_timeseries_event(self, event: Event):
        state_id = event.data['state_id']
        since = event.data['since']
        until = event.data['until']
        timeseries = self._value_repository.get(state_id, since, until)
        event.reply(data={'timeseries': asdict(timeseries)})

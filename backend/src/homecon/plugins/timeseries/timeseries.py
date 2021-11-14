#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time

from dataclasses import dataclass

from homecon.core.plugins.plugin import IPlugin
from homecon.core.states.state import IStateManager, StateEventsTypes
from homecon.core.event import IEventManager, Event


logger = logging.getLogger(__name__)


class TimeseriesEventTypes:
    STATE_TIMESERIES = 'state_timeseries'
    STATE_TIMESERIES_UPDATE = 'state_timeseries_update'


@dataclass
class Subscription:
    target: str
    state_id: int
    valid_until: int
    last_timestamp: float


class TimeSeries(IPlugin):
    """
    Store state history.
    """
    DEFAULT_VALIDITY_TIME = 3600

    def __init__(self, event_manager: IEventManager, state_manager: IStateManager):
        self._event_manager = event_manager
        self._state_manager = state_manager
        self._subscriptions = []

    @property
    def name(self):
        return 'timeseries'

    def handle_event(self, event: Event):
        if event.type == TimeseriesEventTypes.STATE_TIMESERIES:
            self._handle_timeseries_event(event)

        elif event.type == StateEventsTypes.STATE_UPDATED:
            self._handle_state_value_changed_event(event)

        elif event.type == StateEventsTypes.STATE_VALUE_CHANGED:
            self._handle_state_value_changed_event(event)

    def _add_subscription(self, subscription: Subscription):
        for old_subscription in self._subscriptions:
            if subscription.state_id == old_subscription.state_id and subscription.target == old_subscription.target:
                old_subscription.valid_until = int(time.time() + self.DEFAULT_VALIDITY_TIME)
                return

        self._subscriptions.append(subscription)

    def _handle_timeseries_event(self, event):
        state = self._state_manager.get(id=event.data['id'])
        if state is not None:
            since = event.data['since']
            until = event.data.get('until')

            # get data
            timeseries = state.get_values_log(since, until=until)

            # make subscription
            if until is None:
                self._add_subscription(
                    Subscription(
                        target=event.reply_to,
                        state_id=state.id,
                        valid_until=int(time.time() + self.DEFAULT_VALIDITY_TIME),
                        last_timestamp=timeseries[-1].timestamp if len(timeseries) > 0 else since
                    )
                )
            # push data
            event.reply(data={'id': state.id, 'timeseries': [(value.timestamp, value.value) for value in timeseries]})

    def _handle_state_value_changed_event(self, event: Event):
        state = event.data['state']

        # remove outdated subscriptions
        self._subscriptions = [subscription for subscription in self._subscriptions if subscription.valid_until > time.time()]

        data = None
        for subscription in self._subscriptions:
            if state.id == subscription.state_id:

                # get data
                if data is None:
                    timeseries = state.get_values_log(subscription.last_timestamp + 1e-6)
                    if len(timeseries) > 0:
                        subscription.last_timestamp = timeseries[-1].timestamp

                    data = {'id': state.id, 'timeseries': [(value.timestamp, value.value) for value in timeseries]}

                # push new data
                self._event_manager.fire('reply',
                                         data={'event': TimeseriesEventTypes.STATE_TIMESERIES_UPDATE, 'data': data},
                                         target=subscription.target)



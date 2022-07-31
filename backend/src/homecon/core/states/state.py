#!/usr/bin/env python3
import logging

from typing import Any, List, Optional
from dataclasses import dataclass
from uuid import uuid4

from homecon.core.event import IEventManager, Event


logger = logging.getLogger(__name__)


class StateEventsTypes:
    STATE_VALUE_CHANGED = 'state_value_changed'
    STATE_UPDATED = 'state_updated'
    STATE_DELETED = 'state_deleted'
    STATE_ADDED = 'state_added'


class InvalidEventException(Exception):
    pass


@dataclass
class StateValueChangedEvent:
    type = StateEventsTypes.STATE_VALUE_CHANGED
    state: 'State'
    old: Any
    source: Optional[str] = None
    target: Optional[str] = None
    reply_to: Optional[str] = None

    @staticmethod
    def from_event(event: Event) -> 'StateValueChangedEvent':
        if event.type != StateEventsTypes.STATE_VALUE_CHANGED:
            raise InvalidEventException('invalid event type')

        try:
            return StateValueChangedEvent(
                event.data['state'], event.data['old'],
                event.source, event.target, event.reply_to
            )
        except KeyError as e:
            raise InvalidEventException from e

    def event_data(self) -> dict:
        return {'state': self.state, 'old': self.old, 'new': self.state.value}

    def fire(self, event_manager: IEventManager):
        event_manager.fire(self.type,
                           data={'state': self.state, 'old': self.old, 'new': self.state.value},
                           source=self.source, target=self.target, reply_to=self.reply_to)


@dataclass
class TimestampedValue:
    timestamp: float
    value: Any


class State:

    NO_LOGGING_KEY = ''

    # noinspection PyShadowingBuiltins
    def __init__(self, state_manager: 'IStateManager', event_manager: 'IEventManager', key, name,
                 parent: 'State' = None,
                 type: str = None, quantity: str = None, unit: str = None, label: str = None, description: str = None,
                 log_key: Optional[str] = '',
                 config: dict = None, value: Any = None):
        self._state_manager = state_manager
        self._event_manager = event_manager
        self.key = key
        self.name = name
        self.parent = parent
        self.type = type
        self.quantity = quantity
        self.unit = unit
        self.label = label
        self.description = description
        self.log_key = str(uuid4()) if log_key is None else log_key
        self.config = config or {}
        self._value = value

    def notify_created(self):
        self._event_manager.fire(StateEventsTypes.STATE_ADDED, data={'state': self})

    def notify_deleted(self):
        self._event_manager.fire(StateEventsTypes.STATE_DELETED, data={'state': self})

    def notify_updated(self):
        self._event_manager.fire(StateEventsTypes.STATE_UPDATED, data={'state': self})

    def notify_value_changed(self, old_val=None, source=None):
        StateValueChangedEvent(self, old_val, source=source).fire(self._event_manager)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val) -> None:
        if self._value != val or self.config.get('force_change', False):
            self.set_value(val)

    def set_value(self, val, source: str = None) -> None:
        old_val = self._value
        self._value = val
        self._state_manager.update(self)
        self.notify_value_changed(old_val=old_val, source=source)

    def update(self, **kwargs) -> None:
        old_value = None
        notify_value_changed = False

        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'parent' in kwargs:
            self.parent = kwargs['parent']
        if 'type' in kwargs:
            self.type = kwargs['type']
        if 'quantity' in kwargs:
            self.quantity = kwargs['quantity']
        if 'unit' in kwargs:
            self.unit = kwargs['unit']
        if 'label' in kwargs:
            self.label = kwargs['label']
        if 'description' in kwargs:
            self.description = kwargs['description']
        if 'log_key' in kwargs:
            self.log_key = kwargs['log_key']
        if 'config' in kwargs:
            self.config = kwargs['config']
        if 'value' in kwargs:
            old_value = self._value
            self._value = kwargs['value']
            notify_value_changed = True

        self._state_manager.update(self)
        self.notify_updated()
        if notify_value_changed:
            self.notify_value_changed(old_value)

    @property
    def children(self) -> List['State']:
        return [s for s in self._state_manager.all() if s.parent is not None and s.parent.key == self.key]

    @property
    def path(self) -> str:
        if self.parent is None:
            return '/{}'.format(self.name)
        else:
            return '{}/{}'.format(self.parent.path, self.name)

    def get_values_log(self, since: float, until: Optional[float] = None) -> List[TimestampedValue]:
        return self._state_manager.get_state_values_log(self, since, until=until)

    def __call__(self):
        return self.value

    def __repr__(self):
        return f'<State: {self.key}, name: {self.name}, value: {self.value}>'

    def serialize(self):
        return {
            'key': self.key, 'name': self.name, 'path': self.path, 'value': self.value,
            'parent': None if self.parent is None else self.parent.key,
            'type': self.type, 'quantity': self.quantity, 'unit': self.unit, 'label': self.label,
            'description': self.description, 'log_key': self.log_key,
            'config': self.config or {}
        }


class CouldNotStoreStateException(Exception):
    pass


class IStateManager:
    def __init__(self, event_manager: IEventManager):
        self.event_manager = event_manager

    def all(self) -> List[State]:
        raise NotImplementedError

    def get(self, path: str = None, key: str = None) -> Optional[State]:
        raise NotImplementedError

    def find(self, expr: str) -> List[State]:
        raise NotImplementedError

    def exists(self, name: str, parent: Optional[State] = None):
        raise NotImplementedError

    def _create_state(self, key: str, name: str, parent: Optional[State] = None,
                      type: Optional[str] = None, quantity: Optional[str] = None, unit: Optional[str] = None,
                      label: Optional[str] = None, description: Optional[str] = None, log_key: Optional[str] = '',
                      config: Optional[dict] = None, value: Optional[Any] = None) -> State:
        raise NotImplementedError

    def delete(self, state: State):
        state.notify_deleted()

    def update(self, state: State):
        raise NotImplementedError

    def add(self, name: str, parent: Optional[State] = None, parent_path: Optional[str] = None,
            type: Optional[str] = None, quantity: Optional[str] = None, unit: Optional[str] = None,
            label: Optional[str] = None, description: Optional[str] = None, log_key: Optional[str] = '',
            config: Optional[dict] = None, value: Optional[Any] = None, key: Optional[str] = None):

        key = key or str(uuid4())

        if parent is None:
            if parent_path is not None:
                parent = self.get(path=parent_path)

        existing_state = self.exists(name, parent=parent)
        if existing_state:
            return existing_state

        try:
            state = self._create_state(key, name, parent=parent, type=type, quantity=quantity, unit=unit,
                                       label=label, description=description, config=config, log_key=log_key, value=value)
        except CouldNotStoreStateException:
            pass
        else:
            state.notify_created()
            return state

    def get_state_values_log(self, state: State, since: float, until: float) -> List[TimestampedValue]:
        raise NotImplementedError

    def export_states(self) -> List[dict]:
        states_list = []
        for state in self.all():
            dict_ = {
                'key': state.key,
                'name': state.name,
                'parent': state.parent.key if state.parent is not None else None,
                'type': state.type,
                'quantity': state.quantity,
                'unit': state.unit,
                'label': state.label,
                'description': state.description,
                'config': state.config,
                'value': state.value
            }
            if state.log_key != State.NO_LOGGING_KEY:
                dict_['log_key'] = state.log_key
            states_list.append(dict_)
        return sorted(states_list, key=lambda x: len(x.get('parent_path') or ''))

    def import_states(self, states_list: List[dict]):
        old_states = list(self.all())
        for state in old_states:
            self.delete(state)

        maximum_depth = 20
        remaining_states = states_list
        for i in range(maximum_depth):
            if len(remaining_states) == 0:
                break
            new_remaining_states = []
            for state_dict in remaining_states:
                parent = None
                parent_key = state_dict.get('parent')
                if parent_key is not None:
                    parent = self.get(key=parent_key)
                    if parent is None:
                        new_remaining_states.append(state_dict)
                        continue

                state_dict['parent'] = parent
                self.add(**state_dict)
            remaining_states = new_remaining_states

        if len(remaining_states) > 0:
            logger.warning(f'{remaining_states} do not have valid parents and have not been added')

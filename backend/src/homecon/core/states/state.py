#!/usr/bin/env python3

from typing import Any, List, Optional
from dataclasses import dataclass
from uuid import uuid4

from homecon.core.event import IEventManager


class StateEventsTypes:
    STATE_VALUE_CHANGED = 'state_value_changed'
    STATE_UPDATED = 'state_updated'
    STATE_DELETED = 'state_deleted'
    STATE_ADDED = 'state_added'


@dataclass
class TimestampedValue:
    timestamp: float
    value: Any


class State:

    NO_LOGGING_KEY = ''

    # noinspection PyShadowingBuiltins
    def __init__(self, state_manager: 'IStateManager', event_manager: 'IEventManager', id_, name,
                 parent: 'State' = None,
                 type: str = None, quantity: str = None, unit: str = None, label: str = None, description: str = None,
                 log_key: Optional[str] = '',
                 config: dict = None, value: Any = None):
        self._state_manager = state_manager
        self._event_manager = event_manager
        self.id = id_
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
        self._event_manager.fire(StateEventsTypes.STATE_VALUE_CHANGED,
                                 data={'state': self, 'old': old_val, 'new': self._value},
                                 source=source)

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
            self._value = kwargs['value']
        self._state_manager.update(self)
        self.notify_updated()

    @property
    def children(self) -> List['State']:
        return [s for s in self._state_manager.all() if s.parent is not None and s.parent.id == self.id]

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
        return f'<State: {self.id}, name: {self.name}, value: {self.value}>'

    def serialize(self):
        return {
            'id': self.id, 'name': self.name, 'path': self.path, 'value': self.value,
            'parent': None if self.parent is None else self.parent.id,
            'type': self.type, 'quantity': self.quantity, 'unit': self.unit, 'label': self.label,
            'description': self.description, 'log_key': self.log_key,
            'config': self.config or {}
        }


class IStateManager:
    def __init__(self, event_manager: IEventManager):
        self.event_manager = event_manager

    def all(self) -> List[State]:
        raise NotImplementedError

    # noinspection PyShadowingBuiltins
    def get(self, path: str = None, id: int = None) -> Optional[State]:
        raise NotImplementedError

    def find(self, expr: str) -> List[State]:
        raise NotImplementedError

    def exists(self, name: str, parent: Optional[State] = None):
        raise NotImplementedError

    def _create_state(self, name: str, parent: Optional[State] = None,
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
            config: Optional[dict] = None, value: Optional[Any] = None):

        if parent is None:
            if parent_path is not None:
                parent = self.get(path=parent_path)

        existing_state = self.exists(name, parent=parent)
        if existing_state:
            return existing_state

        state = self._create_state(name, parent=parent, type=type, quantity=quantity, unit=unit,
                                   label=label, description=description, config=config, log_key=log_key, value=value)
        state.notify_created()
        return state

    def get_state_values_log(self, state: State, since: float, until: float) -> List[TimestampedValue]:
        raise NotImplementedError

    def export_states(self) -> List[dict]:
        states_list = []
        for state in self.all():
            dict_ = {
                'name': state.name,
                'parent_path': state.parent.path if state.parent is not None else None,
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

        for state_dict in sorted(states_list, key=lambda x: len(x.get('parent_path') or '')):
            self.add(**state_dict)

#!/usr/bin/env python3
from typing import Any, List, Optional

from homecon.core.event import IEventManager


class StateEventsTypes:
    STATE_VALUE_CHANGED = 'state_value_changed'
    STATE_UPDATED = 'state_updated'
    STATE_DELETED = 'state_deleted'
    STATE_ADDED = 'state_added'


class State:
    # noinspection PyShadowingBuiltins
    def __init__(self, state_manager: 'IStateManager', event_manager: 'IEventManager', id_, name, parent: 'State' = None,
                 type: str = None, quantity: str = None, unit: str = None, label: str = None, description: str = None,
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
        self.config = config or {}
        self._value = value

    def notify_created(self):
        self._event_manager.fire(StateEventsTypes.STATE_ADDED, data={'state': self})

    def notify_deleted(self):
        self._event_manager.fire(StateEventsTypes.STATE_DELETED, data={'state': self})

    def notify_updated(self):
        self._event_manager.fire(StateEventsTypes.STATE_UPDATED, data={'state': self})

    def notify_values_changed(self, old_val=None):
        self._event_manager.fire(StateEventsTypes.STATE_VALUE_CHANGED, data={'state': self, 'old': old_val, 'new': self._value})

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        old_val = self._value
        if self._value != val:
            self._value = val
            self._state_manager.update(self)
            self.notify_values_changed(old_val=old_val)

    def update(self, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
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
        if 'config' in kwargs:
            self.config = kwargs['config']
        self._state_manager.update(self)
        self.notify_updated()

    @property
    def children(self):
        return [s for s in self._state_manager.all() if s.parent is not None and s.parent.id == self.id]

    @property
    def path(self):
        if self.parent is None:
            return '/{}'.format(self.name)
        else:
            return '{}/{}'.format(self.parent.path, self.name)

    def __call__(self):
        return self.value

    def __repr__(self):
        return f'<State: {self.id}, name: {self.name}, value: {self.value}>'


class IStateManager:
    def __init__(self, event_manager: IEventManager):
        self.event_manager = event_manager

    def all(self) -> List[State]:
        raise NotImplementedError

    # noinspection PyShadowingBuiltins
    def get(self, id: int = None, path: str = None) -> Optional[State]:
        raise NotImplementedError

    def find(self, expr: str) -> List[State]:
        raise NotImplementedError

    def delete(self, state: State):
        state.notify_deleted()

    def add(self, *args, **kwargs):
        state = State(self, self.event_manager, *args, **kwargs)
        state.notify_created()
        return state

    def update(self, state: State):
        raise NotImplementedError

    def create_state(self, *args, **kwargs) -> State:
        return State(self, *args, **kwargs)


class MemoryStateManager(IStateManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = {}

    def all(self):
        return list(self._states.values())

    # noinspection PyShadowingBuiltins
    def get(self, id: int = None, path: str = None):
        if id is not None:
            return self._states.get(id, None)
        else:
            for state in self._states.values():
                if state.path == path:
                    return state

    def find(self, expr: str):
        return []

    def delete(self, state: State):
        del self._states[state.id]
        super().delete(state)

    def get_new_id(self):
        id_ = 0
        if len(self._states) > 0:
            id_ = max(self._states.keys()) + 1
        return id_

    def add(self, *args, **kwargs):
        id_ = kwargs.pop('id', None) or self.get_new_id()
        state = super().add(id_, *args, **kwargs)
        self._states[state.id] = state
        return state

    def update(self, state: State):
        pass

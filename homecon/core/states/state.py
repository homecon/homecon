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
    def __init__(self, state_manager: 'IStateManager', event_manager: 'IEventManager', id_, name,
                 parent: 'State' = None,
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

    def notify_values_changed(self, old_val=None, source=None):
        self._event_manager.fire(StateEventsTypes.STATE_VALUE_CHANGED, source=source,
                                 data={'state': self, 'old': old_val, 'new': self._value})

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if self._value != val:
            self.set_value(val)

    def set_value(self, val, source=None):
        old_val = self._value
        self._value = val
        self._state_manager.update(self)
        self.notify_values_changed(old_val=old_val, source=source)

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

    def serialize(self):
        return {
            'id': self.id, 'name': self.name, 'path': self.path, 'value': self.value,
            'parent': None if self.parent is None else self.parent.id,
            'type': self.type, 'quantity': self.quantity, 'unit': self.unit, 'label': self.label,
            'description': self.description,
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
                      label: Optional[str] = None, description: Optional[str] = None,
                      config: Optional[dict] = None, value: Optional[Any] = None) -> State:
        raise NotImplementedError

    def delete(self, state: State):
        state.notify_deleted()

    def update(self, state: State):
        raise NotImplementedError

    def add(self, name: str, parent: Optional[State] = None, parent_path: Optional[str] = None,
            type: Optional[str] = None, quantity: Optional[str] = None, unit: Optional[str] = None,
            label: Optional[str] = None, description: Optional[str] = None,
            config: Optional[dict] = None, value: Optional[Any] = None):

        if parent is None:
            if parent_path is not None:
                parent = self.get(path=parent_path)

        existing_state = self.exists(name, parent=parent)
        if existing_state:
            return existing_state

        state = self._create_state(name, parent=parent, type=type, quantity=quantity, unit=unit,
                                   label=label, description=description, config=config, value=value)
        state.notify_created()
        return state

    def export_states(self) -> List[dict]:
        states_list = []
        for state in self.all():
            states_list.append({
                'name': state.name,
                'parent_path': state.parent.path if state.parent is not None else None,
                'type': state.type,
                'quantity': state.quantity,
                'unit': state.unit,
                'label': state.label,
                'description': state.description,
                'config': state.config,
                'value': state.value
            })
        return sorted(states_list, key= lambda x: len(x.get('parent_path') or ''))

    def import_states(self, states_list: List[dict]):
        old_states = list(self.all())
        for state in old_states:
            self.delete(state)

        for state_dict in sorted(states_list, key= lambda x: len(x.get('parent_path') or '')):
            self.add(**state_dict)


class MemoryStateManager(IStateManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = {}

    def all(self):
        return list(self._states.values())

    # noinspection PyShadowingBuiltins
    def get(self, path: str = None, id: int = None):
        if id is not None:
            return self._states.get(id, None)
        else:
            for state in self._states.values():
                if state.path == path:
                    return state

    def exists(self, name, parent: State = None):
        temp_state = State(self, self.event_manager, 0, name, parent=parent)
        path = temp_state.path
        state = self.get(path=path)
        return state or False

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

    def update(self, state: State):
        pass

    def _create_state(self, name: str, parent: Optional[State] = None,
                      type: Optional[str] = None, quantity: Optional[str] = None, unit: Optional[str] = None,
                      label: Optional[str] = None, description: Optional[str] = None,
                      config: Optional[dict] = None, value: Optional[Any] = None) -> State:

        id_ = self.get_new_id()
        state = State(self, self.event_manager, id_, name, parent=parent, type=type,
                      quantity=quantity, unit=unit, label=label,
                      description=description, config=config,
                      value=value)
        self._states[state.id] = state
        return state


def config_state_paths_to_ids(config, state_manager: IStateManager):
    """
    Checks for state paths in a dict and converts them to the correct state id.
    """
    if config is not None:
        for key, val in config.items():
            if isinstance(val, str) and val.startswith('/'):
                try:
                    state = state_manager.get(val)
                except:
                    pass
                else:
                    if state is not None:
                        config[key] = state.id


def config_state_ids_to_paths(config, state_manager: IStateManager):
    """
    Checks for state ids in a dict and converts them to the correct state path.
    """
    if config is not None:
        for key, val in config.items():
            if 'state' in key and isinstance(val, int):
                try:
                    state = state_manager.get(id=val)
                except:
                    pass
                else:
                    if state is not None:
                        config[key] = state.path

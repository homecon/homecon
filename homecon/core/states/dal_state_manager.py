import json
import logging

from typing import Any
from pydal import DAL, Field

from homecon.core.states.state import State, MemoryStateManager


logger = logging.getLogger(__name__)


class DALStateManager(MemoryStateManager):
    def __init__(self, folder: str, uri: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._db = DAL(uri, folder=folder)
        self._table = self._db.define_table(
            'states',
            Field('name', type='string', default=''),
            Field('parent', type='integer'),
            Field('type', type='string'),
            Field('quantity', type='string'),
            Field('unit', type='string'),
            Field('label', type='string'),
            Field('description', type='string'),
            Field('config', type='string', default='{}'),
            Field('value', type='string'),
        )

        # load states into memory
        for row in self._db().select(self._db.states.ALL):
            state = self.row_to_state(row)
            self._states[state.id] = state

    def row_to_state(self, row) -> State:
        parent = self._states.get(row['parent'])  # FIXME this could cause problems related to the order of states in the db
        return State(self, self.event_manager, row['id'], row['name'], parent=parent, type=row['type'], quantity=row['quantity'],
                     unit=row['unit'], label=row['label'], description=row['description'], config=json.loads(row['config']),
                     value=json.loads(row['value']) if row['value'] is not None else row['value'])

    def delete(self, state: State):
        self._db(self._table.id == state.id).delete()
        try:
            self._db.commit()
        except Exception:
            logger.exception('could not store state')
        else:
            super().delete(state)

    def add(self, name, parent: State = None, type: str = None, quantity: str = None, unit: str = None, label: str = None, description: str = None,
            config: dict = None, value: Any = None, **kwargs):

        if isinstance(parent, int):
            parent = self.get(parent)
        elif isinstance(parent, str):
            parent = self.get(path=parent)

        existing_state = self.exists(name, parent=parent)
        if existing_state:
            return existing_state
        try:
            # noinspection PyProtectedMember
            self._db._adapter.reconnect()
            id_ = self._db.states.insert(name=name, parent=None if parent is None else parent.id, type=type, quantity=quantity, unit=unit,
                                         label=label, description=description, config=json.dumps(config), value=json.dumps(value))
            self._db.commit()
            # noinspection PyProtectedMember
            self._db._adapter.close()
        except Exception:
            logger.exception('could not store state')
        else:
            return super().add(name, parent=parent, type=type, quantity=quantity, unit=unit, label=label, description=description, config=config,
                               value=value, id=id_)

    def update(self, state: State):
        try:
            # noinspection PyProtectedMember
            self._db._adapter.reconnect()
            row = self._db(self._table.id == state.id).select().first()
            row.update_record(name=state.name, parent=None if state.parent is None else state.parent.id, type=state.type, quantity=state.quantity,
                              unit=state.unit, label=state.label, description=state.description, config=json.dumps(state.config),
                              value=json.dumps(state.value))
            self._db.commit()
            # noinspection PyProtectedMember
            self._db._adapter.close()
        except Exception:
            logger.exception('could not store state')
        else:
            super().update(state)

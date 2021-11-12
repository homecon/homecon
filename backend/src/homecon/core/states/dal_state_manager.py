import json
import logging
import time

from typing import Any, Optional, List
from pydal import DAL, Field

from homecon.core.states.state import State, TimestampedValue
from homecon.core.states.memory_state_manager import MemoryStateManager

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
            Field('log_key', type='string', default=State.NO_LOGGING_KEY),
            Field('config', type='string', default='{}'),
            Field('value', type='string'),
        )

        self._table_values_log = self._db.define_table(
            'state_values_log',
            Field('state_key', type='string'),
            Field('timestamp', type='integer'),
            Field('value', type='string'),
        )

        # load states into memory
        for row in self._db().select(self._db.states.ALL):
            state = self._row_to_state(row)
            self._states[state.id] = state

    def delete(self, state: State):
        try:
            self._db(self._table.id == state.id).delete()
            self._db.commit()
        except Exception:
            logger.exception('could not delete state')
        else:
            super().delete(state)

    def update(self, state: State):
        try:
            # noinspection PyProtectedMember
            self._db._adapter.reconnect()
            row = self._db(self._table.id == state.id).select().first()
            row.update_record(name=state.name, parent=None if state.parent is None else state.parent.id, type=state.type, quantity=state.quantity,
                              unit=state.unit, label=state.label, description=state.description, log_key=state.log_key,
                              config=json.dumps(state.config), value=json.dumps(state.value))

            if state.log_key != State.NO_LOGGING_KEY:
                self._store_state_log(state)

            self._db.commit()
            # noinspection PyProtectedMember
            self._db._adapter.close()
        except Exception:
            logger.exception('could not store state')

    def get_state_values_log(self, state: State, since: int, until: Optional[int] = None) -> List[TimestampedValue]:
        table = self._table_values_log
        if until is None:
            query = (table.state_key == state.log_key) & (table.timestamp >= since)
        else:
            query = (table.state_key == state.log_key) & (table.timestamp >= since) & (table.timestamp < until)
        rows = self._db(query).select(table.ALL)
        return [TimestampedValue(row['timestamp'], json.loads(row['value'])) for row in rows]

    def _row_to_state(self, row) -> State:
        parent = self._states.get(row['parent'])  # FIXME this could cause problems related to the order of states in the db
        return State(self, self.event_manager, row['id'], row['name'], parent=parent, type=row['type'], quantity=row['quantity'],
                     unit=row['unit'], label=row['label'], description=row['description'], log_key=row['log_key'], config=json.loads(row['config']),
                     value=json.loads(row['value']) if row['value'] is not None else row['value'])

    def _create_state(self, name: str, parent: Optional[State] = None,
                      type: Optional[str] = None, quantity: Optional[str] = None, unit: Optional[str] = None,
                      label: Optional[str] = None, description: Optional[str] = None, log_key: Optional[str] = '',
                      config: Optional[dict] = None, value: Optional[Any] = None) -> State:
        try:
            # noinspection PyProtectedMember
            self._db._adapter.reconnect()
            id_ = self._db.states.insert(name=name, parent=None if parent is None else parent.id, type=type,
                                         quantity=quantity, unit=unit, label=label, description=description, log_key=log_key,
                                         config=json.dumps(config), value=json.dumps(value))
            self._db.commit()
            # noinspection PyProtectedMember
            self._db._adapter.close()
        except Exception:
            logger.exception('could not store state')
        else:
            state = State(self, self.event_manager, id_, name, parent=parent, type=type,
                          quantity=quantity, unit=unit, label=label, description=description, log_key=log_key,
                          config=config, value=value)

            self._store_state_log(state)
            self._db.commit()

            self._states[state.id] = state
            return state

    def _store_state_log(self, state):
        self._table_values_log.insert(state_key=state.log_key, timestamp=int(time.time()), value=json.dumps(state.value))

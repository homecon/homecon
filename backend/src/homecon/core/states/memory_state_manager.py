import re
import time
from typing import Optional, List, Any

from homecon.core.states.state import IStateManager, State, TimestampedValue


class MemoryStateManager(IStateManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = {}
        self._state_timeseries = {}

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
        compiled = re.compile(expr)
        return [state for state in self._states.values() if compiled.match(state.path)]

    def delete(self, state: State):
        del self._states[state.id]
        super().delete(state)

    def get_new_id(self):
        id_ = 0
        if len(self._states) > 0:
            id_ = max(self._states.keys()) + 1
        return id_

    def update(self, state: State):
        if state.store_history:
            if state.id not in self._state_timeseries:
                self._state_timeseries[state.id] = []
            self._state_timeseries[state.id].append((int(time.time()), state.value))

    def get_state_history(self, state_id: int, since: int, until: Optional[int] = None) -> List[TimestampedValue]:
        timeseries = self._state_timeseries.get(state_id)
        return [TimestampedValue(t, v) for t, v in timeseries if since <= t and (until is None or t < until)]

    def _create_state(self, name: str, parent: Optional[State] = None,
                      type: Optional[str] = None, quantity: Optional[str] = None, unit: Optional[str] = None,
                      label: Optional[str] = None, description: Optional[str] = None, store_history: Optional[bool] = False,
                      config: Optional[dict] = None, value: Optional[Any] = None) -> State:

        id_ = self.get_new_id()
        state = State(self, self.event_manager, id_, name, parent=parent, type=type,
                      quantity=quantity, unit=unit, label=label,
                      description=description, store_history=store_history, config=config,
                      value=value)
        self._states[state.id] = state
        return state

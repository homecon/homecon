import re
import time
from typing import Optional, List, Any
from uuid import uuid4

from homecon.core.states.state import IStateManager, State, TimestampedValue


class MemoryStateManager(IStateManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = {}
        self._state_timeseries = {}

    def all(self):
        return list(self._states.values())

    # noinspection PyShadowingBuiltins
    def get(self, path: str = None, key: str = None):
        if key is not None:
            return self._states.get(key, None)
        else:
            for state in self._states.values():
                print(state)
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
        del self._states[state.key]
        super().delete(state)

    def update(self, state: State):
        if state.log_key != state.NO_LOGGING_KEY:
            if state.log_key not in self._state_timeseries:
                self._state_timeseries[state.log_key] = []
            self._state_timeseries[state.log_key].append(TimestampedValue(time.time(), state.value))

    def get_state_values_log(self, state: State, since: float, until: Optional[float] = None) -> List[TimestampedValue]:
        full_timeseries = self._state_timeseries.get(state.log_key, [])

        timeseries = [v for v in full_timeseries if since <= v.timestamp and (until is None or v.timestamp < until)]
        if len(timeseries) > 0 and timeseries[0].timestamp > since:
            initial_values = [v for v in full_timeseries if v.timestamp < timeseries[0].timestamp]
            if len(initial_values) > 0:
                timeseries = [initial_values[-1]] + timeseries
        return timeseries

    def _create_state(self, key: str, name: str, parent: Optional[State] = None,
                      type: Optional[str] = None, quantity: Optional[str] = None, unit: Optional[str] = None,
                      label: Optional[str] = None, description: Optional[str] = None, log_key: Optional[str] = '',
                      config: Optional[dict] = None, value: Optional[Any] = None) -> State:

        state = State(self, self.event_manager, key, name, parent=parent, type=type,
                      quantity=quantity, unit=unit, label=label,
                      description=description, log_key=log_key, config=config,
                      value=value)
        self._states[state.key] = state
        return state

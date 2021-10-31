import logging

from typing import Any, List

from homecon.core.event import Event
from homecon.core.states.state import IStateManager
from homecon.core.plugins.plugin import BasePlugin

import numpy as np


logger = logging.getLogger(__name__)


class EvaluationError(Exception):
    pass


class ValueComputer:
    def __init__(self, state_manger: IStateManager):
        self._state_manger = state_manger
        self._locals = {
            'Value': self.state_value,
            'Values': self.state_values,
            'sin': np.sin,
            'cos': np.cos,
            'exp': np.exp,
            'log': np.log,
        }

    def state_value(self, path: str) -> Any:
        return self._state_manger.get(path).value

    def state_values(self, expr: str) -> List[Any]:
        return [state.value for state in self._state_manger.find(expr)]

    def compute_value(self, expr: str) -> Any:
        try:
            value = eval(expr, self._locals, {})
        except Exception as e:
            raise EvaluationError from e

        return value


class Computed(BasePlugin):
    COMPUTED = 'computed'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value_computer = ValueComputer(self._state_manager)
        self._computed_mapping = {}

    def start(self):
        # build the _computed_mapping
        for state in self._state_manager.all():
            expr = state.config.get(self.COMPUTED)
            if expr is not None:
                self._computed_mapping[state.id] = expr
        logger.debug('Computed plugin initialized')

    def listen_state_added(self, event: Event):
        state = event.data['state']
        if self.COMPUTED in state.config:
            self._computed_mapping[state.id] = state.config[self.COMPUTED]

    def listen_state_updated(self, event: Event):
        state = event.data['state']
        if self.COMPUTED in state.config:
            self._computed_mapping[state.id] = state.config[self.COMPUTED]
            logger.debug(f'added state {state.id} to the computed mapping with expr {state.config[self.COMPUTED]}')
        elif state.id in self._computed_mapping:
            del self._computed_mapping[state.id]
            logger.debug(f'removed state {state.id} from the computed mapping')

    def listen_state_deleted(self, event: Event):
        state = event.data['state']
        if state.id in self._computed_mapping:
            del self._computed_mapping[state.id]

    def listen_state_value_changed(self, event: Event):
        for state_id, expr in self._computed_mapping.items():
            state = self._state_manager.get(id=state_id)
            try:
                value = self._value_computer.compute_value(expr)
            except EvaluationError:
                logger.exception(f'could not compute value for {state} from {expr}')
            else:
                if state.value != value:
                    logger.info(f'computed new value {value} for {state} from {expr}')
                    state.set_value(value, source=self.name)
                else:
                    logger.debug(f'computed equal value {value} for {state} from {expr}')
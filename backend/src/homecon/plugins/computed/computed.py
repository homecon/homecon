import logging

from typing import Any, List
from dataclasses import dataclass

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


@dataclass
class ComputedConfig:
    value: str
    trigger: str

    @staticmethod
    def from_dict(dict_):
        return ComputedConfig(dict_['value'], dict_['trigger'])


class Computed(BasePlugin):
    COMPUTED = 'computed'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value_computer = ValueComputer(self._state_manager)
        self._computed_mapping = {}

    def start(self):
        # build the _computed_mapping
        for state in self._state_manager.all():
            computed_config = state.config.get(self.COMPUTED)
            if computed_config is not None:
                self._computed_mapping[state.id] = ComputedConfig.from_dict(computed_config)
        logger.debug('Computed plugin initialized')

    def listen_state_added(self, event: Event):
        state = event.data['state']
        computed_config = state.config.get(self.COMPUTED)
        if computed_config is not None:
            self._computed_mapping[state.id] = ComputedConfig.from_dict(computed_config)

    def listen_state_updated(self, event: Event):
        state = event.data['state']
        computed_config = state.config.get(self.COMPUTED)
        if computed_config is not None:
            self._computed_mapping[state.id] = ComputedConfig.from_dict(computed_config)
            logger.debug(f'added state {state.id} to the computed mapping with config {ComputedConfig}')
        elif state.id in self._computed_mapping:
            del self._computed_mapping[state.id]
            logger.debug(f'removed state {state.id} from the computed mapping')

    def listen_state_deleted(self, event: Event):
        state = event.data['state']
        if state.id in self._computed_mapping:
            del self._computed_mapping[state.id]

    def listen_state_value_changed(self, event: Event):
        for state_id, computed_config in self._computed_mapping.items():
            trigger_state_ids = [state.id for state in self._state_manager.find(computed_config.trigger)]
            if event.data['state'].id in trigger_state_ids:
                state = self._state_manager.get(id=state_id)
                try:
                    value = self._value_computer.compute_value(computed_config.value)
                except EvaluationError:
                    logger.exception(f'could not compute value for {state} from {computed_config}')
                else:
                    if state.value != value:
                        logger.info(f'computed new value {value} for {state} from {computed_config}')
                        state.set_value(value, source=self.name)
                    else:
                        logger.debug(f'computed equal value {value} for {state} from {computed_config}')
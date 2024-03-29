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


class StateNotFoundError(EvaluationError):
    pass


class ValueComputer:
    def __init__(self, state_manger: IStateManager):
        self._state_manger = state_manger
        self._locals = {
            'Value': self._state_value,
            'Values': self._state_values,
            'sin': np.sin,
            'cos': np.cos,
            'exp': np.exp,
            'log': np.log,
            'abs': np.abs,
            'min': min,
            'max': max,
            'mean': np.nanmean,
        }

    def _state_value(self, path: str) -> Any:
        try:
            return self._state_manger.get(path).value
        except:
            raise StateNotFoundError
    def _state_values(self, expr: str) -> List[Any]:
        values = {state.key: state.value for state in self._state_manger.find(expr)}
        return list(values.values())

    def compute_value(self, expr: str) -> Any:
        try:
            value = eval(expr, self._locals, {})
        except StateNotFoundError as e:
            raise e
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
                try:
                    self._computed_mapping[state.key] = ComputedConfig.from_dict(computed_config)
                except TypeError:
                    logger.exception('could not add state to computed_mapping')

        for state_key, computed_config in self._computed_mapping.items():
            self._compute_and_set_value(state_key, computed_config)

        logger.debug('Computed plugin initialized')

    def _try_to_add_state_to_mapping(self, state):
        computed_config_dict = state.config.get(self.COMPUTED)
        if computed_config_dict is not None:
            try:
                computed_config = ComputedConfig.from_dict(computed_config_dict)
                self._computed_mapping[state.key] = computed_config
                logger.debug(f'added state {state.key} to the computed mapping with config {computed_config}')
            except TypeError:
                logger.exception('could not add state to computed_mapping')
            else:
                self._compute_and_set_value(state.key, computed_config)
        elif state.key in self._computed_mapping:
            del self._computed_mapping[state.key]
            logger.debug(f'removed state {state.key} from the computed mapping')

    def _compute_and_set_value(self, state_key: str, computed_config: ComputedConfig):
        state = self._state_manager.get(key=state_key)
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

    def listen_state_added(self, event: Event):
        state = event.data['state']
        self._try_to_add_state_to_mapping(state)

    def listen_state_updated(self, event: Event):
        state = event.data['state']
        self._try_to_add_state_to_mapping(state)

    def listen_state_deleted(self, event: Event):
        state = event.data['state']
        if state.key in self._computed_mapping:
            del self._computed_mapping[state.key]
            logger.debug(f'removed state {state.key} from the computed mapping')

    def listen_state_value_changed(self, event: Event):
        for state_key, computed_config in self._computed_mapping.items():
            trigger_state_ids = [state.key for state in self._state_manager.find(computed_config.trigger)]
            if event.data['state'].key in trigger_state_ids:
                self._compute_and_set_value(state_key, computed_config)

#!/usr/bin/env python3
import logging
from homecon.core.event import Event
from homecon.core.plugins.plugin import BasePlugin
from homecon.plugins.heat_demand.calculator import HeatingCurveHeatDemandCalculator

logger = logging.getLogger(__name__)


class HeatDemand(BasePlugin):
    """
    Class to control the HomeCon scheduler

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialize()

    def _initialize(self):
        self._state_manager.add('settings', type=None)
        self._state_manager.add('heat_demand', type=None, parent_path='/settings')

        self._ambient_temperature_state = self._state_manager.add(
            'ambient_temperature', parent_path='/settings/heat_demand',
            type='float', quantity='Temperature', unit='degC',
            label='', description='Ambient temperature', value=15)
        self._indoor_temperature_state = self._state_manager.add(
            'indoor_temperature', parent_path='/settings/heat_demand',
            type='float', quantity='Temperature', unit='degC',
            label='', description='Indoor temperature', value=20)
        self._setpoint_temperature_state = self._state_manager.add(
            'setpoint_temperature', parent_path='/settings/heat_demand',
            type='float', quantity='Temperature', unit='degC',
            label='', description='Setpoint temperature', value=20)
        self._heat_demand_state = self._state_manager.add(
            'heat_demand', parent_path='/settings/heat_demand',
            type='float', quantity='Power', unit='W',
            label='', description='Wanted heat gain', value=0)

        self._state_keys = [
            self._ambient_temperature_state.key,
            self._indoor_temperature_state,
            self._setpoint_temperature_state,
        ]

    def start(self):
        logger.debug('Heat Demand plugin Initialized')
        self._calculate_heat_demand()

    def _calculate_heat_demand(self):
        ambient_temperature = self._ambient_temperature_state.value
        if ambient_temperature is None:
            ambient_temperature = 10.

        indoor_temperature = self._indoor_temperature_state.value
        if indoor_temperature is None:
            indoor_temperature = 20.

        setpoint_temperature = self._setpoint_temperature_state.value
        if setpoint_temperature is None:
            setpoint_temperature = 20.

        ambient_temperature_min = self._heat_demand_state.config.get('ambient_temperature_min')
        if ambient_temperature_min is None:
            ambient_temperature_min = -10.

        ambient_temperature_max = self._heat_demand_state.config.get('ambient_temperature_max')
        if ambient_temperature_max is None:
            ambient_temperature_max = 18.

        heat_demand_max = self._heat_demand_state.config.get('heat_demand_max')
        if heat_demand_max is None:
            heat_demand_max = 8000.

        indoor_temperature_correction_factor = self._heat_demand_state.config.get('indoor_temperature_correction_factor')
        if indoor_temperature_correction_factor is None:
            indoor_temperature_correction_factor = 0.2

        heat_demand = HeatingCurveHeatDemandCalculator(
            ambient_temperature, indoor_temperature, setpoint_temperature,
            ambient_temperature_min, ambient_temperature_max, heat_demand_max,
            indoor_temperature_correction_factor).calculate_wanted_heat_gain()

        self._heat_demand_state.set_value(heat_demand, source=self.name)

    def listen_state_value_changed(self, event: Event):
        if event.data['state'].key in self._state_keys:
            self._calculate_heat_demand()

    def listen_state_updated(self, event: Event):
        if event.data['state'].key == self._heat_demand_state.key and event.source != self.name:
            self._calculate_heat_demand()

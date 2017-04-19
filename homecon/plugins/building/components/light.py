#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pyomo.environ as pyomo

from .... import core


class Light(core.component.Component):
    """
    a class implementing an on/off light
    
    """
    default_config = {
        'type': '',
        'power': '',
        'zone': '',
    }
    linked_states = {
        'value': {
            'default_config': {},
            'fixed_config': {},
        },
    }


core.components.register(Light)


class Dimminglight(Light):
    """
    a class implementing an dimmable light
    
    """
    pass

core.components.register(Dimminglight)

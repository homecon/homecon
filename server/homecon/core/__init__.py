#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import importlib


db = None
measurements_db = None

event = None
states = None
components = None
plugins = None
websocket = None



def initialize(dbname='homecon'):
    global db, measurements_db, event, states, components, plugins, websocket
    
    corepackage = 'homecon.core'

    ############################################################################
    # database
    ############################################################################
    if 'homecon.core.database' in sys.modules:
        importlib.reload(database)
    else:
        importlib.import_module('.database',package=corepackage)
    
    db = database.Database(database='{}.db'.format(dbname))
    measurements_db = database.Database(database='{}_measurements.db'.format(dbname))
    database.db = db
    database.measurements_db = measurements_db


    ############################################################################
    # event
    ############################################################################
    if 'homecon.core.event' in sys.modules:
        importlib.reload(event)
    else:
        importlib.import_module('.event',package=corepackage)


    ############################################################################
    # states
    ############################################################################
    if 'homecon.core.state' in sys.modules:
        importlib.reload(state)
    else:
        importlib.import_module('.state',package=corepackage)
    
    states = state.States()
    state.states = states


    ############################################################################
    # components
    ############################################################################
    if 'homecon.core.component' in sys.modules:
        importlib.reload(component)
    else:
        importlib.import_module('.component',package=corepackage)
    
    components = component.Components()
    component.components = components


    ############################################################################
    # plugins
    ############################################################################
    if 'homecon.core.plugin' in sys.modules:
        importlib.reload(plugin)
    else:
        importlib.import_module('.plugin',package=corepackage)
    
    plugins = plugin.Plugins()
    plugin.plugins = plugins


    ############################################################################
    # websocket
    ############################################################################
    if 'homecon.core.ws' in sys.modules:
        importlib.reload(ws)
    else:
        importlib.import_module('.ws',package=corepackage)
    
    websocket = ws.Websocket()
    ws.websocket = websocket


"""
from . import database
from . import event
from . import state
from . import component
from . import plugin
from . import websocket


# create a database
db = database.db
measurements_db = database.measurements_db

# create container objects
states = state.states
components = component.components
plugins = plugin.plugins
websocket = websocket.websocket
"""

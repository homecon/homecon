#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import importlib


db = None
measurements_db = None

event = None
states = None
components = None
plugins = None
websocket = None



def initialize(dbpath='{}/lib/homecon/'.format(sys.prefix),dbname='homecon'):
    global db, measurements_db, event, states, components, plugins, websocket
    
    corepackage = 'homecon.core'

    ############################################################################
    # database
    ############################################################################
    if '{}.database'.format(corepackage) in sys.modules:
        importlib.reload(database)
    else:
        importlib.import_module('.database',package=corepackage)

    db = database.Database(database=os.path.join(dbpath,'{}.db'.format(dbname)))
    measurements_db = database.Database(database=os.path.join(dbpath,'{}_measurements.db'.format(dbname)))
    database.db = db
    database.measurements_db = measurements_db


    ############################################################################
    # event
    ############################################################################
    if '{}.event'.format(corepackage) in sys.modules:
        importlib.reload(event)
    else:
        importlib.import_module('.event',package=corepackage)


    ############################################################################
    # states
    ############################################################################
    if '{}.state'.format(corepackage) in sys.modules:
        importlib.reload(state)
    else:
        importlib.import_module('.state',package=corepackage)
    
    states = state.States()
    state.states = states


    ############################################################################
    # components
    ############################################################################
    if '{}.component'.format(corepackage) in sys.modules:
        importlib.reload(component)
    else:
        importlib.import_module('.component',package=corepackage)
    
    components = component.Components()
    component.components = components


    ############################################################################
    # plugins
    ############################################################################
    if '{}.plugin'.format(corepackage) in sys.modules:
        importlib.reload(plugin)
    else:
        importlib.import_module('.plugin',package=corepackage)
    
    plugins = plugin.Plugins()
    plugin.plugins = plugins


    ############################################################################
    # websocket
    ############################################################################
    if '{}.ws'.format(corepackage) in sys.modules:
        importlib.reload(ws)
    else:
        importlib.import_module('.ws',package=corepackage)
    
    websocket = ws.Websocket()
    ws.websocket = websocket


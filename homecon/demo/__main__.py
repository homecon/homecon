#!/usr/bin/env python3
import json
import os
import logging

from homecon.core.states.state import IStateManager
from homecon.core.states.dal_state_manager import DALStateManager
from homecon.core.event import EventManager
from homecon.core.plugins.plugin import MemoryPluginManager
from homecon.homecon import HomeCon
from concurrent.futures import ThreadPoolExecutor

from homecon.plugins.websocket import Websocket
from homecon.plugins.states import States
# from homecon.plugins.pages import deserialize


# the current file directory
base_path = os.path.dirname(os.path.abspath(__file__))


logger = logging.getLogger(__name__)


def create_states(state_manager: IStateManager):
    logger.info('creating demo states')
    state_manager.add('ground_floor')
    state_manager.add('kitchen', parent='/ground_floor')
    state_manager.add('some_value', parent='/ground_floor/kitchen', type='int', value=20)
    state_manager.add('lights', parent='/ground_floor/kitchen')
    state_manager.add('light', parent='/ground_floor/kitchen/lights',
                      type='boolean', quantity='', unit='',
                      label='Kitchen light', description='',
                      config={'knx_ga_read': '1/1/31', 'knx_ga_write': '1/1/31', 'knx_dpt': '1'})
    state_manager.add('spotlight', parent='/ground_floor/kitchen/lights',
                      type='boolean', quantity='', unit='',
                      label='Kitchen spotlights', description='',
                      config={'knx_ga_read': '1/1/62', 'knx_ga_write': '1/1/62', 'knx_dpt': '1'})
    state_manager.add('dimmer', parent='/ground_floor/kitchen/lights',
                      type='float', quantity='', unit='',
                      label='Kitchen dimmer', description='')

    state_manager.add('living', parent='/ground_floor')
    state_manager.add('lights', parent='/ground_floor/living')
    state_manager.add('light', parent='/ground_floor/living/lights',
                      type='boolean', quantity='', unit='',
                      label='Living room light', description='',
                      config={'knx_ga_read': '1/1/41', 'knx_ga_write': '1/1/41', 'knx_dpt': '1'})

    state_manager.add('windows', parent='/ground_floor/kitchen')
    state_manager.add('south', parent='/ground_floor/kitchen/windows')
    state_manager.add('shading', parent='/ground_floor/kitchen/windows/south')
    state_manager.add('position', parent='/ground_floor/kitchen/windows/south/shading',
                      type='float', quantity='', unit='',
                      label='Position', description='',
                      config={'knx_ga_read': '2/4/61', 'knx_ga_write': '2/3/61', 'knx_dpt': '5'})
    state_manager.add('west', parent='/ground_floor/kitchen/windows')
    state_manager.add('shading', parent='/ground_floor/kitchen/windows/west')
    state_manager.add('position', parent='/ground_floor/kitchen/windows/west/shading',
                      type='float', quantity='', unit='',
                      label='Position', description='',
                      config={'knx_ga_read': '2/4/62', 'knx_ga_write': '2/3/62', 'knx_dpt': '5'})

    state_manager.add('myalarms')
    state_manager.add('dummy', parent='/myalarms', type='action', value=[
        {'state': state_manager.get('/ground_floor/kitchen/some_value').id, 'value': 10},
        {'state': state_manager.get('/ground_floor/kitchen/some_value').id, 'value': 0, 'delay': 5}
    ], label='Dummy')
    state_manager.add('1', parent='/myalarms', type='schedule',
                      value={'trigger': {'day_of_week': '0,1,2,3,6', 'hour': '20', 'minute': '0'},
                             'action': state_manager.get('/myalarms/dummy').id})
    state_manager.add('central')
    state_manager.add('ventilation', parent='/central')
    state_manager.add('speed', parent='/central/ventilation',
                      type='int', quantity='', unit='',
                      label='Ventilation speed', description='',
                      config={'knx_ga_read': None, 'knx_ga_write': '4/0/4', 'knx_dpt': '6'})


def create_pages():
    logger.info('creating demo pages')
    base_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_path, 'pages.json'), 'r') as f:
        pages = json.load(f)
    deserialize(pages)


def get_homecon():
    """
    create the HomeCon object
    """
    db_dir = os.path.abspath(os.path.join(base_path, 'db'))
    try:
        os.mkdir(db_dir)
    except FileExistsError:
        pass

    event_manager = EventManager()
    state_manager = DALStateManager(folder=db_dir, uri='sqlite://homecon_demo.db',
                                    event_manager=event_manager)
    create_states(state_manager)
    # state_manager = MemoryStateManager(event_manager=event_manager)
    plugin_manager = MemoryPluginManager({
        'websocket': Websocket('websocket', event_manager, state_manager),
        'states': States('states', event_manager, state_manager)
    })
    executor = ThreadPoolExecutor(max_workers=10)

    homecon = HomeCon(event_manager, plugin_manager, executor)
    return homecon

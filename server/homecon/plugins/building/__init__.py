#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import datetime
import numpy as np

from ... import core
from ... import util
from . import components
from . import models


class Building(core.plugin.Plugin):
    """
    Class to define the HomeCon building
    
    """

    def initialize(self):
        """
        Initialize

        """

        # add a state for the model
        core.states.add('building/model',value='singlezone_1', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})
        core.states.add('building/identification/result', config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})
        core.states.add('building/validation/result', config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})

        # set the model
        self._set_model(core.states['building/model'].value)

        # schedule cross validation
        #self._loop.create_task(self.schedule_cross_validation())
        self.cross_validation_task = asyncio.ensure_future(self.schedule_cross_validation())


        logging.debug('Building plugin initialized')

    def _set_model(self,key):
        if key in models.models:
            self.model = models.models[key]()


    def identify(self):
        logging.debug('Starting the building system identification')

        result = self.model.identify(verbose=0)
        if not result is None:
            core.states['building/identification/result'].value = result
        else:
            logging.warning('Isufficient data for system identification, retaining previous parameters')

        return result


    def validate(self):
        logging.debug('Starting the building model validation')

        result = self.model.validate(verbose=0)
        if not result is None:
            core.states['building/validation/result'].value = result
        else:
            logging.warning('Isufficient data for model validation')

        return result


    async def schedule_cross_validation(self):
        """
        Schedule cross validation running once a week

        """

        while True:
            # timestamps
            dt_ref = datetime.datetime(1970, 1, 1)
            dt_now = datetime.datetime.utcnow()
            dt_when = (dt_now + datetime.timedelta(days=7)).replace(hour=3,minute=8,second=0,microsecond=0)

            timestamp_now = int( (dt_now-dt_ref).total_seconds() )
            timestamp_when = int( (dt_when-dt_ref).total_seconds() )


            # cross validate
            result = self.validate()

            if result and not result['fitquality']['success']:
                self.identify()
                self.validate()


            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)


    def create_ocp_variables(self,model):
        result = self.model.create_ocp_variables(model)


    def create_ocp_constraints(self,model):
        result = self.model.create_ocp_constraints(model)


    def postprocess_ocp(self,model):
        result = self.model.postprocess_ocp(model)



    def listen_building_list_models(self,event):
        keys = [key for key in models.models.keys()]
        keys = sorted(keys)
        core.websocket.send({'event':'building_list_models', 'path':'', 'value':keys}, clients=[event.client])


    def listen_building_identify(self,event):
        result = self.identify()
        result = self.validate()


    def listen_building_validate(self,event):
        result = self.validate()


    def listen_state_changed(self,event):


        if event.data['state'].path == 'building/model':
            self._set_model(event.data['state'].value)


        if 'component' in event.data['state'].config:
            component = core.components[event.data['state'].config['component']]

            if component.type == 'zonetemperaturesensor':
                zone = core.components[component.config['zone']]
                zone.states['temperature'].value = np.round( zone.calculate_temperature(), 2)

            elif component.type == 'shading' and event.data['state'] == component.states['position']:
                window = core.components[component.config['window']]
                window.states['solargain'].value = np.round( window.calculate_solargain(), 1)

            elif component.type == 'window' and event.data['state'] == component.states['solargain']:
                zone = core.components[component.config['zone']]
                zone.states['solargain'].value = np.round( zone.calculate_solargain(), 1)

        if event.data['state'].path == 'weather/irradiancedirect' or event.data['state'].path == 'weather/irradiancediffuse':
            for window in core.components.find(type='window'):
                window.states['solargain'].value = np.round( window.calculate_solargain(), 1)






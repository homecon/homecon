#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import json
import asyncio
import numpy as np

from .. import core
from .. import util
from ..core import models

class Systemidentification(core.plugin.Plugin):
    """
    Class to control the HomeCon system identification and model predictive control functions
    
    """

    def initialize(self):
        
        # add a state for the model
        core.states.add('systemidentification/model',value='singlezone_2', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})
        core.states.add('systemidentification/identification/result', config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})
        core.states.add('systemidentification/validation/result', config={'type': 'dict', 'quantity':'', 'unit':'','label':'', 'description':'', 'log':False})


        self.set_model()


        # schedule cross validation
        self._loop.create_task(self.schedule_cross_validation())


        # schedule control optimization
        #self._loop.create_task(self.schedule_control_optimization())


        logging.debug('Identification plugin Initialized')

    def set_model(self):

        if core.states['systemidentification/model'].value == 'singlezone_1':
            self.model = models.Singlezone_1()

        elif core.states['systemidentification/model'].value == 'singlezone_2':
            self.model = models.Singlezone_2()

        else:
            self.model = None


    def identify(self):
        if not self.model is None:
            result = self.model.identify()
            core.states['systemidentification/identification/result'].value = result
            return result

        else:
            return False

    def validate(self):
        if not self.model is None:
            result = self.model.validate()
            core.states['systemidentification/validation/result'].value = result
            return result

        else:
            return False



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


    def listen_state_changed(self,event):
        if event.data['state'].path == 'identification/model':
            core.states['systemidentification/model'].value = event.data['value']
            self.change_model()


    def listen_sytemidentification_identify(self,event):
        result = self.identify()


    def listen_sytemidentification_validate(self,event):
        result = self.validate()




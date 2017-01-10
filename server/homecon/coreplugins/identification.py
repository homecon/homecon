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

class Identification(core.plugin.Plugin):
    """
    Class to control the HomeCon system identification and model predictive control functions
    
    """

    def initialize(self):
        
        # add a state for the model
        core.states.add('identification/model',value='singlezone_1', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':''})


        if core.states['identification/model'].value == 'singlezone_1':
            self.model = models.Singlezone_1()


        # schedule cross validation
        self._loop.create_task(self.schedule_cross_validation())


        # schedule control optimization
        #self._loop.create_task(self.schedule_control_optimization())


        logging.debug('Identification plugin Initialized')


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
            result = self.model.validate()

            # save results as states
            print(result)

            if not result['fitquality']['success']:
                result = self.model.identify()

            print(result)


            # sleep until the next call
            await asyncio.sleep(timestamp_when-timestamp_now)




    def listen_state_changed(self,event):
        if event.data['state'].path == 'identification/model':
            pass




    def listen_sytem_identification(self,event):
        print('identify')


    def listen_cross_validation(self,event):
        pass


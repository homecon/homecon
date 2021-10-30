#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import asyncio
import aiohttp

import numpy as np


from ... import core
from ... import util

class Flukso(core.plugin.Plugin):
    """
    Retrieve data from a Fluksometer
    """

    def initialize(self):
        
        core.states.add('flukso/settings/ip', value='192.168.1.1', config={'type': 'string', 'quantity':'', 'unit':'','label':'', 'description':'', 'private':True})

        self._loop.create_task(self.schedule_retrieve_data())

        logging.debug('Flukso plugin Initialized')
    

    async def schedule_retrieve_data(self):
        while self.active:
            # timestamps
            dt_when = (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).replace(second=0,microsecond=0)
            ts_when = util.time.timestamp(dt_when)
            
            await self.retrieve_data()
            
            # sleep until the next call
            await asyncio.sleep(util.time.seconds_until(ts_when))
            
            
    async def retrieve_data(self):
    
        for sensor in core.components.find(type='fluksosensor'):
            try:
                url = 'http://{}:8080/sensor/{}?version=1.0&unit={}&interval=minute'.format(core.states['flukso/settings/ip'].value,sensor.config['id'],sensor.config['unit'])


                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        response = await resp.text()
                        data = eval(response.replace('"nan"','float(\'nan\')'))
                        
                        timestamp =  data[0][0]
                        value = np.round(np.nanmean( [row[1] for row in data] ),3)

                        if np.isnan(value):
                            value = 0

                        # FIXME the values are shifted by one minute or should be plotted with backward steps
                        await sensor.states['value'].set_async( value )
                        #core.event.fire('measurements_add',{'state':sensor.states['value'],'value':value,'timestamp':timestamp})
                        
                        logging.debug('Flukso sensor {} updated'.format(sensor.path))

            except Exception as e:
                logging.error('Could not load data from Flukso sensor {}: {}'.format(sensor.path,e))
                


class Fluksosensor(core.component.Component):

    default_config = {
        'id': '',
        'token': '',
        'type': '',
        'unit': 'watt',
    }
    linked_states = {
        'value': {
            'default_config': {},
            'fixed_config': {'datatype': 'number','timestampdelta':-60},
        },
    }

core.components.register(Fluksosensor)

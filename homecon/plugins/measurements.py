#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################
#    Copyright 2016 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import logging
import json
import datetime
import asyncio

from .. import core
from .. import util

class Measurements(core.plugin.Plugin):
    """
    Class to control the HomeCon measurements
    
    """

    def initialize(self):
        
        self._db_measurements = core.state.State.db_history
        self._db_weekaverage = core.database.Table(core.database.measurements_db,'weekaverage',[
            {'name':'time',   'type':'INT',   'null': '',  'default':'',  'unique':''},
            {'name':'path',   'type':'TEXT',  'null': '',  'default':'',  'unique':''},
            {'name':'value',  'type':'TEXT',  'null': '',  'default':'',  'unique':''},
        ])
        
        self.maxtimedelta = 7*24*3600
        self.measurements = {}
        
        self.weekaverage_maxtimedelta = (366+7+1)*24*3600
        self.weekaverage = {}
        self.this_weekaverage = {}

        optimization_task = asyncio.ensure_future(self.schedule_compute_weekaverage())
        logging.debug('Measurements plugin Initialized')

        
    async def schedule_compute_weekaverage(self):
        while True:
            await asyncio.sleep(8564)  # run some time later

            # timestamps
            dt_now = util.time.timestamp_to_datetime(util.time.timestamp())
            dt_when = (dt_now + datetime.timedelta(days=(dt_now.weekday()+7)%7,hours=3)).replace(hour=0,minute=0,second=0,microsecond=0)
            ts_when = util.time.timestamp(dt_when)
            
            self.compute_weekaverage()

            # sleep until the next call
            await asyncio.sleep(util.time.seconds_until(ts_when))
        
    def compute_weekaverage(self):
        dt_now = util.time.timestamp_to_datetime(util.time.timestamp())
        
        dt_end = (dt_now + datetime.timedelta(days=-dt_now.weekday())).replace(hour=0,minute=0,second=0,microsecond=0)
        dt_sta = (dt_end + datetime.timedelta(days=-6.5)).replace(hour=0,minute=0,second=0,microsecond=0)
        
        ts_sta = util.time.timestamp(dt_when)
        ts_end = util.time.timestamp(dt_end)
    
        logging.debug('Computing week averages from {} to {}'.format(ts_sta,ts_end))

        for state in core.states:
            if state.config['log']:
                try:
                    if state.path in self.this_weekaverage:
                        value = self.this_weekaverage[state.path]
                    else:
                        value = 0
                    # FIXME

                except Exception as e:
                    logging.error('Could not compute the week average for state {}:'.format(state.path,e))


        
    def add(self,state,time=None,timedelta=0,readusers=None,readgroups=None):
        """
        Parameters
        ----------
        state: state object
            The state to be logged
        """

        if time is None:
            time = util.time.timestamp()
            
        time = time+timedelta

        value = state.value
        if 'datatype' in state.config and (state.config['datatype'] == 'number' or state.config['datatype'] == 'boolean'):
            value = float(value)
        print(value)
        self._db_measurements.post(time=time, path=state.path, value=value)

        # FIXME add the value to this_weekaverage

        if state.path in self.measurements:
            self.measurements[state.path].append([time,value])
            
            # remove values older then maxtimedelta
            ind = []
            for i,data in enumerate(self.measurements[state.path]):
                if data[0] < time - self.maxtimedelta:
                    ind.append(i)
                else:
                    break

            for i in ind:
                del self.measurements[state.path][i]


            core.websocket.send({'event':'append_timeseries', 'path':state.path, 'value':[time,value]}, readusers=readusers, readgroups=readgroups)


    def get(self,path):
        """
        """

        if not path in self.measurements:
            data = self._db_measurements.get(path=path, time__ge=util.time.timestamp() - self.maxtimedelta)
            
            self.measurements[path] = []
            for d in data:
                self.measurements[path].append([d['time'],json.loads(d['value'])])

        return self.measurements[path]


    def listen_state_changed(self,event):
        if 'log' in event.data['state'].config and event.data['state'].config['log']:
            self.add(event.data['state'],timedelta=event.data['state'].config['timestampdelta'],readusers=event.data['state'].config['readusers'],readgroups=event.data['state'].config['readgroups'])



    def listen_timeseries(self,event):
        """
        retrieve a list of measurements
        """
        
        if not 'value' in event.data:
            data = self.get(event.data['path'])
            state = core.states[event.data['path']]
            core.websocket.send({'event':'timeseries', 'path':event.data['path'], 'value':data}, clients=[event.client],readusers=state.config['readusers'],readgroups=state.config['readgroups'])



        

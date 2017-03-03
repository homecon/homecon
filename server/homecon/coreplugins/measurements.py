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

from .. import core

class Measurements(core.plugin.Plugin):
    """
    Class to control the HomeCon measurements
    
    """

    def initialize(self):
        
        self._db_measurements = core.state.State.db_history

        self.maxtimedelta = 7*24*3600
        self.measurements = {}

        logging.debug('Measurements plugin Initialized')

    def time(self):
        """
        returns a UTC timestamp
        """

        return int( (datetime.datetime.utcnow()-datetime.datetime(1970,1,1)).total_seconds() )
    

    def add(self,path,value,readusers=None,readgroups=None):
        """
        Parameters
        ----------
        path : string
            the path of a state

        value : string
            the value as json

        """

        time = self.time()
        self._db_measurements.POST(time=time,path=path,value=value)

        if path in self.measurements:
            self.measurements[path].append([time,value])
            
            # remove values older then maxtimedelta
            ind = []
            for i,data in enumerate(self.measurements[path]):
                if data[0] < time - self.maxtimedelta:
                    ind.append(i)
                else:
                    break

            for i in ind:
                del self.measurements[path][i]


            core.websocket.send({'event':'append_timeseries', 'path':path, 'value':[time,value]}, readusers=readusers, readgroups=readgroups)


    def get(self,path):
        """
        """

        if not path in self.measurements:
            data = self._db_measurements.GET(path=path,time__ge=self.time()-self.maxtimedelta)
            
            self.measurements[path] = []
            for d in data:
                self.measurements[path].append([d['time'],json.loads(d['value'])])

        return self.measurements[path]


    def listen_state_changed(self,event):
        if 'log' in event.data['state'].config and event.data['state'].config['log']:
            self.add(event.data['state'].path,event.data['state'].value,readusers=event.data['state'].config['readusers'],readgroups=event.data['state'].config['readgroups'])


    def listen_timeseries(self,event):
        """
        retrieve a list of measurements
        """
        
        if not 'value' in event.data:
            data = self.get(event.data['path'])
            state = core.states[event.data['path']]
            core.websocket.send({'event':'timeseries', 'path':event.data['path'], 'value':data}, clients=[event.client],readusers=state.config['readusers'],readgroups=state.config['readgroups'])



        

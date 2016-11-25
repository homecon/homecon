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

from .. import database
from .. import plugin

class Measurements(plugin.Plugin):
    """
    Class to control the HomeCon measurements
    
    """

    def initialize(self):
        

        self._db = database.Database(database='homecon_measurements.db')
        self._db_measurements = database.Table(self._db,'measurements',[
            {'name':'time',   'type':'INT',   'null': '',  'default':'',  'unique':''},
            {'name':'path',   'type':'TEXT',  'null': '',  'default':'',  'unique':''},
            {'name':'value',  'type':'TEXT',  'null': '',  'default':'',  'unique':''},
        ])

        self.maxtimedelta = 7*24*3600
        self.measurements = {}


    def time(self):
        """
        returns a UTC timestamp
        """

        return int( datetime.datetime.now().timestamp() )
    

    def add(self,path,value):
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
            self.measurements[path].append({'time':time,'value':value})
            
            # remove values older then maxtimedelta
            ind = []
            for i,data in enumerate(self.measurements[path]):
                if data['time'] < time - self.maxtimedelta:
                    ind.append(i)
                else:
                    break

            for i in ind:
                del self.measurements[path][i]

            self.fire('send',{'event':'append_measurement', 'path':event.data['path'], 'value':{'time':time,'value':value}})


    def get(self,path):
        """
        """

        if not path in self.measurements:
            data = self._db_measurements.GET(path=path,time__ge=self.time()-self.maxtimedelta)
            
            self.measurements[path] = []
            for d in data:
                self.measurements[path].append({'time':d['time'],'value':json.loads(d['value'])})

        return self.measurements[path]


    def listen_state_changed(self,event):
 
        self.add(event.data['path'],event.data['value'])


    def listen_measurement(self,event):
        """
        retrieve a list of measurements
        """

        data = self.get(event.data['path'])
        self.fire('send_to',{'event':'measurement', 'path':event.data['path'], 'value':data, 'clients':[event.client]})
        


        

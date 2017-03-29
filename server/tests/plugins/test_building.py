#!/usr/bin/env python3
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


import asyncio
import numpy as np
import datetime

from .. import common

import homecon.core
import homecon.coreplugins.building

class BuildingTests(common.TestCase):

    def test_initialize(self):
        building = homecon.coreplugins.building.Building()


class Singlezone_1Tests(common.TestCase):

    def test_identify(self):

        class Singlezone_1_patch(homecon.coreplugins.building.models.singlezone_1.Singlezone_1):
            def get_identification_data(self):
                timestep = 15*60

                dt_ref = datetime.datetime(1970, 1, 1)
                dt_end = datetime.datetime.utcnow()
                dt_ini = dt_end - datetime.timedelta(days=7)

                timestamp_end = int( (dt_end-dt_ref).total_seconds() )
                timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

                timestamps = np.arange(timestamp_ini,timestamp_end,timestep)

                data = {'timestamp':timestamps}

                data['T_amb'] = 5+5*np.sin(2*np.pi*data['timestamp']/3600/24)
                data['T_liv'] = 20+1*np.sin(2*np.pi*data['timestamp']/3600/24)
                data['Q_sol'] = 0*np.ones(len(data['timestamp']))
                data['Q_int'] = 0*np.ones(len(data['timestamp']))
                data['Q_hea'] = 1000*np.ones(len(data['timestamp']))

                return data

        buildingmodel = Singlezone_1_patch()

        result = buildingmodel.identify()

        self.assertNotEqual(result,None)

    def test_identify_validate(self):

        class Singlezone_1_patch(homecon.coreplugins.building.models.singlezone_1.Singlezone_1):
            def get_identification_data(self):
                timestep = 15*60

                dt_ref = datetime.datetime(1970, 1, 1)
                dt_end = datetime.datetime.utcnow()
                dt_ini = dt_end - datetime.timedelta(days=7)

                timestamp_end = int( (dt_end-dt_ref).total_seconds() )
                timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

                timestamps = np.arange(timestamp_ini,timestamp_end,timestep)

                data = {'timestamp':timestamps}

                data['T_amb'] = 5+5*np.sin(2*np.pi*data['timestamp']/3600/24)
                data['T_liv'] = 20+1*np.sin(2*np.pi*data['timestamp']/3600/24)
                data['Q_sol'] = 0*np.ones(len(data['timestamp']))
                data['Q_int'] = 0*np.ones(len(data['timestamp']))
                data['Q_hea'] = 1000*np.ones(len(data['timestamp']))
                return data

        buildingmodel = Singlezone_1_patch()

        result = buildingmodel.identify()

        result = buildingmodel.validate()
        self.assertNotEqual(result,None)


    def test_identify_missing_data(self):

        class Singlezone_1_patch(homecon.coreplugins.building.models.singlezone_1.Singlezone_1):
            def get_identification_data(self):
                timestep = 15*60

                dt_ref = datetime.datetime(1970, 1, 1)
                dt_end = datetime.datetime.utcnow()
                dt_ini = dt_end - datetime.timedelta(days=7)

                timestamp_end = int( (dt_end-dt_ref).total_seconds() )
                timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

                timestamps = np.arange(timestamp_ini,timestamp_end,timestep)

                data = {'timestamp':timestamps}

                data['T_amb'] = 5+5*np.sin(2*np.pi*data['timestamp']/3600/24)
                data['T_liv'] = 20+1*np.sin(2*np.pi*data['timestamp']/3600/24)
                data['Q_sol'] = 0*np.ones(len(data['timestamp']))
                data['Q_int'] = 0*np.ones(len(data['timestamp']))
                data['Q_hea'] = 1000*np.ones(len(data['timestamp']))

                data['T_liv'][round(0.1*len(data['timestamp'])):round(0.3*len(data['timestamp']))] = np.nan
                data['Q_hea'][round(0.1*len(data['timestamp'])):round(0.3*len(data['timestamp']))] = np.nan

                return data

        buildingmodel = Singlezone_1_patch()

        result = buildingmodel.identify()

        self.assertNotEqual(result,None)


    def test_identify_insufficient_data(self):

        class Singlezone_1_patch(homecon.coreplugins.building.models.singlezone_1.Singlezone_1):
            def get_identification_data(self):
                timestep = 15*60

                dt_ref = datetime.datetime(1970, 1, 1)
                dt_end = datetime.datetime.utcnow()
                dt_ini = dt_end - datetime.timedelta(days=7)

                timestamp_end = int( (dt_end-dt_ref).total_seconds() )
                timestamp_ini = int( (dt_ini-dt_ref).total_seconds() )

                timestamps = np.arange(timestamp_ini,timestamp_end,timestep)

                data = {'timestamp':timestamps}

                data['T_amb'] = 5+5*np.sin(2*np.pi*data['timestamp']/3600/24)
                data['T_liv'] = 20+1*np.sin(2*np.pi*data['timestamp']/3600/24)
                data['Q_sol'] = 0*np.ones(len(data['timestamp']))
                data['Q_int'] = 0*np.ones(len(data['timestamp']))
                data['Q_hea'] = 1000*np.ones(len(data['timestamp']))

                data['T_liv'][round(0.1*len(data['timestamp'])):round(0.7*len(data['timestamp']))] = np.nan
                
                return data

        buildingmodel = Singlezone_1_patch()

        result = buildingmodel.identify()

        self.assertEqual(result,None)









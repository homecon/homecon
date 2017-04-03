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


import unittest
import pytz
import datetime
import numpy as np

import homecon.util as util

class TimeTests(unittest.TestCase):

    def test_timestamp_of_the_week(self):
        util.time.set_timezone('Europe/Brussels')
        dt = datetime.datetime(2017,4,3)

        dt_utc = dt - (datetime.datetime.now() - datetime.datetime.utcnow())

        ts_ini = util.time.timestamp(dt_utc)
        timestamps = [ts for ts in np.arange(ts_ini,ts_ini+7*24*3600,24*3600)]
        timestamps_of_the_week = [util.time.timestamp_of_the_week(ts) for ts in timestamps]

        self.assertEqual(timestamps_of_the_week,[0, 86400, 172800, 259200, 345600, 432000, 518400])


    def test_seconds_until(self):
        ts = util.time.timestamp()
        delta = util.time.seconds_until(ts+100)

        self.assertEqual(delta,100)

    def test_all(self):
        util.time.set_timezone('Europe/Brussels')

        # common data gathering
        dt_ini = datetime.datetime.utcnow()

        # make the optimization timesteps coincide with 0min, 15min, 30min, 45min
        nsecs = dt_ini.minute*60 + dt_ini.second + dt_ini.microsecond*1e-6
        delta = int( np.round( nsecs/900 ) * 900 - nsecs )
        timestamp_ini = util.time.timestamp(dt_ini)+delta

        timestamps = [ts for ts in range(timestamp_ini,timestamp_ini+7*24*3600,900)]
        timestamps_of_the_week = [util.time.timestamp_of_the_week(ts) for ts in timestamps]

        print(timestamps[0])
        print(timestamps_of_the_week[0]/3600)




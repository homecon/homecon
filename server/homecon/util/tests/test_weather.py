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
import sys
import os
import datetime

sys.path.append(os.path.abspath('..'))
import weather

class WeatherTests(unittest.TestCase):
    
    def test_sunposition(self):

        latitude = 51.053715
        longitude = 5.6127946
        elevation = 73


        dt_now = datetime.datetime.utcnow()
        utcdatetimes = [dt_now + datetime.timedelta(minutes=i) for i in range(60*24)]

        for utcdatetime in utcdatetimes:
            solar_azimuth,solar_altitude = weather.sunposition(latitude,longitude,elevation,utcdatetime=utcdatetime)
            
            self.assertIsNotNaN(solar_azimuth)
            self.assertIsNotNaN(solar_altitude)
            self.assertNotEqual(solar_azimuth,None)
            self.assertNotEqual(solar_altitude,None)


    def test_clearskyirrradiance(self):

        latitude = 51.053715
        longitude = 5.6127946
        elevation = 73

        dt_now = datetime.datetime.utcnow()
        utcdatetimes = [dt_now + datetime.timedelta(minutes=i) for i in range(60*24)]

        for utcdatetime in utcdatetimes:
            solar_azimuth,solar_altitude = weather.sunposition(latitude,longitude,elevation,utcdatetime=utcdatetime)
            I_direct_clearsky,I_diffuse_clearsky = weather.clearskyirrradiance(solar_azimuth,solar_altitude,utcdatetime=utcdatetime)
            
            self.assertIsNotNaN(I_direct_clearsky)
            self.assertIsNotNaN(I_diffuse_clearsky)


    def test_incidentirradiance(self):

        latitude = 51.053715
        longitude = 5.6127946
        elevation = 73

        surface_azimuth = 180
        surface_tilt = 10

        dt_now = datetime.datetime.utcnow()
        utcdatetimes = [dt_now + datetime.timedelta(minutes=i) for i in range(60*24)]

        for utcdatetime in utcdatetimes:
            solar_azimuth,solar_altitude = weather.sunposition(latitude,longitude,elevation,utcdatetime=utcdatetime)
            I_direct_clearsky,I_diffuse_clearsky = weather.clearskyirrradiance(solar_azimuth,solar_altitude,utcdatetime=utcdatetime)
            I_total_surface, I_direct_surface, I_diffuse_surface, I_ground_surface = weather.incidentirradiance(I_direct_clearsky,I_diffuse_clearsky,solar_azimuth,solar_altitude,surface_azimuth,surface_tilt)
            
            self.assertIsNotNaN(I_total_surface)
            self.assertIsNotNaN(I_direct_surface)
            self.assertIsNotNaN(I_diffuse_surface)
            self.assertIsNotNaN(I_ground_surface)


    def test_cloudyskyirrradiance(self):

        latitude = 51.053715
        longitude = 5.6127946
        elevation = 73

        dt_now = datetime.datetime.utcnow()
        utcdatetimes = [dt_now + datetime.timedelta(minutes=i) for i in range(60*24)]
        cloudcover = 0.5

        for utcdatetime in utcdatetimes:
            solar_azimuth,solar_altitude = weather.sunposition(latitude,longitude,elevation,utcdatetime=utcdatetime)
            I_direct_clearsky,I_diffuse_clearsky = weather.clearskyirrradiance(solar_azimuth,solar_altitude,utcdatetime=utcdatetime)
            I_direct_cloudy,I_diffuse_cloudy = weather.cloudyskyirrradiance(I_direct_clearsky,I_diffuse_clearsky,cloudcover,solar_azimuth,solar_altitude,utcdatetime=utcdatetime)

            self.assertIsNotNaN(I_direct_cloudy)
            self.assertIsNotNaN(I_diffuse_cloudy)





    def assertIsNotNaN(self, value, msg=None):
        """
        Fail if provided value is NaN
        """
        standardMsg = "Provided value is NaN"
        try:
            if math.isnan(value):
                self.fail(self._formatMessage(msg, standardMsg))
        except:
            pass


if __name__ == '__main__':
    # run tests
    unittest.main()


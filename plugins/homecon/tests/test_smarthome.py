#!/usr/bin/env python3
######################################################################################
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
######################################################################################

import unittest
import time

from common import HomeConTestCase



class SmarthomeTests(HomeConTestCase):

    def test_start_smarthome(self):
        self.start_smarthome()
        time.sleep(5)
        self.stop_smarthome()

        self.save_smarthome_log()


    def test_restart_smarthome(self):
        self.start_smarthome()
        time.sleep(5)
        self.stop_smarthome()

        self.save_smarthome_log('_1')


        self.start_smarthome()
        time.sleep(5)
        self.stop_smarthome()

        self.save_smarthome_log('_2')


if __name__ == '__main__':
    # run tests
    unittest.main()


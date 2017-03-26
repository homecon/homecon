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
import time
import asyncio

sys.path.append(os.path.abspath('..'))
import common

import homecon.core.event


class EventTests(unittest.TestCase):

    def test_fire(self):

        homecon.core.event.fire('myevent',{'key':'value'},source='thesource',client=None)

        async def get_event():
            event = await homecon.core.event.queue.get()
            self.assertEqual(event.type,'myevent')
            self.assertEqual(event.data,{'key':'value'})
            self.assertEqual(event.source,'thesource')
            self.assertEqual(event.client,None)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(get_event())



if __name__ == '__main__':
    # run tests
    unittest.main()


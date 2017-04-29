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

import time
import asyncio

from .. import common

import homecon.util


class ExecutorTests(common.TestCase):

    def test_run_in_executor(self):

        data = {}

        def foo(key,val):
            data[key] = 0
            time.sleep(2)
            data[key] = val

        homecon.util.executor.run_in_executor(foo,'key1',1)
        homecon.util.executor.run_in_executor(foo,'key2',2)

        self.assertEqual(data,{'key1':0,'key2':0})

        time.sleep(2)
        self.assertEqual(data,{'key1':1,'key2':2})


    def test_debounce(self):

        data = {}

        def foo(key,val):
            data[key] = val

        homecon.util.executor.debounce(3,foo,'key1',1)

        self.assertEqual(data,{})
        time.sleep(2)
        self.assertEqual(data,{})

        homecon.util.executor.debounce(3,foo,'key1',2)

        time.sleep(2)
        self.assertEqual(data,{})

        time.sleep(2)
        self.assertEqual(data,{'key1':2})





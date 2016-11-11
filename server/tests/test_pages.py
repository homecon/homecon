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
import json
import sys
import os
import asyncio

from common import HomeConTestCase, Client

sys.path.append(os.path.abspath('..'))
from homecon import HomeCon

from core.pages import Pages


class PagesTests(HomeConTestCase):
    
    def test_initialize_pages(self):
        queue = asyncio.Queue()

        self.clear_database()
        pages  = Pages(queue)

        self.assertIn('home',pages._groups)


    def test_get_menu(self):
        queue = asyncio.Queue()

        self.clear_database()
        pages  = Pages(queue)

        menu = pages.get_menu()
        self.assertEqual(menu[0]['pages'][0]['path'], 'central/heating')


    def test_get_page(self):
        queue = asyncio.Queue()

        self.clear_database()
        pages  = Pages(queue)

        page = pages.get_page('home/home')
        self.assertIn('sections',page)


    def test_add_page(self):
        queue = asyncio.Queue()

        self.clear_database()
        pages  = Pages(queue)

        page = pages.add_page('central',{'title':'Sometitle','icon':'someicon'})
        page = pages.get_page('central/sometitle')

        self.assertEqual(page['sections'],[])


    def test_set_page(self):
        queue = asyncio.Queue()

        self.clear_database()
        pages  = Pages(queue)

        page = pages.add_page('central',{'title':'Sometitle','icon':'someicon'})
        page = pages.set_page('central/sometitle',{'title':'Newtitle','icon':'anothericon'})
        page = pages.get_page('central/sometitle')

        self.assertEqual(page['config']['title'],'Newtitle')





if __name__ == '__main__':
    # run tests
    unittest.main()


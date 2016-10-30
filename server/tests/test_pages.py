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

import core.pages as pages

pgs = {
    'sections': [{
        'id': 'home',
        'title': 'Home',
        'order': 0,
    },{
        'id': 'central',
        'title': 'Central',
        'order': 1,
    },{
        'id': 'groundfloor',
        'title': 'Ground floor',
        'order': 2,
    },],
    'pages':[{
        'id':'home',
        'section': 'home',
        'title': 'Home',
        'icon': 'none',
        'order': 0,
        'pagesections': [{
            'widgets': [],
        },]
    },{
        'id':'central_heating',
        'section': 'central',
        'title': 'Heating',
        'icon': 'none',
        'order': 0,
        'pagesections': [{
            'widgets': [],
        },]
    },{
        'id':'central_shading',
        'section': 'central',
        'title': 'Heating',
        'icon': 'none',
        'order': 1,
        'pagesections': [{
            'widgets': [],
        },]
    },{
        'id':'groundfloor_living',
        'section': 'groundfloor',
        'title': 'Living',
        'icon': 'none',
        'order': 0,
        'pagesections': [{
            'widgets': [],
        },]
    },{
        'id':'groundfloor_kitchen',
        'section': 'groundfloor',
        'title': 'Kitchen',
        'icon': 'none',
        'order': 1,
        'pagesections': [{
            'widgets': [],
        },],
    },],
}


class PagesTests(HomeConTestCase):
    
    def test_initialize_pages(self):
        q = asyncio.Queue()
        pg  = pages.Pages(q)


    def test_check_pages(self):
        q = asyncio.Queue()
        pg  = pages.Pages(q)

        result = pg.check_pages(pgs)
        


    def test_update_pages(self):
        q = asyncio.Queue()
        pg  = pages.Pages(q)

        pg.update(1,json.dumps(pgs))
        self.assertEqual(pg._active_pages['pages'],pgs)

    
    def test_add_pages(self):
        q = asyncio.Queue()
        pg  = pages.Pages(q)

        olddata = dict(pg._active_pages)

        newdata = pg.add('newpages',json.dumps(pgs))

        self.assertEqual(pg._active_pages['pages'],olddata['pages'])
        self.assertEqual(newdata['pages'],pgs)


    def test_activate_pages(self):
        q = asyncio.Queue()
        pg  = pages.Pages(q)

        olddata = dict(pg._active_pages)

        newdata = pg.add('newpages',json.dumps(pgs))

        for key,val in pg._pages.items():
            if val['name'] == 'newpages':
                id = val['id']
                break

        newdata = pg.activate_pages(id)

        self.assertEqual(pg._active_pages['pages'],pgs)



if __name__ == '__main__':
    # run tests
    unittest.main()


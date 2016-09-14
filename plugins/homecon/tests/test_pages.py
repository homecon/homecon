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
import time
import json

from common import HomeConTestCase,Client,import_homecon_module

database = import_homecon_module('database')
pages = import_homecon_module('pages')

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
        'icon': '',
        'order': 0,
        'pagesections': [{
            'widgets': [],
        },]
    },{
        'id':'central_heating',
        'section': 'central',
        'title': 'Heating',
        'icon': '',
        'order': 0,
        'pagesections': [{
            'widgets': [],
        },]
    },{
        'id':'central_shading',
        'section': 'central',
        'title': 'Heating',
        'icon': '',
        'order': 1,
        'pagesections': [{
            'widgets': [],
        },]
    },{
        'id':'groundfloor_living',
        'section': 'groundfloor',
        'title': 'Living',
        'icon': '',
        'order': 0,
        'pagesections': [{
            'widgets': [],
        },]
    },{
        'id':'groundfloor_kitchen',
        'section': 'groundfloor',
        'title': 'Kitchen',
        'icon': '',
        'order': 1,
        'pagesections': [{
            'widgets': [],
        },],
    },],
}

class PagesTests(HomeConTestCase):
    """
    Pages tests
    """

    def test_initialize_pages(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        pg  = pages.Pages(db)


    def test_check_pages(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        pg = pages.Pages(db)

        result = pg.check_pages(pgs)
        
        self.assertEqual(result,True)


    def test_update_pages(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        pg = pages.Pages(db)

        pg.update_pages('default',json.dumps(pgs))

        self.assertEqual(pg.data['pages'],pgs)


    def test_add_pages(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        pg = pages.Pages(db)

        olddata = dict(pg.data)

        success = pg.add_pages('newpages',json.dumps(pgs))
        self.assertEqual(success,True)

        newdata = pg.get_pages('newpages')

        self.assertNotEqual(newdata,False)
        self.assertEqual(pg.data['pages'],olddata['pages'])
        self.assertEqual(newdata['pages'],json.dumps(pgs))


    def test_publish_pages(self):
        db = database.Mysql('homecon_test','homecon_test','passwordusedfortesting')
        pg = pages.Pages(db)

        olddata = dict(pg.data)

        success = pg.add_pages('newpages',json.dumps(pgs))

        success = pg.publish_pages('newpages')

        self.assertEqual(pg.data['pages'],pgs)


class PagesWebSocketTests(HomeConTestCase):
    """
    Pages tests through the websocket
    """

    pass




if __name__ == '__main__':
    # run tests
    unittest.main()


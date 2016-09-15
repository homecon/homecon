#!/usr/bin/python3
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

import os
import json
import logging

logger = logging.getLogger('')


class Pages(object):
    def __init__(self,database):
        """
        """

        self._db = database

        self.ws_commands = {
            'pages': self._ws_pages,
            'publish_pages': self._ws_publish_pages,
        }

        # define default pages
        self.data = self._default_pages()
        self.add_pages('default',json.dumps(self.data['pages']),active=1)

        # load the homecon pages from the database
        self._load_active_pages()


    def _default_pages(self):
        data = {
            'id': 1,
            'name': 'default',
            'active': 1,
            'pages': {
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
                    'title': 'Shading',
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
        }

        return data


    def _load_active_pages(self):
        """
        load the active pages from the database
        """
        result = self._db.pages_GET(active=1)
        if not result==None:
            result['pages'] = json.loads(result['pages'])
            logger.warning(result)
            self.data = result
            return True
        return False


    def check_pages(self,pages):
        """
        performs checks on a pages dict
        """
        return True


    def permitted_pages(self,userid,groupids):
        return self.data['pages']


    def get_pages(self,name):
        """
        Loads pages by name

        Returns
        -------
        pages : JSON string

        """
        result = self._db.pages_GET(name=name)
        if not result==None:
            return result

        return False


    def update_pages(self,name,pages):
        """
        Loads pages by name

        Parameters
        ----------
        pages : JSON string

        """

        if self.check_pages(pages):

            # update the database
            success = self._db.pages_PUT(name=name,pages=pages)
            if success:
                self._load_active_pages()
                return success

        return False


    def add_pages(self,name,pages,active=0):
        """
        Loads pages by name

        Parameters
        ----------
        pages : JSON string

        """

        if self.check_pages(pages):
            # update the database
            success = self._db.pages_POST(name=name,pages=pages,active=active)
            if success:
                return success

        return False


    def publish_pages(self,name):
        """
        Sets the active pages by name

        Parameters
        ----------
        name : string

        """

        # deactivate the old pages
        success = self._db.pages_PUT(id=self.data['id'],active=0)

        if success:
            # set the new pages to active
            success = self._db.pages_PUT(name=name,active=1)
        
            if success:
                # load the new pages
                success = self._load_active_pages()
                return success

        
        # make sure the old pages are active and loaded
        self._db.pages_PUT(id=self.data['id'],active=1)
        self._load_active_pages()

        return False


    ############################################################################
    # websocket commands
    ############################################################################

    def _ws_pages(self,client,data,tokenpayload):

        success = False

        if tokenpayload and tokenpayload['permission']>=1 and data['path'] == '':
            result = json.dumps(self.permitted_pages(tokenpayload['userid'],tokenpayload['groupids']))
            success = True
            logger.info("User {} on client {} requested pages {}".format(tokenpayload['userid'],client.addr,result))
            return {'cmd':'pages', 'path':data['path'],'val':result}


        elif tokenpayload and tokenpayload['permission']>=5 and 'path' in data:
            if 'val' in data:
                # delete
                if data['val'] == None:
                    success = True

                # put
                else:
                    success = self.update_pages(data['path'],data['val'])
                    result = json.dumps(self.data)
                
                # post
                if not success:
                    success = self.add_pages(data['path'],data['val'])
                    result = json.dumps(data['val'])

            else:
                # get
                if data['path'] == '':
                    result = json.dumps(self.data)
                    success = True
                else:
                    result = json.dumps(self.data)
                    success = True

                logger.warning(result)


        if success:
            logger.info("User {} on client {} updated pages {} to {}".format(tokenpayload['userid'],client.addr,data['path'],result))
            return {'cmd':'pages', 'path':data['path'],'val':result}
        else:
            logger.debug("User {} on client {} tried to update a setting {}".format(tokenpayload['userid'],client.addr,data))
            return {'cmd':'pages', 'path':data['path'],'val':result}


    def _ws_publish_pages(self,client,data,tokenpayload):
        return {'cmd':'publish_pages', 'path':'','val':''}



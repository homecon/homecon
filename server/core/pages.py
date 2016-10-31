#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json

from . import database
from .plugin import BasePlugin

class Pages(BasePlugin):
 
    def initialize(self):

        self._pages = {}
        self._active_pages = {}
        self._db = database.Database(database='homecon.db')
        self._db_pages = database.Table(self._db,'pages',[
            {'name':'name',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'pages',       'type':'text',       'null': '',  'default':'',  'unique':''},
            {'name':'active',      'type':'int(2)',     'null': '',  'default':'',  'unique':''},
        ])

        # list all pages
        result = self._db_pages.GET(columns=['id','name','active'])
        for p in result:
            self._pages[p['id']] = {'id':p['id'],'name':p['name'],'active':p['active']}


        # define default pages
        if len(self._pages) == 0:
            self.add('default',json.dumps(self._default_pages()),active=1)
            self.add('default copy',json.dumps(self._default_pages()),active=0)


        # load the active homecon pages from the database
        self._get_active_pages()


    def check_pages(self,pages):
        """
        performs checks on a pages dict
        """
        return True


    def permitted_pages(self,userid,groupids):
        return self._active_pages['pages']


    def get(self,id):
        """
        Loads pages by id

        Returns
        -------
        pages : dict

        """

        result = self._db_pages.GET(id=id)
        result = result[0]
        result['pages'] = json.loads(result['pages'])

        return result


    def update(self,id,pages):
        """
        Update pages by name

        Parameters
        ----------
        pages : JSON string

        """

        if self.check_pages(pages):

            # update the database
            self._db_pages.PUT(where='id={}'.format(id),pages=pages)
            self._get_active_pages()

            return True

        return False

    def add(self,name,pages,active=0):
        """
        Loads pages by name

        Parameters
        ----------
        pages : JSON string

        """
        
        if self.check_pages(pages) and not name in self._pages:

            # update the database
            self._db_pages.POST(name=name,pages=pages,active=active)
            pages = self._db_pages.GET(columns=['id','name','pages','active'],order='id',desc=True,limit=1)[0]
            pages['pages'] = json.loads(pages['pages'])

            self._pages[pages['id']] = {'id':pages['id'],'name':pages['name'],'active':pages['active']}

            return pages

        else:
            return False


    def activate_pages(self,id):
        """
        Sets the active pages by id

        Parameters
        ----------
        name : string

        """

        # set the new pages to active
        self._db_pages.PUT(where='id={}'.format(id),active=1)

        # deactivate the old pages
        self._db_pages.PUT(where='id={}'.format(self._active_pages['id']),active=0)

        # load the new pages
        self._get_active_pages()



    def listen(self,event):
        """
        Listen for events

        """

        if event.type == 'get_pages':
            tokenpayload = self._homecon.authentication.jwt_decode(event.data['token'])

            if tokenpayload and tokenpayload['permission']>=5 and 'id' in event.data:
                pages = self.get(event.data['id'])
     
                logging.info("User {} on client {} loaded pages {}".format(tokenpayload['userid'],client.addr,pages['name']))
                self.fire('send_to',{'event':'pages', 'id':pages['id'], 'name':pages['name'], 'pages':pages['pages'], 'clients':[event.client]})

            elif tokenpayload and tokenpayload['permission']>=1:
                pages = self.permitted_pages(tokenpayload['userid'],tokenpayload['groupids'])

                logging.info("User {} on client {} loaded pages {}".format(tokenpayload['userid'],event.client.address,self._active_pages['name']))
                self.fire('send_to',{'event':'pages', 'pages':pages, 'clients':[event.client]})
                

        if event.type == 'delete_pages':
            if tokenpayload and tokenpayload['permission']>=5:
                # do delete
                logging.info("User {} on client {} deleted pages {}".format(tokenpayload['userid'],event.client.address,event.data['id']))
                self.fire('send_to',{'event':'pages', 'id':event.data['id'], 'name':None, 'pages':None, 'clients':[event.client]})
                    

        if event.type == 'add_pages':
            if tokenpayload and tokenpayload['permission']>=5:
                pages = self.add(event.data['name'],event.data['pages'],active=0)
                logging.info("User {} on client {} added pages {}".format(tokenpayload['userid'],event.client.addr,pages['name']))
                self.fire('send_to',{'event':'pages', 'id':pages['id'], 'name':pages['name'], 'pages':pages['pages'], 'clients':[event.client]})


        if event.type == 'set_pages':
            if tokenpayload and tokenpayload['permission']>=5:
                logging.warning(event.data['id'])
                pages = self.update(data['id'],data['pages'])
                logging.info("User {} on client {} updated pages {}".format(tokenpayload['userid'],event.client.addr,pages['name']))
                self.fire('send_to',{'event':'pages', 'id':pages['id'], 'name':pages['name'], 'pages':pages['pages'], 'clients':[event.client]})


        if event.type == 'list_pages':
            self.fire('send_to',{'event':'list_pages', 'pages':self._pages, 'clients':[event.client]})


        if event.type == 'publish_pages':
            self.activate_pages(event.data['id'])
            self.fire('send_to',{'event':'activate_pages', 'success':True, 'clients':[event.client]})


    def _get_active_pages(self):
        result = self._db_pages.GET(active=1)
        result = result[0]
        result['pages'] = json.loads(result['pages'])
        
        self._active_pages = result


    def _default_pages(self):
        pages = {
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

        return pages

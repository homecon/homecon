#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import uuid

from . import database
from .plugin import BasePlugin
from .authentication import jwt_decode

class Pages(BasePlugin):
    """
    Notes
    -----
    A homecon app is structured using groups, pages, sections and widgets

    """

    def initialize(self):


        self._db = database.Database(database='homecon.db')

        self._db_groups = database.Table(self._db,'pages_groups',[
            {'name':'path',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'config',      'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'order',       'type':'int(8)',     'null': '',  'default':'',  'unique':''},
        ])
        self._db_pages = database.Table(self._db,'pages_pages',[
            {'name':'path',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'group',       'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'config',      'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'order',       'type':'int(8)',     'null': '',  'default':'',  'unique':''},
        ])
        self._db_sections = database.Table(self._db,'pages_sections',[
            {'name':'path',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'page',        'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'config',       'type':'char(255)', 'null': '',  'default':'',  'unique':''},
            {'name':'order',       'type':'int(8)',     'null': '',  'default':'',  'unique':''},
        ])
        self._db_widgets = database.Table(self._db,'pages_widgets',[
            {'name':'path',        'type':'char(255)',  'null': '',  'default':'',  'unique':'UNIQUE'},
            {'name':'section',     'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'type',        'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'config',      'type':'char(255)',  'null': '',  'default':'',  'unique':''},
            {'name':'order',       'type':'int(8)',     'null': '',  'default':'',  'unique':''},
        ])

        # local references
        self._groups = {}
        self._pages = {}
        self._sections = {}
        self._widgets = {}


        # load data from the database
        result = self._db_groups.GET()
        for group in result:
            self.add_group_local(group['path'],json.loads(group['config']),group['order'])

        result = self._db_pages.GET()
        for page in result:
            self.add_page_local(page['path'],page['group'],json.loads(page['config']),page['order'])

        result = self._db_sections.GET()
        for section in result:
            self.add_section_local(section['path'],section['page'],json.loads(section['config']),section['order'])

        result = self._db_widgets.GET()
        for widget in result:
            self.add_widget_local(widget['path'],widget['section'],widget['type'],json.loads(widget['config']),widget['order'])


        # define defaults
        if len(self._groups) == 0:
            self.add_group({'title':'Home'})
            self.add_group({'title':'Central'})
            self.add_group({'title':'Ground floor'})

        if len(self._pages) == 0:
            self.add_page('home',{'title':'Home','icon':'blank'})
            self.add_page('central',{'title':'Heating','icon':'blank'})


    def add_group_local(self,path,config,order):
        """
        """
        
        group = {'path':path,'config':config,'order':order}
        self._groups[path] = group
        
        return group


    def add_group(self,config,order=None):
        """
        """

        if 'title' in config:
            temppath = self._title_to_path(config['title'])
            path = temppath
            i = 1
            while path in self._groups:
                i += 1
                path = '{}{}'.format(temppath,i)
        else:
            path = uuid.uuid4()

        if order is None:
            order = self._get_next_order(self._groups)

        self._db_groups.POST(path=path,config=json.dumps(config),order=order)
        group = self.add_group_local(path,config,order)

        return group


    def add_page_local(self,path,group,config,order):
        """
        """
        
        page = {'path':path,'group':group,'config':config,'order':order}
        self._pages[path] = page
        
        return page


    def add_page(self,group,config,order=None):
        """
        """

        basepath = self._groups[group]['path'] + '/'
        if 'title' in config:
            temppath = basepath + self._title_to_path(config['title'])
            path = temppath
            i = 1
            while path in self._pages:
                i += 1
                path = '{}{}'.format(temppath,i)
        else:
            path = basepath + uuid.uuid4()

        if order is None:
            order = self._get_next_order(self._pages)

        self._db_pages.POST(path=path,group=group,config=json.dumps(config),order=order)
        page = self.add_page_local(path,group,config,order)
        
        return page


    def add_section_local(self,path,page,config,order):
        """
        """
        
        section = {'path':path,'page':page,'config':config,'order':order}
        self._sections[path] = section
        
        return section

    def add_section(self,page,config=None,order=None):
        """
        """
        
        path = uuid.uuid4()
        
        if config is None:
            config = {}

        if order is None:
            order = self._get_next_order(self._sections)

        self._db_sections.POST(path=path,page=page,config=json.dumps(config),order=order)
        section = self.add_section_local(path,page,config,order)
        
        return section


    def add_widget_local(self,path,section,widgettype,config,order):
        """
        """
        
        widget = {'path':path,'section':section,'type':widgettype,'config':config,'order':order}
        self._widgets[path] = widget
        
        return section

    def add_widget(self,section,widgettype,config=None,order=None):
        """
        """
        
        path = uuid.uuid4()
        
        if config is None:
            config = {}

        if order is None:
            order = self._get_next_order(self._widgets)


        self._db_widgets.POST(path=path,section=section,type=widgettype,config=json.dumps(config),order=order)
        widget = self.add_widget_local(path,section,widgettype,config,order)
        
        return widget


    def get_menu(self):

        groups = []
        for key,group in self._groups.items():
            if not key == 'home':
                pages = []
                for key,page in self._pages.items():
                    if page['group'] == group['path']:
                        pages.append({'path':page['path'],'config':page['config']})

                pages = sorted(pages, key=lambda x:self._pages[x['path']]['order'])

                group = {
                    'path': group['path'],
                    'config': group['config'],
                    'pages' : pages
                }

                groups.append(group)
                groups = sorted(groups, key=lambda x:self._groups[x['path']]['order'])

        return groups


    def get_page(self,path):
        
        sections = [section['path'] for section in self._sections.values() if section['page'] == path]
        sections = sorted(sections, key=lambda x:self._sections[x]['order'])

        page = {
            'path': self._pages[path]['path'],
            'config': self._pages[path]['config'],
            'sections': sections,
        }

        return page


    def get_section(self,path):
        
        widgets = [widget['path'] for widget in self._widgets.values() if widget['section'] == path]
        widgets = sorted(widgets, key=lambda x:self._widgets[x]['order'])

        section = {
            'path': self._sections[path]['path'],
            'config': self._sections[path]['config'],
            'widgets': widgets,
        }

        return section


    def get_widget(self,path):

        return self._widgets[path]




    def get_all(self):
        """
        Returns the complete pages structured and sorted

        """

        # sort groups, pages, sections and widgets by order
        group_keys = [k for k,v in sorted(self._groups.items(),key=lambda x:x[1]['order'])]
        page_keys = [k for k,v in sorted(self._pages.items(),key=lambda x:x[1]['order'])]
        section_keys = [k for k,v in sorted(self._sections.items(),key=lambda x:x[1]['order'])]
        widget_keys = [k for k,v in sorted(self._widgets.items(),key=lambda x:x[1]['order'])]

        groups = []
        for group_key in group_keys:

            group = {'id':self._groups[group_key]['id'],'config':self._groups[group_key]['config']}
            pages = []

            for page_key in page_keys:
                if self._pages[page_key]['group'] == group['id']:

                    page = {'id':self._pages[group_key]['id'], 'config':self._pages[page_key]['config']}
                    sections = []

                    for section_key in section_keys:
                        if self._sections[section_key]['page'] == page['id']:

                            section = {'id':self._sections[section_key]['id'], 'config':self._sections[section_key]['config']}
                            widgets = []

                            for widget_key in widget_keys:
                                if self._widgets[widget_key]['section'] == section['id']:
                                    widget = {'id':self._sections[section_key]['id'], 'config':self._sections[section_key]['config']}
                                    widgets.append(widget)

                            section['widgets'] = widgets
                            sections.append(section)

                    page['sections'] = sections
                    pages.append(page)

            group['pages'] = pages
            groups.append(group)

        return groups



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

        Parameters
        ----------
        id : int

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
        id : int

        pages : JSON string

        """

        if self.check_pages(pages):
            # update the database
            self._db_pages.PUT(where='id=\'{}\''.format(id),pages=pages)
            self._get_active_pages()

            pages = self._db_pages.GET(id=id)[0]
            pages['pages'] = json.loads(pages['pages'])

            return pages

        return False

    def add(self,name,pages,active=0):
        """
        adds page

        Parameters
        ----------
        name : string
            pages name
            
        pages : JSON string
            the pages

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

    def delete(self,id):
        """
        dDeltes pages by id

        Parameters
        ----------
        id : int
            the id

        """
        self._db_pages.DELETE(where='id=\'{}\''.format(id))

    def activate_pages(self,id):
        """
        Sets the active pages by id

        Parameters
        ----------
        id : int

        """

        # set the new pages to active
        self._db_pages.PUT(where='id={}'.format(id),active=1)

        # deactivate the old pages
        self._db_pages.PUT(where='id={}'.format(self._active_pages['id']),active=0)

        # load the new pages
        self._get_active_pages()







    def listen_pages_menu(self,event):
        
        tokenpayload = jwt_decode(event.data['token'])
        
        if tokenpayload['permission'] > 1:
            self.fire('send_to',{'event':'pages_menu', 'path':'', 'value':self.get_menu(), 'clients':[event.client]})

    def listen_pages_page(self,event):

        if not 'value' in event.data and tokenpayload['permission'] > 1:
            # get
            page = self.get_page(event.data['path'])
            self.fire('send_to',{'event':'pages_page', 'path':page['path'], 'value':page, 'clients':[event.client]})

        elif not event.data['value'] == '' and tokenpayload['permission'] > 6:
            # set
            self._pages[event.data['path']]['config'] = event.data['value']

            page = self.get_page(event.data['path'])
            self.fire('send_to',{'event':'pages_page', 'path':page['path'], 'value':page, 'clients':[event.client]})


    def listen_pages_section(self,event):
        pass
    

    def listen_pages_widget(self,event):
        pass













    def listen_pages(self,event):
        """
        Listen for events

        """
        # set or get
        tokenpayload = event.client.tokenpayload  # fixme, retrieve the payload from the token tokenpayload = self._homecon.authentication.jwt_decode(event.data['token'])

        if tokenpayload and tokenpayload['permission']>=6 and 'value' in event.data:
            # set
            if event.data['path'] == '':
                id = self._active_pages['id']
            else:
                id = event.data['path']

            pages = self.update(id,event.data['value'])
            logging.info("User {} on client {} updated pages {}".format(tokenpayload['userid'],event.client.address,pages['name']))
            self.fire('send_to',{'event':'pages', 'path':pages['id'], 'value':pages['pages'], 'clients':[event.client]})

        elif tokenpayload and tokenpayload['permission']>=5 and not event.data['path'] == '':
            # get
            pages = self.get(event.data['path'])

            logging.info("User {} on client {} loaded pages {}".format(tokenpayload['userid'],event.client.address,pages['name']))
            self.fire('send_to',{'event':'pages', 'path':pages['id'], 'value':pages['pages'], 'clients':[event.client]})

        elif tokenpayload and tokenpayload['permission']>=4:
            # get active
            pages = self.permitted_pages(tokenpayload['userid'],tokenpayload['groupids'])

            logging.info("User {} on client {} loaded pages {}".format(tokenpayload['userid'],event.client.address,self._active_pages['name']))
            self.fire('send_to',{'event':'pages', 'path':event.data['path'], 'value':pages, 'clients':[event.client]})


    def listen_delete_pages(self,event):
        if tokenpayload and tokenpayload['permission']>=7:
            self.delete(event.data['path'])
            logging.info("User {} on client {} deleted pages {}".format(tokenpayload['userid'],event.client.address,event.data['path']))
            self.fire('send_to',{'event':'pages', 'path':event.data['path'], 'value':None, 'clients':[event.client]})


    def listen_add_pages(self,event):
        if tokenpayload and tokenpayload['permission']>=7:
            pages = self.add(event.data['name'],event.data['pages'],active=0)
            logging.info("User {} on client {} added pages {}".format(tokenpayload['userid'],event.client.addr,pages['name']))
            self.fire('send_to',{'event':'pages', 'path':pages['id'], 'value':pages['pages'], 'clients':[event.client]})


    def listen_list_pages(self,event):
        self.fire('send_to',{'event':'list_pages', 'path':'', 'value':[page for page in self._pages.values()], 'clients':[event.client]})


    def listen_publish_pages(self,event):
        self.activate_pages(event.data['id'])
        self.fire('send_to',{'event':'activate_pages', 'success':True, 'clients':[event.client]})


    def _get_active_pages(self):
        result = self._db_pages.GET(active=1)
        result = result[0]
        result['pages'] = json.loads(result['pages'])
        
        self._active_pages = result


    def _get_next_order(self,data):
        """
        Parameters
        ----------
        data : dict
            a dictionary with an order key
        """
        order = 0
        for d in data.values():
            order = max(order,d['order'])

        order += 1

        return order


    def _title_to_path(self,title):
        return title.lower().replace(' ','_')



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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import uuid

from homecon.core.event import Event
from homecon.core.database import get_database, close_database, Field, DatabaseObject
from homecon.core.plugin import Plugin
from .authentication import jwt_decode


logger = logging.getLogger(__name__)


class Group(DatabaseObject):
    def __init__(self, id=None, path=None, config=None, order=None):
        super().__init__(id=id)
        self._path = path
        self._config = config
        self._order = order

    @staticmethod
    def get_table():
        db = get_database()
        if 'page_groups' in db:
            table = db.page_groups
        else:
            table = db.define_table(
                'page_groups',
                Field('path', type='string', default='', unique=True),
                Field('config', type='string', default='{}'),
                Field('order', type='integer', default=0),
            )
        return table

    @classmethod
    def add(cls, path, config=None, order=None):
        """
        Add a group
        """
        # check if it already exists
        entry = cls.get_table()(path=path)
        if entry is None:
            id = cls.get_table().insert(path=path, config=json.dumps(config or '{}'), order=order)
            close_database()
            # get the state FIXME error checking
            obj = cls.get(id=id)
            logger.debug('added group')
            Event.fire('group_added', {'group': object}, 'Group')
        else:
            obj = cls(**entry.as_dict())
        return obj

    @property
    def path(self):
        self._path = self.get_property('path')
        return self._path

    @property
    def full_path(self):
        return self.path

    @property
    def config(self):
        self._config = json.loads(self.get_property('config'))
        return self._config

    @property
    def order(self):
        self._order = self.get_property('order') or 0
        return self._order

    @property
    def pages(self):
        return sorted([page for page in Page.all() if page.group.id == self.id], key=lambda x: x.order)


class Page(DatabaseObject):
    def __init__(self, id=None, path=None, group=None, config=None, order=None):
        super().__init__(id=id)
        self._path = path
        self._group = group
        self._config = config
        self._order = order

    @staticmethod
    def get_table():
        db = get_database()
        if 'pages' in db:
            table = db.pages
        else:
            table = db.define_table(
                'pages',
                Field('path', type='string', default='', unique=True),
                Field('group', type='integer'),
                Field('config', type='string', default='{}'),
                Field('order', type='integer', default=0),
            )
        return table

    @classmethod
    def add(cls, path, group, config=None, order=None):
        """
        Add a state to the database
        """
        # check if it already exists
        entry = cls.get_table()(path=path, group=group.id)
        if entry is None:
            id = cls.get_table().insert(path=path, group=group.id, config=json.dumps(config or '{}'), order=order)
            close_database()
            # FIXME error checking
            obj = cls.get(id=id)
            logger.debug('added page')
            Event.fire('page_added', {'page': obj}, 'Page')
        else:
            obj = cls(**entry.as_dict())
        return obj

    @property
    def path(self):
        self._path = self.get_property('path')
        return self._path

    @property
    def full_path(self):
        self._path = self.get_property('path')
        return '{}/{}'.format(self.group.full_path, self.path)

    @property
    def group(self):
        self._group = self.get_property('group')
        return Group.get(self._group)

    @property
    def config(self):
        self._config = json.loads(self.get_property('config'))
        return self._config

    @property
    def order(self):
        self._order = self.get_property('order') or 0
        return self._order

    @property
    def sections(self):
        return sorted([section for section in Section.all() if section.page.id == self.id], key=lambda x: x.order)


class Section(DatabaseObject):
    def __init__(self, id=None, path=None, page=None, config=None, order=None):
        super().__init__(id=id)
        self._path = path
        self._page = page
        self._config = config
        self._order = order

    @staticmethod
    def get_table():
        db = get_database()
        if 'sections' in db:
            table = db.sections
        else:
            table = db.define_table(
                'sections',
                Field('path', type='string', default=''),
                Field('page', type='integer'),
                Field('config', type='string', default='{}'),
                Field('order', type='integer', default=0),
            )
        return table

    @classmethod
    def add(cls, path, page, config=None, order=None):
        """
        Add a state to the database
        """
        # check if it already exists
        entry = cls.get_table()(path=path, page=page.id)
        if entry is None:
            id = cls.get_table().insert(path=path, page=page.id, config=json.dumps(config or '{}'), order=order)
            close_database()
            # FIXME error checking
            obj = cls.get(id=id)
            logger.debug('added section')
            Event.fire('section_added', {'section': obj}, 'Section')
        else:
            obj = cls(**entry.as_dict())
        return obj

    @property
    def path(self):
        self._path = self.get_property('path')
        return self._path

    @property
    def full_path(self):
        self._path = self.get_property('path')
        return '{}/{}'.format(self.page.full_path, self.path)

    @property
    def page(self):
        self._page = self.get_property('page')
        return Page.get(self._page)

    @property
    def config(self):
        self._config = json.loads(self.get_property('config'))
        return self._config

    @property
    def order(self):
        self._order = self.get_property('order') or 0
        return self._order

    @property
    def widgets(self):
        return sorted([widget for widget in Widget.all() if widget.section.id == self.id], key=lambda x: x.order)


class Widget(DatabaseObject):
    def __init__(self, id=None, path=None, section=None, type=type, config=None, order=None):
        super().__init__(id=id)
        self._path = path
        self._section = section
        self._type = type
        self._config = config
        self._order = order

    @staticmethod
    def get_table():
        db = get_database()
        if 'widgets' in db:
            table = db.widgets
        else:
            table = db.define_table(
                'widgets',
                Field('path', type='string', default='', unique=True),
                Field('section', type='integer'),
                Field('type', type='string'),
                Field('config', type='string', default='{}'),
                Field('order', type='integer', default=0),
            )
        return table

    @classmethod
    def add(cls, path, section, config=None, order=None):
        """
        Add a state to the database
        """
        # check if it already exists
        entry = cls.get_table()(path=path, section=section.id)
        if entry is None:
            id = cls.get_table().insert(path=path, section=section.id, config=json.dumps(config or '{}'), order=order)
            close_database()
            # FIXME error checking
            obj = cls.get(id=id)
            logger.debug('added widget')
            Event.fire('widget_added', {'widget': obj}, 'Widget')
        else:
            obj = cls(**entry.as_dict())
        return obj

    @property
    def path(self):
        self._path = self.get_property('path')
        return self._path

    @property
    def full_path(self):
        self._path = self.get_property('path')
        return '{}/{}'.format(self.section.full_path, self.path)

    @property
    def section(self):
        self._section = self.get_property('section')
        return Section.get(self._section)

    @property
    def config(self):
        self._config = json.loads(self.get_property('config'))
        return self._config

    @property
    def order(self):
        self._order = self.get_property('order') or 0
        return self._order


class Pages(Plugin):
    """
    Notes
    -----
    A homecon app is structured using groups, pages, sections and widgets

    """

    def initialize(self):

        if len(Group.all()) == 0:
            Group.add('home', config={'title': 'Home'})
            Group.add('central', config={'title': 'Central'})
            Group.add('ground_floor', config={'title': 'Ground floor'})
            Group.add('first_floor', config={'title': 'First floor'})



        # local references
        self._groups = {}
        self._pages = {}
        self._sections = {}
        self._widgets = {}


        # load data from the database
        result = self._db_groups.get()
        for group in result:
            self.add_group_local(group['path'],json.loads(group['config']),group['order'])

        result = self._db_pages.get()
        for page in result:
            self.add_page_local(page['path'],page['group'],json.loads(page['config']),page['order'])

        result = self._db_sections.get()
        for section in result:
            self.add_section_local(section['path'],section['page'],json.loads(section['config']),section['order'])

        result = self._db_widgets.get()
        for widget in result:
            self.add_widget_local(widget['path'],widget['section'],widget['type'],json.loads(widget['config']),widget['order'])


        # define defaults
        if len(self._groups) == 0:
            self.add_group({'title':'Home'})
            self.add_group({'title':'Central'})
            self.add_group({'title':'Ground floor'})
            self.add_group({'title':'First floor'})

        if len(self._pages) == 0:
            self.add_page('home',{'title':'Home','icon':'blank'})
            self.add_page('central',{'title':'Heating','icon':'sani_heating'})
            self.add_page('groundfloor',{'title':'Living room','icon':'scene_livingroom'})
            self.add_page('groundfloor',{'title':'Kitchen','icon':'scene_dinner'})
            self.add_page('firstfloor',{'title':'Bathroom','icon':'scene_bath'})
            self.add_page('firstfloor',{'title':'Master Bedroom','icon':'scene_sleeping'})

        if len(self._sections) == 0:

            s = self.add_section('home/home',{'type':'underlined'})

            self.add_widget(s['path'],'clock',config={},order=None)
            self.add_widget(s['path'],'date',config={},order=None)

            s = self.add_section('home/home',{'type':'underlined'})

            self.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':0},order=None)
            self.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':24},order=None)
            self.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':48},order=None)
            self.add_widget(s['path'],'weather-block',config={'daily':True, 'timeoffset':72},order=None)


        logging.debug('Pages plugin Initialized')

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
            path = str(uuid.uuid4())

        if order is None:
            order = self._get_next_order(self._groups)

        self._db_groups.post(path=path, config=json.dumps(config), order=order)
        group = self.add_group_local(path,config,order)

        return group

    def update_group(self,path,config):
        """
        """

        group =  self._groups[path]
        for key in config:
            group['config'][key] = config[key]

        self._db_groups.put(config=json.dumps(group['config']), where='path=\'{}\''.format(path))

        return group

    def delete_group(self,path):
        """
        """
    
        del self._groups[path]
        self._db_groups.delete(path=path)

        # cascade
        for page in self._pages.values():
            if page['group'] == path:
                self.delete_page(page['path'])

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
            path = basepath + str(uuid.uuid4())

        if order is None:
            order = self._get_next_order(self._pages)

        self._db_pages.post(path=path, group=group, config=json.dumps(config), order=order)
        page = self.add_page_local(path,group,config,order)
        
        return page

    def update_page(self,path,config):
        """
        """

        page =  self._pages[path]
        for key in config:
            page['config'][key] = config[key]

        self._db_pages.put(config=json.dumps(page['config']), where='path=\'{}\''.format(path))

        return page

    def delete_page(self,path):
        """
        """
    
        del self._pages[path]
        self._db_pages.delete(path=path)

        # cascade
        for section in self._sections.values():
            if section['page'] == path:
                self.delete_section(section['path'])


    def add_section_local(self,path,page,config,order):
        """
        """
        
        section = {'path':path,'page':page,'config':config,'order':order}
        self._sections[path] = section
        
        return section

    def add_section(self,page,config=None,order=None):
        """
        """
        
        path = str(uuid.uuid4())
        
        if config is None:
            config = {}

        if order is None:
            order = self._get_next_order(self._sections)

        self._db_sections.post(path=path, page=page, config=json.dumps(config), order=order)
        section = self.add_section_local(path,page,config,order)
        
        return section

    def update_section(self,path,config):
        """
        """

        section =  self._sections[path]
        for key in config:
            section['config'][key] = config[key]

        self._db_sections.put(config=json.dumps(section['config']), where='path=\'{}\''.format(path))

        return section

    def delete_section(self,path):
        """
        """
    
        del self._sections[path]
        self._db_sections.delete(path=path)

        # cascade
        for widget in self._widgets.values():
            if widget['section'] == path:
                self.delete_widget(widget['path'])


    def add_widget_local(self,path,section,widgettype,config,order):
        """
        """
        
        widget = {'path':path,'section':section,'type':widgettype,'config':config,'order':order}
        self._widgets[path] = widget
        
        return section

    def add_widget(self,section,widgettype,config=None,order=None):
        """
        """
        
        path = str(uuid.uuid4())
        
        if config is None:
            config = {}

        if order is None:
            order = self._get_next_order(self._widgets)


        self._db_widgets.post(path=path, section=section, type=widgettype, config=json.dumps(config), order=order)
        widget = self.add_widget_local(path,section,widgettype,config,order)
        
        return widget

    def update_widget(self,path,config):
        """
        """

        widget =  self._widgets[path]
        for key in config:
            widget['config'][key] = config[key]

        self._db_widgets.put(config=json.dumps(widget['config']), where='path=\'{}\''.format(path))

        return widget

    def delete_widget(self,path):
        """
        """
    
        del self._widgets[path]
        self._db_widgets.delete(path=path)



    def get_menu(self):
        """
        """

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

    def get_pages_paths(self):
        pages = [page['path'] for page in self._pages.values()]
        pages = sorted(pages,key=lambda x:self._pages[x]['order'])
        return pages

    def get_page(self,path):
        """
        """

        sections = [section['path'] for section in self._sections.values() if section['page'] == path]
        sections = sorted(sections, key=lambda x:self._sections[x]['order'])

        page = {
            'path': self._pages[path]['path'],
            'config': self._pages[path]['config'],
            'sections': sections,
        }

        return page

    def set_page(self,path,config):
        """
        """

        page = self._pages[path]
        page['config'] = config
        self._db_pages.put(config=json.dumps(page['config']), where='path=\'{}\''.format(page['path']))

        return page

    def get_section(self,path):
        """
        """

        widgets = [widget['path'] for widget in self._widgets.values() if widget['section'] == path]
        widgets = sorted(widgets, key=lambda x:self._widgets[x]['order'])

        section = {
            'path': self._sections[path]['path'],
            'config': self._sections[path]['config'],
            'widgets': widgets,
        }

        return section


    def get_widget(self,path):
        """
        """

        return self._widgets[path]



    def listen_pages_menu(self,event):
        
        tokenpayload = jwt_decode(event.data['token'])
        
        if tokenpayload and tokenpayload['permission'] > 1:
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])

    def listen_pages_paths(self,event):
        
        tokenpayload = jwt_decode(event.data['token'])
        
        if tokenpayload and tokenpayload['permission'] > 1:
            core.websocket.send({'event':'pages_paths', 'path':'', 'value':self.get_pages_paths()}, clients=[event.client])

    def listen_pages_group(self,event):

        tokenpayload = jwt_decode(event.data['token'])

        if 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # delete
            self.delete_group(event.data['path'])
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # update
            self.update_group(event.data['path'],event.data['value'])
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])

        if not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
            # add
            self.add_group({'title':'newgroup'})
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])

    def listen_pages_page(self,event):

        tokenpayload = jwt_decode(event.data['token'])

        if 'path' in event.data and not 'value' in event.data and tokenpayload and tokenpayload['permission'] > 1:
            # get
            if event.data['path'] in self._pages:
                page = self.get_page(event.data['path'])
                core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])

            else:
                logging.warning('{} not in pages'.format(event.data['path']))

        elif 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # delete
            self.delete_page(event.data['path'])
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
            core.websocket.send({'event':'pages_paths', 'path':'', 'value':self.get_pages_paths()}, clients=[event.client])
            
        elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # update
            page = self._pages[event.data['path']]
            self.update_page(event.data['path'],event.data['value']['config'])
            page = self.get_page(event.data['path'])
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
            core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])


        elif not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
            # add
            self.add_page(event.data['group'],{'title':'newpage','icon':'blank'})
            core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
            core.websocket.send({'event':'pages_paths', 'path':'', 'value':self.get_pages_paths()}, clients=[event.client])


    def listen_pages_section(self,event):

        tokenpayload = jwt_decode(event.data['token'])

        if 'path' in event.data and not 'value' in event.data and tokenpayload and tokenpayload['permission'] > 1:
            # get
            section = self.get_section(event.data['path'])
            core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # delete
            pagepath = self._sections[event.data['path']]['page']
            self.delete_section(event.data['path'])
            page = self.get_page(pagepath)
            core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # update
            self.update_section(event.data['path'],event.data['value']['config'])
            section = self.get_section(event.data['path'])
            core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])

        elif not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
            # add
            self.add_section(event.data['page'],{'title':'newsection','type':'raised'})
            page = self.get_page(event.data['page'])
            core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])


    def listen_pages_widget(self,event):

        tokenpayload = jwt_decode(event.data['token'])

        if 'path' in event.data and not 'value' in event.data and tokenpayload and tokenpayload['permission'] > 1:
            # get
            widget = self.get_widget(event.data['path'])
            core.websocket.send({'event':'pages_widget', 'path':widget['path'], 'value':widget}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # delete
            sectionpath = self._widgets[event.data['path']]['section']
            self.delete_widget(event.data['path'])
            section = self.get_section(sectionpath)
            core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])

        elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
            # update
            self.update_widget(event.data['path'],event.data['value']['config'])
            widget = self._widgets[event.data['path']]
            core.websocket.send({'event':'pages_widget', 'path':widget['path'], 'value':widget}, clients=[event.client])

        elif not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
            # add
            self.add_widget(event.data['section'],event.data['type'],{'initialize':True})
            section = self.get_section(event.data['section'])
            core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])










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
        return title.lower().replace(' ','')



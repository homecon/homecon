#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import uuid

from uuid import uuid4

from homecon.core.event import Event
from homecon.core.database import get_database, Field, DatabaseObject
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
        return db, table

    @classmethod
    def add(cls, path, config=None, order=None):
        """
        Add a group
        """
        # check if it already exists
        db, table = cls.get_table()
        entry = table(path=path)
        if entry is None:
            id = table.insert(path=path, config=json.dumps(config or '{}'), order=order)
            db.close()
            # FIXME error checking
            obj = cls.get(id=id)
            logger.debug('added group')
            Event.fire('group_added', {'group': object}, 'Group')
        else:
            obj = cls(**entry.as_dict())
        return obj

    @classmethod
    def get(cls, path=None, id=None):
        db, table = cls.get_table()
        if id is not None:
            db_entry = table(id)
            db.close()
        elif path is not None:
            db_entry = table(path=path)
            db.close()
        else:
            logger.error("id or path must be supplied")
            return None
        if db_entry is not None:
            return cls(**db_entry.as_dict())
        else:
            return None

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

    def get_page(self, path):
        pages = [page for page in Page.all() if page.group.id == self.id and page.path == path]
        if len(pages) == 1:
            return pages[0]
        return None

    def serialize(self):
        return {
            'id': self.id,
            'path': self.full_path,
            'config': self.config,
            'pages': [page.id for page in self.pages]
        }


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
                Field('path', type='string', default=''),
                Field('group', type='integer'),
                Field('config', type='string', default='{}'),
                Field('order', type='integer', default=0),
            )
        return db, table

    @classmethod
    def add(cls, path, group, config=None, order=None):
        """
        Add a state to the database
        """
        # check if it already exists
        db, table = cls.get_table()
        entry = table(path=path, group=group.id)
        if entry is None:
            id = table.insert(path=path, group=group.id, config=json.dumps(config or '{}'), order=order)
            db.close()
            # FIXME error checking
            obj = cls.get(id=id)
            logger.debug('added page')
            Event.fire('page_added', {'page': obj}, 'Page')
        else:
            obj = cls(**entry.as_dict())
        return obj

    @classmethod
    def get(cls, full_path=None, id=None):
        db, table = cls.get_table()
        if id is not None:
            db_entry = table(id)
            db.close()
        elif full_path is not None:
            group_path, page_path = full_path.split('/')
            group = Group.get(path=group_path)
            db_entry = table(path=page_path, group=group.id)
            db.close()
        else:
            logger.error("id or path must be supplied")
            return None
        if db_entry is not None:
            return cls(**db_entry.as_dict())
        else:
            return None

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
        return Group.get(id=self._group)

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

    def get_section(self, path):
        objs = [obj for obj in Page.all() if obj.page.id == self.id and obj.path == path]
        if len(objs) == 1:
            return objs[0]
        return None

    def serialize(self):
        return {
            'id': self.id,
            'path': self.full_path,
            'config': self.config,
            'sections': [section.id for section in self.sections]
        }


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
        return db, table

    @classmethod
    def add(cls, path, page, config=None, order=None):
        """
        Add a state to the database
        """
        # check if it already exists
        db, table = cls.get_table()
        entry = table(path=path, page=page.id)
        if entry is None:
            id = table.insert(path=path, page=page.id, config=json.dumps(config or '{}'), order=order)
            db.close()
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
        return Page.get(id=self._page)

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

    def get_widget(self, path):
        objs = [obj for obj in Page.all() if obj.page.id == self.id and obj.path == path]
        if len(objs) == 1:
            return objs[0]
        return None

    def serialize(self):
        return {
            'id': self.id,
            'path': self.full_path,
            'config': self.config,
            'widgets': [widgets.id for widgets in self.widgets]
        }


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
                Field('path', type='string', default=''),
                Field('section', type='integer'),
                Field('type', type='string'),
                Field('config', type='string', default='{}'),
                Field('order', type='integer', default=0),
            )
        return db, table

    @classmethod
    def add(cls, path, section, type, config=None, order=None):
        """
        Add a state to the database
        """
        # check if it already exists
        if path is None:
            path = uuid4()
        db, table = cls.get_table()
        entry = table(path=path, section=section.id)
        if entry is None:
            id = table.insert(path=path, section=section.id, type=type, config=json.dumps(config or '{}'), order=order)
            db.close()
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
        return Section.get(id=self._section)

    @property
    def config(self):
        self._config = json.loads(self.get_property('config'))
        return self._config

    @property
    def order(self):
        self._order = self.get_property('order') or 0
        return self._order

    @property
    def type(self):
        self._type = self.get_property('type')
        return self._type

    def serialize(self):
        return {
            'id': self.id,
            'path': self.full_path,
            'type': self.type,
            'config': self.config,
        }


class Pages(Plugin):
    """
    Notes
    -----
    A homecon app is structured using groups, pages, sections and widgets

    """

    def initialize(self):

        # set defaults
        if len(Group.all()) == 0 and len(Page.all()) == 0 and len(Section.all()) == 0 and len(Widget.all()) == 0:
            g0 = Group.add('home', config={'title': 'Home'})
            g1 = Group.add('central', config={'title': 'Central'})
            g2 = Group.add('ground_floor', config={'title': 'Ground floor'})
            g3 = Group.add('first_floor', config={'title': 'First floor'})

            p0 = Page.add('home', g0, config={'title': 'Home', 'icon': 'blank'})
            p1 = Page.add('heating', g1, config={'title': 'Heating', 'icon': 'sani_heating'})
            p2 = Page.add('kitchen', g2, config={'title': 'Kitchen', 'icon': 'scene_dinner'})
            p3 = Page.add('bathroom', g3, config={'title': 'Bathroom', 'icon': 'scene_bath'})
            p4 = Page.add('master_bedroom', g3, config={'title': 'Master Bedroom', 'icon': 'scene_sleeping'})

            s0 = Section.add('time', p0, config={'type': 'underlined'})
            Widget.add('w0', s0, 'clock', config={})
            Widget.add('w1', s0, 'date', config={})

            s1 = Section.add('weather', p0, config={'type': 'underlined'})
            Widget.add('w0', s1, 'weather-block', config={'daily': True, 'timeoffset': 0})
            Widget.add('w1', s1, 'weather-block', config={'daily': True, 'timeoffset': 24})
            Widget.add('w2', s1, 'weather-block', config={'daily': True, 'timeoffset': 48})
            Widget.add('w3', s1, 'weather-block', config={'daily': True, 'timeoffset': 72})

            s2 = Section.add('lights', p2, config={'type': 'raised', 'title': 'Lights'})
            Widget.add('w0', s2, 'switch', config={'icon': 'light_light', 'state': 5})

            # s3 = Section.add('shading', p2, config={'type': 'collapsible', 'title': 'Shading'})
            # Widget.add('w0', s3, 'shading')

        logging.debug('Pages plugin initialized')

    def get_menu(self):
        """
        Return the data required to make the menu
        """
        menu = []
        for group in sorted(Group.all(), key=lambda x: group.order):
            if not group.path == 'home':
                menu.append({
                    'path': group.path,
                    'config': group.config,
                    'pages': [{'id': page.id, 'path': page.full_path, 'config': page.config} for page in group.pages]
                })
        menu = sorted(menu, key=lambda x: self._groups[x['path']]['order'])
        return menu

    # def listen_pages_menu(self, event):
    #     # FIXME authentication
    #     # tokenpayload = jwt_decode(event.data['token'])
    #
    #     # if tokenpayload and tokenpayload['permission'] > 1:
    #     #     core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
    #     Event.fire('websocket_send',
    #                {'event': 'pages_menu', 'path': '', 'value': self.get_menu()},
    #                source=self, target=event.reply_to)

    def listen_pages_group_ids(self, event):
        # FIXME check user authentication
        groups = [group.id for group in sorted([group for group in Group.all()], key=lambda x: x.order)
                  if group.path != 'home']
        event.reply('websocket_reply', {'event': 'pages_group_ids', 'data': {'id': '', 'value': groups}})

    def listen_pages_group(self, event):
        if 'id' in event.data and 'value' not in event.data:
            group = Group.get(id=event.data['id']).serialize()
            event.reply('websocket_reply', {'event': 'pages_group', 'data': {'id': event.data['id'], 'value': group}})

    def listen_pages_page(self, event):
        if 'id' in event.data and 'value' not in event.data:
            page = Page.get(id=event.data['id']).serialize()
            event.reply('websocket_reply', {'event': 'pages_page', 'data': {'id': event.data['id'], 'value': page}})
        elif 'path' in event.data and 'value' not in event.data:
            page = Page.get(full_path=event.data['path']).serialize()
            event.reply('websocket_reply', {'event': 'pages_page',
                                            'data': {'path': event.data['path'], 'value': page}})

    def listen_pages_section(self, event):
        if 'id' in event.data and 'value' not in event.data:
            section = Section.get(id=event.data['id']).serialize()
            event.reply('websocket_reply', {'event': 'pages_section', 'data': {'id': event.data['id'],
                                                                               'value': section}})

    def listen_pages_widget(self, event):
        if 'id' in event.data and 'value' not in event.data:
            widget = Widget.get(id=event.data['id']).serialize()
            event.reply('websocket_reply', {'event': 'pages_widget', 'data': {'id': event.data['id'], 'value': widget}})
    #
    # def listen_pages_paths(self, event):
    #
    #     tokenpayload = jwt_decode(event.data['token'])
    #
    #     if tokenpayload and tokenpayload['permission'] > 1:
    #         core.websocket.send({'event': 'pages_paths', 'path': '', 'value': self.get_pages_paths()}, clients=[event.client])

    # def listen_pages_group(self, event):
    #
    #     tokenpayload = jwt_decode(event.data['token'])
    #
    #     if 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
    #         # delete
    #         self.delete_group(event.data['path'])
    #         core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
    #
    #     elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
    #         # update
    #         self.update_group(event.data['path'],event.data['value'])
    #         core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
    #
    #     if not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
    #         # add
    #         self.add_group({'title':'newgroup'})
    #         core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])

    # def listen_pages_page(self,event):
    #
    #     tokenpayload = jwt_decode(event.data['token'])
    #
    #     if 'path' in event.data and not 'value' in event.data and tokenpayload and tokenpayload['permission'] > 1:
    #         # get
    #         if event.data['path'] in self._pages:
    #             page = self.get_page(event.data['path'])
    #             core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])
    #
    #         else:
    #             logging.warning('{} not in pages'.format(event.data['path']))
    #
    #     elif 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
    #         # delete
    #         self.delete_page(event.data['path'])
    #         core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
    #         core.websocket.send({'event':'pages_paths', 'path':'', 'value':self.get_pages_paths()}, clients=[event.client])
    #
    #     elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
    #         # update
    #         page = self._pages[event.data['path']]
    #         self.update_page(event.data['path'],event.data['value']['config'])
    #         page = self.get_page(event.data['path'])
    #         core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
    #         core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])
    #
    #
    #     elif not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
    #         # add
    #         self.add_page(event.data['group'],{'title':'newpage','icon':'blank'})
    #         core.websocket.send({'event':'pages_menu', 'path':'', 'value':self.get_menu()}, clients=[event.client])
    #         core.websocket.send({'event':'pages_paths', 'path':'', 'value':self.get_pages_paths()}, clients=[event.client])


    # def listen_pages_section(self,event):
    #
    #     tokenpayload = jwt_decode(event.data['token'])
    #
    #     if 'path' in event.data and not 'value' in event.data and tokenpayload and tokenpayload['permission'] > 1:
    #         # get
    #         section = self.get_section(event.data['path'])
    #         core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])
    #
    #     elif 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
    #         # delete
    #         pagepath = self._sections[event.data['path']]['page']
    #         self.delete_section(event.data['path'])
    #         page = self.get_page(pagepath)
    #         core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])
    #
    #     elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
    #         # update
    #         self.update_section(event.data['path'],event.data['value']['config'])
    #         section = self.get_section(event.data['path'])
    #         core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])
    #
    #     elif not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
    #         # add
    #         self.add_section(event.data['page'],{'title':'newsection','type':'raised'})
    #         page = self.get_page(event.data['page'])
    #         core.websocket.send({'event':'pages_page', 'path':page['path'], 'value':page}, clients=[event.client])


    # def listen_pages_widget(self,event):
    #
    #     tokenpayload = jwt_decode(event.data['token'])
    #
    #     if 'path' in event.data and not 'value' in event.data and tokenpayload and tokenpayload['permission'] > 1:
    #         # get
    #         widget = self.get_widget(event.data['path'])
    #         core.websocket.send({'event':'pages_widget', 'path':widget['path'], 'value':widget}, clients=[event.client])
    #
    #     elif 'path' in event.data and 'value' in event.data and event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
    #         # delete
    #         sectionpath = self._widgets[event.data['path']]['section']
    #         self.delete_widget(event.data['path'])
    #         section = self.get_section(sectionpath)
    #         core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])
    #
    #     elif 'path' in event.data and 'value' in event.data and not event.data['value'] is None and tokenpayload and tokenpayload['permission'] > 6:
    #         # update
    #         self.update_widget(event.data['path'],event.data['value']['config'])
    #         widget = self._widgets[event.data['path']]
    #         core.websocket.send({'event':'pages_widget', 'path':widget['path'], 'value':widget}, clients=[event.client])
    #
    #     elif not 'path' in event.data and tokenpayload and tokenpayload['permission'] > 6:
    #         # add
    #         self.add_widget(event.data['section'],event.data['type'],{'initialize':True})
    #         section = self.get_section(event.data['section'])
    #         core.websocket.send({'event':'pages_section', 'path':section['path'], 'value':section}, clients=[event.client])

    def _get_next_order(self,data):
        """
        Parameters
        ----------
        data : dict
            a dictionary with an order key
        """
        order = 0
        for d in data.values():
            order = max(order, d['order'])

        order += 1

        return order

    def _title_to_path(self, title):
        return title.lower().replace(' ', '')

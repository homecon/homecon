#!/usr/bin/env python3

import logging
import json
import time

from pydal import DAL, Field

from homecon.core.event import Event, IEventManager
from homecon.core.pages.pages import Group, Page, Section, Widget, IPagesManager, MemoryObjectManager, MemoryPagesManager
from homecon.core.states.state import IStateManager
from homecon.core.plugins.plugin import BasePlugin


logger = logging.getLogger(__name__)


class DALObjectManager(MemoryObjectManager):
    def __init__(self, db, table, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._db = db
        self._table = table

        # load objects into memory
        for row in self._db().select(self._table.ALL):
            obj = self.row_to_obj(row)
            self._objects[obj.id] = obj

    def row_to_obj(self, row):
        raise NotImplementedError


class DALGroupManager(DALObjectManager):
    def row_to_obj(self, row):
        id = row.pop('id')
        name = row.pop('name')
        return self._object_factory(self, id, name, **row)


class DALPageManager(DALObjectManager):
    def row_to_obj(self, row):
        id = row.pop('id')
        name = row.pop('name')
        page = row.pop('name')
        return self._object_factory(self, id, name, **row)


class DALPagesManager(MemoryPagesManager):
    def __init__(self, folder: str, uri: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._db = DAL(uri, folder=folder)
        self._groups_table = self._db.define_table(
            'page_groups',
            Field('name', type='string', default='', unique=True),
            Field('config', type='string', default='{}'),
            Field('order', type='integer', default=0),
        )

    def get_group(self, path=None, id=None):
        if id is not None:
            db_entry = table(id)
            db.close()
        elif path is not None:
            parts = path.split('/')
            db_entry = table(name=parts[-1])
            db.close()
        else:
            logger.error("id or path must be supplied")
            return None
        if db_entry is not None:
            return cls(**db_entry.as_dict())
        else:
            return None

    def add_group(self, name, config=None, order=None):
        """
        Add a group
        """
        # check if it already exists
        entry = self._groups_table(name=name)
        if entry is None:
            id = self._groups_table.insert(name=name, config=json.dumps(config or {}), order=order)
            self._db.commit()

            # FIXME error checking
            obj = self.get_group(id=id)
            logger.debug('added group')
            Event.fire('group_added', {'group': object}, 'Group')
        else:
            obj = cls(**entry.as_dict())
        return obj

    def clear(self):
        db, table = Widget.get_table()
        table.drop()
        db.commit()
        db.close()

        db, table = Section.get_table()
        table.drop()
        db.commit()
        db.close()

        db, table = Page.get_table()
        table.drop()
        db.commit()
        db.close()

        db, table = Group.get_table()
        table.drop()
        db.commit()
        db.close()


# class DALGroup(DatabaseObject):
#     def __init__(self, id=None, name=None, config=None, order=None):
#         super().__init__(id=id)
#         self._name = name
#         self._config = config
#         self._order = order
#
#     @staticmethod
#     def get_table():
#         db = get_database()
#         if 'page_groups' in db:
#             table = db.page_groups
#         else:
#             table = db.define_table(
#                 'page_groups',
#                 Field('name', type='string', default='', unique=True),
#                 Field('config', type='string', default='{}'),
#                 Field('order', type='integer', default=0),
#             )
#         return db, table
#
#     @classmethod
#     def add(cls, name, config=None, order=None):
#         """
#         Add a group
#         """
#         # check if it already exists
#         db, table = cls.get_table()
#         entry = table(name=name)
#         if entry is None:
#             id = table.insert(name=name, config=json.dumps(config or {}), order=order)
#             db.close()
#             # FIXME error checking
#             obj = cls.get(id=id)
#             logger.debug('added group')
#             Event.fire('group_added', {'group': object}, 'Group')
#         else:
#             obj = cls(**entry.as_dict())
#         return obj
#
#
#     @property
#     def name(self):
#         self._name = self.get_property('name')
#         return self._name
#
#     @property
#     def path(self):
#         return '/{}'.format(self.name)
#
#     @property
#     def config(self):
#         self._config = json.loads(self.get_property('config'))
#         return self._config
#
#     @property
#     def order(self):
#         self._order = self.get_property('order') or 0
#         return self._order
#
#     @property
#     def pages(self):
#         return sorted([page for page in Page.all() if page.group.id == self.id], key=lambda x: x.order)
#
#     def get_page(self, name):
#         pages = [page for page in Page.all() if page.group.id == self.id and page.name == name]
#         if len(pages) == 1:
#             return pages[0]
#         return None
#
#     def add_page(self, name, config=None, order=None):
#         return Page.add(name, self, config=config, order=order)
#
#     def serialize(self):
#         return {
#             'id': self.id,
#             'path': self.path,
#             'config': self.config,
#             'pages': [page.id for page in self.pages]
#         }
#
#
# class DALPage(DatabaseObject):
#     def __init__(self, id=None, name=None, group=None, config=None, order=None):
#         super().__init__(id=id)
#         self._name = name
#         self._group = group
#         self._config = config
#         self._order = order
#
#     @staticmethod
#     def get_table():
#         db = get_database()
#         if 'pages' in db:
#             table = db.pages
#         else:
#             table = db.define_table(
#                 'pages',
#                 Field('name', type='string', default=''),
#                 Field('group', type='integer'),
#                 Field('config', type='string', default='{}'),
#                 Field('order', type='integer', default=0),
#             )
#         return db, table
#
#     @classmethod
#     def add(cls, name, group, config=None, order=None):
#         """
#         Add a state to the database
#         """
#         # check if it already exists
#         db, table = cls.get_table()
#
#         if isinstance(group, str):
#             group = Group.get(path=group)
#         elif isinstance(group, int):
#             group = Group.get(id=group)
#         elif isinstance(group, Group):
#             pass
#         else:
#             raise Exception('invalid group specifier {}, provide a group, path or id'.format(group))
#
#         entry = table(name=name, group=group.id)
#         if entry is None:
#             id = table.insert(name=name, group=group.id, config=json.dumps(config or {}), order=order)
#             db.close()
#             # FIXME error checking
#             obj = cls.get(id=id)
#             logger.debug('added page')
#             Event.fire('page_added', {'page': obj}, 'Page')
#         else:
#             obj = cls(**entry.as_dict())
#         return obj
#
#     @classmethod
#     def get(cls, path=None, id=None):
#         db, table = cls.get_table()
#         if id is not None:
#             db_entry = table(id)
#             db.close()
#         elif path is not None:
#             parts = path.split('/')
#             group = Group.get(path='/'.join(parts[:-1]))
#             db_entry = table(name=parts[-1], group=group.id)
#             db.close()
#         else:
#             logger.error("id or path must be supplied")
#             return None
#         if db_entry is not None:
#             return cls(**db_entry.as_dict())
#         else:
#             return None
#
#     @property
#     def name(self):
#         self._name = self.get_property('name')
#         return self._name
#
#     @property
#     def path(self):
#         return '{}/{}'.format(self.group.path, self.name)
#
#     @property
#     def group(self):
#         self._group = self.get_property('group')
#         return Group.get(id=self._group)
#
#     @property
#     def config(self):
#         self._config = json.loads(self.get_property('config'))
#         return self._config
#
#     @property
#     def order(self):
#         self._order = self.get_property('order') or 0
#         return self._order
#
#     @property
#     def sections(self):
#         return sorted([section for section in Section.all() if section.page.id == self.id], key=lambda x: x.order)
#
#     def get_section(self, name):
#         objs = [obj for obj in Page.all() if obj.page.id == self.id and obj.name == name]
#         if len(objs) == 1:
#             return objs[0]
#         return None
#
#     def add_section(self, name, config=None, order=None):
#         return Section.add(name, self, config=config, order=order)
#
#     def serialize(self):
#         return {
#             'id': self.id,
#             'path': self.path,
#             'config': self.config,
#             'sections': [section.id for section in self.sections]
#         }
#
#
# class DALSection(DatabaseObject):
#     def __init__(self, id=None, name=None, page=None, config=None, order=None):
#         super().__init__(id=id)
#         self._name = name
#         self._page = page
#         self._config = config
#         self._order = order
#
#     @staticmethod
#     def get_table():
#         db = get_database()
#         if 'sections' in db:
#             table = db.sections
#         else:
#             table = db.define_table(
#                 'sections',
#                 Field('name', type='string', default=''),
#                 Field('page', type='integer'),
#                 Field('config', type='string', default='{}'),
#                 Field('order', type='integer', default=0),
#             )
#         return db, table
#
#     @classmethod
#     def add(cls, name, page, config=None, order=None):
#         """
#         Add a state to the database
#         """
#         # check if it already exists
#         db, table = cls.get_table()
#         entry = table(name=name, page=page.id)
#         if entry is None:
#             id = table.insert(name=name, page=page.id, config=json.dumps(config or {}), order=order)
#             db.close()
#             # FIXME error checking
#             obj = cls.get(id=id)
#             logger.debug('added section')
#             Event.fire('section_added', {'section': obj}, 'Section')
#         else:
#             obj = cls(**entry.as_dict())
#         return obj
#
#     @classmethod
#     def get(cls, path=None, id=None):
#         db, table = cls.get_table()
#         if id is not None:
#             db_entry = table(id)
#             db.close()
#         elif path is not None:
#             parts = path.split('/')
#             page = Page.get(path='/'.join(parts[:-1]))
#             db_entry = table(name=parts[-1], page=page.id)
#             db.close()
#         else:
#             logger.error("id or path must be supplied")
#             return None
#         if db_entry is not None:
#             return cls(**db_entry.as_dict())
#         else:
#             return None
#
#     @property
#     def name(self):
#         self._name = self.get_property('name')
#         return self._name
#
#     @property
#     def path(self):
#         return '{}/{}'.format(self.page.path, self.name)
#
#     @property
#     def page(self):
#         self._page = self.get_property('page')
#         return Page.get(id=self._page)
#
#     @property
#     def config(self):
#         self._config = json.loads(self.get_property('config'))
#         return self._config
#
#     @property
#     def order(self):
#         self._order = self.get_property('order') or 0
#         return self._order
#
#     @property
#     def widgets(self):
#         return sorted([widget for widget in Widget.all() if widget.section.id == self.id], key=lambda x: x.order)
#
#     def get_widget(self, path):
#         objs = [obj for obj in Page.all() if obj.page.id == self.id and obj.path == path]
#         if len(objs) == 1:
#             return objs[0]
#         return None
#
#     def add_widget(self, name, type, config=None, order=None):
#         return Widget.add(name, self, type, config=config, order=order)
#
#     def serialize(self):
#         return {
#             'id': self.id,
#             'path': self.path,
#             'config': self.config,
#             'widgets': [widgets.id for widgets in self.widgets]
#         }
#
#     def __repr__(self):
#         return '<{} id={} path={}>'.format(self.__class__.__name__, self.id, self.path)
#
#
# class DALWidget(DatabaseObject):
#     def __init__(self, id=None, name=None, section=None, type=None, config=None, order=None):
#         super().__init__(id=id)
#         self._name = name
#         self._section = section
#         self._type = type
#         self._config = config
#         self._order = order
#
#     @staticmethod
#     def get_table():
#         db = get_database()
#         if 'widgets' in db:
#             table = db.widgets
#         else:
#             table = db.define_table(
#                 'widgets',
#                 Field('name', type='string', default=''),
#                 Field('section', type='integer'),
#                 Field('type', type='string'),
#                 Field('config', type='string', default='{}'),
#                 Field('order', type='integer', default=0),
#             )
#         return db, table
#
#     @classmethod
#     def add(cls, name, section, type, config=None, order=None):
#         """
#         Add a state to the database
#         """
#         # check if it already exists
#         if name is None:
#             name = uuid4()
#         db, table = cls.get_table()
#         entry = table(name=name, section=section.id)
#         if entry is None:
#             id = table.insert(name=name, section=section.id, type=type, config=json.dumps(config or {}), order=order)
#             db.close()
#             # FIXME error checking
#             obj = cls.get(id=id)
#             logger.debug('added widget')
#             Event.fire('widget_added', {'widget': obj}, 'Widget')
#         else:
#             obj = cls(**entry.as_dict())
#         return obj
#
#     @classmethod
#     def get(cls, path=None, id=None):
#         db, table = cls.get_table()
#         if id is not None:
#             db_entry = table(id)
#             db.close()
#         elif path is not None:
#             parts = path.split('/')
#             section = Section.get(path='/'.join(parts[:-1]))
#             db_entry = table(name=parts[-1], section=section.id)
#             db.close()
#         else:
#             logger.error("id or path must be supplied")
#             return None
#         if db_entry is not None:
#             return cls(**db_entry.as_dict())
#         else:
#             return None
#
#     @property
#     def name(self):
#         self._name = self.get_property('name')
#         return self._name
#
#     @property
#     def path(self):
#         return '{}/{}'.format(self.section.path, self.name)
#
#     @property
#     def section(self):
#         self._section = self.get_property('section')
#         return Section.get(id=self._section)
#
#     @property
#     def config(self):
#         self._config = json.loads(self.get_property('config'))
#         return self._config
#
#     @property
#     def order(self):
#         self._order = self.get_property('order') or 0
#         return self._order
#
#     @property
#     def type(self):
#         self._type = self.get_property('type')
#         return self._type
#
#     def serialize(self):
#         return {
#             'id': self.id,
#             'path': self.path,
#             'type': self.type,
#             'config': self.config,
#         }
#
#     def __repr__(self):
#         return '<{} id={} path={}>'.format(self.__class__.__name__, self.id, self.path)
#


class Pages(BasePlugin):
    """
    Notes
    -----
    A homecon app is structured using groups, pages, sections and widgets

    """
    def __init__(self, *args, now=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_update_timestamp = now or time.time()

    def start(self):
        # set defaults
        if len(self._pages_manager.all_groups()) == 0 and len(self._pages_manager.all_pages()) == 0 and \
                len(self._pages_manager.all_sections()) == 0 and len(self._pages_manager.all_widgets()) == 0:
            g0 = self._pages_manager.add_group('home', config={'title': 'Home'})
            g1 = self._pages_manager.add_group('central', config={'title': 'Central'})
            g2 = self._pages_manager.add_group('ground_floor', config={'title': 'Ground floor'})
            g3 = self._pages_manager.add_group('first_floor', config={'title': 'First floor'})

            p0 = self._pages_manager.add_page('home', g0, config={'title': 'Home', 'icon': 'blank'})
            p1 = self._pages_manager.add_page('heating', g1, config={'title': 'Heating', 'icon': 'sani_heating'})
            p2 = self._pages_manager.add_page('kitchen', g2, config={'title': 'Kitchen', 'icon': 'scene_dinner'})
            p3 = self._pages_manager.add_page('bathroom', g3, config={'title': 'Bathroom', 'icon': 'scene_bath'})
            p4 = self._pages_manager.add_page('master_bedroom', g3, config={'title': 'Master Bedroom', 'icon': 'scene_sleeping'})

            s0 = self._pages_manager.add_section('time', p0, config={'type': 'underlined'})
            self._pages_manager.add_widget('w0', s0, 'clock', config={})
            self._pages_manager.add_widget('w1', s0, 'date', config={})

            s1 = self._pages_manager.add_section('weather', p0, config={'type': 'underlined'})
            self._pages_manager.add_widget('w0', s1, 'weather-block', config={'daily': True, 'timeoffset': 0})
            self._pages_manager.add_widget('w1', s1, 'weather-block', config={'daily': True, 'timeoffset': 24})
            self._pages_manager.add_widget('w2', s1, 'weather-block', config={'daily': True, 'timeoffset': 48})
            self._pages_manager.add_widget('w3', s1, 'weather-block', config={'daily': True, 'timeoffset': 72})

            s2 = self._pages_manager.add_section('lights', p2, config={'type': 'raised', 'title': 'Lights'})
            self._pages_manager.add_widget('w0', s2, 'switch', config={'icon': 'light_light', 'state': 10})

            # s3 = Section.add('shading', p2, config={'type': 'collapsible', 'title': 'Shading'})
            # Widget.add('w0', s3, 'shading')

        logger.debug('Pages plugin initialized')

    def get_menu(self):
        """
        Return the data required to make the menu
        """
        menu = []
        groups = self._pages_manager.all_groups()
        for group in sorted(groups, key=lambda x: group.order):
            if not group.path == 'home':
                menu.append({
                    'path': group.path,
                    'config': group.config,
                    'pages': [{'id': page.id, 'path': page.path, 'config': page.config} for page in group.pages]
                })
        return menu

    def listen_pages_timestamp(self, event):
        # FIXME check permissions
        event.reply({'id': event.data['id'], 'value': self._last_update_timestamp})

    def listen_pages_pages(self, event):
        # FIXME check permissions
        d = self._pages_manager.serialize(self._state_manager)
        event.reply({'id': event.data['id'], 'value': {'timestamp': self._last_update_timestamp, 'groups': d}})

    def listen_pages_export(self, event):
        # FIXME check permissions
        d = self._pages_manager.serialize(self._state_manager, convert_state_ids_to_paths=True)
        event.reply({'id': event.data['id'], 'value': d})

    def listen_pages_import(self, event):
        # FIXME check permissions
        if 'value' in event.data:
            self.import_pages(event.data['value'])
            # FIXME send pages to all connected clients this should be independent of the websocket plugin.
            #  so there should be a IIOManager in core which is accessible through the plugins
            d = self._pages_manager.serialize(self._state_manager)
            self.fire('websocket_send', data={'timestamp': self._last_update_timestamp, 'groups': d})

    def import_pages(self, groups: dict):
        self._pages_manager.clear()
        self._pages_manager.deserialize(groups)
        self._last_update_timestamp = time.time()

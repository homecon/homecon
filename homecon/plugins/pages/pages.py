#!/usr/bin/env python3

import logging
import json
import time

from pydal import DAL, Field

from homecon.core.event import Event
from homecon.core.pages.pages import Group, Page, Section, Widget, IPagesManager, MemoryObjectManager, MemoryPagesManager
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

    def delete(self, obj):
        self._db(self._table.id == obj.id).delete()
        try:
            self._db.commit()
        except Exception:
            logger.exception('could not store state')
        else:
            super().delete(obj)

    def clear(self):
        self._table.drop()
        self._db.commit()


class DALGroupManager(DALObjectManager):
    def row_to_obj(self, row):
        id = row.pop('id')
        name = row.pop('name')
        return self._object_factory(self._pages_manager, id, name, **row)

    def add(self, name: str, **kwargs):
        try:
            # noinspection PyProtectedMember
            self._db._adapter.reconnect()
            id_ = self._table.insert(name=name, **kwargs)
            self._db.commit()
            # noinspection PyProtectedMember
            self._db._adapter.close()
        except Exception:
            logger.exception('could not store group')
        else:
            super().add(name, id=id_, **kwargs)


class DALPageManager(DALObjectManager):
    def row_to_obj(self, row):
        id = row.pop('id')
        name = row.pop('name')
        group = self._pages_manager.get_group(id=row.pop('group'))
        return self._object_factory(self, id, name, group, **row)

    def add(self, name: str, *args, **kwargs):
        try:
            # noinspection PyProtectedMember
            self._db._adapter.reconnect()
            id_ = self._table.insert(name=name, **kwargs)
            self._db.commit()
            # noinspection PyProtectedMember
            self._db._adapter.close()
        except Exception:
            logger.exception('could not store state')
        else:
            super().add(name, id=id_, *args, **kwargs)


class DALSectionManager(DALObjectManager):
    def row_to_obj(self, row):
        id = row.pop('id')
        name = row.pop('name')
        page = self._pages_manager.get_page(id=row.pop('page'))
        return self._object_factory(self, id, name, page, **row)


class DALWidgetManager(DALObjectManager):
    def row_to_obj(self, row):
        id = row.pop('id')
        name = row.pop('name')
        section = self._pages_manager.get_section(id=row.pop('section'))
        return self._object_factory(self, id, name, section, **row)


class DALPagesManager(MemoryPagesManager):
    def __init__(self, folder: str, uri: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._db = DAL(uri, folder=folder)
        self._groups_table = self._db.define_table(
            'pages_groups',
            Field('name', type='string', default='', unique=True),
            Field('config', type='string', default='{}'),
            Field('order', type='integer', default=0),
        )
        self._pages_table = self._db.define_table(
            'pages_pages',
            Field('name', type='string', default='', unique=True),
            Field('group', type='int'),
            Field('config', type='string', default='{}'),
            Field('order', type='integer', default=0),
        )
        self._sections_table = self._db.define_table(
            'pages_sections',
            Field('name', type='string', default='', unique=True),
            Field('page', type='int'),
            Field('config', type='string', default='{}'),
            Field('order', type='integer', default=0),
        )
        self._widgets_table = self._db.define_table(
            'pages_widget',
            Field('name', type='string', default='', unique=True),
            Field('section', type='int'),
            Field('config', type='string', default='{}'),
            Field('order', type='integer', default=0),
        )

        self._groups_manager = DALGroupManager(self, Group, self._db, self._groups_table)
        self._pages_manager = DALPageManager(self, Page, self._db, self._pages_table)
        self._sections_manager = DALSectionManager(self, Section, self._db, self._sections_table)
        self._widgets_manager = DALWidgetManager(self, Widget, self._db, self._widgets_table)

    def clear(self):
        self._groups_manager.clear()
        self._pages_manager.clear()
        self._sections_manager.clear()
        self._widgets_manager.clear()


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

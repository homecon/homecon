from copy import deepcopy
from typing import List, Any
from uuid import uuid4

from homecon.core.states.state import config_state_paths_to_ids, IStateManager, config_state_ids_to_paths


class Group:
    def __init__(self, pages_manager: 'IPagesManager', _id: int, name: str, config: dict = None, order: int = None):
        self._pages_manager = pages_manager
        self._id = _id
        self._name = name
        self._config = config or {}
        self._order = order or 0

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return f'/{self.name}'

    @property
    def config(self):
        return self._config

    @property
    def order(self):
        return self._order

    @property
    def pages(self) -> List['Page']:
        return [p for p in self._pages_manager.all_pages() if p.group == self]

    def serialize(self):
        return {
            'id': self.id,
            'path': self.path,
            'config': self.config,
            'order': self.order,
            'pages': [page.id for page in self.pages]
        }


class Page:
    def __init__(self, pages_manager: 'IPagesManager', _id: int, name: str, group: Group, config: dict = None, order: int = None):
        self._pages_manager = pages_manager
        self._id = _id
        self._name = name
        self._group = group
        self._config = config or {}
        self._order = order or 0

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def group(self):
        return self._group

    @property
    def path(self):
        return f'{self.group.path}/{self.name}'

    @property
    def config(self):
        return self._config

    @property
    def order(self):
        return self._order

    @property
    def sections(self) -> List['Section']:
        return [p for p in self._pages_manager.all_sections() if p.page == self]

    def serialize(self):
        return {
            'id': self.id,
            'path': self.path,
            'config': self.config,
            'order': self.order,
            'sections': [section.id for section in self.sections]
        }


class Section:
    def __init__(self, pages_manager: 'IPagesManager', _id: int, name: str, page: Page, config: dict = None, order: int = None):
        self._pages_manager = pages_manager
        self._id = _id
        self._name = name
        self._page = page
        self._config = config or {}
        self._order = order or 0

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def page(self):
        return self._page

    @property
    def path(self):
        return f'{self.page.path}/{self.name}'

    @property
    def config(self):
        return self._config

    @property
    def order(self):
        return self._order

    @property
    def widgets(self) -> List['Widget']:
        return [p for p in self._pages_manager.all_widgets() if p.section == self]

    def serialize(self):
        return {
            'id': self.id,
            'path': self.path,
            'config': self.config,
            'order': self.order,
            'widgets': [widget.id for widget in self.widgets]
        }


class Widget:
    def __init__(self, pages_manager: 'IPagesManager', _id: int, name: str, section: Section, _type: str, config: dict = None, order: int = None):
        self._pages_manager = pages_manager
        self._id = _id
        self._name = name
        self._section = section
        self._type = _type
        self._config = config or {}
        self._order = order or 0

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def section(self):
        return self._section

    @property
    def type(self):
        return self._type

    @property
    def path(self):
        return f'{self.section.path}/{self.name}'

    @property
    def config(self):
        return self._config

    @property
    def order(self):
        return self._order

    def serialize(self):
        return {
            'id': self._id,
            'path': self.path,
            'type': self.type,
            'config': self._config,
        }


class IPagesManager:

    def all_groups(self) -> List[Group]:
        raise NotImplementedError

    def add_group(self, name: str, config: dict = None, order: int = None) -> Group:
        raise NotImplementedError

    # noinspection PyShadowingBuiltins
    def get_group(self, path: str = None, id: int = None) -> Group:
        raise NotImplementedError

    def update_group(self, group: Group):
        raise NotImplementedError

    def delete_group(self, group: Group):
        pass

    def all_pages(self) -> List[Page]:
        raise NotImplementedError

    def add_page(self, name: str, group: Group, config: dict = None, order: int = None) -> Page:
        raise NotImplementedError

    # noinspection PyShadowingBuiltins
    def get_page(self, path: str = None, id: int = None) -> Page:
        raise NotImplementedError

    def update_page(self, page: Page):
        raise NotImplementedError

    def delete_page(self, page: Page):
        pass

    def all_sections(self) -> List[Section]:
        raise NotImplementedError

    def add_section(self, name: str, page: Page, config: dict = None, order: int = None) -> Section:
        raise NotImplementedError

    # noinspection PyShadowingBuiltins
    def get_section(self, path: str = None, id: int = None) -> Section:
        raise NotImplementedError

    def update_section(self, section: Section):
        raise NotImplementedError

    def delete_section(self, section: Section):
        pass

    def all_widgets(self) -> List[Widget]:
        raise NotImplementedError

    def add_widget(self, name: str, section: Section, _type: str, config: dict = None, order: int = None) -> Widget:
        raise NotImplementedError

    # noinspection PyShadowingBuiltins
    def get_widget(self, path: str = None, id: int = None) -> Widget:
        raise NotImplementedError

    def update_widget(self, widget: Widget):
        raise NotImplementedError

    def delete_widget(self, widget: Widget):
        pass

    def clear(self):
        raise NotImplementedError

    def deserialize(self, groups: dict, state_manager):
        """
        Reads a list of groups and adds states from it.
        """
        groups = deepcopy(groups)
        for group in groups:
            group.pop('id', None)
            name = group.pop('name', str(uuid4()))
            pages = group.pop('pages', [])
            config_state_paths_to_ids(group.get('config', {}).get('widget', {}).get('config'), state_manager)
            g = self.add_group(name, **group)
            for page in pages:
                page.pop('id', None)
                name = page.pop('name', str(uuid4()))
                sections = page.pop('sections', [])
                config_state_paths_to_ids(page.get('config', {}).get('widget', {}).get('config'), state_manager)
                p = self.add_page(name, g, **page)
                for section in sections:
                    section.pop('id', None)
                    name = section.pop('name', str(uuid4()))
                    widgets = section.pop('widgets', [])
                    config_state_paths_to_ids(section.get('config', {}).get('widget', {}).get('config'), state_manager)
                    s = self.add_section(name, p, **section)
                    for widget in widgets:
                        widget.pop('id', None)
                        name = widget.pop('name', str(uuid4()))
                        _type = widget.pop('type', None)
                        config_state_paths_to_ids(widget.get('config'), state_manager)
                        self.add_widget(name, s, _type, **widget)

    def serialize(self, state_manager: IStateManager, convert_state_ids_to_paths=False):
        d = []
        for group in self.all_groups():
            g = {
                'id': group.id,
                'name': group.name,
                'path': group.path,
                'config': group.config,
                'pages': []
            }
            for page in group.pages:
                p = {
                    'id': page.id,
                    'name': page.name,
                    'path': page.path,
                    'config': page.config,
                    'sections': []
                }
                for section in page.sections:
                    s = {
                        'id': section.id,
                        'name': section.name,
                        'path': section.path,
                        'config': section.config,
                        'widgets': []
                    }
                    for widget in section.widgets:
                        config = deepcopy(widget.config)
                        if convert_state_ids_to_paths:
                            config_state_ids_to_paths(config, state_manager)
                        w = {
                            'id': widget.id,
                            'name': widget.name,
                            'path': widget.path,
                            'type': widget.type,
                            'config': config,
                        }
                        s['widgets'].append(w)
                    p['sections'].append(s)
                g['pages'].append(p)
            d.append(g)
        return d


class MemoryObjectManager:
    def __init__(self, pages_manager,  object_factory: callable):
        self._pages_manager = pages_manager
        self._object_factory = object_factory
        self._objects = {}

    def all(self):
        return list(self._objects.values())

    # noinspection PyShadowingBuiltins
    def get(self, path: str = None, id: int = None) -> Any:
        if id is not None:
            return self._objects.get(id)
        else:
            for obj in self._objects.values():
                if obj.path == path:
                    return obj

    def exists(self, name, *args, **kwargs):
        temp = self._object_factory(self._pages_manager, 0, name, *args, **kwargs)
        path = temp.path
        obj = self.get(path=path)
        return obj or False

    def get_new_id(self):
        id_ = 0
        if len(self._objects) > 0:
            id_ = max(self._objects.keys()) + 1
        return id_

    def add(self, name: str, *args, **kwargs):
        obj = self.exists(name, *args, **kwargs)
        if obj:
            return obj
        else:
            id_ = self.get_new_id()
            obj = self._object_factory(self._pages_manager, id_, name, *args, **kwargs)
            self._objects[obj.id] = obj
            return obj

    def delete(self, obj):
        del self._objects[obj.id]

    def update(self, obj):
        pass

    def clear(self):
        self._objects = {}


class MemoryPagesManager(IPagesManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._groups_manager = MemoryObjectManager(self, Group)
        self._pages_manager = MemoryObjectManager(self, Page)
        self._sections_manager = MemoryObjectManager(self, Section)
        self._widgets_manager = MemoryObjectManager(self, Widget)

    def all_groups(self) -> List[Group]:
        return self._groups_manager.all()

    # noinspection PyShadowingBuiltins
    def get_group(self, path: str = None, id: int = None) -> Group:
        return self._groups_manager.get(path=path, id=id)

    def add_group(self, name: str, **kwargs) -> Group:
        return self._groups_manager.add(name, **kwargs)

    def delete_group(self, group):
        return self._groups_manager.delete(group)

    def update_group(self, group):
        return self._groups_manager.update(group)

    def all_pages(self) -> List[Page]:
        return self._pages_manager.all()

    # noinspection PyShadowingBuiltins
    def get_page(self, path: str = None, id: int = None) -> Page:
        return self._pages_manager.get(path=path, id=id)

    def add_page(self, name: str, group: Group, **kwargs) -> Page:
        return self._pages_manager.add(name, group, **kwargs)

    def delete_page(self, page):
        return self._pages_manager.delete(page)

    def update_page(self, page):
        return self._sections_manager.update(page)

    def all_sections(self) -> List[Section]:
        return self._sections_manager.all()

    # noinspection PyShadowingBuiltins
    def get_section(self, path: str = None, id: int = None) -> Section:
        return self._sections_manager.get(path=path, id=id)

    def add_section(self, name: str, page: Page, **kwargs) -> Section:
        return self._sections_manager.add(name, page, **kwargs)

    def delete_section(self, section):
        return self._sections_manager.delete(section)

    def update_section(self, section):
        return self._sections_manager.update(section)

    def all_widgets(self) -> List[Widget]:
        return self._widgets_manager.all()

    # noinspection PyShadowingBuiltins
    def get_widget(self, path: str = None, id: int = None) -> Widget:
        return self._widgets_manager.get(path=path, id=id)

    def add_widget(self, name: str, section: Section, _type: str, **kwargs) -> Widget:
        return self._widgets_manager.add(name, section, _type, **kwargs)

    def delete_widget(self, widget):
        return self._widgets_manager.delete(widget)

    def update_widget(self, widget):
        return self._widgets_manager.update(widget)

    def clear(self):
        self._groups_manager.clear()
        self._pages_manager.clear()
        self._sections_manager.clear()
        self._widgets_manager.clear()

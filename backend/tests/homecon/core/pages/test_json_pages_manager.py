import os
import shutil

from unittest import TestCase

from homecon.core.pages.pages import JSONPagesManager
from homecon.core.event import IEventManager


class DummyEventManager(IEventManager):
    def fire(self, type_: str, data: dict, source: str = None, target: str = None, reply_to: str = None):
        pass

    def get(self):
        pass


class TestJSONPagesManager(TestCase):
    DIR = 'db'
    NAME = 'test.json'

    def setUp(self):
        try:
            shutil.rmtree(self.DIR)
        except FileNotFoundError:
            pass
        os.mkdir(self.DIR)

    def tearDown(self):
        try:
            shutil.rmtree(self.DIR)
        except FileNotFoundError:
            pass

    def test_add(self):
        manager = JSONPagesManager(os.path.join(self.DIR, self.NAME))
        g = manager.add_group('group')
        p = manager.add_page('page', g)
        s = manager.add_section('section', p)
        manager.add_widget('widget', s, 'test')

        w = manager.get_widget(path='/group/page/section/widget')
        assert w.name == 'widget'

    def test_load(self):
        manager = JSONPagesManager(os.path.join(self.DIR, self.NAME))
        g = manager.add_group('group')
        p = manager.add_page('page', g)
        s = manager.add_section('section', p)
        manager.add_widget('widget', s, 'test')

        w = manager.get_widget(path='/group/page/section/widget')
        assert w.name == 'widget'

        manager2 = JSONPagesManager(os.path.join(self.DIR, self.NAME))
        w = manager2.get_widget(path='/group/page/section/widget')
        assert w.name == 'widget'

    def test_delete_page(self):
        manager = JSONPagesManager(os.path.join(self.DIR, self.NAME))
        g = manager.add_group('group')
        p = manager.add_page('page', g)
        s = manager.add_section('section', p)
        manager.add_widget('widget', s, 'test')

        w = manager.get_widget(path='/group/page/section/widget')
        assert w.name == 'widget'

        manager.delete_page(p)

        w = manager.get_widget(path='/group/page/section/widget')
        assert w is None

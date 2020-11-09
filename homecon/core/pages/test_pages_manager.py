from unittest import TestCase
from homecon.core.pages.pages import MemoryPagesManager


class TestMemoryPagesManager(TestCase):

    def test_add(self):
        manager = MemoryPagesManager()
        g = manager.add_group('group')
        p = manager.add_page('page', g)
        s = manager.add_section('section', p)
        manager.add_widget('widget', s, 'test')

        w = manager.get_widget(path='/group/page/section/widget')
        assert w.name == 'widget'

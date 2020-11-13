from unittest import TestCase
from homecon.core.pages.pages import MemoryPagesManager
from homecon.core.states.state import MemoryStateManager
from homecon.core.event import IEventManager


class DummyEventManager(IEventManager):
    def fire(self, type_: str, data: dict, source: str = None, target: str = None, reply_to: str = None):
        pass

    def get(self):
        pass


class TestMemoryPagesManager(TestCase):

    def test_add(self):
        manager = MemoryPagesManager()
        g = manager.add_group('group')
        p = manager.add_page('page', g)
        s = manager.add_section('section', p)
        manager.add_widget('widget', s, 'test')

        w = manager.get_widget(path='/group/page/section/widget')
        assert w.name == 'widget'

    def test_serialize(self):
        manager = MemoryPagesManager()
        g = manager.add_group('group')
        p = manager.add_page('page', g)
        s = manager.add_section('section', p)
        manager.add_widget('widget', s, 'test', config={'state': 1})

        state_manager = MemoryStateManager(DummyEventManager())
        serialized = manager.serialize(state_manager)
        assert isinstance(serialized, list)

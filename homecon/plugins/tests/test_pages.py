
from homecon.tests import common
from homecon.plugins.pages import Group, Page, Section, Widget


class TestObjects(common.TestCase):
    def test_add_group(self):
        g = Group.add('central', config={'Title': 'Central'})
        self.assertEqual(g.path, 'central')

    def test_full_path(self):
        g = Group.add('group', config={'Title': 'Some group'})
        p = Page.add('page', g, config={'Title': 'Some page'})
        s = Section.add('section', p, config={'Title': 'Some section'})
        w = Widget.add('widget', s, 'sometype', config={'Title': 'Some widget'})
        self.assertEqual(w.full_path, 'group/page/section/widget')

    def test_group_pages(self):
        g = Group.add('group', config={'Title': 'Some group'})
        p1 = Page.add('page1', g, config={'Title': 'Page1'})
        p2 = Page.add('page2', g, config={'Title': 'Page2'})
        self.assertEqual(len(g.pages), 2)

    def test_page_from_full_path(self):
        g = Group.add('group', config={'Title': 'Some group'})
        p1 = Page.add('page1', g, config={'Title': 'Page1'})
        p = Page.get(full_path='group/page1')
        self.assertEqual(p.id, p1.id)

    def test_page_sections(self):
        g = Group.add('group', config={'Title': 'Some group'})
        p = Page.add('page', g, config={'Title': 'Some page'})
        s1 = Section.add('section1', p, config={'Title': 'Some section'})
        s2 = Section.add('section2', p, config={'Title': 'Some section'})
        self.assertEqual(len(p.sections), 2)

    def test_section_widgets(self):
        g = Group.add('group', config={'Title': 'Some group'})
        p = Page.add('page', g, config={'Title': 'Some page'})
        s = Section.add('section', p, config={'Title': 'Some section'})
        w1 = Widget.add('widget1', s, 'sometype', config={})
        w2 = Widget.add('widget2', s, 'sometype', config={})
        self.assertEqual(len(s.widgets), 2)

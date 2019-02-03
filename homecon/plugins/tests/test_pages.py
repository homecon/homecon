import json

from homecon.tests import common
from homecon.plugins.pages import Group, Page, Section, Widget, Pages


class TestObjects(common.TestCase):
    def test_add_group(self):
        g = Group.add('central', config={'Title': 'Central'})
        self.assertEqual(g.path, '/central')

    def test_path(self):
        g = Group.add('group', config={'Title': 'Some group'})
        p = Page.add('page', g, config={'Title': 'Some page'})
        s = Section.add('section', p, config={'Title': 'Some section'})
        w = Widget.add('widget', s, 'sometype', config={'Title': 'Some widget'})
        self.assertEqual(w.path, '/group/page/section/widget')

    def test_group_pages(self):
        g = Group.add('group', config={'Title': 'Some group'})
        p1 = Page.add('page1', g, config={'Title': 'Page1'})
        p2 = Page.add('page2', g, config={'Title': 'Page2'})
        self.assertEqual(len(g.pages), 2)

    def test_group_from_path(self):
        g = Group.add('group', config={'Title': 'Some group'})
        g1 = Group.get(path='/group')
        self.assertEqual(g, g1)

    def test_page_from_path(self):
        g = Group.add('group', config={'Title': 'Some group'})
        p1 = Page.add('page1', g, config={'Title': 'Page1'})
        p = Page.get(path='/group/page1')
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


class TestPlugin(common.TestCase):

    def test_from_json(self):
        p = Pages()
        string = json.dumps([{
            'name': 'group1',
            'pages': [{
                'name': 'page1',
                'sections': [{
                    'config': {
                        'title': 'test'
                    },
                    'widgets': [{
                        'type': 'button',
                        'config': {
                            'state': 1
                        }
                    }]
                }]
            }]
        }], indent=4)
        p.from_json(string)
        page = Page.get(path='/group1/page1')
        self.assertEqual(page.sections[0].widgets[0].type, 'button')

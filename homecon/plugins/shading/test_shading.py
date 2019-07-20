
from homecon.tests import common
from homecon.core.state import State
from homecon.core.event import Event
from homecon.plugins.shading import Shading


class TestShading(common.TestCase):

    def test_listen_add_shading(self):
        plugin = Shading()
        s = State.add('my_shading', parent=None, type='screen')
        plugin.listen_state_added(Event('state_added', data={'state': s}))
        states = State.all()

        assert len(states) == 6
        for i in range(1, len(states)):
            assert states[i].config['shading'] == states[0].id

    def test_get_position_state(self):
        plugin = Shading()
        s = State.add('my_shading', parent=None, type='screen')
        plugin.listen_state_added(Event('state_added', data={'state': s}))
        p = plugin.get_position_state(s)
        assert p.name == 'position'

    def test_auto_position(self):
        plugin = Shading()
        z1 = State.add('zone1', parent=None, type='zone')

        w1 = State.add('window1', parent=z1, type='window', config={'zone': z1.id, 'area': 4.2,
                                                                    'orientation': 180, 'tilt': 90,
                                                                    'transmittance': 0.5})
        w1s1 = State.add('shading1', parent=w1, type='screen', config={'window': w1.id,
                                                                       'transmittance_open': 1,
                                                                       'transmittance_closed': 0.3,
                                                                       'position_open': 0,
                                                                       'position_closed': 255})
        plugin.listen_state_added(Event('state_added', data={'state': w1s1}))

        w2 = State.add('window2', parent=z1, type='window', config={'zone': z1.id})
        w2s1 = State.add('shading1', parent=w1, type='screen', config={'window': w2.id})
        plugin.listen_state_added(Event('state_added', data={'state': w2s1}))

        print(State.all())
        plugin.auto_position(force_recalculate=True)

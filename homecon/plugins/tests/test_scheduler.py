from unittest.mock import patch

import time

from homecon.tests import common
from homecon.core.event import Event, queue
from homecon.core.state import State
from homecon.plugins.scheduler import Scheduler


@patch('homecon.plugins.scheduler.Scheduler.timezone', new='Europe/Brussels')
class TestScheduler(common.TestCase):
    def test_add_job(self):
        plugin = Scheduler()
        plugin.start()
        time.sleep(0.1)

        plugin.initialize()
        s = State.add('test', parent='/scheduler', type='dict', value={'action': [], 'trigger': {'minute': '15'}})
        plugin.listen_state_value_changed(Event('state_value_changed', {'state': s}))
        jobs = plugin.scheduler.get_jobs()
        plugin.stop()
        plugin.join()

        assert len(jobs) == 1
        assert str(jobs[0].trigger.fields[6]) == '15'
        assert str(jobs[0].trigger.timezone) == 'Europe/Brussels'

    def test_update_job(self):
        plugin = Scheduler()
        plugin.start()
        time.sleep(0.1)

        plugin.initialize()
        s = State.add('test', parent='/scheduler', type='dict', value={'action': [], 'trigger': {'minute': '15'}})
        plugin.listen_state_value_changed(Event('state_value_changed', {'state': s}))
        s.set_value({'action': [], 'trigger': {'minute': '30'}})
        plugin.listen_state_value_changed(Event('state_value_changed', {'state': s}))

        jobs = plugin.scheduler.get_jobs()
        plugin.stop()
        plugin.join()

        assert len(jobs) == 1
        assert str(jobs[0].trigger.fields[6]) == '30'
        assert str(jobs[0].trigger.timezone) == 'Europe/Brussels'

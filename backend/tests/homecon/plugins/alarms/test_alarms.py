from homecon.core.event import Event, IEventManager
from homecon.core.states.state import MemoryStateManager
from homecon.plugins.alarms.alarms import Alarms


class DummyEventManager(IEventManager):
    def fire(self, type_: str, data: dict, source: str = None, target: str = None, reply_to: str = None):
        pass

    def get(self):
        pass


class TestScheduler:
    def test_add_job(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        pages_manager = None
        plugin = Alarms('alarms', event_manager, state_manager, pages_manager, timezone='Europe/Brussels')
        plugin.start()

        s = state_manager.add('test', type='alarm', value={'action': [], 'trigger': {'minute': '15'}})
        plugin.listen_state_value_changed(Event(event_manager, 'state_value_changed', {'state': s}))
        jobs = plugin.scheduler.get_jobs()
        plugin.stop()
        plugin.join()

        assert len(jobs) == 1
        assert str(jobs[0].trigger.fields[6]) == '15'
        assert str(jobs[0].trigger.timezone) == 'Europe/Brussels'

    def test_update_job(self):
        event_manager = DummyEventManager()
        state_manager = MemoryStateManager(event_manager)
        pages_manager = None
        plugin = Alarms('alarms', event_manager, state_manager, pages_manager, timezone='Europe/Brussels')
        plugin.start()

        s = state_manager.add('test', type='alarm', value={'action': [], 'trigger': {'minute': '15'}})
        plugin.listen_state_value_changed(Event(event_manager, 'state_value_changed', {'state': s}))
        s.set_value({'action': [], 'trigger': {'minute': '30'}})
        plugin.listen_state_value_changed(Event(event_manager, 'state_value_changed', {'state': s}))

        jobs = plugin.scheduler.get_jobs()
        plugin.stop()
        plugin.join()

        assert len(jobs) == 1
        assert str(jobs[0].trigger.fields[6]) == '30'
        assert str(jobs[0].trigger.timezone) == 'Europe/Brussels'

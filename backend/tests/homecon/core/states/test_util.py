from homecon.core.states.memory_state_manager import MemoryStateManager
from homecon.core.event import EventManager
from homecon.core.states.util import config_state_paths_to_ids, config_state_ids_to_paths


class TestUtil:

    def test_config_state_paths_to_ids(self):
        state_manager = MemoryStateManager(EventManager())
        s = state_manager.add('mystate')

        config = config_state_paths_to_ids({
            'state': s.path
        }, state_manager)
        assert config['state'] == s.key

    def test_config_state_paths_to_ids_list(self):
        state_manager = MemoryStateManager(EventManager())
        s1 = state_manager.add('mystate')
        s2 = state_manager.add('myotherstate')

        config = config_state_paths_to_ids({
            'states': [s1.path, s2.path]
        }, state_manager)
        assert config['states'] == [s1.key, s2.key]

    def test_config_state_paths_to_ids_dict(self):
        state_manager = MemoryStateManager(EventManager())
        s1 = state_manager.add('mystate')
        s2 = state_manager.add('myotherstate')

        config = config_state_paths_to_ids({
            'states': {'a': s1.path, 'b': s2.path}
        }, state_manager)
        assert config['states'] == {'a': s1.key, 'b': s2.key}

    def test_config_state_ids_to_paths(self):
        state_manager = MemoryStateManager(EventManager())
        s = state_manager.add('mystate')

        config = config_state_ids_to_paths({
            'state': s.key
        }, state_manager)
        assert config['state'] == s.path

    def test_config_state_ids_to_paths_list(self):
        state_manager = MemoryStateManager(EventManager())
        s1 = state_manager.add('mystate')
        s2 = state_manager.add('myotherstate')

        config = config_state_ids_to_paths({
            'states': [s1.key, s2.key]
        }, state_manager)
        assert config['states'] == [s1.path, s2.path]

    def test_config_state_ids_to_paths_dict(self):
        state_manager = MemoryStateManager(EventManager())
        s1 = state_manager.add('mystate')
        s2 = state_manager.add('myotherstate')

        config = config_state_ids_to_paths({
            'states': {'a': s1.key, 'b': s2.key}
        }, state_manager)
        assert config['states'] == {'a': s1.path, 'b': s2.path}

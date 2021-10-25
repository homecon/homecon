import pytest

from homecon.plugins.computed.computed import ValueComputer, EvaluationError
from homecon.core.states.state import MemoryStateManager
from homecon.tests.mocks import DummyEventManager


class TestValueComputer:
    def test_value(self):
        state_manager = MemoryStateManager(DummyEventManager())
        a = state_manager.add('a', None)
        b = state_manager.add('b', parent=a, value=10)

        value_computer = ValueComputer(state_manager)
        value = value_computer.compute_value('10 * Value("/a/b")')
        assert value == 10 * b.value

    def test_values(self):
        state_manager = MemoryStateManager(DummyEventManager())
        a = state_manager.add('a', None)
        b = state_manager.add('b', parent=a, value=10)
        c = state_manager.add('c', parent=a, value=20)
        d = state_manager.add('d', parent=a, value=30)

        value_computer = ValueComputer(state_manager)
        value = value_computer.compute_value('sum(Values("/a/.*"))')
        assert value == b.value + c.value + d.value

    def test_exception(self):
        state_manager = MemoryStateManager(DummyEventManager())
        value_computer = ValueComputer(state_manager)
        with pytest.raises(EvaluationError):
            value_computer.compute_value('sum(Value("/a/.*"))')

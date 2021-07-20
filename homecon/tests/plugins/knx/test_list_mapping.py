from homecon.plugins.knx import ListMapping


class TestListMapping:

    def test_add(self):
        mapping = ListMapping()
        mapping.add('a', 0)
        mapping.add('a', 1)
        mapping.add('b', 0)
        mapping.add('b', 2)
        mapping.add('c', 3)

        assert mapping.get('a') == [0, 1]
        assert mapping.get('b') == [0, 2]
        assert mapping.get('c') == [3]
        assert mapping.get('d') == []

    def test_remove(self):
        mapping = ListMapping()
        mapping.add('a', 0)
        mapping.add('a', 1)
        mapping.add('b', 0)
        mapping.add('b', 2)
        mapping.add('c', 3)
        mapping.remove(0)

        assert mapping.get('a') == [1]
        assert mapping.get('b') == [2]
        assert mapping.get('c') == [3]
        assert mapping.get('d') == []

    def test_keys(self):
        mapping = ListMapping()
        mapping.add('a', 0)
        mapping.add('a', 1)
        mapping.add('b', 0)
        mapping.add('b', 2)
        mapping.add('c', 3)
        assert list(mapping.keys()) == ['a', 'b', 'c']

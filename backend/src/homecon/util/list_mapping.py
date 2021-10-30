class ListMapping:
    def __init__(self):
        self._map = {}

    def add(self, key, val):
        if key not in self._map:
            self._map[key] = []
        if val not in self._map[key]:
            self._map[key].append(val)

    def remove(self, val):
        for values in self._map.values():
            try:
                values.pop(values.index(val))
            except ValueError:
                pass

    def get(self, key) -> list:
        return self._map.get(key, [])

    def keys(self):
        return self._map.keys()

    def values(self):
        return self._map.values()

    def items(self):
        return self._map.items()

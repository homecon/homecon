from homecon.core.event import IEventManager


class DummyEventManager(IEventManager):
    def fire(self, type_: str, data: dict, source: str = None, target: str = None, reply_to: str = None):
        pass

    def get(self):
        pass
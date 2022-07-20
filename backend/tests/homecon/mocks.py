from homecon.core.event import IEventManager, Event


class DummyEventManager(IEventManager):
    def __init__(self):
        self.events = []

    def fire(self, type_: str, data: dict, source: str = None, target: str = None, reply_to: str = None):
        event = Event(self, type_, data, source=source, target=target, reply_to=reply_to)
        self.events.append(event)

    def get(self):
        pass

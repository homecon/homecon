import logging

from enum import Enum

from homecon.core.event import Event, IEventManager
from homecon.core.plugins.plugin import IPlugin
from homecon.core.auth import EventType as CoreAuthEventType, IAuthManager

from homecon.core.config import PASSWORD

logger = logging.getLogger(__name__)


class EventType(Enum):
    REQUEST_TOKEN = CoreAuthEventType.REQUEST_TOKEN


class Auth(IPlugin):
    def __init__(self, event_manager: IEventManager, auth_manager: IAuthManager):
        self._event_manager = event_manager
        self._auth_manager = auth_manager

    @property
    def name(self):
        return 'auth'

    def handle_event(self, event: Event):
        if event.type == EventType.REQUEST_TOKEN.value:
            self.handle_request_token(event)

    def handle_request_token(self, event: Event):
        if event.data['password'] == PASSWORD:
            allowed_event_types = [
                'state_value', 'state_list', 'state_add', 'state_update', 'states_export', 'states_import', 'state_delete',
                'add_schedule', 'delete_schedule',
                'pages_timestamp', 'pages_page', 'pages_export', 'pages_import'
            ]
            token = self._auth_manager.create_token(allowed_event_types=allowed_event_types)
            event.reply({'token': token})
            logger.info('granted token')
        else:
            logger.info('gwrong password')

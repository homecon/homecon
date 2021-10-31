#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from typing import List

import jwt
import logging

from homecon.core.config import JWT_SECRET, JWT_ALGORITHM

logger = logging.getLogger(__name__)


class EventType(Enum):
    REQUEST_TOKEN = 'request_token'


class JWTDecodeException(Exception):
    pass


class IAuthManager:
    def is_authorized(self, event_type: str, data: dict, token: str) -> bool:
        raise NotImplementedError

    def create_token(self, allowed_event_types: List[str]) -> str:
        raise NotImplementedError


class AuthManager(IAuthManager):
    ALLOWED_EVENT_TYPES = 'allowed_event_types'

    def is_authorized(self, event_type: str, data: dict, token: str) -> bool:
        if event_type == EventType.REQUEST_TOKEN.value:
            return True
        else:
            try:
                decoded_token = jwt_decode(token)
            except JWTDecodeException:
                logger.error('could not decode token')
            else:
                if event_type in decoded_token.get(self.ALLOWED_EVENT_TYPES, []):
                    return True
        return False

    def create_token(self, allowed_event_types: List[str]) -> str:
        return jwt_encode({self.ALLOWED_EVENT_TYPES: allowed_event_types})


def jwt_encode(payload):
    """
    Parameters
    ----------
    payload : dict
        a payload dictionary

    Returns
    -------
    a JSON web token

    """

    return jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)


def jwt_decode(token) -> dict:
    """
    Checks if a token is valid

    Parameters
    ----------
    token : string
        a jwt

    Returns
    -------
    the token payload or False

    """

    try:
        return jwt.decode(token.encode('utf-8'), JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        raise JWTDecodeException

#
# servertoken = jwt_encode({'userid': -1})

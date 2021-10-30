#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jwt

from homecon.core.config import jwt_secret, jwt_algorithm


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

    return jwt.encode(payload, jwt_secret, jwt_algorithm).decode('utf-8')


def jwt_decode(token):
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
        return jwt.decode(token.encode('utf-8'), jwt_secret, algorithms=[jwt_algorithm])
    except:
        return False


servertoken = jwt_encode({'userid': -1, 'groupids': [1], 'username': '', 'permission': 9})

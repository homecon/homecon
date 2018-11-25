#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from pydal import DAL, Field


logger = logging.getLogger(__name__)

database_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
_database = None
_measurements_database = None


def get_database_uri():
    return 'sqlite://{}'.format(os.path.join(database_path, 'homecon.db'))


def get_database():
    global _database
    if _database is None:
        _database = DAL(get_database_uri())
    return _database


def close_database():
    global _database
    if _database is not None:
        _database.close()
    _database = None


def get_measurements_database_uri():
    return 'sqlite://{}'.format(os.path.join(database_path, 'measurements.db'))


def get_measurements_database():
    global _measurements_database
    if _measurements_database is None:
        _measurements_database = DAL('sqlite://{}'.format(os.path.join(database_path, 'measurements.db')))
    return _measurements_database


def close_measurements_database():
    global _measurements_database
    if _measurements_database is not None:
        _measurements_database.close()
    _measurements_database = None

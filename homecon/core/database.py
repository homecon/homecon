#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from pydal import DAL, Field


logger = logging.getLogger(__name__)

base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
database_path = os.path.join(base_path, 'db')


def get_database_uri():
    if not os.path.exists(database_path):
        os.mkdir(database_path)
    return 'sqlite://{}'.format(os.path.join(database_path, 'homecon.db'))


def get_database():
    return DAL(get_database_uri())


def get_measurements_database_uri():
    if not os.path.exists(database_path):
        os.mkdir(database_path)
    return 'sqlite://{}'.format(os.path.join(database_path, 'measurements.db'))


def get_measurements_database():
    return DAL(get_measurements_database_uri())


class DatabaseObject(object):

    def __init__(self, id=None):
        self._id = id

    @staticmethod
    def get_table():
        return None

    @classmethod
    def all_paths(cls):
        db = get_database()
        paths = [db_entry['path'] for db_entry in db(cls.get_table()).select()]
        db.close()
        return paths

    @classmethod
    def all(cls):
        db, table = cls.get_table()
        states = [cls(**db_entry.as_dict()) for db_entry in db(table).select()]
        db.close()
        return states

    @classmethod
    def get(cls, id):
        db, table = cls.get_table()
        entry = table(id)
        db.close()
        if entry is not None:
            return cls(**entry.as_dict())
        else:
            return None

    def get_property(self, property):
        # FIXME implement some temporary caching
        db, table = self.get_table()
        entry = table(self.id)
        db.close()
        if entry is not None:
            return entry[property]
        else:
            return None

    @property
    def id(self):
        return self._id


class UniquePathDatabaseObject(DatabaseObject):
    def __init__(self, id=None, path=None):
        super().__init__(id=id)
        self._path = path

    @classmethod
    def get(cls, path=None, id=None):
        if id is not None:
            db, table = cls.get_table()
            entry = table(id)
            db.close()
        elif path is not None:
            db, table = cls.get_table()
            entry = table(path=path)
            db.close()
        else:
            raise Exception('id or path must be supplied')

        if entry is not None:
            return cls(**entry.as_dict())
        else:
            return None

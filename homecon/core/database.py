#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from pydal import DAL, Field


logger = logging.getLogger(__name__)

base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
database_path = os.path.join(base_path, 'db')
database_name = 'homecon'
measurements_database_name = 'measurements'


def set_database(name):
    global database_name
    database_name = name


def get_database_uri():
    if not os.path.exists(database_path):
        os.mkdir(database_path)
    return 'sqlite://{}'.format(os.path.join(database_path, '{}.db'.format(database_name)))


def get_database():
    return DAL(get_database_uri())


def set_measurements_database(name):
    global measurements_database_name
    measurements_database_name = name


def get_measurements_database_uri():
    if not os.path.exists(database_path):
        os.mkdir(database_path)
    return 'sqlite://{}'.format(os.path.join(database_path, '{}.db'.format(measurements_database_name)))


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
        entries = [cls(**db_entry.as_dict()) for db_entry in db(table).select()]
        db.close()
        return entries

    @classmethod
    def all_ids(cls):
        db, table = cls.get_table()
        ids = [db_entry.id for db_entry in db(table).select()]
        db.close()
        return ids

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

    def get_row(self):
        db, table = self.get_table()
        entry = table(self.id)
        return db, entry

    def update(self, **kwargs):
        db, entry = self.get_row()
        entry.update_record(**kwargs)
        db.close()

    @property
    def id(self):
        return self._id

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.id == other.id

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import pytz

# globals
dt_ref = datetime.datetime(1970,1,1)
timezone = pytz.utc


def set_timezone(timezonestr):
    global timezone

    try:
        timezone = pytz.timezone(timezonestr)
        logging.debug('set timezone to {}'.format(timezone))
    except:
        logging.error('timezone {} is not available in pytz'.format(timezonestr))


def timestamp(dt_utc=None):
    """
    Returns the unix timestamp from a given utc datetime or now
    """

    if dt_utc is None:
        dt_utc = datetime.datetime.utcnow() 

    return int((dt_utc-dt_ref).total_seconds())


def timestamp_to_datetime(ts,timezonestr=None):
    """
    Returns a localized datetime object from a given unix timestamp

    """

    if not timezonestr is None:
        timezone = pytz.timezone(timezonestr)
    else:
        timezone = globals()['timezone']

    dt_utc = datetime.datetime.utcfromtimestamp(ts)
    dt = pytz.utc.localize( dt_utc ).astimezone(timezone)

    return dt

def timestamp_of_the_week(ts):
    """
    Return a timestamp corresponding to a weekday 
    Mon 00:00 = 0, Mon 00:15 = 900, ..., Sun 23:45 = 603900

    """
    dt = timestamp_to_datetime(ts)

    return dt.weekday()*24*3600 + dt.hour*3600 + dt.minute*60 + dt.second


def seconds_until(ts=None):
    """
    Returns the number of seconds until a given timestamp
    """
    ts_now = timestamp()

    return ts-ts_now


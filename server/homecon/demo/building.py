#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os
import datetime
import numpy as np

from .. import core
from .. import util


def emulate_building(initialdata,weatherdata,lookahead=0,heatingcurve=False):
    """
    emulate extremely simple building dynamics
    C_em*d(T_em)/dt = UA_em*(T_em-T_in) + Q_em 
    C_in*d(T_in)/dt = UA_in*(T_in-T_am) + UA_em*(T_in-T_em) + Q_so + Q_in

    Parameters
    ----------
    initialdata : dict
        Dictionary with intial data.
        Must have a 'utcdatetime', 'T_in', 'T_em' keys with array like values

    lookahead : number
        Number of seconds to look ahead from now

    """

    # time
    dt_ref = datetime.datetime(1970, 1, 1)
    dt_now = datetime.datetime.utcnow()
    timestep = 300

    utcdatetime = [initialdata['utcdatetime'][-1]+datetime.timedelta(seconds=t) for t in np.arange(0,(dt_now-initialdata['utcdatetime'][-1]).total_seconds()+lookahead,timestep)]
    if utcdatetime[-1] < dt_now:
        utcdatetime.append(dt_now)

    utcdatetime = np.array(utcdatetime)

    timestamp = np.array( [int( (dt-dt_ref).total_seconds() ) for dt in utcdatetime] )

    # parameters
    UA_in = 800
    C_in = 10e6

    UA_em = 600
    C_em = 8e6

    Q_em_max = 16000
    T_set = 20
    K_set = 5000
    K_am = 800


    # disturbances
    T_am = np.interp(timestamp,weatherdata['timestamp'],weatherdata['ambienttemperature'])

    Q_so = np.zeros(len(timestamp))
    for window in core.components.find(type='window'):
        Q_so = Q_so + window.calculate_solargain(
            I_direct=np.interp(timestamp,weatherdata['timestamp'],weatherdata['I_direct_cloudy']),
            I_diffuse=np.interp(timestamp,weatherdata['timestamp'],weatherdata['I_diffuse_cloudy']),
            solar_azimuth=np.interp(timestamp,weatherdata['timestamp'],weatherdata['solar_azimuth']),
            solar_altitude=np.interp(timestamp,weatherdata['timestamp'],weatherdata['solar_altitude']),
            shading_relativeposition=[np.zeros(len(timestamp)) for shading in core.components.find(type='shading',window=window.path) ])

    Q_in = np.zeros(len(timestamp))
    Q_em = np.zeros(len(timestamp))


    # initialization
    T_in = np.zeros(len(timestamp))
    T_in[0] = initialdata['T_in'][-1]

    T_em = np.zeros(len(timestamp))
    T_em[0] = initialdata['T_em'][-1]


    # solve discrete equation
    for i,t in enumerate(utcdatetime[:-1]):

        delta_t = timestamp[i+1]-timestamp[i]

        # emission heat flow
        if heatingcurve:
            Q_em[i] = min(Q_em_max,max(0, (T_in[i]-T_am[i])*K_am + (T_set-T_in[i])*K_set ))
        else:
            Q_em[i] = core.components['floorheating_groundfloor'].calculate_power()

        T_em[i+1] = T_em[i] + (T_in[i]-T_em[i])*delta_t*UA_em/C_em + Q_em[i]*delta_t/C_em
        T_in[i+1] = T_in[i] + (T_am[i]-T_in[i])*delta_t*UA_in/C_in + (T_em[i]-T_in[i])*delta_t*UA_em/C_in + Q_so[i]*delta_t/C_in + Q_in[i]*delta_t/C_in

    # set the output data
    data = {
        'utcdatetime': utcdatetime[1:],
        'timestamp': timestamp[1:],
        'T_in': T_in[1:],
        'T_em': T_em[1:],
        'Q_em': Q_em[1:],
        'Q_so': Q_so[1:],
        'dayzone/temperature': T_in[1:],
        'dayzone/solargain': 0.7*Q_so[1:],
        'dayzone/internalgain': 0*np.ones(len(utcdatetime[1:])),
        'nightzone/temperature': T_in[1:],
        'nightzone/solargain': 0.3*Q_so[1:],
        'nightzone/internalgain': 0*np.ones(len(utcdatetime[1:])),
        'bathroomzone/temperature': T_in[1:],
        'bathroomzone/solargain': 0.0*Q_so[1:],
        'bathroomzone/internalgain': 0*np.ones(len(utcdatetime[1:])),
        'living/temperature_wall/value': 0.90*T_in[1:] + 0.10*T_em[1:],
        'living/temperature_window/value': 0.98*T_in[1:] + 0.02*T_em[1:],
        'heatpump/power_setpoint': Q_em[1:],
        'heatpump/power': Q_em[1:],
        'floorheating_groundfloor/valve_position': 1.0*np.ones(len(utcdatetime[1:])),
        'living/window_west_1/screen/position': 0.0*np.ones(len(utcdatetime[1:])),
        'living/window_west_2/screen/position': 0.0*np.ones(len(utcdatetime[1:])),
        'kitchen/window_west/screen/position': 0.0*np.ones(len(utcdatetime[1:])),
        'kitchen/window_south/screen/position': 0.0*np.ones(len(utcdatetime[1:])),
        'bedroom/window_east/shutter/position': 0.0*np.ones(len(utcdatetime[1:])),
        'bedroom/window_north/shutter/position': 0.0*np.ones(len(utcdatetime[1:])),

    }
    return data



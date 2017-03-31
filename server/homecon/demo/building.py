#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os
import datetime
import numpy as np

from .. import core
from .. import util


def emulate_building(initialdata,weatherdata,finaltimestamp=-1,heatingcurve=False):
    """
    emulate extremely simple building dynamics
    C_em*d(T_em)/dt = UA_em*(T_em-T_in) + Q_em 
    C_in*d(T_in)/dt = UA_in*(T_in-T_am) + UA_em*(T_in-T_em) + Q_sol + Q_int

    Parameters
    ----------
    initialdata : dict
        Dictionary with intial data.
        Must have a 'timestamp', 'T_in', 'T_em' keys with array like values

    lookahead : number
        Number of seconds to look ahead from now

    """

    # generate timestep vector
    timestep = 150

    if finaltimestamp < 0:
        
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        finaltimestamp = int( (dt_now-dt_ref).total_seconds() )

    timestamp = np.arange( initialdata['timestamp'][-1],finaltimestamp,timestep )
    if not timestamp[-1] == finaltimestamp:
        timestamp = np.append(timestamp,finaltimestamp)


    # parameters
    UA_in = 600
    C_in = 10e6

    UA_em = 1200
    C_em = 8e6

    Q_em_max = 16000
    T_set = 20
    K_set = 5000
    K_amb = 800
    K_sha = 0.2

    # disturbances
    T_am = np.interp(timestamp,weatherdata['timestamp'],weatherdata['ambienttemperature'])

    Q_sol_zone = {}
    Q_int_zone = {}
    for zone in core.components.find(type='zone'):
        # FIXME take actual shading position into account in min/max shading position dertermination
        shading_relativeposition = [[0.0*np.ones(len(timestamp)) for shading in core.components.find(type='shading',window=window.path)] for window in core.components.find(type='window',zone=zone.path)]
        Q_sol_zone[zone.path] = zone.calculate_solargain(
            I_direct=np.interp(timestamp,weatherdata['timestamp'],weatherdata['I_direct_cloudy']),
            I_diffuse=np.interp(timestamp,weatherdata['timestamp'],weatherdata['I_diffuse_cloudy']),
            solar_azimuth=np.interp(timestamp,weatherdata['timestamp'],weatherdata['solar_azimuth']),
            solar_altitude=np.interp(timestamp,weatherdata['timestamp'],weatherdata['solar_altitude']),
            shading_relativeposition=shading_relativeposition)

        Q_int_zone[zone.path] = 0.0*np.ones(len(timestamp))
        

    Q_sol = np.sum([Q for Q in Q_sol_zone.values()],axis=0) + 0.0*np.ones(len(timestamp))
    Q_int = np.sum([Q for Q in Q_int_zone.values()],axis=0) + 0.0*np.ones(len(timestamp))
    Q_em = np.zeros(len(timestamp))
    p_sha = np.zeros(len(timestamp))

    # initialization
    T_in = np.zeros(len(timestamp))
    T_in[0] = initialdata['T_in'][-1]

    T_em = np.zeros(len(timestamp))
    T_em[0] = initialdata['T_em'][-1]


    # solve discrete equation
    for i,ts in enumerate(timestamp[:-1]):

        delta_t = timestamp[i+1]-timestamp[i]

        # emission heat flow
        if heatingcurve:
            Q_em[i] = min(Q_em_max,max(0, (T_in[i]-T_am[i])*K_amb + (T_set-T_in[i])*K_set ))
            p_sha[i] = min(1,max(0, (T_in[i]-T_set-2)*K_sha))

        else:
            Q_em[i] = sum(component.calculate_power() for component in core.components.find(type='heatemissionsystem'))
            p_sha[i] = 0

        T_em[i+1] = T_em[i] + (T_in[i]-T_em[i])*delta_t*UA_em/C_em + Q_em[i]*delta_t/C_em
        T_in[i+1] = T_in[i] + (T_am[i]-T_in[i])*delta_t*UA_in/C_in + (T_em[i]-T_in[i])*delta_t*UA_em/C_in + p_sha[i]*Q_sol[i]*delta_t/C_in + Q_int[i]*delta_t/C_in

    # set the output data
    data = {
        'timestamp': timestamp[1:],
        'T_in': T_in[1:],
        'T_em': T_em[1:],
        'Q_em': Q_em[1:],
        'Q_sol': Q_sol[1:],
    }


    for zone in core.components.find(type='zone'):
        data[ zone.states['temperature'].path ] = T_in[1:]
        data[ zone.states['solargain'].path ] = Q_sol_zone[zone.path][1:]
        data[ zone.states['internalgain'].path ] = Q_int_zone[zone.path][1:]

    for sensor in core.components.find(type='zonetemperaturesensor'):
        f = 0.9+0.1*np.random.random()
        data[ sensor.states['value'].path ] = f*T_in[1:] + (1-f)*T_em[1:]

    for shading in core.components.find(type='shading'):
        data[ shading.states['position'].path ] = 0.0*np.ones(len(timestamp[1:]))

    for system in core.components.find(type='heatemissionsystem'):
        data[ system.states['valve_position'].path ] = 1.0*np.ones(len(timestamp[1:]))

    heatgenerationsystems = core.components.find(type='heatgenerationsystem')
    if len(heatgenerationsystems) >0:
        system = heatgenerationsystems[0]
        data[ system.states['power'].path ] = Q_em[1:]
        data[ system.states['power_setpoint'].path ] = Q_em[1:]


    return data



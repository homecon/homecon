#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os
import datetime
import numpy as np

from .. import core
from .. import util


def emulate_weather(initialdata,lookahead=0):
    """
    emulate weather conditions

    Parameters
    ----------
    initialdata : dict
        Dictionary with intial data.
        Must have a 'utcdatetime', 'cloudcover' and 'ambienttemperature' 
        keys with array like values

    lookahead : number
        Number of seconds to look ahead from now

    """

    # generate new datetime vector
    dt_ref = datetime.datetime(1970, 1, 1)
    dt_now = datetime.datetime.utcnow()
    timestep = 300

    utcdatetime = [initialdata['utcdatetime'][-1]+datetime.timedelta(seconds=t) for t in np.arange(0,(dt_now-initialdata['utcdatetime'][-1]).total_seconds()+lookahead,timestep)]
    if utcdatetime[-1] < dt_now:
        utcdatetime.append(dt_now)

    utcdatetime = np.array(utcdatetime)

    timestamp = np.array( [int( (dt-dt_ref).total_seconds() ) for dt in utcdatetime] )


    solar_azimuth = np.zeros(len(timestamp))
    solar_altitude = np.zeros(len(timestamp))
    I_direct_clearsky = np.zeros(len(timestamp))
    I_diffuse_clearsky = np.zeros(len(timestamp))
    I_direct_cloudy = np.zeros(len(timestamp))
    I_diffuse_cloudy = np.zeros(len(timestamp))
    cloudcover = np.zeros(len(timestamp))
    ambienttemperature = np.zeros(len(timestamp))
    I_total_horizontal = np.zeros(len(timestamp))
    I_direct_horizontal = np.zeros(len(timestamp))
    I_diffuse_horizontal = np.zeros(len(timestamp))
    I_ground_horizontal = np.zeros(len(timestamp))


    cloudcover[0] = initialdata['cloudcover'][-1]
    ambienttemperature[0] = initialdata['ambienttemperature'][-1]
    
    latitude = core.states['settings/location/latitude'].value
    longitude = core.states['settings/location/longitude'].value
    elevation = core.states['settings/location/elevation'].value

    for i,ts in enumerate(timestamp):
        

        solar_azimuth[i],solar_altitude[i] = util.weather.sunposition(latitude,longitude,elevation=elevation,timestamp=ts)
        I_direct_clearsky[i],I_diffuse_clearsky[i] = util.weather.clearskyirrradiance(solar_azimuth[i],solar_altitude[i],timestamp=ts)

        # random variation in cloud cover
        if i < len(timestamp)-1:
            delta_t = timestamp[i+1]-timestamp[i]
            cloudcover[i+1] = min(1.,max(0., cloudcover[i] + 0.0001*(2*np.random.random()-1)*delta_t ))

        I_direct_cloudy[i],I_diffuse_cloudy[i] = util.weather.cloudyskyirrradiance(I_direct_clearsky[i],I_diffuse_clearsky[i],cloudcover[i],solar_azimuth[i],solar_altitude[i],timestamp=ts)
        
        I_total_horizontal[i], I_direct_horizontal[i], I_diffuse_horizontal[i], I_ground_horizontal[i] = util.weather.incidentirradiance(I_direct_cloudy[i],I_diffuse_cloudy[i],solar_azimuth[i],solar_altitude[i],0,0)

        # ambient temperature dependent on horizontal irradiance
        if i < len(timestamp)-1:
            delta_t = timestamp[i+1]-timestamp[i]
            ambienttemperature[i+1] = ambienttemperature[i] + I_total_horizontal[i]*delta_t/(30*24*3600) + (-10-ambienttemperature[i])*delta_t/(5*24*3600) + 10*delta_t/(30*24*3600)  + (2*np.random.random()-1)*delta_t/(2*3600)


    utcdatetime_ref = datetime.datetime(1970, 1, 1)

    data = {
        'utcdatetime': utcdatetime,
        'timestamp': timestamp,
        'solar_azimuth': solar_azimuth,
        'solar_altitude': solar_altitude,
        'I_direct_clearsky': I_direct_clearsky,
        'I_diffuse_clearsky': I_diffuse_clearsky,
        'I_direct_cloudy': I_direct_cloudy,
        'I_diffuse_cloudy': I_diffuse_cloudy,
        'cloudcover': cloudcover,
        'ambienttemperature': ambienttemperature,
        'I_total_horizontal': I_total_horizontal,
        'I_direct_horizontal': I_direct_horizontal,
        'I_diffuse_horizontal': I_diffuse_horizontal,
        'I_ground_horizontal': I_ground_horizontal,
    }

    return data

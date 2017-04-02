#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os
import datetime
import numpy as np

from .. import core
from .. import util


def emulate_weather(initialdata,finaltimestamp=-1,mincloudcover=0,maxcloudcover=1,minambienttemperature=-10,maxambienttemperature=30):
    """
    emulate weather conditions

    Parameters
    ----------
    initialdata : dict
        Dictionary with intial data.
        Must have a 'timestamp', 'cloudcover' and 'ambienttemperature' 
        keys with array like values

    lookahead : number
        Number of seconds to look ahead from now

    """

    
    # generate timestep vector
    timestep = 300

    if finaltimestamp < 0:
        
        dt_ref = datetime.datetime(1970, 1, 1)
        dt_now = datetime.datetime.utcnow()
        finaltimestamp = int( (dt_now-dt_ref).total_seconds() )

    timestamp = np.arange( initialdata['timestamp'][-1],finaltimestamp,timestep )
    if not timestamp[-1] == finaltimestamp:
        timestamp = np.append(timestamp,finaltimestamp)


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
            cloudcover[i+1] = min(maxcloudcover,max(mincloudcover, cloudcover[i] + 0.0001*(2*np.random.random()-1)*delta_t ))

        I_direct_cloudy[i],I_diffuse_cloudy[i] = util.weather.cloudyskyirrradiance(I_direct_clearsky[i],I_diffuse_clearsky[i],cloudcover[i],solar_azimuth[i],solar_altitude[i],timestamp=ts)
        
        I_total_horizontal[i], I_direct_horizontal[i], I_diffuse_horizontal[i], I_ground_horizontal[i] = util.weather.incidentirradiance(I_direct_cloudy[i],I_diffuse_cloudy[i],solar_azimuth[i],solar_altitude[i],0,0)

        # ambient temperature dependent on horizontal irradiance and cloud cover
        if i+1 < len(timestamp):
            c_tot = 800e3

            skytemperature = -20*(1-cloudcover[i]) -15*cloudcover[i]
            U_sky = 7.5*(1-cloudcover[i]) + 2.0*cloudcover[i]
            
            T_avg = ambienttemperature[i]
            q_corr = 100*( np.exp(-(T_avg-minambienttemperature)) - np.exp(-(maxambienttemperature-T_avg)) )
            

            delta_t = timestamp[i+1]-timestamp[i]
            ambienttemperature[i+1] = ambienttemperature[i] + (skytemperature-ambienttemperature[i])*U_sky*delta_t/c_tot + I_total_horizontal[i]*delta_t/c_tot + q_corr*delta_t/c_tot

    data = {
        'timestamp': timestamp.tolist(),
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



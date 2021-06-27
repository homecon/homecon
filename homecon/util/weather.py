#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import ephem
import numpy as np


def sunposition(latitude: float, longitude: float, elevation=0, timestamp=None):
    """
    Returns the sun azimuth and altitude at a certain time at the current
    location
    
    Parameters
    ----------
    latitude : number
        the location latitude in degrees N > 0

    longitude : number
        the location longitude in degrees E > 0

    elevation : number
        the location elevation in m above sea level?

    timestamp : int
        the unix timestamp when to compute the sun position

    Returns
    -------
    solar_azimuth : number
        sun azimuth in degrees
        0deg is N, 90deg is E, 180deg is S, 270deg is W

    solar_altitude : number
        sun altitude in degrees
        0deg is the horizon, 90deg is vertical

    Notes
    -----
    See http://rhodesmill.org/pyephem/quick.html for an ephem introduction

    """

    if timestamp == None:
        utcdatetime = datetime.datetime.utcnow()
    else:
        utcdatetime = datetime.datetime.utcfromtimestamp(timestamp)

    # create an ephem observer
    obs = ephem.Observer()

    solar_azimuth = None
    solar_altitude = None

    if not latitude is None and not longitude is None:
        obs.lat = np.radians(latitude)
        obs.lon = np.radians(longitude)
        obs.elev = elevation
        obs.date = utcdatetime

        sun = ephem.Sun(obs)
        sun.compute(obs)
        
        solar_azimuth = np.degrees(sun.az)
        solar_altitude = np.degrees(sun.alt)

    return solar_azimuth,solar_altitude


def clearskyirrradiance(solar_azimuth: float, solar_altitude: float, timestamp=None):
    """
    Compute the clear sky theoretical direct and diffuse solar irradiance
    at a certain time at the current location according to [1] results are
    similar to [2]

    Parameters
    ----------
    solar_azimuth : number
        sun azimuth in degrees
        0deg is N, 90deg is E, 180deg is S, 270deg is W

    solar_altitude : number
        sun altitude in degrees
        0deg is the horizon, 90deg is vertical

    timestamp : int
        the unix timestamp when to compute the sun position

    Returns
    -------
    I_direct_clearsky : number
        direct normal irrradiance (W/m2)

    I_diffuse_clearsky : number
        diffuse horrizontal irrradiance (W/m2)

    Notes
    -----
    [1] ASHRAE 2009, H28, p9-11.
    [2] ASHRAE 2005, H31

    """

    # day of the year
    if timestamp == None:
        utcdatetime = datetime.datetime.utcnow()
    else:
        utcdatetime = datetime.datetime.utcfromtimestamp(timestamp)

    # air mass between the observer and the sun
    if 6.07995 + np.radians(solar_altitude) > 0:
        m = 1/(np.sin(np.radians(solar_altitude)) + 0.50572*(6.07995 + np.radians(solar_altitude))**-1.6364);
    else:
        m = 0

    dayoftheyear = float(utcdatetime.strftime('%j'))

    # extraterrestrial solar radiation
    Esc = 1367 # solar constant
    E0 = Esc*(1 + 0.033*np.cos(2*np.pi*(dayoftheyear-3)/365))

    # optical depths
    tau_b = np.interp(dayoftheyear,np.cumsum([-10,31,31,28,31,30,31,30,31,31,30,31,30,31]),[0.320,0.325,0.349,0.383,0.395,0.448,0.505,0.556,0.593,0.431,0.373,0.339,0.320,0.325])
    tau_d = np.interp(dayoftheyear,np.cumsum([-10,31,31,28,31,30,31,30,31,31,30,31,30,31]),[2.514,2.461,2.316,2.176,2.175,2.028,1.892,1.779,1.679,2.151,2.317,2.422,2.514,2.461])

    ab = 1.219 - 0.043*tau_b - 0.151*tau_d - 0.204*tau_b*tau_d
    ad = 0.202 + 0.852*tau_b - 0.007*tau_d -0.357*tau_b*tau_d

    if m>=0:
        I_direct_clearsky = max(0,E0*np.exp(-tau_b*m**ab))
    else:
        I_direct_clearsky = 0

    if m>=0:
        I_diffuse_clearsky = max(0,E0*np.exp(-tau_d*m**ad))
    else:
        I_diffuse_clearsky = 0

    return I_direct_clearsky, I_diffuse_clearsky


def incidentirradiance(I_direct, I_diffuse, solar_azimuth, solar_altitude, surface_azimuth, surface_tilt):
    """
    Method returns irradiation on a tilted surface according to ASHRAE

    Parameters
    ----------
    I_direct : number
        local beam irradiation (W/m2)

    I_diffuse : number
        local diffuse irradiation (W/m2)

    solar_azimuth : number
        solar azimuth angle from N in E direction (0=N, 90=E, 180=S, -270 = W) (deg)

    solar_altitude : number
        solar altitude angle (deg)

    surface_azimuth: number
        surface normal azimuth angle from N in E direction (0=N, 90=E, 180=S, 270 = W) (deg)

    surface_tilt: number
        surface tilt angle (0: facing up, pi/2: vertical, pi: facing down) (deg)

    output:
    I_total_surface : number
        total irradiance on tilted surface  (W/m2)

    I_direct_surface : number
        Direct irradiance on tilted surface  (W/m2)

    I_diffuse_surface : number
        Diffuse irradiance on tilted surface  (W/m2)

    I_ground_surface : number
        Ground reflected radiation on tilted surface  (W/m2)

    """

    # surface solar azimuth (-pi/2< gamma < pi/2, else surface is in shade)
    gamma = solar_azimuth-surface_azimuth

    # incidence
    cos_theta = np.cos(np.radians(solar_altitude))*np.cos(np.radians(gamma))*np.sin(np.radians(surface_tilt)) + np.sin(np.radians(solar_altitude))*np.cos(np.radians(surface_tilt))

    # beam irradiation
    if cos_theta > 0:
        I_direct_surface = I_direct*cos_theta
    else:
        I_direct_surface = 0

    # diffuse irradiation
    Y = max(0.45, 0.55 + 0.437*cos_theta+ 0.313*cos_theta**2)
    if surface_tilt < 90:
        I_diffuse_surface = I_diffuse*(Y*np.sin(np.radians(surface_tilt)) + np.cos(np.radians(surface_tilt)))
    else:
        I_diffuse_surface = I_diffuse*Y*np.sin(np.radians(surface_tilt))

    # ground reflected radiation
    rho_g = 0.2
    I_ground_surface = (I_direct*np.sin(np.radians(solar_altitude)) + I_diffuse)*rho_g*(1-np.cos(np.radians(surface_tilt)))/2

    # total irradiation
    I_total_surface = (I_direct_surface + I_diffuse_surface + I_ground_surface)

    return I_total_surface, I_direct_surface, I_diffuse_surface, I_ground_surface



def cloudyskyirrradiance(I_direct_clearsky, I_diffuse_clearsky, cloudcover, solar_azimuth, solar_altitude, timestamp=None):
    """
    Correction of the direct normal and diffuse horizontal irradiance using
    the the cloudcover fraction in accordance with [3] and [4].
    Credits to Damien Picard for the literature and coding

    Parameters
    ----------
    I_direct_clearsky : number
        direct clearsky solar irradiance

    I_diffuse_clearsky : number
        diffuse clearsky solar irradiance

    cloudcover : number
        fraction of the sky covered by clouds

    timestamp : int
        the unix timestamp when to compute the sun position

    Returns
    -------
    I_direct_cloudy : number
        direct solar normal irradiance corrected by cloud coverage

    I_diffuse_cloudy : number
        diffuse solar horizontal irradiance corrected by cloud coverage

    Notes
    -----
    [3] K. Kimura and D. G. Stephenson, Solar radiation on cloudy days. Res.
        Paper 418, Division of Building Research, National Research Council,
        Ottawa (1969).
    [4] R. Brinsfield, M. Yaramanogly, F. Wheaton, Ground level solar
        radiation prediction model including cloud cover effects, Solar
        Energy, Volume 33, Issue 6, 1984, Pages 493-499

    """

    # clear sky irradiance on a horizontal surface
    I_total_horizontal_clearsky, I_direct_horizontal_clearsky, I_diffuse_horizontal_clearsky, I_ground_horizontal_clearsky = incidentirradiance(I_direct_clearsky,I_diffuse_clearsky,solar_azimuth,solar_altitude,0,0)


    if I_total_horizontal_clearsky > 0.1:

        if timestamp == None:
            utcdatetime = datetime.datetime.utcnow()
        else:
            utcdatetime = datetime.datetime.utcfromtimestamp(timestamp)


        # month of the year.
        month = float(utcdatetime.strftime('%m'))

        # Data from table 1 of [1]. Month of december and march are repeated for interpolation.
        P = np.interp(month, [-1., 3., 6., 9., 12., 15. ], [1.14, 1.06, 0.96, 0.95, 1.14, 1.06])
        Q = np.interp(month, [-1., 3., 6., 9., 12., 15. ], [0.003, 0.012, 0.033, 0.030, 0.003, 0.012])
        R = np.interp(month, [-1., 3., 6., 9., 12., 15. ], [-0.0082, -0.0084, -0.0106, -0.0108, -0.0082, -0.0084])

        # Cloud coverage and cloud coverage factor
        CC = cloudcover*10.
        CCF = P + Q*CC + R*CC**2
        # Notice: CCF can be > 1 (higher radiation than average) and has a maximum at CC = 2-3 (see Fig.3, [1])

        # Correction for horizontal surface, according to [1]

        # equation 1, [1]: total radiation on horizontal surface, corrected with cloud coverage factor
        I_total_horizontal_cloudy = (I_total_horizontal_clearsky - I_ground_horizontal_clearsky) * CCF

        # Direct radiation is proportional to cloud fraction (eq. 12, [1])
        I_direct_cloudy = max(0,I_direct_clearsky*(1-cloudcover))
        I_direct_horizontal_cloudy = max(0,I_direct_horizontal_clearsky*(1-cloudcover))

        # Diffuse radiation = total radiation - direct radiation (equivalent to eq. 13, [1])
        I_diffuse_cloudy = max(0,I_total_horizontal_cloudy - I_direct_horizontal_cloudy)

    else:
        I_direct_cloudy = I_direct_clearsky
        I_diffuse_cloudy = I_diffuse_clearsky


    return I_direct_cloudy , I_diffuse_cloudy



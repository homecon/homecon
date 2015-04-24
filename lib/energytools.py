#!/usr/bin/env python3
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of KNXControl.
#
#    KNXControl is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KNXControl is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import ephem
import datetime
import numpy as np

class Energytools():
	"""
	Provides tools for building energy calculations
	"""
	
	def __init__(self,smarthome):
		self._sh = smarthome

		
	def sunposition(self,utcdate=datetime.datetime.utcnow()):
		"""
		Method returns the sun azimuth and altitude at a certain utcdate
		at the location specified in smarthome.conf
		Output is in radians
		"""
		
		# http://rhodesmill.org/pyephem/quick.html
		obs = ephem.Observer()
		obs.lat = float(self._sh._lat())     #N+
		obs.lon = float(self._sh._lon())     #E+
		obs.elevation = float(self._sh._elev())
		obs.date = utcdate
		sun = ephem.Sun(obs)
		sun.compute(obs)
		
		return (sun.az,sun.alt)
		
		
	def clearskyirrradiation(self,utcdate):
		"""
		Method returns the clear sky theoretical direct and diffuse solar irradiation
		according to ASHRAE
		"""
		
		(azi,alt) = self.sunposition(utcdate)
		
		# air mass between the observer and the sun
		if 6.07995 + alt > 0:
			m = 1/(np.sin(alt) + 0.50572*(6.07995 + alt)**-1.6364);
		else:
			m = 0

		# day of the year
		n = strftime(utcdate,'%j');
		
		# optical depths
		tau_b = np.interp(n,np.cumsum([-10,31,31,28,31,30,31,30,31,31,30,31,30,31]),[0.320,0.325,0.349,0.383,0.395,0.448,0.505,0.556,0.593,0.431,0.373,0.339,0.320,0.325]);
		tau_d = np.interp(n,np.cumsum([-10,31,31,28,31,30,31,30,31,31,30,31,30,31]),[2.514,2.461,2.316,2.176,2.175,2.028,1.892,1.779,1.679,2.151,2.317,2.422,2.514,2.461]);
	   
		ab = 1.219 - 0.043*tau_b - 0.151*tau_d - 0.204*tau_b*tau_d; 
		ad = 0.202 + 0.852*tau_b - 0.007*tau_d -0.357*tau_b*tau_d;
		
		if np.degrees(alt) > 0:
			I_b = E0*np.exp(-tau_b*m**ab);
		else:
			I_b = 0
			
		if np.degrees(alt) > -2:	
			I_d = E0*np.exp(-tau_d*m**ad);
		else:
			I_b = 0
		
		return (I_b,I_d)

	def incidentradiation(self,I_b,I_d,solar_azimuth,solar_altitude,surface_azimuth,surface_tilt)
		"""
		Method returns irradiation on a surface 
		according to ASHRAE
		
		input:
		I_b: local beam irradiation (W/m²)
		I_d: local diffuse irradiation (W/m²)
		solar_azimuth:   sun azimuth angle from N in E direction (0=N, pi/2=E, pi=S, -pi/2 = W) (radians)
		solar_altitude:  sun altitude angle (radians)
		surface_azimuth: surface normal azimuth angle from N in E direction (0=N, pi/2=E, pi=S, -pi/2 = W) (radians)
		surface_tilt:    surface tilt angle (0: facing up, pi/2: vertical, pi: facing down) (radians)
		
		output:
		I: irradiation (W/m²)
		"""
		
		# surface solar azimuth (-pi/2< gamma < pi/2, else surface is in shade)
		gamma = solar_azimuth-surface_azimut;
		
		# incidence
		cos_theta = np.cos(solar_altitude)*np.cos(gamma)*np.sin(surface_tilt) + np.sin(solar_altitude)*np.cos(surface_tilt)
    
		# beam radiation
		if cos_theta > 0:
			I_tb = I_b*cos_theta
		else:
			I_tb = 0
		
		# diffuse radiation
		Y = max(0.45, 0.55 + 0.437*cos_theta+ 0.313*cos_theta.^2)
		if surf_tilt < np.pi/2:
			I_td = I_d*(Y*np.sin(surface_tilt) + cos(surface_tilt))
		else:
			I_td = I_d*Y*np.sin(surface_tilt)
			
		# ground reflected radiation
		rho_g = 0.2;
		I_gr = (I_b*np.sin(solar_altitude) +I_d)*rho_g*(1-np.cos(surface_tilt))/2
		
		# total irradiation
		I_t = I_tb + I_td + I_gr
		
		return I_t
		
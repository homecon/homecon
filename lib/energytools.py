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
import numpy

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
		
		
    def clearskyirrradiation(self,utcdate)
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
			E_b = E0*np.exp(-tau_b*m**ab);
		else:
			E_b = 0
			
		if np.degrees(alt) > -2:	
			E_d = E0*np.exp(-tau_d*m**ad);
		else:
			E_b = 0
		
		return (E_b,E_d)
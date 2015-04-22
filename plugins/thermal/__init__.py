#!/usr/bin/env python3

import logging
import numpy as np
import ephem

class thermal:

	def __init__(self, smarthome):
		self._sh = smarthome
		
        self._obs = ephem.Observer()
		self._obs.lat = self._sh._lat()
		self._obs.long= self._sh._lon()
		self._obs.elevation= self._sh._elev()
	
	def sunposition(utcdate)
		self._obs.date = str(utcdate)
		# http://rhodesmill.org/pyephem/quick.html
		sun = ephem.Sun(obs)
		sun.compute(obs)
		logger.info( str(sun.alt) )
		logger.info( str(sun.azi) )

		return (sun.azi*180/np.pi,sun.alt*180/np.pi)
	
	def clearskyirrradiation(utcdate)
		"""
		According to ASHRAE
		"""
		(azimuth,altitude) = sunposition(utcdate)
		
		# air mass between the observer and the sun
		m = 1./(np.sin(altitude) + 0.50572.*(6.07995 + altitude).^-1.6364);
		m = max(0,m);
    
		n = strftime(utcdate,'%j');
		
		# optical depths
		tau_b = np.interp(n,np.cumsum([-10 31 31 28 31 30 31 30 31 31 30 31 30 31]),[0.320 0.325 0.349 0.383 0.395 0.448 0.505 0.556 0.593 0.431 0.373 0.339 0.320 0.325]);
		tau_d = np.interp(n,np.cumsum([-10 31 31 28 31 30 31 30 31 31 30 31 30 31]),[2.514 2.461 2.316 2.176 2.175 2.028 1.892 1.779 1.679 2.151 2.317 2.422 2.514 2.461]);
	   
		ab = 1.219 - 0.043.*tau_b - 0.151.*tau_d - 0.204.*tau_b.*tau_d; 
		ad = 0.202 + 0.852.*tau_b -0.007.*tau_d -0.357.*tau_b.*tau_d;
		
		E_b = E0.*exp(-tau_b.*m.^ab).*(sin_beta>0);
		E_d = E0.*exp(-tau_d.*m.^ad).*(sin_beta>0);
		
		
		
	def calculate_theoretical_solar_irradiation(azimuth,altitude):
		""" Function to calculate theoretical direct and diffuse solar irradiation
		
		Arguments:
		azimuth: solar azimuth in degrees
		altitude: solar altitude in degrees
		"""
		
		d2r = np.pi/180
		
		#day of the year
		n = datetime.datetime.utcnow().timetuple().tm_yday

		Esc = 1367;   # solar constant  (W/m2)
		# extraterrestrial solar radiation
		E0 = Esc*(1 + 0.033*np.cos(2*np.pi*(n-3)/365))
		   
		# air mass
		if 6.07995 + altitude/d2r <= 0:
			m = 0
		else:
			m = 1/(np.sin(altitude) + 0.50572*(6.07995 + altitude/d2r)**-1.6364)

		# optical depth
		tau_b = numpy.interp(n,[ -10, 21, 52, 80, 111, 141, 172, 202, 233, 264, 294, 325, 355, 386],[0.320, 0.325, 0.349, 0.383, 0.395, 0.448, 0.505, 0.556, 0.593, 0.431, 0.373, 0.339, 0.320, 0.325])
		tau_d = numpy.interp(n,[ -10, 21, 52, 80, 111, 141, 172, 202, 233, 264, 294, 325, 355, 386],[2.514, 2.461, 2.316, 2.176, 2.175, 2.028, 1.892, 1.779, 1.679, 2.151, 2.317, 2.422, 2.514, 2.461])

		ab = 1.219 - 0.043*tau_b - 0.151*tau_d - 0.204*tau_b*tau_d
		ad = 0.202 + 0.852*tau_b -0.007*tau_d -0.357*tau_b*tau_d

		if altitude/d2r > -2:
			E_d = E0*np.exp(-tau_d*m**ad)
		else:
			E_d = 0

		if altitude/d2r > 0:
			E_b = E0*np.exp(-tau_b*m**ab)
		else:
			E_b = 0
			
			
		return (E_b, E_d)	
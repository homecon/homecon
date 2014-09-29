###########################################################################
# subfunctions
###########################################################################
#
#
#

import math
import datetime
import numpy
		

class subfunctions():
	
	####################################################################
	# calculate theoretical beam and diffuse radiation from the sun
	####################################################################
	def theoretical_irradiation(azimut,altitude):

		d2r = math.pi/180

		# sun position
		#azimut, altitude = sh.sun.pos(offset)
		#azimut = azimut-180*d2r  # sh returns the position relative to north, while the consensus is than 0deg is south

		#sh.building.irradiation.azimut(azimut/d2r)
		#sh.building.irradiation.altitude(altitude/d2r)

		sin_altitude = math.sin(altitude)
		cos_altitude = math.cos(altitude)  # beta

		#day of the year
		n = datetime.datetime.utcnow().timetuple().tm_yday

		Esc = 1367;   # solar constant  (W/m2)
		# extraterrestrial solar radiation
		E0 = Esc*(1 + 0.033*math.cos(2*math.pi*(n-3)/365))
		   
		# air mass
		if 6.07995 + altitude/d2r <= 0:
			m = 0
		else:
			m = 1/(sin_altitude + 0.50572*(6.07995 + altitude/d2r)**-1.6364)

		# optical depth
		tau_b = numpy.interp(n,[ -10, 21, 52, 80, 111, 141, 172, 202, 233, 264, 294, 325, 355, 386],[0.320, 0.325, 0.349, 0.383, 0.395, 0.448, 0.505, 0.556, 0.593, 0.431, 0.373, 0.339, 0.320, 0.325])
		tau_d = numpy.interp(n,[ -10, 21, 52, 80, 111, 141, 172, 202, 233, 264, 294, 325, 355, 386],[2.514, 2.461, 2.316, 2.176, 2.175, 2.028, 1.892, 1.779, 1.679, 2.151, 2.317, 2.422, 2.514, 2.461])

		ab = 1.219 - 0.043*tau_b - 0.151*tau_d - 0.204*tau_b*tau_d
		ad = 0.202 + 0.852*tau_b -0.007*tau_d -0.357*tau_b*tau_d

		if altitude/d2r > -2:
			E_d = E0*math.exp(-tau_d*m**ad)
		else:
			E_d = 0

		if altitude/d2r > 0:
			E_b = E0*math.exp(-tau_b*m**ab)
		else:
			E_b = 0
			
			
		return (E_b, E_d)	
			
	
	
	
	####################################################################
	# calculate surface irradiation
	####################################################################
	def surface_irradiation(azimut,altitude,orientation,tilt,E_b,E_d):
		
		d2r = math.pi/180
		
		tilt = tilt*d2r
		orientation = orientation*d2r
		
		# surface solar azimuth (-90deg< gamma < 90deg, else surface is in shade)
		gamma = azimut-orientation
		
		# surface solar incidence angle
		cos_theta = math.cos(altitude)*math.cos(gamma)*math.sin(tilt) + math.sin(altitude)*math.cos(tilt)
		# beam radiation
		if cos_theta > 0:
			E_tb = E_b*cos_theta
		else:
			E_tb = 0
			
		# diffuse radiation
		Y = max(0.45, 0.55 + 0.437*cos_theta+ 0.313*cos_theta**2)
		E_td = E_d*Y*math.sin(tilt)
		
		# ground reflected radiation
		rho_g = 0.2
		E_tr = (E_b*math.sin(altitude) + E_d)*rho_g*(1-math.cos(tilt))/2
		
		# total irradiation
		return (E_tb + E_td + E_tr)

import math
from datetime import datetime
from numpy import interp

from logics.subfunctions import subfunctions


###########################################################################
# calculate beam and diffuse radiation from the sun
###########################################################################
d2r = math.pi/180

# sun position
azimut, altitude = sh.sun.pos()
azimut = azimut-180*d2r  # sh returns the position relative to north, while the consensus is than 0deg is south

sh.building.irradiation.azimut(azimut/d2r)
sh.building.irradiation.altitude(altitude/d2r)

# calculate theoretical beam and diffuse irradiation
E_b,E_d = subfunctions.theoretical_irradiation(azimut,altitude)
	
sh.building.irradiation.direct_theoretical(E_b)
sh.building.irradiation.diffuse_theoretical(E_d)
	
	
# theoretical sensor irradiation
lightsensor = sh.building.irradiation.sensor
lightsensor_orientation = float(lightsensor.conf['orientation'])
lightsensor_tilt = float(lightsensor.conf['tilt'])

E_sensor_theoretical = subfunctions.surface_irradiation(azimut,altitude,lightsensor_orientation,lightsensor_tilt,E_b,E_d)
lightsensor.theoretical_value(E_sensor_theoretical)

# create a cloud factor to correct E_b and E_d to correspond to the measured light strength	
lightstrength = sh.return_item(lightsensor.conf['item'])
E_sensor = lightstrength()/127    #  127 lux = 1W/m2

if (E_sensor < E_sensor_theoretical) and (E_sensor_theoretical>0):
	cloud_factor = min(1,max(0,E_sensor/E_sensor_theoretical))
else:
	cloud_factor = 1


sh.building.irradiation.cloud_factor(cloud_factor)
# horizontal radiation used for validation with other measured data on the internet
sh.building.irradiation.horizontal(cloud_factor*(E_b*math.sin(altitude)+E_d))
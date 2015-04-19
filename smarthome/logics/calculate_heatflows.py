import math

# calculate the heat flows through the building envelope for every zone
# heat flow to the zone is counted positive
d2r = math.pi/180

# sun position
azimut, altitude = sh.sun.pos()
azimut = azimut-180*d2r

num_zones = 3

for zone in sh.building.zones:
	# set the operational temperature
	T_op = sh.return_item(zone.T_operational.conf['item'])
	T_op = T_op()
	zone.T_operational(T_op)
	
	# set the ambient temperature
	T_amb = sh.return_item(sh.building.ambient_temperature.sensor.conf['item'])
	T_amb = T_amb()
	
	# correct T_amb because the sensor is in the sun
	lightstrength = sh.return_item(sh.building.irradiation.sensor.conf['item'])
	lightstrength = lightstrength()
	T_amb = T_amb - 2*lightstrength/100000   # when the lightstrength is at its maximum 2degC is subtracted
	
	sh.building.ambient_temperature(T_amb)

	# set rain and wind
	rain = sh.return_item(sh.building.rain.sensor.conf['item'])
	rain = rain()
	sh.building.rain(rain)
	
	wind = sh.return_item(sh.building.wind_velocity.sensor.conf['item'])
	wind = wind()
	sh.building.wind_velocity(wind)
	
	# calculate heat flows for each room in the zone
	zone_str  = zone.id().split('.')
	zone_str = zone_str[-1]
	
	heat_flow_transmission = 0
	heat_flow_ventilation  = 0
	heat_flow_infiltration = 0
	heat_flow_internal     = 0
	heat_flow_irradiation  = 0
	heat_flow_irradiation_max = 0
	heat_flow_irradiation_min = 0


	# calculate using the estimated model parameters
	# transmission to the exterior
	# UA = [UA_1amb UA_12 UA_13 UA_2amb UA_23 UA_3amb]
	# i = zone number
	# n = number of zones
	# 0 -> 0   1 -> 0+n  2 -> 0+n+n-1  3 -> 0+n+n+n-3
	#
	# transform UA list into UA matrix
	# UA_item = building.model.UA()
	# UA = [[ UA_item[0],UA_item[1],UA_item[2]],[UA_item[1],UA_item[3],UA_item[4]],[UA_item[2],UA_item[4],UA_item[5]]]
	# heat_flow_transmission = UA[i,i]*(T_amb-T_op)
	# for tempzone in sh.building.zones:
	#   if not(i==j):
	#	heat_flow_transmission = heat_flow_transmission + UA[i,j]*(tempzone.T_operational()-T_op)	
	
	
	for room in sh.find_items('zone'):
		if room.conf['zone'] == zone_str:
		
			logger.info(room.id())

			# transmission heat flow
			# calculate the UA value taking windows into account
			A_windows = 0
			UA_windows = 0
			
			if hasattr(room, 'windows'):
				for window in room.windows.return_children():
					A_windows = A_windows + float(window.conf['area'])
					UA_windows = UA_windows + float(window.conf['area'])*float(window.conf['U'])

			UA = float(room.conf['U'])*(float(room.conf['lossarea'])-A_windows) + UA_windows
			heat_flow_transmission = heat_flow_transmission + UA*(T_amb-T_op)
				
			# irradiation heat flow through windows
			if hasattr(room, 'windows'):
				for window in room.windows.return_children():
			
					# solar irradiation values
					E_b = sh.building.irradiation.direct_theoretical()*sh.building.irradiation.cloud_factor()
					E_d = sh.building.irradiation.diffuse_theoretical()*sh.building.irradiation.cloud_factor()
					
					window_tilt = float(window.conf['tilt'])*d2r
					window_orientation = float(window.conf['orientation'])*d2r
					
					# surface solar azimuth (-90deg< gamma < 90deg, else surface is in shade)
					gamma = azimut-window_orientation
					
					# surface solar incidence angle
					cos_theta = math.cos(altitude)*math.cos(gamma)*math.sin(window_tilt) + math.sin(altitude)*math.cos(window_tilt)
					# beam radiation
					if cos_theta > 0:
						E_tb = E_b*cos_theta
					else:
						E_tb = 0
					# diffuse radiation
					Y = max(0.45, 0.55 + 0.437*cos_theta+ 0.313*cos_theta**2)
					E_td = E_d*Y*math.sin(window_tilt)
					
					# ground reflected radiation
					rho_g = 0.2
					E_tr = (E_b*math.sin(altitude) +E_d)*rho_g*(1-math.cos(window_tilt))/2
					
					# total irradiation as if shading was competely open
					window_heat_flow_irradiation_max = float(window.conf['area'])*float(window.conf['transmittance'])*(E_tb + E_td + E_tr)
					heat_flow_irradiation_max = heat_flow_irradiation_max + window_heat_flow_irradiation_max
					window.heat_flow_irradiation_max(window_heat_flow_irradiation_max)
					
					# get shading position if shading is present
					shading_pos = 0
					shading_trans = 1
					if hasattr(window, 'shading'):
						shading = window.shading
						shading_pos = shading.pos()/255
						shading_trans = float(shading.conf['transmittance'])
					
					heat_flow_irradiation = heat_flow_irradiation + window_heat_flow_irradiation_max*shading_pos*shading_trans + window_heat_flow_irradiation_max*(1-shading_pos)
					heat_flow_irradiation_min = heat_flow_irradiation_min + window_heat_flow_irradiation_max*shading_trans
			else:
				heat_flow_irradiation = 0
				heat_flow_irradiation_max = 0
				heat_flow_irradiation_min = 0

		
	# internal heat gains
	electricity = sh.building.flukso.elektriciteit_totaal() - sh.building.flukso.elektriciteit_verwarming()
	heat_flow_internal = electricity/num_zones
	
	# ventilation heat flow
	V_flow = 1
	heat_flow_ventilation     = 0*(1-0.85)*1.22*1004/3600*(T_amb-T_op)
	heat_flow_ventilation_max = 0*(1-0.85)*1.22*1004/3600*(T_amb-T_op)
	heat_flow_ventilation_min = 0*(1-0.85)*1.22*1004/3600*(T_amb-T_op)
		
	# set the value of the heat flows
	zone.heat_flow_transmission(heat_flow_transmission)
	zone.heat_flow_ventilation(heat_flow_ventilation)
	zone.heat_flow_ventilation_max(heat_flow_ventilation_max)
	zone.heat_flow_ventilation_min(heat_flow_ventilation_min)
	zone.heat_flow_internal(heat_flow_internal)
	zone.heat_flow_irradiation(heat_flow_irradiation)
	zone.heat_flow_irradiation_max(heat_flow_irradiation_max)
	zone.heat_flow_irradiation_min(heat_flow_irradiation_min)
	

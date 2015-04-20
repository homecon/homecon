# Create entries in measurements_legend for items that must be logged when they are present
#
#
#


import pymysql

con = pymysql.connect('localhost', 'knxcontrol', sh.building.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()

query = "REPLACE INTO measurements_legend (id,item,name,quantity,unit,description) VALUES "
id = 0

id = id+1
query = query+"('"+str(id)+"','building.ambient_temperature','Temperature','Temperature','degC','Outside temperature'),"
id = id+1
query = query+"('"+str(id)+"','building.irradiation.azimut','Azimut','Angle','deg','Solar azimut'),"
id = id+1
query = query+"('"+str(id)+"','building.irradiation.altitude','Altitude','Angle','deg','Solar altitude'),"
id = id+1
query = query+"('"+str(id)+"','building.irradiation.direct_theoretical','Direct','Heat flux','W/m2','Theoretical direct solar irradiation'),"
id = id+1
query = query+"('"+str(id)+"','building.irradiation.diffuse_theoretical','Diffuse','Heat flux','W/m2','Theoretical diffuse solar irradiation'),"
id = id+1
query = query+"('"+str(id)+"','building.irradiation.cloud_factor','Clouds','','-','Cloud factor'),"
id = id+1
query = query+"('"+str(id)+"','building.wind_velocity','Wind speed','Velocity','m/s','Wind speed'),"
id = id+1
query = query+"('"+str(id)+"','building.rain','Rain','','-','Rain or not'),"											


id = 8
if hasattr(sh.building, 'flukso'):
	for sensor in sh.building.flukso:
		id = id + 1
		name = sensor.id().split(".")[-1]
		if sensor.conf['unit']=='watt':
			quantity  = 'Power'
			unit = 'W'
		elif sensor.conf['unit']=='l/min':
			quantity  = 'Flow rate'
			unit = 'l/min'	
		else:
			quantity  = 'Power'
			unit = 'W'
			
		query = query+"('"+str(id)+"','"+sensor.id()+"','"+name+"','"+quantity+"','"+unit+"','flukso "+name+"'),"

id = 14	
if hasattr(sh.building, 'zones'):
	for zone in sh.building.zones:
		id = id + 1
		zone_name = zone.id().split(".")[-1]
		query = query+"('"+str(id)+"','"+zone.T_operational.id()+"','Temperature','Temperature','degC','"+zone_name+" temperature'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+zone.heat_flow_transmission.id()+"','Transmission','Heat flow','W','"+zone_name+" transmission heat flow'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+zone.heat_flow_ventilation.id()+"','Ventilation','Heat flow','W','"+zone_name+" ventilation heat flow'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+zone.heat_flow_internal.id()+"','Internal','Heat flow','W','"+zone_name+" internal heat flow'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+zone.heat_flow_irradiation.id()+"','Irradiation','Heat flow','W','"+zone_name+" irradiation heat flow'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+zone.heat_flow_heating_wanted.id()+"','Heating','Heat flow','W','"+zone_name+" wanted heating heat flow'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+zone.heat_flow_cooling_wanted.id()+"','Cooling','Heat flow','W','"+zone_name+" wanted cooling heat flow'),"
		
		
query = query[:-1]

# try to execute query
try:
	cur.execute( query )
except:
	logger.warning("could not add default measurements to database")
	logger.warning(query)
	
con.commit()	
con.close()

def _measurements_init(sh)
	""" Function fills in the mysql measurement_legend with items required for knxcontrol
	arguments:
	sh: smarthome object
	"""
	con = pymysql.connect('localhost', 'knxcontrol', sh.knxcontrol.mysql.conf['password'], 'knxcontrol')
	cur = con.cursor()

	query = "REPLACE INTO measurement_legend (id,item,name,quantity,unit,description) VALUES "

	id = 0
	# current weather 20 components max
	id = id+1
	query = query+"('"+str(id)+"','knxcontrol.weather.current.temperature','Temperature','Temperature','degC','Ambient temperature'),"
	id = id+1
	query = query+"('"+str(id)+"','knxcontrol.weather.current.humidity','Humidity','Humidity','-','Relative ambient humidity'),"
	id = id+1
	query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.direct','Direct','Heat flux','W/m2','Estimated direct solar irradiation'),"
	id = id+1
	query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.diffuse','Diffuse','Heat flux','W/m2','Estimated diffuse solar irradiation'),"
	id = id+1
	query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.clouds','Clouds','','-','Cloud factor'),"
	id = id+1
	query = query+"('"+str(id)+"','knxcontrol.weather.current.precipitation','Rain','','-','Rain or not'),"											
	id = id+1
	query = query+"('"+str(id)+"','knxcontrol.weather.current.wind.speed','Wind speed','Velocity','m/s','Wind speed'),"
	id = id+1
	query = query+"('"+str(id)+"','knxcontrol.weather.current.wind.direction','Wind direction','Angle','deg','Wind direction (0deg is North)'),"



	id = 20
	# energy use 5 components max
	for item in sh.knxcontrol.energy:
		item_name = item.id().split(".")[-1]
		id = id+1
		query = query+"('"+str(id)+"','"+item.id()+"','"+item_name+"','"+item.conf['quantity']+"','"+item.conf['unit']+"','"+item_name+" use'),"



	id = 100
	# building zones 10 zones max
	for item in sh.knxcontrol.building:
		item_name = item.id().split(".")[-1]
		id = id + 1
		query = query+"('"+str(id)+"','"+item.temperature.id()+"','Temperature','Temperature','degC','"+item_name+" temperature'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+item.airquality.id()+"','Air quality','Concentration','g CO2/m3','"+item_name+" CO2 concentration'),"



	id = 120
	# ventilation 10 systems max
	for item in sh.knxcontrol.ventilation:
		item_name = item.id().split(".")[-1]
		id = id + 1
		query = query+"('"+str(id)+"','"+item.fanspeed.id()+"','"+item_name+" fanspeed','','-','"+item_name+" fan speed control signal'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+item.heatrecovery.id()+"','"+item_name+" heatrecovery','','-','"+item_name+" heat recovery control signal'),"



	id = 140
	# heat production 10 systems max
	for system in sh.knxcontrol.heat.production:
		system_name = system.id().split(".")[-1]
		id = id + 1
		query = query+"('"+str(id)+"','"+system.power.id()+"','"+system_name+" Power','Power','W','"+system_name+" heat production'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+system.control.id()+"','"+system_name+" Control','','-','"+system_name+" control signal'),"



	id = 160
	# heat emission 10 systems max
	for system in sh.knxcontrol.heat.emission:
		system_name = system.id().split(".")[-1]
		id = id + 1
		query = query+"('"+str(id)+"','"+system.power.id()+"','"+system_name+" Power','Power','W','"+system_name+" heat emission'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+system.control.id()+"','"+system_name+" Control','','-','"+system_name+" control signal'),"



	id = 180
	# electricity generation 10 systems max
	for system in sh.knxcontrol.electricity.production:
		system_name = system.id().split(".")[-1]
		id = id + 1
		query = query+"('"+str(id)+"','"+system.power.id()+"','"+system_name+" Power','Power','W','"+system_name+" electricity generation'),"
		id = id + 1
		query = query+"('"+str(id)+"','"+system.control.id()+"','"+system_name+" Control','','-','"+system_name+" control signal'),"

	# try to execute query
	query = query[:-1]
	try:
		cur.execute( query )
		logger.info("Measurements initialized")
	except:
		logger.warning("could not add default measurements to database")
		logger.warning(query)

	con.commit()	
	con.close()


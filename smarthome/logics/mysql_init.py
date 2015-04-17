# Create basic mysql structure if it is not present yet


import pymysql

con = pymysql.connect('localhost', 'knxcontrol', sh.knxcontrol.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()


# users table
query = ("CREATE TABLE IF NOT EXISTS `users` ("
         "`id` int(11) NOT NULL AUTO_INCREMENT,"
         "`username` varchar(255) NOT NULL,"
         "`password` varchar(255) NOT NULL,"
         "PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )
try:
	cur.execute( query )
except:
	logger.warning("Could not add users table to database")

# default user
query = "INSERT IGNORE INTO `users` (id,username,password) VALUES (1,'admin','c3284d0f94606de1fd2af172aba15bf3')"
try:
	cur.execute( query )
except:
	logger.warning("Could not add admin to database")

# data
query = ("CREATE TABLE IF NOT EXISTS `data` ("
         "`id` int(11) NOT NULL AUTO_INCREMENT,"
         "`ip` varchar(255) NOT NULL,"
         "`port` varchar(255) NOT NULL,"
         "`web_ip` varchar(255) NOT NULL,"
         "`web_port` varchar(255) NOT NULL,"
         "`token` varchar(255) NOT NULL,"
         "`latitude` float NOT NULL,"
         "`longitude` float NOT NULL,"
         "`elevation` float NOT NULL,"
         "PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
	)
try:
	cur.execute( query )
except:
	logger.warning("Could not add data table to database")

# default data
query = "INSERT IGNORE INTO `data` (id,ip,port,web_ip,web_port,token,latitude,longitude,elevation) VALUES (1,'192.168.255.1','2424','mydomain.duckdns.org','9024','admin',51,5,70)"
try:
	cur.execute( query )
except:
	logger.warning("Could not add data to database")

# location data
query = "UPDATE data SET latitude=%f,longitude=%f,elevation=%f WHERE id=1" % (float(sh._lat),float(sh._lon),float(sh._elev))
try:
	cur.execute( query )
except:
	logger.warning("Could not add location to database")

# alarms
query = ("CREATE TABLE IF NOT EXISTS `alarms` ("
         "`id` int(11) NOT NULL AUTO_INCREMENT,"
         "`sectionid` int(11) NOT NULL DEFAULT '1',"
         "`active` tinyint(4) NOT NULL DEFAULT '1',"
         "`action_id` int(11) DEFAULT NULL,"
         "`hour` tinyint(4) NOT NULL DEFAULT '12',"
         "`minute` tinyint(4) NOT NULL DEFAULT '0',"
         "`sunrise` tinyint(4) NOT NULL DEFAULT '0',"
         "`sunset` tinyint(4) NOT NULL DEFAULT '0',"
         "`mon` tinyint(4) NOT NULL DEFAULT '1',"
         "`tue` tinyint(4) NOT NULL DEFAULT '1',"
         "`wed` tinyint(4) NOT NULL DEFAULT '1',"
         "`thu` tinyint(4) NOT NULL DEFAULT '1',"
         "`fri` tinyint(4) NOT NULL DEFAULT '1',"
         "`sat` tinyint(4) NOT NULL DEFAULT '0',"
         "`sun` tinyint(4) NOT NULL DEFAULT '0',"
         "PRIMARY KEY (`id`) ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )
try:
	cur.execute( query )
except:
	logger.warning("Could not add alarms table to database")


# actions
query = ("CREATE TABLE IF NOT EXISTS `actions` ("
         "`id` int(11) NOT NULL AUTO_INCREMENT,"
         "`name` varchar(255) DEFAULT NULL,"
         "`sectionid` varchar(255) DEFAULT NULL,"
         "`delay1` int(11) DEFAULT NULL,"
         "`item1` varchar(255) DEFAULT NULL,"
         "`value1` varchar(255) DEFAULT NULL,"
         "`delay2` int(11) DEFAULT NULL,"
         "`item2` varchar(255) DEFAULT NULL,"
         "`value2` varchar(255) DEFAULT NULL,"
         "`delay3` int(11) DEFAULT NULL,"
         "`item3` varchar(255) DEFAULT NULL,"
         "`value3` varchar(255) DEFAULT NULL,"	
         "`delay4` int(11) DEFAULT NULL,"
         "`item4` varchar(255) DEFAULT NULL,"
         "`value4` varchar(255) DEFAULT NULL,"	
         "`delay5` int(11) DEFAULT NULL,"
         "`item5` varchar(255) DEFAULT NULL,"
         "`value5` varchar(255) DEFAULT NULL,"	
         "PRIMARY KEY (`id`) ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )
try:
	cur.execute( query )
except:
	logger.warning("Could not add actions table to database")

# measurements legend
query = ("CREATE TABLE IF NOT EXISTS `measurement_legend` ("
         "`id` int(11) NOT NULL AUTO_INCREMENT,"
         "`item` varchar(255) DEFAULT NULL,"
         "`name` varchar(255) DEFAULT NULL,"
         "`quantity` varchar(255) DEFAULT NULL,"
         "`unit` varchar(255) DEFAULT NULL,"
         "`description` text DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )
try:
	cur.execute( query )
except:
	logger.warning("Could not add measurement_legend table to database")


# measurements
query = ("CREATE TABLE IF NOT EXISTS `measurement` ("
         "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
         "`signal_id` tinyint(4) NOT NULL,"
         "`time` bigint(20) NOT NULL,"
         "`value` float DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )
try:
	cur.execute( query )
except:
	logger.warning("Could not add measurement table to database")

query = "CREATE INDEX time_signal_id ON measurement(time, signal_id)"
try:
	cur.execute( query )
except:
	logger.warning("Index on measurements allready exists")

# quarterhour average measurements
query = ("CREATE TABLE IF NOT EXISTS `measurement_average_quarterhour` ("
         "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
         "`signal_id` tinyint(4) NOT NULL,"
         "`time` int(11) NOT NULL,"
         "`value` float DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )												 						 
try:
	cur.execute( query )
except:
	logger.warning("Could not add quarterhour measurement_average_quarterhour table to database")

query = "CREATE INDEX time_signal_id ON measurement_average_quarterhour(time, signal_id)"
try:
	cur.execute( query )
except:
	logger.warning("Index on measurement_average_quarterhour allready exists")

# week average measurements
query = ("CREATE TABLE IF NOT EXISTS `measurement_average_week` ("
         "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
         "`signal_id` tinyint(4) NOT NULL,"
         "`time` int(11) NOT NULL,"
         "`value` float DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )												 						 
try:
	cur.execute( query )
except:
	logger.warning("Could not add measurement_average_week table to database")

query = "CREATE INDEX time_signal_id ON measurement_average_week(time, signal_id)"
try:
	cur.execute( query )
except:
	logger.warning("Index on measurement_average_week allready exists")

# month average measurements
query = ("CREATE TABLE IF NOT EXISTS `measurement_average_month` ("
         "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
         "`signal_id` tinyint(4) NOT NULL,"
         "`time` int(11) NOT NULL,"
         "`value` float DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )												 						 
try:
	cur.execute( query )
except:
	logger.warning("Could not add measurement_average_month table to database")

query = "CREATE INDEX time_signal_id ON measurement_average_month(time, signal_id)"
try:
	cur.execute( query )
except:
	logger.warning("Index on measurement_average_month allready exists")


# profile legend
query = ("CREATE TABLE IF NOT EXISTS `profile_legend` ("
         "`id` tinyint(4) NOT NULL AUTO_INCREMENT,"
         "`name` varchar(255) DEFAULT NULL,"
         "`quantity` varchar(255) DEFAULT NULL,"
         "`unit` varchar(255) DEFAULT NULL,"
         "`description` text DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )
try:
	cur.execute( query )
except:
	logger.warning("Could not add profile_legend table to database")

# profile
query = ("CREATE TABLE IF NOT EXISTS `profile` ("
         "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
         "`profile_id` tinyint(4) NOT NULL,"
         "`time` bigint(20) NOT NULL,"
         "`value` float DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )
try:
	cur.execute( query )
except:
	logger.warning("Could not add profile table to database")


# pagebuilder
query = ("CREATE TABLE IF NOT EXISTS `pagebuilder` ("
         "`id` int(11) NOT NULL AUTO_INCREMENT,"
         "`model` MEDIUMTEXT DEFAULT NULL,"
         "PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
         )
try:
	cur.execute( query )
except:
	logger.warning("Could not add pagebuilder table to database")

query = "INSERT IGNORE INTO `pagebuilder` (id,model) VALUES (1,'[{\"id\":\"home\",\"name\":\"Home\",\"page\":[{\"id\":\"home\",\"name\":\"Home\",\"img\":\"\",\"temperature_item\":\"\",\"section\":[]}]}]')"
try:
	cur.execute( query )
except:
	logger.warning("Could not add pagebuilder data to database")

query = "INSERT IGNORE INTO `pagebuilder` (id,model) VALUES (2,'[{\"id\":\"home\",\"name\":\"Home\",\"page\":[{\"id\":\"home\",\"name\":\"Home\",\"img\":\"\",\"temperature_item\":\"\",\"section\":[]}]}]')"
try:
	cur.execute( query )
except:
	logger.warning("Could not add pagebuilder data to database")

logger.info("Database initialized")



########################################################################################
# Create entries in measurements_legend for items that must be logged

query = "REPLACE INTO measurement_legend (id,item,name,quantity,unit,description) VALUES "


# current weather 15 components max
id = 0
query = query+"('"+str(id)+"','knxcontrol.weather.current.temperature','Temperature','Temperature','degC','Ambient temperature'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.theoretical.azimut','Azimut','Angle','deg','Solar azimut (0deg is south)'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.theoretical.altitude','Altitude','Angle','deg','Solar altitude'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.theoretical.direct','Direct','Heat flux','W/m2','Theoretical direct solar irradiation'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.theoretical.diffuse','Diffuse','Heat flux','W/m2','Theoretical diffuse solar irradiation'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.estimate.direct','Direct','Heat flux','W/m2','Estimated direct solar irradiation'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.estimate.diffuse','Diffuse','Heat flux','W/m2','Estimated diffuse solar irradiation'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.irradiation.estimate.clouds','Clouds','','-','Cloud factor'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.precipitation','Rain','','-','Rain or not'),"											
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.wind.speed','Wind speed','Velocity','m/s','Wind speed'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.weather.current.wind.direction','Wind direction','Angle','deg','Wind direction (0deg is North)'),"


# leave some blanks
id = 20
# energy use 5 components max
id = id+1
query = query+"('"+str(id)+"','knxcontrol.energy.electricity','Electricity','Power','W','Electricity use'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.energy.gas','Gas','Power','W','Natural gas use'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.energy.fueloil','Fuel oil','Power','W','Fuel oil use'),"
id = id+1
query = query+"('"+str(id)+"','knxcontrol.energy.water','Water','Flow','l/min','Water use'),"



# building zones 10 zones max
id = 100
for zone in sh.knxcontrol.building:
	zone_name = zone.id().split(".")[-1]
	id = id + 1
	query = query+"('"+str(id)+"','"+zone.temperature.id()+"','Temperature','Temperature','degC','"+zone_name+" temperature'),"
	id = id + 1
	query = query+"('"+str(id)+"','"+zone.airquality.id()+"','Air quality','Concentration','g CO2/m3','"+zone_name+" CO2 concentration'),"
	

# ventilation 10 systems max
id = 120
id = id + 1
query = query+"('"+str(id)+"','knxcontrol.ventilation.fanspeed','Ventilation control','','-','Ventilation fan speed control signal'),"
id = id + 1
query = query+"('"+str(id)+"','knxcontrol.ventilation.heatrecovery','Heat recovery control','','-','Ventilation heat recovery control signal'),"


# heat production 10 systems max
id = 140
for system in sh.knxcontrol.heat.production:
	system_name = system.id().split(".")[-1]
	id = id + 1
	query = query+"('"+str(id)+"','"+system.power.id()+"','"+system_name+" Power','Power','W','"+system_name+" heat production'),"
	id = id + 1
	query = query+"('"+str(id)+"','"+system.control.id()+"','"+system_name+" Control','','-','"+system_name+" control signal'),"


# heat emission 10 systems max
id = 160
for system in sh.knxcontrol.heat.emission:
	system_name = system.id().split(".")[-1]
	id = id + 1
	query = query+"('"+str(id)+"','"+system.power.id()+"','"+system_name+" Power','Power','W','"+system_name+" heat emission'),"
	id = id + 1
	query = query+"('"+str(id)+"','"+system.control.id()+"','"+system_name+" Control','','-','"+system_name+" control signal'),"


# electricity generation 10 systems max
id = 180
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

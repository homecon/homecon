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
#query = "UPDATE data (latitude,longitude,elevation) VALUES (%f,%f,%f) WHERE id=1" % (sh._lat(),sh._lon(),sh._elev())
#try:
#	cur.execute( query )
#except:
#	logger.warning("Could not add location to database")

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
query = ("CREATE TABLE IF NOT EXISTS `measurements_legend` ("
         "`id` tinyint(4) NOT NULL AUTO_INCREMENT,"
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
	logger.warning("Could not add measurements_legend table to database")


# measurements
query = ("CREATE TABLE IF NOT EXISTS `measurements` ("
         "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
         "`signal_id` tinyint(4) NOT NULL,"
         "`time` bigint(20) NOT NULL,"
         "`value` float DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )
try:
	cur.execute( query )
except:
	logger.warning("Could not add measurements table to database")

query = "CREATE INDEX time_signal_id ON measurements(time, signal_id)"
try:
	cur.execute( query )
except:
	logger.warning("Could not add index to measurements table")

# quarterhour average measurements
query = ("CREATE TABLE IF NOT EXISTS `measurements_average_quarterhour` ("
         "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
         "`signal_id` tinyint(4) NOT NULL,"
         "`time` int(11) NOT NULL,"
         "`value` float DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )												 						 
try:
	cur.execute( query )
except:
	logger.warning("Could not add quarterhour measurements table to database")

query = "CREATE INDEX time_signal_id ON measurements_average_quarterhour(time, signal_id)"
try:
	cur.execute( query )
except:
	logger.warning("Could not add index to quarterhour measurements table")

# week average measurements
query = ("CREATE TABLE IF NOT EXISTS `measurements_average_week` ("
         "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
         "`signal_id` tinyint(4) NOT NULL,"
         "`time` int(11) NOT NULL,"
         "`value` float DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )												 						 
try:
	cur.execute( query )
except:
	logger.warning("Could not add week measurements table to database")

query = "CREATE INDEX time_signal_id ON measurements_average_week(time, signal_id)"
try:
	cur.execute( query )
except:
	logger.warning("Could not add index to week measurements table")

# month average measurements
query = ("CREATE TABLE IF NOT EXISTS `measurements_average_month` ("
         "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
         "`signal_id` tinyint(4) NOT NULL,"
         "`time` int(11) NOT NULL,"
         "`value` float DEFAULT NULL,"
         "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1"
        )												 						 
try:
	cur.execute( query )
except:
	logger.warning("Could not add month measurements table to database")

query = "CREATE INDEX time_signal_id ON measurements_average_month(time, signal_id)"
try:
	cur.execute( query )
except:
	logger.warning("Could not add index to month measurements table")

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

logger.warning("Database initialized")

con.commit()	
con.close()

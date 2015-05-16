#!/usr/bin/env python3

import logging
import pymysql
import datetime

logger = logging.getLogger('')

class Mysql:

	def __init__(self,knxcontrol):
		"""
		A mysql object is created
		and mysql tables required for knxcontrol are created
		
		arguments:
		smarthome:   smarthome object
		mysql_pass:  mysql password 
		"""

		self.knxcontrol = knxcontrol
		self._sh = knxcontrol._sh
		self._mysql_pass = knxcontrol._mysql_pass

		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		# users table
		query = ("CREATE TABLE IF NOT EXISTS `users` ("
				 "`id` int(11) NOT NULL AUTO_INCREMENT,"
				 "`username` varchar(255) NOT NULL,"
				 "`password` varchar(255) NOT NULL,"
				 "PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
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
				 "PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
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
		query = "UPDATE data SET latitude=%f,longitude=%f,elevation=%f WHERE id=1" % (float(self._sh._lat),float(self._sh._lon),float(self._sh._elev))
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
				 "PRIMARY KEY (`id`) ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
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
				 "PRIMARY KEY (`id`) ) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
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
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add measurement_legend table to database")


		# measurements
		query = ("CREATE TABLE IF NOT EXISTS `measurement` ("
				 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
				 "`signal_id` int(11) NOT NULL,"
				 "`time` bigint(20) NOT NULL,"
				 "`value` float DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add measurement table to database")

		query = "CREATE INDEX time_signal_id ON measurement(time, signal_id)"
		try:
			cur.execute( query )
		except:
			pass

		# quarterhour average measurements
		query = ("CREATE TABLE IF NOT EXISTS `measurement_average_quarterhour` ("
				 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
				 "`signal_id` int(11) NOT NULL,"
				 "`time` int(11) NOT NULL,"
				 "`value` float DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")												 						 
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add quarterhour measurement_average_quarterhour table to database")

		query = "CREATE INDEX time_signal_id ON measurement_average_quarterhour(time, signal_id)"
		try:
			cur.execute( query )
		except:
			pass

		# week average measurements
		query = ("CREATE TABLE IF NOT EXISTS `measurement_average_week` ("
				 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
				 "`signal_id` int(11) NOT NULL,"
				 "`time` int(11) NOT NULL,"
				 "`value` float DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")												 						 
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add measurement_average_week table to database")

		query = "CREATE INDEX time_signal_id ON measurement_average_week(time, signal_id)"
		try:
			cur.execute( query )
		except:
			pass

		# month average measurements
		query = ("CREATE TABLE IF NOT EXISTS `measurement_average_month` ("
				 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
				 "`signal_id` int(11) NOT NULL,"
				 "`time` int(11) NOT NULL,"
				 "`value` float DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")												 						 
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add measurement_average_month table to database")

		query = "CREATE INDEX time_signal_id ON measurement_average_month(time, signal_id)"
		try:
			cur.execute( query )
		except:
			pass

		# profile legend
		query = ("CREATE TABLE IF NOT EXISTS `profile_legend` ("
				 "`id` int(11) NOT NULL AUTO_INCREMENT,"
				 "`name` varchar(255) DEFAULT NULL,"
				 "`quantity` varchar(255) DEFAULT NULL,"
				 "`unit` varchar(255) DEFAULT NULL,"
				 "`description` text DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add profile_legend table to database")

		# profile
		query = ("CREATE TABLE IF NOT EXISTS `profile` ("
				 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
				 "`profile_id` int(11) NOT NULL,"
				 "`time` bigint(20) NOT NULL,"
				 "`value` float DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add profile table to database")


		# pagebuilder
		query = ("CREATE TABLE IF NOT EXISTS `pagebuilder` ("
				 "`id` int(11) NOT NULL AUTO_INCREMENT,"
				 "`model` MEDIUMTEXT DEFAULT NULL,"
				 "PRIMARY KEY (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
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
		
		
		
	def backup(self):
		"""
		backup mysql data without measurements to backupdir
		"""
		pass


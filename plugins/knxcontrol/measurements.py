#!/usr/bin/env python3

import logging
import pymysql
import datetime
import numpy as np

logger = logging.getLogger('')

class Measurements:

	def __init__(self,knxcontrol):
		"""
		A measurements object is created
		and mysql measurement_legend is filled with items required for knxcontrol
		and measurement ids are stored for reference
		
		arguments:
		smarthome:   smarthome object
		mysql_pass:  mysql password 


		there are 2 kinds of measurements: defined by knxcontrol, required for functioning and defined by the user, for reference
		both kinds should have the same capabilities
		the string in item determines the value which is stored.
		"""

		self._sh = knxcontrol._sh
		self._mysql_pass = knxcontrol._mysql_pass
		self.legend = {}

		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()
		

		# measurements legend
		query = ("CREATE TABLE IF NOT EXISTS `measurements_legend` ("
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
			logger.warning("Could not add measurements_legend table to database")


		# measurements
		query = ("CREATE TABLE IF NOT EXISTS `measurements` ("
				 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
				 "`signal_id` int(11) NOT NULL,"
				 "`time` bigint(20) NOT NULL,"
				 "`value` float DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add measurements table to database")

		query = "CREATE INDEX time_signal_id ON measurements(time, signal_id)"
		try:
			cur.execute( query )
		except:
			pass

		# quarterhour average measurements
		query = ("CREATE TABLE IF NOT EXISTS `measurements_average_quarterhour` ("
				 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
				 "`signal_id` int(11) NOT NULL,"
				 "`time` int(11) NOT NULL,"
				 "`value` float DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")												 						 
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add quarterhour measurements_average_quarterhour table to database")

		query = "CREATE INDEX time_signal_id ON measurements_average_quarterhour(time, signal_id)"
		try:
			cur.execute( query )
		except:
			pass

		# week average measurements
		query = ("CREATE TABLE IF NOT EXISTS `measurements_average_week` ("
				 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
				 "`signal_id` int(11) NOT NULL,"
				 "`time` int(11) NOT NULL,"
				 "`value` float DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")												 						 
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add measurements_average_week table to database")

		query = "CREATE INDEX time_signal_id ON measurements_average_week(time, signal_id)"
		try:
			cur.execute( query )
		except:
			pass

		# month average measurements
		query = ("CREATE TABLE IF NOT EXISTS `measurements_average_month` ("
				 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
				 "`signal_id` int(11) NOT NULL,"
				 "`time` int(11) NOT NULL,"
				 "`value` float DEFAULT NULL,"
				 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1")												 						 
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add measurements_average_month table to database")

		query = "CREATE INDEX time_signal_id ON measurements_average_month(time, signal_id)"
		try:
			cur.execute( query )
		except:
			pass


		id = 0
		# current weather 20 components max
		item = self._sh.return_item('knxcontrol.weather.current.temperature')
		id = id+1
		self.add_legend_item(id,item,name='Temperature',quantity='Temperature',unit='degC',description='Ambient temperature')
		
		item = self._sh.return_item('knxcontrol.weather.current.humidity')
		id = id+1
		self.add_legend_item(id,item,name='Humidity',quantity='Humidity',unit='-',description='Relative ambient humidity')

		item = self._sh.return_item('knxcontrol.weather.current.irradiation.horizontal')
		id = id+1
		self.add_legend_item(id,item,name='Horizontal irradiation',quantity='Heat flux',unit='W/m2',description='Estimated global horizontal solar irradiation')

		item = self._sh.return_item('knxcontrol.weather.current.irradiation.clouds')
		id = id+1
		self.add_legend_item(id,item,name='Clouds',quantity='',unit='-',description='Estimated cloud cover')
		
		item = self._sh.return_item('knxcontrol.weather.current.precipitation')
		id = id+1
		self.add_legend_item(id,item,name='Rain',quantity='Boolean',unit='-',description='Rain or not')
										
		item = self._sh.return_item('knxcontrol.weather.current.wind.speed')
		id = id+1
		self.add_legend_item(id,item,name='Wind speed',quantity='Velocity',unit='m/s',description='Wind speed')

		item = self._sh.return_item('knxcontrol.weather.current.wind.direction')
		id = id+1
		self.add_legend_item(id,item,name='Wind direction',quantity='Angle',unit='deg',description='Wind direction (0deg is North, 90deg is East)')

		id = 20
		# energy use 10 components max
		for item in self._sh.return_item('knxcontrol.energy'):
			item_name = item.id().split(".")[-1]
			id = id+1 
			self.add_legend_item(id,item,name=item_name,quantity=item.conf['quantity'],unit=item.conf['unit'],description=item_name+' use')

		id = 100
		# building zones 10 zones max
		for item in self._sh.find_items('zonetype'):
			item_name = item.id().split(".")[-1]
			id = id + 1
			self.add_legend_item(id,item.temperature,name='Temperature',quantity='Temperature',unit='degC',description=item_name+' temperature')

			id = id + 1
			self.add_legend_item(id,item.airquality,name='Air quality',quantity='Concentration',unit='g CO2/m3',description=item_name+' CO2 concentration')

			id = id + 1
			self.add_legend_item(id,item.irradiation,name='Solar gains',quantity='Power',unit='W',description=item_name+' irradiation power')

			id = id + 1
			self.add_legend_item(id,item.emission,name='Emission',quantity='Power',unit='W',description=item_name+' emission power')

		id = 250
		# ventilation 10 systems max
		for item in self._sh.return_item('knxcontrol.ventilation'):
			item_name = item.id().split(".")[-1]
			id = id + 1
			self.add_legend_item(id,item.fanspeed,name=item_name+' fanspeed',quantity='',unit='-',description=item_name+' fan speed control signal')

			id = id + 1
			self.add_legend_item(id,item.heatrecovery,name=item_name+' heatrecovery',quantity='',unit='-',description=item_name+' heat recovery control signal')

		id = 270
		# heat production 10 systems max
		for item in self._sh.return_item('knxcontrol.heat_production'):
			item_name = item.id().split(".")[-1]
			id = id + 1
			self.add_legend_item(id,item.power,name=item_name+' power',quantity='Power',unit='W',description=item_name+' heat production')

		id = 290
		# electricity generation 10 systems max
		for item in self._sh.return_item('knxcontrol.electricity_production'):
			item_name = item.id().split(".")[-1]
			id = id + 1
			self.add_legend_item(id,item.power,name=item_name+' power',quantity='Power',unit='W',description=item_name+' electricity generation')



		logger.warning('Measurements initialized')



	def add_legend_item(self,id,item,name,quantity,unit,description):
		"""
		Adds an object to the local legend dict.
		obj must be a SmartHome.py item
		"""
		item.conf['mysql_id'] = id
		
		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()
		try:
			query = "REPLACE INTO measurements_legend (id,item,name,quantity,unit,description) VALUES ('"+str(id)+"','"+item.id()+"','"+name+"','"+quantity+"','"+unit+"','"+description+"')"
			cur.execute( query )
		except:
			logger.warning('could not add legend item: '+name)

		con.commit()	
		con.close()


	def minute(self):
		"""
		store all measurements in MySQL
		"""
		# remove seconds from utctime and add :00 and subtract 60 seconds as it is data of the past minute
		now = datetime.datetime.utcnow().replace( second=0, microsecond=0)
		timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )-60

		# connect to the mysql database
		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		legend = con.cursor()
		legend.execute("SELECT id,item FROM measurements_legend WHERE item <> ''")


		# create mysql query
		query = "INSERT INTO measurements (signal_id,time,value) VALUES "

		# run through legend
		for measurement in legend:
			try:
				item = self._sh.return_item(measurement[1])
				
				query = query + "(%s,%s,%f)," % (measurement[0],timestamp,item())
			except:
				logger.warning( "legend entry "+measurement[0]+": "+measurement[1]+", is not an item")
			
		query = query[:-1]

		# try to execute query
		try :
			cur.execute( query )
		except:
			logger.warning("could not add measurements to database")
			
		con.commit()	
		con.close()


	def _set_average_values(self,table,starttimestamp,endtimestamp):
		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		# connect to database
		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		query = "INSERT INTO %s(signal_id,time,value) VALUES " % (table)

		cur.execute("SELECT * FROM measurements_legend")

		for measurement in cur:

			signalcur = con.cursor()
	
			signalcur.execute("SELECT AVG(value) FROM measurements WHERE signal_id=%s AND time >= '%s' AND time < '%s'" % (measurement[0],starttimestamp,endtimestamp))
			row = signalcur.fetchall()
			if (row[0][0] is None):
				avg = 0
			else:
				avg = row[0][0]
		
			query = query + "(%s,%s,%f),"  % (measurement[0],starttimestamp,avg)	
	
		query = query[:-1]	
		cur.execute(query)
	
		con.commit()
		con.close()


	def quarterhour(self):
		"""
		calculate 15 minute average of the past 15 minutes and store in MySQL
		"""
		# get the last 15 minutes date
		now = datetime.datetime.utcnow();
		minute = int(np.floor(int(now.strftime('%M'))/15)*15)
		now = now.replace(minute=minute,second=0, microsecond=0)
		epoch = datetime.datetime(1970,1,1)

		startdate = now - datetime.timedelta(minutes=15)
		endddate  = now

		starttimestamp = int( (startdate - epoch).total_seconds() )
		endtimestamp = int( (endddate - epoch).total_seconds() )

		self._set_average_values('measurements_average_quarterhour',starttimestamp,endtimestamp)
		
	def week(self):
		"""
		calculate week average of the past week and store in MySQL
		"""
		# get the last monday's date
		now = datetime.datetime.now(self._sh.tzinfo())
		now = now.replace( hour=0 ,minute=0, second=0, microsecond=0)
		epoch = datetime.datetime(1970,1,1).replace(tzinfo=self._sh.utcinfo())

		monday = now + datetime.timedelta(days=-now.weekday())
		monday = monday.astimezone( self._sh.utcinfo() )

		startdate = monday - datetime.timedelta(weeks=1)
		endddate  = monday

		starttimestamp = int( (startdate - epoch).total_seconds() )
		endtimestamp = int( (endddate - epoch).total_seconds() )

		self._set_average_values('measurements_average_week',starttimestamp,endtimestamp)
		logger.warning('Average week measurements added')

	def month(self):	
		"""
		calculate month average of the past month and store in MySQL
		"""
		pass


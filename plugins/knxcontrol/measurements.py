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

		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()


		# create tables
		# measurements legend
		try:
			cur.execute( "CREATE TABLE IF NOT EXISTS `measurements_legend` ("
						 "`id` int(11) NOT NULL AUTO_INCREMENT,"
						 "`item` varchar(255) DEFAULT NULL,"
						 "`name` varchar(255) DEFAULT NULL,"
						 "`quantity` varchar(255) DEFAULT NULL,"
						 "`unit` varchar(255) DEFAULT NULL,"
						 "`description` text DEFAULT NULL,"
						 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1" )
		except:
			logger.warning("Could not add measurements_legend table to database")

		# measurements
		try:
			cur.execute( "CREATE TABLE IF NOT EXISTS `measurements` ("
						 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
						 "`signal_id` int(11) NOT NULL,"
						 "`time` bigint(20) NOT NULL,"
						 "`value` float DEFAULT NULL,"
						 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1" )
		except:
			logger.warning("Could not add measurements table to database")
		try:
			cur.execute( "CREATE INDEX time_signal_id ON measurements(time, signal_id)" )
		except:
			pass

		# quarterhour average measurements												 						 
		try:
			cur.execute( "CREATE TABLE IF NOT EXISTS `measurements_average_quarterhour` ("
						 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
						 "`signal_id` int(11) NOT NULL,"
						 "`time` int(11) NOT NULL,"
						 "`value` float DEFAULT NULL,"
						 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1" )
		except:
			logger.warning("Could not add quarterhour measurements_average_quarterhour table to database")
		try:
			cur.execute( "CREATE INDEX time_signal_id ON measurements_average_quarterhour(time, signal_id)" )
		except:
			pass

		# week average measurements											 						 
		try:
			cur.execute( "CREATE TABLE IF NOT EXISTS `measurements_average_week` ("
						 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
						 "`signal_id` int(11) NOT NULL,"
						 "`time` int(11) NOT NULL,"
						 "`value` float DEFAULT NULL,"
						 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1" )
		except:
			logger.warning("Could not add measurements_average_week table to database")
		try:
			cur.execute( "CREATE INDEX time_signal_id ON measurements_average_week(time, signal_id)" )
		except:
			pass

		# month average measurements											 						 
		try:
			cur.execute( "CREATE TABLE IF NOT EXISTS `measurements_average_month` ("
						 "`id` bigint(20) NOT NULL AUTO_INCREMENT,"
						 "`signal_id` int(11) NOT NULL,"
						 "`time` int(11) NOT NULL,"
						 "`value` float DEFAULT NULL,"
						 "UNIQUE KEY `ID` (`id`)) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1" )
		except:
			logger.warning("Could not add measurements_average_month table to database")
		try:
			cur.execute( "CREATE INDEX time_signal_id ON measurements_average_month(time, signal_id)" )
		except:
			pass


			
		# create measurements legend
		# get the old legend
		self.get_legend()
		
		# current weather
		item = self._sh.return_item('knxcontrol.weather.current.temperature')
		self.add_legend_item(item,name='Temperature',quantity='Temperature',unit='degC',description='Ambient temperature')
		item = self._sh.return_item('knxcontrol.weather.current.humidity')
		self.add_legend_item(item,name='Humidity',quantity='Humidity',unit='-',description='Relative ambient humidity')
		item = self._sh.return_item('knxcontrol.weather.current.irradiation.horizontal')
		self.add_legend_item(item,name='Horizontal irradiation',quantity='Heat flux',unit='W/m2',description='Estimated global horizontal solar irradiation')
		item = self._sh.return_item('knxcontrol.weather.current.irradiation.clouds')
		self.add_legend_item(item,name='Clouds',quantity='',unit='-',description='Estimated cloud cover')
		item = self._sh.return_item('knxcontrol.weather.current.precipitation')
		self.add_legend_item(item,name='Rain',quantity='Boolean',unit='-',description='Rain or not')							
		item = self._sh.return_item('knxcontrol.weather.current.wind.speed')
		self.add_legend_item(item,name='Wind speed',quantity='Velocity',unit='m/s',description='Wind speed')
		item = self._sh.return_item('knxcontrol.weather.current.wind.direction')
		self.add_legend_item(item,name='Wind direction',quantity='Angle',unit='deg',description='Wind direction (0deg is North, 90deg is East)')

		# energy use
		for item in self._sh.return_item('knxcontrol.energy'):
			item_name = item.id().split(".")[-1]
			self.add_legend_item(item,name=item_name,quantity=item.conf['quantity'],unit=item.conf['unit'],description=item_name+' use')

		# building zones
		for item in self._sh.find_items('zonetype'):
			item_name = item.id().split(".")[-1]
			self.add_legend_item(item.temperature,name='Temperature',quantity='Temperature',unit='degC',description=item_name+' temperature')
			self.add_legend_item(item.airquality,name='Air quality',quantity='Concentration',unit='g CO2/m3',description=item_name+' CO2 concentration')
			self.add_legend_item(item.irradiation,name='Solar gains',quantity='Power',unit='W',description=item_name+' irradiation power')
			self.add_legend_item(item.emission,name='Emission',quantity='Power',unit='W',description=item_name+' emission power')

		# ventilation
		for item in self._sh.return_item('knxcontrol.ventilation'):
			item_name = item.id().split(".")[-1]
			self.add_legend_item(item.fanspeed,name=item_name+' fanspeed',quantity='',unit='-',description=item_name+' fan speed control signal')
			self.add_legend_item(item.heatrecovery,name=item_name+' heatrecovery',quantity='',unit='-',description=item_name+' heat recovery control signal')

		# heat production 10 systems max
		for item in self._sh.return_item('knxcontrol.heat_production'):
			item_name = item.id().split(".")[-1]
			self.add_legend_item(item.power,name=item_name+' power',quantity='Power',unit='W',description=item_name+' heat production')

		# electricity generation 10 systems max
		for item in self._sh.return_item('knxcontrol.electricity_production'):
			item_name = item.id().split(".")[-1]
			self.add_legend_item(item.power,name=item_name+' power',quantity='Power',unit='W',description=item_name+' electricity generation')

		# update the legend, this is unused for now but at least up to date
		self.get_legend()

		
		logger.warning('Measurements initialized')

		
		
	def get_legend(self):
		"""
		Loads the current legend from mysql, if there are duplicate items in the database the 1st is kept
		"""
		self.legend = {}
		
		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()
		cur.execute("SELECT id,item FROM measurements_legend WHERE item <> ''")

		# run through legend
		for measurement in cur:
			if not measurement[1] in self.legend.keys():
				self.legend[measurement[1]] = measurement[0]
			
			
	def add_legend_item(self,item,name,quantity,unit,description):
		"""
		Adds an object to the mysql legend table and the local legend dict.
		If the item is already in the database the id is maintained
		Otherwise the item is inserted and a new id is generated
		
		Arguments:
		item: 			SmartHome.py item
		name: 			name string
		quantity: 		quantity string
		unit: 			unit string
		description: 	description string
		"""

		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		# check if the item was allready logged and copy the data if required
		succes = True
		if item.id() in self.legend.keys():
			try:
				id = self.legend[item.id()]
				cur.execute( "REPLACE INTO measurements_legend (id,item,name,quantity,unit,description) VALUES ('%s','%s','%s','%s','%s','%s')"%(id,item.id(),name,quantity,unit,description) )	
			except:
				succes = False
		else:
			try:
				cur.execute( "INSERT INTO measurements_legend (item,name,quantity,unit,description) VALUES ('%s','%s','%s','%s','%s')"%(item.id(),name,quantity,unit,description) )	
				id = cur.lastrowid
			except:
				succes = False
				
		if succes:
			item.conf['mysql_id'] = id
		else:
			logger.warning( 'could not add legend item: %s: %s'%(name,item.id()) )

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


	def quarterhour(self):
		"""
		Calculate 15 minute average of the past 15 minutes and store in MySQL
		"""
		# get the last 15 minutes date
		now = datetime.datetime.now(self._sh.tzinfo())
		minute = int(np.floor(int(now.strftime('%M'))/15)*15)
		now = now.replace(minute=minute,second=0, microsecond=0).astimezone( self._sh.utcinfo() )

		startdate = now - datetime.timedelta(minutes=15)
		endddate  = now

		self._set_average_values('measurements_average_quarterhour',startdate,endddate)
		
		
	def week(self):
		"""
		Calculate week average of the past week and store in MySQL
		"""
		# get the last monday's date
		now = datetime.datetime.now(self._sh.tzinfo())
		now = now.replace( hour=0 ,minute=0, second=0, microsecond=0)

		monday = now + datetime.timedelta(days=-now.weekday())
		monday = monday.astimezone( self._sh.utcinfo() )

		startdate = monday - datetime.timedelta(weeks=1)
		endddate  = monday

		self._set_average_values('measurements_average_week',startdate,endddate)

		
	def month(self):	
		"""
		calculate month average of the past month and store in MySQL
		"""
		# get the last 1st of month date
		now = datetime.datetime.now(self._sh.tzinfo())

		startdate = now.replace( month=(now.month-1) % 12 + 1,day=1, hour=0 ,minute=0, second=0, microsecond=0).astimezone( self._sh.utcinfo() )
		enddate   = now.replace( day=1, hour=0 ,minute=0, second=0, microsecond=0).astimezone( self._sh.utcinfo() )

		self._set_average_values('measurements_average_week',startdate,enddate)	
		

	def _set_average_values(self,table,startdate,endddate):
		"""
		Set some average values in MySQL
		
		Arguments:
		table:  			string, name of a MySQL table to set result in
		startdate:  		datetime with local timezone to start averaging
		endddate:  			datetime with local timezone to end averaging
		"""
		
		# convert datetimes to timestamps
		epoch = datetime.datetime(1970,1,1).replace(tzinfo=self._sh.utcinfo())
		
		starttimestamp = int( (startdate - epoch).total_seconds() )
		endtimestamp = int( (endddate - epoch).total_seconds() )

		# connect to database
		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		# build query
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
	
		# execute query
		query = query[:-1]
		try:
			cur.execute(query)
		except:
			logger.warning("could not add average measurements to database")

		con.commit()
		con.close()



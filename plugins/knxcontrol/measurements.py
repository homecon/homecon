#!/usr/bin/env python3

import logging
import pymysql
import datetime

logger = logging.getLogger('')

class Measurements:

	def __init__(self,smarthome,mysql_pass):
		"""
		A measurements object is created
		and mysql measurement_legend is filled with items required for knxcontrol
		and measurement ids are stored for reference
		
		arguments:
		smarthome:   smarthome object
		mysql_pass:  mysql password 
		"""

		self._sh = smarthome
		self._mysql_pass = _mysql_pass;
		self.items = self._sh.return_item('knxcontrol')

		
		logger.warning('started')

		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		query = "REPLACE INTO measurement_legend (id,item,name,quantity,unit,description) VALUES "

		id = 0
		# current weather 20 components max
		item = self._sh.return_item('knxcontrol.weather.current.temperature')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"',"+item.id()+",'Temperature','Temperature','degC','Ambient temperature'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.humidity')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"',"+item.id()+",'Humidity','Humidity','-','Relative ambient humidity'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.irradiation.direct')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"',"+item.id()+",'Direct','Heat flux','W/m2','Estimated direct solar irradiation'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.irradiation.diffuse')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"',"+item.id()+",'Diffuse','Heat flux','W/m2','Estimated diffuse solar irradiation'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.irradiation.clouds')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"',"+item.id()+",'Clouds','','-','Cloud factor'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.precipitation')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"',"+item.id()+",'Rain','','-','Rain or not'),"											
		
		item = self._sh.return_item('knxcontrol.weather.current.wind.speed')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"',"+item.id()+",'Wind speed','Velocity','m/s','Wind speed'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.wind.direction')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"',"+item.id()+",'Wind direction','Angle','deg','Wind direction (0deg is North)'),"


		id = 20
		# energy use 5 components max
		for item in self.items.energy:
			item_name = item.id().split(".")[-1]
			id = id+1 
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.id()+"','"+item_name+"','"+item.conf['quantity']+"','"+item.conf['unit']+"','"+item_name+" use'),"



		id = 100
		# building zones 10 zones max
		for item in self.items.building:
			item_name = item.id().split(".")[-1]
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.temperature.id()+"','Temperature','Temperature','degC','"+item_name+" temperature'),"
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.airquality.id()+"','Air quality','Concentration','g CO2/m3','"+item_name+" CO2 concentration'),"



		id = 120
		# ventilation 10 systems max
		for item in self.items.ventilation:
			item_name = item.id().split(".")[-1]
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.fanspeed.id()+"','"+item_name+" fanspeed','','-','"+item_name+" fan speed control signal'),"
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.heatrecovery.id()+"','"+item_name+" heatrecovery','','-','"+item_name+" heat recovery control signal'),"



		id = 140
		# heat production 10 systems max
		for item in self.items.heat.production:
			item_name = item.id().split(".")[-1]
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.power.id()+"','"+item_name+" Power','Power','W','"+item_name+" heat production'),"
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.control.id()+"','"+item_name+" Control','','-','"+item_name+" control signal'),"



		id = 160
		# heat emission 10 systems max
		for item in self.items.heat.emission:
			item_name = item.id().split(".")[-1]
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.power.id()+"','"+item_name+" Power','Power','W','"+item_name+" heat emission'),"
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.control.id()+"','"+item_name+" Control','','-','"+item_name+" control signal'),"



		id = 180
		# electricity generation 10 systems max
		for item in self.items.electricity.production:
			item_name = item.id().split(".")[-1]
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.power.id()+"','"+item_name+" Power','Power','W','"+item_name+" electricity generation'),"
			id = id + 1
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.control.id()+"','"+item_name+" Control','','-','"+item_name+" control signal'),"


		# try to execute query
		query = query[:-1]
		logger.warning('query built')
		try:
			cur.execute( query )
			logger.info("Measurements initialized")
		except:
			logger.warning("could not add default measurements to database")
			logger.warning(query)

		con.commit()	
		con.close()


	def minute(self):
		"""
		store all measurements in MySQL
		"""

		now = datetime.datetime.utcnow();
		# remove seconds from time and add :00
		now.replace( second=0, microsecond=0)

		# connect to the mysql database
		con = pymysql.connect('localhost', 'knxcontrol', self.mysql_pass, 'knxcontrol')
		cur = con.cursor()

		# convert time to seconds from epoch
		timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

		legend = con.cursor()
		legend.execute("SELECT id,item FROM measurement_legend WHERE item <> ''")

		# create mysql querry
		query = "INSERT INTO measurement (signal_id,time,value) VALUES "

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
		calculate 15 minute average of the past 15 minutes and store in MySQL
		"""
		pass
		
	def week(self):
		"""
		calculate week average of the past week and store in MySQL
		"""
		pass
		
	def month(self):	
		"""
		calculate month average of the past month and store in MySQL
		"""
		pass


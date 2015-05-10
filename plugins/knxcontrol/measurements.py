#!/usr/bin/env python3

import logging
import pymysql
import datetime
import numpy as np

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
		self._mysql_pass = mysql_pass
		self.items = self._sh.return_item('knxcontrol')


		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		query = "REPLACE INTO measurement_legend (id,item,name,quantity,unit,description) VALUES "

		id = 0
		# current weather 20 components max
		item = self._sh.return_item('knxcontrol.weather.current.temperature')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"','"+item.id()+"','Temperature','Temperature','degC','Ambient temperature'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.humidity')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"','"+item.id()+"','Humidity','Humidity','-','Relative ambient humidity'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.irradiation.horizontal')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"','"+item.id()+"','Horizontal irradiation','Heat flux','W/m2','Estimated global horizontal solar irradiation'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.irradiation.clouds')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"','"+item.id()+"','Clouds','','-','Cloud factor'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.precipitation')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"','"+item.id()+"','Rain','','-','Rain or not'),"											
		
		item = self._sh.return_item('knxcontrol.weather.current.wind.speed')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"','"+item.id()+"','Wind speed','Velocity','m/s','Wind speed'),"
		
		item = self._sh.return_item('knxcontrol.weather.current.wind.direction')
		id = id+1
		item.conf['mysql_id'] = id
		query = query+"('"+str(id)+"','"+item.id()+"','Wind direction','Angle','deg','Wind direction (0deg is North)'),"



		id = 20
		# energy use 10 components max
		for item in self._sh.return_item('knxcontrol.energy'):
			item_name = item.id().split(".")[-1]
			id = id+1 
			item.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.id()+"','"+item_name+"','"+item.conf['quantity']+"','"+item.conf['unit']+"','"+item_name+" use'),"

		

		id = 100
		# building zones 16 zones max
		for item in self._sh.return_item('knxcontrol.building'):
			item_name = item.id().split(".")[-1]
			id = id + 1
			item.temperature.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.temperature.id()+"','Temperature','Temperature','degC','"+item_name+" temperature'),"
			id = id + 1
			item.airquality.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.airquality.id()+"','Air quality','Concentration','g CO2/m3','"+item_name+" CO2 concentration'),"
			id = id + 1
			item.irradiation.power.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.irradiation.power.id()+"','Solar gains','Power','W','"+item_name+" irradiation power'),"
			id = id + 1
			item.irradiation.setpoint.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.irradiation.setpoint.id()+"','Solar gains setpoint','Power','W','"+item_name+" irradiation power setpoint'),"
			id = id + 1
			item.emission.power.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.emission.power.id()+"','Emission','Power','W','"+item_name+" emission power'),"
			id = id + 1
			item.emission.setpoint.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.emission.setpoint.id()+"','Emission setpoint','Power','W','"+item_name+" emission power setpoint'),"
		


		id = 200
		# ventilation 10 systems max
		for item in self._sh.return_item('knxcontrol.ventilation'):
			item_name = item.id().split(".")[-1]
			id = id + 1
			item.fanspeed.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.fanspeed.id()+"','"+item_name+" fanspeed','','-','"+item_name+" fan speed control signal'),"
			id = id + 1
			item.heatrecovery.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.heatrecovery.id()+"','"+item_name+" heatrecovery','','-','"+item_name+" heat recovery control signal'),"

		
		id = 220
		# heat production 10 systems max
		for item in self._sh.return_item('knxcontrol.heat_production'):
			item_name = item.id().split(".")[-1]
			id = id + 1
			item.power.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.power.id()+"','"+item_name+" Power','Power','W','"+item_name+" heat production'),"
			id = id + 1
			item.setpoint.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.setpoint.id()+"','"+item_name+" Power setpoint','Power','W','"+item_name+" heat production setpoint'),"

		
		id = 240
		# electricity generation 10 systems max
		for item in self._sh.return_item('knxcontrol.electricity_production'):
			item_name = item.id().split(".")[-1]
			id = id + 1
			item.power.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.power.id()+"','"+item_name+" Power','Power','W','"+item_name+" electricity generation'),"
			id = id + 1
			item.setpoint.conf['mysql_id'] = id
			query = query+"('"+str(id)+"','"+item.setpoint.id()+"','"+item_name+" Power setpoint','Power','W','"+item_name+" electricity generation setpoint'),"

		
		# try to execute query
		query = query[:-1]
		try:
			cur.execute( query )
			logger.warning("Measurements initialized")
		except:
			logger.warning("Could not add default measurements to database")
			logger.warning(query)

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
		legend.execute("SELECT id,item FROM measurement_legend WHERE item <> ''")

		# create mysql query
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

	def _set_average_values(self,table,starttimestamp,endtimestamp):
		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		# connect to database
		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		query = "INSERT INTO %s(signal_id,time,value) VALUES " % (table)

		cur.execute("SELECT * FROM measurement_legend")

		for measurement in cur:

			signalcur = con.cursor()
	
			signalcur.execute("SELECT AVG(value) FROM measurement WHERE signal_id=%s AND time >= '%s' AND time < '%s'" % (measurement[0],starttimestamp,endtimestamp))
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

		self._set_average_values('measurement_average_quarterhour',starttimestamp,endtimestamp)
		
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

		self._set_average_values('measurement_average_week',starttimestamp,endtimestamp)
		logger.warning('Average week measurements added')

	def month(self):	
		"""
		calculate month average of the past month and store in MySQL
		"""
		pass


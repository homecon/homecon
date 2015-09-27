#!/usr/bin/env python3

import logging
import pymysql
import datetime

logger = logging.getLogger('')

class Mysql:

	def __init__(self,homecon):
		"""
		A mysql object is created
		and mysql tables required for homecon are created
		
		arguments:
		smarthome:   smarthome object
		mysql_pass:  mysql password 
		"""

		self.homecon = homecon
		self._sh = homecon._sh
		self._mysql_pass = homecon._mysql_pass

		con,cur = self.create_cursor()

		# set location data
		query = "UPDATE data SET latitude=%f,longitude=%f,elevation=%f WHERE id=1" % (float(self._sh._lat),float(self._sh._lon),float(self._sh._elev))
		try:
			cur.execute( query )
		except:
			logger.warning("Could not add location to database")


		logger.warning("Database initialized")
		con.commit()	
		con.close()
		

	def create_cursor(self):
		con = pymysql.connect('localhost', 'homecon', self._mysql_pass, 'homecon')
		cur = con.cursor()

		return con,cur


	def backup(self):
		"""
		backup mysql data without measurements to backupdir
		"""
		pass


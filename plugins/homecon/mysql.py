#!/usr/bin/env python3

import logging
import pymysql
import datetime

logger = logging.getLogger('')

class Mysql:

	def __init__(self,homecon,mysql_pass):
		"""
		A mysql object is created
		and mysql tables required for homecon are created
		
		arguments:
		smarthome:   smarthome object
		mysql_pass:  mysql password 
		"""

		self.homecon = homecon
		self._mysql_pass = mysql_pass

		#con,cur = self.create_cursor()

		# set location data
		#query = "UPDATE data SET latitude=%f,longitude=%f,elevation=%f WHERE id=1" % (float(self._sh._lat),float(self._sh._lon),float(self._sh._elev))
		#try:
		#	cur.execute( query )
		#except:
		#	logger.warning("Could not add location to database")


		logger.warning("Database initialized")
		#con.commit()	
		#con.close()
		

	def create_cursor(self):
		con = pymysql.connect('localhost', 'homecon', self._mysql_pass, 'homecon')
		cur = con.cursor()

		return con,cur


	def create_dict_cursor(self):
		con = pymysql.connect('localhost', 'homecon', self._mysql_pass, 'homecon')
		cur = con.cursor(pymysql.cursors.DictCursor)

		return con,cur


	def POST(self,table,data):
		keys = []
		vals = []

		for key,val in data.items():
			keys.append('`'+key+'`')
			vals.append('\''+val+'\'')

		query = "INSERT INTO `{}` ({}) VALUES ({})".format(table,','.join(keys),','.join(vals))	
		id_query = "SELECT LAST_INSERT_ID()"

		con,cur = self.create_cursor()

		try:
			self.execute_query(cur,query)
			cur = self.execute_query(cur,id_query)

			id = cur[0][0]
		except:
			id = None

		con.commit()
		con.close()

		return id


	def GET(self,table,selector=None):

		if selector==None:
			query = "SELECT {} FROM `{}`".format('*',table)
		else:
			query = "SELECT {} FROM `{}` WHERE {}".format('*',table,selector)

		con,cur = self.create_dict_cursor()
		try:
			self.execute_query(cur,query)
			values = list( cur.fetchall() )
		except:
			values = []

		con.commit()
		con.close()

		return values

	def GET_JSON(self,table,selector=None):
		values = self.GET(table,selector=None)

		return json.loads( values )

	def PUT(self,table,selector,data):

		keyvals = []
		for key,val in data.items():
			keyvals.append(key+' = \''+val+'\'')

		query = "UPDATE `{}` SET {} WHERE {}".format(table,','.join(keyvals),selector)

		con,cur = self.create_cursor()
		try:
			self.execute_query(cur,query)
		except:
			pass

		con.commit()
		con.close()

	def DELETE(self,table,selector):

		query = "DELETE {} FROM `{}` WHERE {}".format('*',table,selector)

		con,cur = self.create_cursor()
		try:
			self.execute_query(cur,query)
		except:
			pass

		con.commit()
		con.close()

	def execute_query(self,cur,query):
		try:
			cur.execute( query )
		except:
			logger.warning('There was a problem executing query {}.'.format(query))

	def backup(self):
		"""
		backup mysql data without measurements to backupdir
		"""
		pass


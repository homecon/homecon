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
		logger.warning(self._mysql_pass)
		con = pymysql.connect('localhost', 'homecon', self._mysql_pass, 'homecon')
		cur = con.cursor()

		return con,cur


	def create_dict_cursor(self):
		logger.warning(self._mysql_pass)
		con = pymysql.connect('localhost', 'homecon', self._mysql_pass, 'homecon')
		cur = con.cursor(pymysql.cursors.DictCursor)

		return con,cur


	def POST(self,table,data):

		keys = []
		vals = []
		for key,val in data.iteritems():
			keys.append('`'+key+'`')
			vals.append('\''+val+'\'')

		query = "INSERT INTO `{}` ({}) VALUES ({})".format(table,','.join(keys),','.join(vals))	
		id_query = "SELECT LAST_INSERT_ID()"

		con,cur = self.create_cursor()
		try:
			cur = self.execute_query(cur,query)
			cur = self.execute_query(cur,id_query)

			for row in cur:
				print(row)
			id = 1
		except:
			id = None

		return id
		con.close()


	def GET(self,table,selector=None):

		if selector==None:
			query = "SELECT {} FROM `{}`".format('*',table)
		else:
			query = "SELECT {} FROM `{}` WHERE {}".format('*',table,selector)

		con,cur = self.create_dict_cursor()
		try:
			cur = self.execute_query(cur,query)
			values = cur.fetchall()
		except:
			values = []

		con.close()
		return values


	def PUT(self,table,selector,data):

		keyvals = []
		for key,val in data.iteritems():
			keyvals.append(key+' = \''+val+'\'')

		query = "UPDATE `{}` SET {} WHERE {}".format(table,keyvals,selector)

		con,cur = self.create_cursor()
		try:
			cur = self.execute_query(cur,query)
		except:
			pass

		con.close()

	def DELETE(self,table,selector):

		query = "DELETE {} FROM `{}` WHERE {}".format('*',table,selector)

		con,cur = self.create_cursor()
		try:
			cur = self.execute_query(cur,query)
		except:
			pass

		con.close()

	def execute_query(self,cur,query):
		try:
			cur.execute( query )
		except:
			logger.warning('There was a problem executing query {}.'.format(query))
		else:
			return cur

	def backup(self):
		"""
		backup mysql data without measurements to backupdir
		"""
		pass


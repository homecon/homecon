#!/usr/bin/env python3
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import logging
import numpy as np
import pymysql
import threading
import types
import lib
import os
import dateutil.tz


from . import items
from . import mysql
from . import alarms
from . import measurements
from . import weather
from . import building
from . import mpc


logger = logging.getLogger('')

class HomeCon:

	def __init__(self, smarthome, mysql_pass='mysql_pass'):
		logger.info('HomeCon started')
		
		# set basic attributes
		self._sh = smarthome
		self.mysql = mysql.Mysql(self,mysql_pass)
		
		# prepare other attributes
		#self.item = None
		self.alarms = None
		self.weather = None
		self.measurements = None
		self.zones = []
		

		self.sh_listen_items = {}


	def run(self):
		# called once after the items have been parsed
		self.alive = True

		########################################################################
		# configure position from the database
		########################################################################
		self._sh._lat = 50.
		self._sh._lon = 5.
		self._sh._elev = 0.

		self._sh.sun = lib.orb.Orb('sun', self._sh._lon, self._sh._lat, self._sh._elev)
		self._sh.moon = lib.orb.Orb('moon', self._sh._lon, self._sh._lat, self._sh._elev)


		########################################################################
		# configure timezone from the database
		########################################################################
		tz = 'Europe/Brussels'
		tzinfo = dateutil.tz.gettz(tz)
		if tzinfo is not None:
			TZ = tzinfo
			self._sh._tz = tz
			self._sh.tz = tz
			os.environ['TZ'] = tz
		else:
			logger.warning("Problem parsing timezone: {}. Using UTC.".format(tz))


		########################################################################
		# configure items from the database
		########################################################################
		item_config =  self.mysql.GET('item_config')

		# sort the items so parents come before children
		item_config.sort( key=lambda config: len(config['path']) )

		for config in item_config:
			items.create_item(self._sh,config)
			




		# print all items for testing
		for item in self._sh.return_items():
			print(item.id())


		########################################################################
		# create objects after all items have been parsed
		########################################################################
		#self.alarms = alarms.Alarms(self)
		#self.weather = weather.Weather(self)
		#self.measurements = measurements.Measurements(self)
		

		# zone objects
		for item in self.find_item('zone'):
			logger.warning(item)
			self.zones.append( building.Zone(self,item) )

		logger.warning('New objects created')

		


 		# schedule low_level_control
		#self._sh.scheduler.add('HomeCon_update', self.low_level_control, prio=2, cron='* * * *')

		# schedule measurements
		#self._sh.scheduler.add('Measurements_minute', self.measurements.minute, prio=2, cron='* * * *')
		#self._sh.scheduler.add('Measurements_average_quarterhour', self.measurements.quarterhour, prio=5, cron='1,16,31,46 * * *')
		#self._sh.scheduler.add('Measurements_average_week', self.measurements.week, prio=5, cron='2 0 * 0')
		#self._sh.scheduler.add('Measurements_average_month', self.measurements.month, prio=5, cron='2 0 1 *')
		
		# schedule forecast loading
		#self._sh.scheduler.add('Weater_forecast', self.weather.forecast, prio=5, cron='1 * * *')



		# create the mpc objects
		#self.mpc = MPC(self)
		#self.mpc.model.identify()
		#self.mpc.model.validate()

		logger.warning('Initialization Complete')


	def stop(self):
		self.alive = False


	def parse_item(self, item):
		# called once while parsing the items

		# add default attributes to items
		if not 'quantity' in item.conf:
			item.conf['quantity'] = ''

		if not 'unit' in item.conf:
			item.conf['unit'] = ''

		if not 'label' in item.conf:
			item.conf['label'] = ''

		if not 'description' in item.conf:
			item.conf['description'] = ''

		if not 'persistent' in item.conf:
			item.conf['persistent'] = '0'

		# add or update the item in the database
		db_items = self.mysql.GET( 'items','path=\'{}\''.format(item.id()) )
		item_data = {'path':item.id(),'quantity':item.conf['quantity'],'unit':item.conf['unit'],'label':item.conf['label'],'description':item.conf['description'],'persistent':item.conf['persistent'],'value':str(item())}

		if db_items == []:
			self.mysql.POST( 'items', item_data)
		else:
			if item.conf['persistent'] == '1':
				# update the value
				db_item = db_items[0]
				item(db_item['value']) 
				item_data['value'] = str(item())

			self.mysql.PUT( 'items','path=\'{}\''.format(item.id()),item_data )


		# find the items in sh_listen and
		if 'sh_listen' in item.conf:
			listenitems = self.find_items_in_str(item.conf['sh_listen'])
			for listenitem in listenitems:
				if listenitem in self.sh_listen_items:
					self.sh_listen_items[listenitem].append(item)
				else:
					self.sh_listen_items[listenitem] = [item]
		
		return self.update_item
	


	def update_item(self, item, caller=None, source=None, dest=None):
		# called each time an item changes

		########################################################################
		# evaluate expressions in sh_listen
		if item.id() in self.sh_listen_items:
			for dest_item in self.sh_listen_items[item.id()]:
				try:
					dest_item( eval( dest_item.conf['sh_listen'].replace('sh.','self._sh.') ) )
				except:
					logger.warning('Could not parse \'%s\' to %s' % (dest_item.conf['sh_listen'],dest_item.id()))

		########################################################################
		# check if shading override values need to be set
		#if item in self._sh.match_items('*.shading.set_override'):
		#	window = item.return_parent().conf['homeconobject']
		#	window.shading_override()

		#if item in self._sh.match_items('*.shading.value'):
		#	if caller!='KNX' and caller != 'Logic':
		#		window = item.return_parent().conf['homeconobject']
		#		window.shading_override()

		########################################################################
		# check for rain
		if item.id() == 'homecon.weather.current.precipitation':
			pass
			#for zone in self.zones:
			#	zone.shading_control()

		########################################################################
		# check for model identify
		if item.id() == 'homecon.mpc.model.identification':
			pass
			#self.mpc.model.identify()

		########################################################################
		# check for model validation
		if item.id() == 'homecon.mpc.model.validation':
			pass
			#self.mpc.model.validate()



	def parse_logic(self, logic):
		pass


	def low_level_control(self):
		"""
		Update all values dependent on time
		Run every minute
		"""
		pass
		#logger.warning('low level control')
		
		# check for alarms
		#self.alarms.run()

		# update weather calculations
		#self.weather.update()

		# set controls
		#for zone in self.zones:
			#zone.irradiation.setpoint(500)
			#zone.emission.setpoint(0)

		#	zone.shading_control()








	def find_item(self,homeconitem,parent=None):
		"""
		function to find items with a certain homecon attribute
		"""
		items = []
		if parent == None:
			itemiterator = self._sh.find_items('homeconitem')
		else:
			itemiterator = self._sh.find_children(parent, 'homeconitem')

		for item in itemiterator:
			if item.conf['homeconitem'] == homeconitem:
				items.append(item)

		return items
		

	def find_items_in_str(self,searchstr):
		"""
		function to find all items in a string. It looks for instances starting with "sh." and ending with "()"
		"""
		items = []
		tempstr = searchstr
		while len(tempstr)>0:
			try:
				start = tempstr.index('sh.')+3
				tempstr = tempstr[start:]
				try:
					end  = tempstr.index('()')
					items.append(tempstr[:end])
					tempstr = tempstr[end:]
				except:
					tempstr = ''
			except:
				tempstr = ''
	
		return items


			


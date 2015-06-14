#!/usr/bin/env python3
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of KNXControl.
#
#    KNXControl is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KNXControl is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import logging
import numpy as np
import pymysql
import threading
import types


from plugins.knxcontrol.mysql import *
from plugins.knxcontrol.alarms import *
from plugins.knxcontrol.measurements import *
from plugins.knxcontrol.item_methods import *
from plugins.knxcontrol.mpc import *


logger = logging.getLogger('')

class KNXControl:

	def __init__(self, smarthome, mysql_pass='admin'):
		logger.info('KNXControl started')
		
		self._sh = smarthome
		self._mysql_pass = mysql_pass

		self.sh_listen_items = {}

		self.zones = []
		self.weather = None

		self.lat  = float(self._sh._lat)
		self.lon  = float(self._sh._lon)
		self.elev = float(self._sh._elev)

		self.knxcontrolitems = []


	def run(self):
		# called once after the items have been parsed
		self.alive = True
			

		# find all items with a knxcontrolitem attribute
		for item in self._sh.find_items('knxcontrolitem'):
			self.knxcontrolitems.append(item)


		# create objects
		self.mysql = Mysql(self)
		self.alarms = Alarms(self)
		self.measurements = Measurements(self)
		self.weather = Weather(self)

		# Zone objects
		for item in self.find_item('zone'):
			self.zones.append( Zone(self,item) )

		logger.warning('New objects created')

		self.update()

			
		# schedule alarms
		self._sh.scheduler.add('Alarm_run', self.alarms.run, prio=1, cron='* * * *')
		
 		# schedule update
		self._sh.scheduler.add('KNXControl_update', self.update, prio=2, cron='* * * *')

		# schedule measurements
		self._sh.scheduler.add('Measurements_minute', self.measurements.minute, prio=2, cron='* * * *')
		self._sh.scheduler.add('Measurements_average_quarterhour', self.measurements.quarterhour, prio=5, cron='1,16,31,46 * * *')
		self._sh.scheduler.add('Measurements_average_week', self.measurements.week, prio=5, cron='2 0 * 0')
		self._sh.scheduler.add('Measurements_average_month', self.measurements.month, prio=5, cron='2 0 1 *')
		
		# schedule forecast loading
		self._sh.scheduler.add('Detailed_weater_forecast', self.weather.prediction_detailed_load, prio=5, cron='1 * * *')
		self._sh.scheduler.add('Daily_weater_forecast', self.weather.prediction_daily_load, prio=5, cron='1 * * *')

		# schedule control actions
		#self._sh.scheduler.add('Shading_control', self.building.control, prio=3, cron='0,30 * * *')



		# create a parameter estimation object
		#self.optimization_model = Optimization_model(self._sh)
		
		logger.warning('Initialization Complete')






	def stop(self):
		self.alive = False


	def find_item(self,knxcontrolitem):
		"""
		function to find items with a certain knxcontrol attribute
		"""
		items = []
		for item in self.knxcontrolitems:
			if item.conf['knxcontrolitem'] == knxcontrolitem:
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
	






	def parse_item(self, item):
		# called once while parsing the items

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


		# evaluate expressions in sh_listen
		if item.id() in self.sh_listen_items:
			for dest_item in self.sh_listen_items[item.id()]:
				try:
					dest_item( eval( dest_item.conf['sh_listen'].replace('sh.','self._sh.') ) )
				except:
					logger.warning('Could not parse \'%s\' to %s' % (dest_item.conf['sh_listen'],dest_item.id()))



		# check if override values need to be set
		if item in self._sh.match_items('*.shading.move'):
			logger.warning('Overriding %s control'%shading)
			shading.override(True)

			# release override after 4h
			def release():
				shading.override(False)
				logger.warning('Override of %s control released'%shading)
			threading.Timer(4*3600,release).start()


		if item in self._sh.match_items('*.shading.value'):
			override = False
			lock_override = False
			shading = item.return_parent()
			if caller=='KNX':
				if 'lock_override' in shading.conf:
					if not shading.conf['lock_override']:
						override = True
				else:
					override = True
					
			if override:
				logger.warning('Overriding %s control'%shading)
				shading.override(True)
				# release override after 4h
				def release():
					shading.override(False)
					logger.warning('Override of %s control released'%shading)
				threading.Timer(4*3600,release).start()

			# lock override
			if 'lock_override' in shading.conf:
				if not shading.conf['lock_override']:
					lock_override = True
			else:
				lock_override = True

			if lock_override:
				shading.conf['lock_override'] = True
				# unlock after 15s
				def unlock():
					shading.conf['lock_override'] = False
				threading.Timer(15,unlock).start()

		# check if a shading closed value changed
		if item in self._sh.match_items('*.shading.closed'):
			shading = item.return_parent()
			
			if item:
				shading.value(shading.conf['closed_value'])
			else:
				window = shading.return_parent()
				room = window.return_parent().return_parent()
				zone = room.return_parent()
				logger.warning(zone)

				zone.shading_control()

				#if zone.irradiation() < zone.irradiation.setpoint():
				#	shading.value(shading.conf['open_value'])

		# check for rain
		if item.id() == 'knxcontrol.weather.current.precipitation':
			self._sh.knxcontrol.shading_control()
			
	def parse_logic(self, logic):
		pass


	def update(self):
		"""
		Update all values dependent on time
		"""
		self.weather.update()

		for zone in self.zones:
			zone.irradiation_est()
			

	def control(self):
		"""
		Execute control actions
		"""

		# optimization	


		# set controls
		self.shading_control()
	
	def shading_control(self):
		for zone in self._sh.find_items('zonetype'):
			zone.irradiation.setpoint(5000)
			zone.emission.setpoint(5000)
			zone.shading_control()


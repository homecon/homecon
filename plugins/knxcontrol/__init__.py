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

from plugins.knxcontrol.measurements import *
from plugins.knxcontrol.mysql import *
from plugins.knxcontrol.alarms import *
from plugins.knxcontrol.weather import *
from plugins.knxcontrol.building import *
from plugins.knxcontrol.mpc import *


logger = logging.getLogger('')

class KNXControl:

	def __init__(self, smarthome, mysql_pass='admin'):
		logger.info('KNXControl started')
		
		self._sh = smarthome
		self._mysql_pass = mysql_pass
		self.sh_listen_items = {}


	def run(self):
		# called once after the items have been parsed
		self.alive = True
		
		# create objects
		self.mysql = Mysql(self)
		self.alarms = Alarms(self)
		self.measurements = Measurements(self)


		# bind new methods to items
		knxcontrol = self._sh.knxcontrol
		knxcontrol.update_irradiation = types.MethodType( knxcontrol_update_irradiation, knxcontrol )
		knxcontrol.control = types.MethodType( knxcontrol_control, knxcontrol )

		weather = self._sh.knxcontrol.weather
		weather.set_irradiation = types.MethodType( weather_set_irradiation, weather )
		weather.update_irradiation = types.MethodType( weather_update_irradiation, weather )
		weather.incidentradiation = types.MethodType( weather_incidentradiation, weather )
		weather.prediction.detailed.load = types.MethodType( prediction_detailed_load, weather.prediction.detailed )
		weather.prediction.daily.load = types.MethodType( prediction_daily_load, weather.prediction.daily )

		for zone in self._sh.find_items('zonetype'):
			zone.find_windows = types.MethodType( zone_find_windows, zone )
			zone.irradiation_max = types.MethodType( zone_irradiation_max, zone )
			zone.irradiation_min = types.MethodType( zone_irradiation_min, zone )
			zone.irradiation_est = types.MethodType( zone_irradiation_est, zone )
			zone.shading_control = types.MethodType( zone_shading_control, zone )

			for room in zone.return_children():
				if hasattr(room,'windows'):
					for window in room.windows.return_children():
						window.irradiation_open   = types.MethodType( window_irradiation_open, window )
						window.irradiation_closed = types.MethodType( window_irradiation_closed, window )
						window.irradiation_min    = types.MethodType( window_irradiation_min, window )
						window.irradiation_max    = types.MethodType( window_irradiation_max, window )
						window.irradiation_est    = types.MethodType( window_irradiation_est, window )

		self._sh.knxcontrol.weather.update_irradiation()

		logger.warning('New methods bound to items')

		for zone in self._sh.find_items('zonetype'):
			pass
			
		# schedule alarms
		self._sh.scheduler.add('Alarm_run', self.alarms.run, prio=1, cron='* * * *')
		
		# schedule measurements
		self._sh.scheduler.add('Measurements_minute', self.measurements.minute, prio=2, cron='* * * *')
		self._sh.scheduler.add('Measurements_average_quarterhour', self.measurements.quarterhour, prio=5, cron='1,16,31,46 * * *')
		self._sh.scheduler.add('Measurements_average_week', self.measurements.week, prio=5, cron='2 0 * 0')
		self._sh.scheduler.add('Measurements_average_month', self.measurements.month, prio=5, cron='2 0 1 *')
		
		# schedule forecast loading
		self._sh.scheduler.add('Detailed_weater_forecast', self._sh.knxcontrol.weather.prediction.detailed.load, prio=5, cron='1 * * *')
		self._sh.scheduler.add('Daily_weater_forecast', self._sh.knxcontrol.weather.prediction.daily.load, prio=5, cron='1 * * *')
		self._sh.scheduler.add('Irradiation_update', self._sh.knxcontrol.weather.update_irradiation, prio=4, cron='* * * *')

		# schedule control actions
		#self._sh.scheduler.add('Shading_control', self.building.control, prio=3, cron='0,30 * * *')



		# create a parameter estimation object
		#self.optimization_model = Optimization_model(self._sh)
		
		logger.warning('Initialization Complete')

	def stop(self):
		self.alive = False

	def find_items(self,searchstr):
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
			listenitems = self.find_items(item.conf['sh_listen'])
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
				room = window.return_parent()
				zone = room.return_parent()
				logger.warning(zone)

				zone.shading_control()

				#if zone.irradiation() < zone.irradiation.setpoint():
				#	shading.value(shading.conf['open_value'])

	def parse_logic(self, logic):
		pass


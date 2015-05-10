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
import re

from plugins.knxcontrol.measurements import *
from plugins.knxcontrol.mysql import *
from plugins.knxcontrol.alarms import *
from plugins.knxcontrol.weather import *
from plugins.knxcontrol.mpc import *


logger = logging.getLogger('')

class KNXControl:

	def __init__(self, smarthome, mysql_pass='admin'):
		logger.info('KNXControl started')
		
		self._sh = smarthome
		self._mysql_pass = mysql_pass
		self.sh_listen_items = {}

		# initialize mysql
		self.mysql = Mysql(self._sh,self._mysql_pass)

		# initialize alarms		
		self.alarms = Alarms(self._sh,self._mysql_pass)

	def run(self):
		# called once after the items have been parsed
		self.alive = True

		# create measurements object
		self.measurements = Measurements(self._sh,self._mysql_pass)

		# schedule measurements
		self._sh.scheduler.add('Measurements_minute', self.measurements.minute, prio=2, cron='* * * *')
		self._sh.scheduler.add('Measurements_average_quarterhour', self.measurements.quarterhour, prio=5, cron='1,16,31,46 * * *')
		self._sh.scheduler.add('Measurements_average_week', self.measurements.week, prio=5, cron='2 0 * 0')
		self._sh.scheduler.add('Measurements_average_month', self.measurements.month, prio=5, cron='2 0 1 *')
		
		# create weather object
		self.weather = Weather(self._sh)
		# schedule forecast loading
		self._sh.scheduler.add('Detailed_weater_forecast', self.weather.load_detailed_predictions, prio=5, cron='1 * * *')
		self._sh.scheduler.add('Daily_weater_forecast', self.weather.load_daily_predictions, prio=5, cron='1 * * *')
		self._sh.scheduler.add('Irradiation update', self.weather.update_irradiation, prio=2, cron='* * * *')
		

		# schedule alarms
		self._sh.scheduler.add('Alarm_run', self.alarms.run, prio=1, cron='* * * *')
		

		# create a parameter estimation object
		#self.optimization_model = Optimization_model(self._sh)
		

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

	
	def parse_logic(self, logic):
		pass


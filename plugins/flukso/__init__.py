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
from urllib.request import urlopen

logger = logging.getLogger('')

class Flukso:

	def __init__(self, smarthome, ip=None):
		
		self._sh = smarthome
		if ip:
			self.ip = ip
		
		self.sensors = self._sh.find_items('flukso_sensor')

	def run(self):

		# schedule measurements
		self._sh.scheduler.add('Flukso', self.read_api, prio=2, cron='* * * *')
		logger.info('Flukso initialized')


	def read_api(self):

		for item in self.sensors:
			try:
				# get data from the flukso api
				response = urlopen( 'http://%s:8080/sensor/%s?version=1.0&unit=%s&interval=minute' % (self.ip,item.conf['flukso_sensor'],item.conf['unit']) )
				line = response.read().decode("utf-8")

				# split line into array and take the mean value
				if line:
					data = eval(line.replace('"nan"',"float('nan')"))
					values = [row[1] for row in data]

					# calculate the average of all values and set item to this value
					item(np.nanmean(values))

			except:
				logger.warning('Could not read flukso api for sensor %s' % (item.conf['flukso_sensor']) )


	def stop(self):
		self.alive = False
		
	def parse_item(self, item):
		pass
	
	def update_item(self, item, caller=None, source=None, dest=None):
		pass

	def parse_logic(self, logic):
		pass


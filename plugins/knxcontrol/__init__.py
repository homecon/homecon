#!/usr/bin/env python3

import logging

import numpy as np
import pymysql

from measurements import *
from mysql import *

logger = logging.getLogger('')


class KNXControl:

	def __init__(self, smarthome, mysql_pass='admin'):
		logger.info('KNXControl started')
		
		self._sh = smarthome
		self._mysql_pass = mysql_pass

		# initialize mysql
		self.mysql = Mysql(self._sh,self._mysql_pass)


		logger.warning(self)
		logger.warning(dir(self.mysql))

	def run(self):
		self.alive = True
		
		# create measurements object
		self.measurements = Measurements(self._sh,self._mysql_pass)
		logger.warning(dir(self.measurements))
		
		# initialize measurements
		self._sh.scheduler.add('measurements', self.measurements.minute(), prio=2, cron='* * * *')
		self._sh.scheduler.add('measurements average quarterhour', self.measurements.quarterhour(), prio=5, cron='0,15,30,45  * * *')
		self._sh.scheduler.add('measurements average week', self.measurements.week(), prio=5, cron='1 0 * 0')
		self._sh.scheduler.add('measurements average month', self.measurements.month(), prio=5, cron='0 0 1 *')
		
	def stop(self):
		self.alive = False

	def parse_item(self, item):
		# do nothing
		0
		
	def _test(self):
		logger.warning(self)
	
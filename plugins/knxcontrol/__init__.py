#!/usr/bin/env python3

import logging
import threading

import numpy as np
import pymysql



logger = logging.getLogger('')


class KNXControl:

	def __init__(self, smarthome):
		logger.info('KNXControl started')
		
		self._sh = smarthome
		self._lock = threading.Lock()

		
		self._sh.scheduler.add('MysqlMeasurements', self._test, prio=5, cron='* * * *')

	
	def _test():
		logger.info('KNXControl _test')

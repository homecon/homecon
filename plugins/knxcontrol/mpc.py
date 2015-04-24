#!/usr/bin/env python3

import logging
import pymysql
import datetime
import numpy as np
import pyipopt


logger = logging.getLogger('')

class MPC:

	def __init__(self,smarthome):
		self._sh = smarthome
		
	def _load_measurement(self,mysqlcur,ids,time):
	
		temp = np.zeros((N+1,len(ids)))
		for idx,val in enumerate(ids):
			try:
				mysqlcur.execute("SELECT time,value FROM  measurement_average_quarterhour WHERE signal_id=%s AND time>%s" %(val,time[0]))
				data = np.asarray(list(mysqlcur))
				temp[:,idx] = np.interp(time,data[:,0],data[:,1],left=data[0,1],right=data[-1,1])
			except:
				logger.warning('Not enough data in quarter hour measurements')
	
		return temp
		
	def system_identification(self):
		con = pymysql.connect('localhost', 'knxcontrol', sh.knxcontrol.mysql.conf['password'], 'knxcontrol')
		cur = con.cursor()

		# define time
		dt = 900
		t = np.arange(0,7*24*3600,dt)
		N = t.shape[0]-1

		now = datetime.datetime.utcnow();
		timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )
		timestamp_start = timestamp - 3600 - t[-1]

		# load required measurements
		T_zon_meas = self._load_measurement(self,cur,signal_id['zone_temperature'],timestamp_start+t)
		T_amb_meas = np.mean(self._load_measurement(self,cur,signal_id['ambient_temperature'],timestamp_start+t),axis=1)
		fanspeed_meas = self._load_measurement(self,cur,signal_id['fanspeed'],timestamp_start+t)
		direct_meas = np.mean(self._load_measurement(self,cur,signal_id['direct'],timestamp_start+t),axis=1)
		diffuse_meas = np.mean(self._load_measurement(self,cur,signal_id['diffuse'],timestamp_start+t),axis=1)
		shading_meas = self._load_measurement(self,cur,signal_id['shading'],timestamp_start+t)
		heat_emission = self._load_measurement(self,cur,signal_id['heat_emission'],timestamp_start+t)
		heat_production = self._load_measurement(self,cur,signal_id['heat_production'],timestamp_start+t)

		
		
		
		
		

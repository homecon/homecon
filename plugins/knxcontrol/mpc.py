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

		# load the required measurment ids
		self.measurement_id = {}
		self.measurement_id['ambient_temperature'] = self._load_ids('knxcontrol.weather.current.temperature')
		self.measurement_id['direct_irradiation']  = self._load_ids('knxcontrol.weather.current.irradiation.direct')
		self.measurement_id['diffuse_irradiation'] = self._load_ids('knxcontrol.weather.current.irradiation.diffuse')
		self.measurement_id['clouds']              = self._load_ids('knxcontrol.weather.current.irradiation.clouds')
		self.measurement_id['zone_temperature']    = self._load_ids('knxcontrol.building',value='temperature')
		self.measurement_id['zone_emission']       = self._load_ids('knxcontrol.building',value='emission.power')
		self.measurement_id['zone_irradiation']    = self._load_ids('knxcontrol.building',value='irradiation.power')
		self.measurement_id['heat_production']     = self._load_ids('knxcontrol.heat_production',value='power')
		self.measurement_id['fanspeed']            = self._load_ids('knxcontrol.ventilation',value='fanspeed')

		logger.warning(self.measurement_id)
		
		system_identification(self)



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
		T_amb_meas   = np.mean(self._load_measurement(self,cur,self.measurement_id['ambient_temperature'],timestamp_start+t),axis=1)
		direct_meas  = np.mean(self._load_measurement(self,cur,self.measurement_id['direct_irradiation'],timestamp_start+t),axis=1)
		diffuse_meas = np.mean(self._load_measurement(self,cur,self.measurement_id['diffuse_irradiation'],timestamp_start+t),axis=1)
		clouds_meas  = self._load_measurement(self,cur,self.measurement_id['clouds'],timestamp_start+t)
		
		T_zon_meas    = np.mean(self._load_measurement(self,cur,self.measurement_id['zone_temperature'],timestamp_start+t),axis=1)
		Q_emi_meas    = self._load_measurement(self,cur,self.measurement_id['zone_emission'],timestamp_start+t)
		Q_sol_meas    = self._load_measurement(self,cur,self.measurement_id['zone_irradiation'],timestamp_start+t)
		fanspeed_meas = np.sum(self._load_measurement(self,cur,self.measurement_id['fanspeed'],timestamp_start+t))
		Q_pro_meas    = self._load_measurement(self,cur,self.measurement_id['heat_production'],timestamp_start+t)

		logger.warning(T_zon_meas)


	def _load_ids(self,parent,value=None):
		"""
		"""
		signal_id= []
		if value:
			for child in self._sh.return_item(parent):
				item = self._sh.return_item(child.id()+'.'+value)
				signal_id.append(item.conf['mysql_id'])
		else:
			item = self._sh.return_item(parent)
			signal_id.append(item.conf['mysql_id'])

		return signal_id


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
	
		

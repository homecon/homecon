#!/usr/bin/env python3

import logging
import pymysql
import datetime
import numpy as np
import pyipopt


logger = logging.getLogger('')

class OCmodel:

	def __init__(self,smarthome):

		self._sh = smarthome

		# define time
		self.dt = 900
		self.t = np.arange(0,0.5*24*3600,self.dt)
		self.N = self.t.shape[0]-1

		now = datetime.datetime.utcnow();
		minute = int(np.floor(int(now.strftime('%M'))/15)*15)
		enddate = now.replace(minute=minute,second=0, microsecond=0)
		epoch = datetime.datetime(1970,1,1)

		self.starttimestamp = int( (enddate - datetime.datetime(1970,1,1)).total_seconds() ) -self.t[-1]



		# create variables
		self.nvars = 0
		self.vars = {}
		self.vars['T_zon'] = _op_variable(self._sh,self,False,items=['knxcontrol.building.living_zone.temperature'],operation='avg')
		self.vars['T_amb'] = _op_variable(self._sh,self,False,items=['knxcontrol.weather.current.temperature'],operation='avg')
		self.vars['P_emi'] = _op_variable(self._sh,self,False,items=['knxcontrol.building.*.emission.power'],operation='sum')
		self.vars['P_sol'] = _op_variable(self._sh,self,False,items=['knxcontrol.building.*.irradiation.power'],operation='sum')
		self.vars['P_pro'] = _op_variable(self._sh,self,False,items=['knxcontrol.heat_production.*.power'],operation='sum')
		self.vars['V_ven'] = _op_variable(self._sh,self,False,items=['knxcontrol.ventilation.*.fanspeed'],operation='sum')
		self.vars['C_zon'] = _op_variable(self._sh,self,True)		
		self.vars['UA_zon_amb'] = _op_variable(self._sh,self,True)
		self.vars['n_emi'] = _op_variable(self._sh,self,True)
		self.vars['n_sol'] = _op_variable(self._sh,self,True)
		self.vars['n_pro'] = _op_variable(self._sh,self,True)
		self.vars['n_ven'] = _op_variable(self._sh,self,True)
		

		logger.warning(self.vars['T_zon'].measurement)
		

		#self.identify()



	def identify(self):
		pass


	
class _op_variable:

	def __init__(self,smarthome,ocmodel,parameter,items=None,operation=None):
		"""
		Defines a variable in the optimization problems
		Inputs:
		smarthome:  the smarthome object
		ocmodel:    the parent optimal control model
		parameter:  true/false if it is a parameter (fixed over time)
		items:      list of itemstrings for the measurement item and
        avg:        a boolean if an average or total is to be taken
		"""
		self._sh = smarthome
		self._ocmodel = ocmodel

		if parameter:
			self.ind = self._ocmodel.nvars
			self._ocmodel.nvars = self._ocmodel.nvars + 1
		else:
			self.ind = self._ocmodel.nvars + np.arange(len(self._ocmodel.t))
			self._ocmodel.nvars = self._ocmodel.nvars + np.arange(len(self._ocmodel.t))
		
		values = np.empty((self._ocmodel.N+1,0))

		if items:
			for itemstr in items:
				# load the data
				value = self._load_measurement(itemstr)
				if np.any(value):
					values = np.concatenate((values,value),axis=1)

		# average or total the data if required
		if operation == 'avg':
			self.measurement = np.mean(values,axis=1)
		elif operation == 'sum':
			self.measurement = np.sum(values,axis=1)
		else:
			self.measurement = values

		self.value = None
		
		
	def _load_measurement(self,itemstr):
		"""
		Loads measurement data from mysql
		Inputs:
		itemstr:     item string
		"""
		time = self._ocmodel.t + self._ocmodel.starttimestamp

		ids = []
		try:
			for item in self._sh.match_items(itemstr):
				ids.append(item.conf['mysql_id'])
		except:
			logger.warning('Could not find mysql_id for %s' % (itemstr))
			return None

		value = np.empty((self._ocmodel.N+1,0))

		con = pymysql.connect('localhost', 'knxcontrol', self._sh.knxcontrol.mysql.conf['password'], 'knxcontrol')
		cur = con.cursor()

		for ind,id in enumerate(ids):
			try:
				# get the data from mysql
				cur.execute("SELECT time,value FROM  measurement_average_quarterhour WHERE signal_id=%s AND time>%s" % (id,time[0]))		
				data = np.asarray(list(cur))
				temp = np.expand_dims(np.interp(time,data[:,0],data[:,1],left=data[0,1],right=data[-1,1]),axis=1)			
				value = np.concatenate((value,temp),axis=1)
			except:
				logger.warning('Not enough data for id:%s in quarter hour measurements' % (id) )


		con.commit()
		con.close()
		return value
			

class _op_constraint:
	def __init__(self,smarthome,ocmodel,parameter,items=None,operation=None):
	"""
	Defines a constraint in the optimization problems
	Inputs:
	smarthome:  the smarthome object
	ocmodel:    the parent optimal control model
	parameter:  true/false if it is a parameter (fixed over time)
	items:      list of itemstrings for the measurement item and
    avg:        a boolean if an average or total is to be taken
	"""
	self._sh = smarthome
	self._ocmodel = ocmodel




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
		self.vars['T_zon'] = _op_variable(self,False,items=['knxcontrol.building.living_zone.temperature'],operation='avg')
		self.vars['T_amb'] = _op_variable(self,False,items=['knxcontrol.weather.current.temperature'],operation='avg')
		self.vars['P_emi'] = _op_variable(self,False,items=['knxcontrol.building.*.emission.power'],operation='sum')
		self.vars['P_sol'] = _op_variable(self,False,items=['knxcontrol.building.*.irradiation.power'],operation='sum')
		self.vars['P_pro'] = _op_variable(self,False,items=['knxcontrol.heat_production.*.power'],operation='sum')
		self.vars['V_ven'] = _op_variable(self,False,items=['knxcontrol.ventilation.*.fanspeed'],operation='sum')
		self.vars['C_zon'] = _op_variable(self,True)		
		self.vars['UA_zon_amb'] = _op_variable(self,True)
		self.vars['n_emi'] = _op_variable(self,True)
		self.vars['n_sol'] = _op_variable(self,True)
		self.vars['n_pro'] = _op_variable(self,True)
		self.vars['n_ven'] = _op_variable(self,True)
		

		logger.warning(self.vars['P_sol'].measurement)
		logger.warning(self.vars['P_sol'].ind)

		# create constraints
		self.cons['T_zon_state'] = _op_constraint(self,'C_zon*(T_zon[i+1]-T_zon[i])/dt - UA_zon_amb*(T_amb[i]-T_zon[i]) - n_emi*P_emi[i] - n_sol*P_sol[i]',0,0,
                                                      {'C_zon':'(T_zon[i+1]-T_zon[i])/dt','T_zon[i+1]':'C_zon/dt','T_zon[i]':'-C_zon/dt+UA_zon_amb','UA_zon,amb':'-(T_amb[i]-T_zon[i])','T_amb[i]':'-UA_zon_amb','n_emi':'-P_emi[i]','P_emi[i]':'-n_emi','n_sol':'-P_sol[i]','P_sol[i]':'-n_sol'},
 													  {'C_zon*T_zon[i+1]':'1/dt','C_zon*T_zon[i]':'-1/dt','UA_zon_amb*T_amb[i]':'-1','UA_zon_amb*T_zon[i]':'-1','n_emi*P_emi[i]':'-1','n_sol*P_sol[i]':'-1'},i=np.arange(self.N))

		logger.warning(self.cons['T_zon_state'].c)
		#self.identify()



	def identify(self):
		pass


	
class _op_variable:

	def __init__(self,ocmodel,parameter,items=None,operation=None):
		"""
		Defines a variable in the optimization problems
		Inputs:
		ocmodel:    the parent optimal control model
		parameter:  true/false if it is a parameter (fixed over time)
		items:      list of itemstrings for the measurement item and
        avg:        a boolean if an average or total is to be taken
		"""
		self._ocmodel = ocmodel

		if parameter:
			self.ind = [self._ocmodel.nvars]
			self._ocmodel.nvars = self._ocmodel.nvars + 1
		else:
			self.ind = self._ocmodel.nvars + np.arange(self._ocmodel.N+1)
			self._ocmodel.nvars = self._ocmodel.nvars + self._ocmodel.N + 1
		
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
		else:
			self.measurement = None

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
			for item in self._ocmodel._sh.match_items(itemstr):
				ids.append(item.conf['mysql_id'])
		except:
			logger.warning('Could not find mysql_id for %s' % (itemstr))
			return None

		value = np.empty((self._ocmodel.N+1,0))

		con = pymysql.connect('localhost', 'knxcontrol', self._ocmodel._sh.knxcontrol.mysql.conf['password'], 'knxcontrol')
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

	def __init__(self,ocmodel,constraint,constraint_min,constraint_max,jacobian,hessian,i=0):
		"""
		Defines a constraint in the optimization problems of the form c_min <= c <= c_max
	
		Inputs:
		ocmodel:          the parent optimal control model
		constraint:       an expression for the value of the constraint function 
		constraint_min:   a minimum value or array of minimum values for the constraint
		constraint_max:   a maximum value or array of maximum values for the constraint
		jacobian:         a dict defining the nonzero 1st derivatives of the constraint with expressions e.g. {'x':'dc/dx'}
		hessian:          a dict defining the nonzero 2nd derivatives of the constraint with expressions e.g. {'x*y':'d2c/dx/dy'}
		i                 an array of indices len(i) constriants will be created,'[i-1]','[i]' and '[i+1]' will be replaced by its value
		"""

		self._ocmodel = ocmodel
		
		self.c_min = constraint_min
		self.c_max = constraint_max
	
		self.c = []
		self.J = []
		for ind in i:
			# parse the constraint string
			temp = constraint
			for v in self._ocmodel.vars:
				if ind   >= 0 and ind   < len(self._ocmodel.vars[v].ind):
					temp = temp.replace(v+'[i]', 'x[%s]' % (self._ocmodel.vars[v].ind[ind]))
				if ind+1 >= 0 and ind+1 < len(self._ocmodel.vars[v].ind):
					temp = temp.replace(v+'[i+1]', 'x[%s]' % (self._ocmodel.vars[v].ind[ind+1]))
				if ind-1 >= 0 and ind-1 < len(self._ocmodel.vars[v].ind):
					temp = temp.replace(v+'[i-1]', 'x[%s]' % (self._ocmodel.vars[v].ind[ind-1]))

				temp = temp.replace(v, 'x[%s]' % (self._ocmodel.vars[v].ind[0]))

				temp = temp.replace('dt', '%s' % (self._ocmodel.dt))
			self.c.append(temp)


			# parse jacobian string
			#self.J.append( '[0' + ',0'*(self._ocmodel.nvars-1) + ']' )
			

		logger.warning(self.c)






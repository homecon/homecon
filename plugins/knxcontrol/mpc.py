#!/usr/bin/env python3

import logging
import pymysql
import datetime
import numpy as np
import pyipopt
import sympy

logger = logging.getLogger('')

class Optimization_model:

	def __init__(self,smarthome):

		self._sh = smarthome

		logger.warning('Start defining optimization model')

		# define time
		self.dt = 900
		self.t = np.arange(0,7*24*3600,self.dt)
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
		
		logger.warning('Adding constraints')
		# create constraints
		self.cons = {}
		self.ncons = 0
		self.cons['T_zon_state'] = _op_constraint(self,'C_zon*(T_zon[i+1]-T_zon[i])/dt - UA_zon_amb*(T_amb[i]-T_zon[i]) - n_emi*P_emi[i] - n_sol*P_sol[i]',0,0,i=np.arange(self.N))
		self.cons['P_emi_P_pro'] = _op_constraint(self,'P_emi[i]-n_pro*P_pro[i]',0,0,i=np.arange(self.N+1))
		
		self.cons['T_amb']       = _op_constraint(self,'T_amb[i]-T_amb.value[i]',0,0,i=np.arange(self.N+1))
		self.cons['P_emi']       = _op_constraint(self,'P_emi[i]-P_emi.value[i]',0,0,i=np.arange(self.N+1))
		self.cons['P_sol']       = _op_constraint(self,'P_sol[i]-P_sol.value[i]',0,0,i=np.arange(self.N+1))
		self.cons['P_pro']       = _op_constraint(self,'P_pro[i]-P_pro.value[i]',0,0,i=np.arange(self.N+1))
		self.cons['V_ven']       = _op_constraint(self,'V_ven[i]-V_ven.value[i]',0,0,i=np.arange(self.N+1))
		self.cons['n_emi']       = _op_constraint(self,'n_emi[i]-1',0,0,i=np.arange(self.N+1))
		
		
		logger.warning('Creating objective')
		# create objective
		self.obj = {}
		self.obj['T_zon'] = _op_objective(self,'(T_zon[i]-T_zon.value[i])**2',i=np.arange(self.N))

		# test
		x = np.random.rand(self.nvars)

		logger.warning('Start evaluation')
		logger.warning( self.objective(x) )
		logger.warning( self.gradient(x) )
		logger.warning( self.constraint(x) )
		logger.warning( self.jacobian(x,True) )
		logger.warning( self.jacobian(x,False) )
		logger.warning('End evaluation')
		
		# # prepare ipopt
	
		#self.solve()

		logger.warning('Optimization model ready')
		
	def objective(self,x):
		total = 0
		for key in self.obj:
			total = total + np.array(self.obj[key].f(x))
		
		return total
		
	def gradient(self,x):
		total = np.zeros(self.nvars)
		for key in self.obj:
			total = total + np.array(self.obj[key].g(x))
		
		return total
		
	def constraint(self,x):
		total = np.zeros(self.ncons)
		for key in self.cons:
			total[self.cons[key].ind] = self.cons[key].c(x)
		
		return total

	def jacobian(self,x,flag):
		
		if flag:
			row = np.empty((1,0))
			col = np.empty((1,0))
			for key in self.cons:
				(row_temp,col_temp) = self.cons[key].J(x,True)
				row = np.append(row,row_temp)
				col = np.append(col,col_temp)
			return (row,col)

		else:
			total = np.empty((1,0))
			for key in self.cons:
				total = np.append(total,self.cons[key].J(x,False))
			return total
	
	
	def solve(self):
		pass
		
		# prepare ipopt
		# nlp = pyipopt.create(self.nvars, x_L, x_U, ncons, c_L, c_U, nnzj, nnzh, objective, gradient, constraint, jacobian)
		# 
		# 
		# x, zl, zu, constraint_multipliers, obj, status = nlp.solve(x0)
		# print()
		# print( 'solution: ' + str(x) )
		# print()
		# print()
		# print()


	
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
				if value.size:
					values = np.concatenate((values,value),axis=1)

			# average or total the data if required
			if operation == 'avg':
				self.value = np.mean(values,axis=1)
			elif operation == 'sum':
				self.value = np.sum(values,axis=1)
			else:
				self.value = values
		else:
			self.value = []

		
		
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
				logger.warning('Not enough data for id:%s in quarterhour measurements' % (id) )

		con.commit()
		con.close()
		return value
			

class _op_constraint:

	def __init__(self,ocmodel,constraint,constraint_min,constraint_max,i=0):
		"""
		Defines a constraint in the optimization problems of the form c_min <= c <= c_max
	
		Inputs:
		ocmodel:          the parent optimal control model
		constraint:       an expression for the value of the constraint function 
		constraint_min:   a minimum value or array of minimum values for the constraint
		constraint_max:   a maximum value or array of maximum values for the constraint
		i:                an array of indices len(i) constraints will be created, '[i-1]', '[i]' and '[i+1]' will be replaced by its value
		"""

		self._ocmodel = ocmodel
		
		self.c_min = constraint_min
		self.c_max = constraint_max
	
		# create symbolic variables
		x = sympy.MatrixSymbol('x', self._ocmodel.nvars, 1)


		temp_c_str = []
		temp_J_str = []
		self.J_row = []
		self.J_col = []
		self.ind = []
		for ind in i:
			self.ind.append(self._ocmodel.ncons)
			self._ocmodel.ncons = self._ocmodel.ncons+1
			# parse the constraint string
			for v in self._ocmodel.vars:
				if ind   >= 0 and ind   < len(self._ocmodel.vars[v].ind):
					if len(self._ocmodel.vars[v].value) > ind:
						constraint = constraint.replace(v+'.value[i]', '%s' % (self._ocmodel.vars[v].value[ind]))
					constraint = constraint.replace(v+'[i]', 'x[%s]' % (self._ocmodel.vars[v].ind[ind]))

				if ind+1 >= 0 and ind+1 < len(self._ocmodel.vars[v].ind):
					if len(self._ocmodel.vars[v].value) > ind+1:
						constraint = constraint.replace(v+'.value[i+1]', '%s' % (self._ocmodel.vars[v].value[ind+1]))
					constraint = constraint.replace(v+'[i+1]', 'x[%s]' % (self._ocmodel.vars[v].ind[ind+1]))
				if ind-1 >= 0 and ind-1 < len(self._ocmodel.vars[v].ind):
					if len(self._ocmodel.vars[v].value) > ind-1:
						constraint = constraint.replace(v+'.value[i-1]', '%s' % (self._ocmodel.vars[v].value[ind-1]))
					constraint = constraint.replace(v+'[i-1]', 'x[%s]' % (self._ocmodel.vars[v].ind[ind-1]))
						
				if len(self._ocmodel.vars[v].value) > 0:
					constraint = constraint.replace(v+'.value', '%s' % (self._ocmodel.vars[v].value[0]))
				constraint = constraint.replace(v, 'x[%s]' % (self._ocmodel.vars[v].ind[0]))
				constraint = constraint.replace('dt', '%s' % (self._ocmodel.dt))
			
			temp_c_str.append(constraint)

			# create a jacobian strings,rows and cols
			for k in np.arange(self._ocmodel.nvars):
				if constraint.find('x[%s]' % k) >= 0:
					self.J_row.append(ind)
					self.J_col.append(k)
					# added '+0.01' because of bug in sympy, doesn't make a difference anyway 
					temp_J_str.append( str(sympy.diff( eval(constraint+'+0.01'),eval('x[%s]' % k) )).replace(', 0]',']') )
					

		# combine the arrays into a single string
		temp_c_str = ' , '.join(temp_c_str)
		self.c_str = '['+temp_c_str+']'

		temp_J_str = ' , '.join(temp_J_str)
		self.J_str = '['+temp_J_str+']'

	def c(self,x):
		return np.array(eval(self.c_str))


	def J(self,x,flag):
		if flag:
			return (np.array(self.J_row),np.array(self.J_col))
		else:
			return np.array(eval(self.J_str))


class _op_objective:

	def __init__(self,ocmodel,objective,i=0):
		"""
		Defines an objective. All objectives are added in the end
		Inputs:
		ocmodel:          the parent optimal control model
		objective:        an expression for the value of the objective function 
		i:                an array of indices len(i) objectives will be created, '[i-1]', '[i]' and '[i+1]' will be replaced by its value
		"""

		self._ocmodel = ocmodel
		
		# create symbolic variables
		x = sympy.MatrixSymbol('x', self._ocmodel.nvars, 1)

		temp_f_str = []
		temp_g_str = []
		
		for ind in i:
			# parse the objective string
			for v in self._ocmodel.vars:
				if ind   >= 0 and ind   < len(self._ocmodel.vars[v].ind):
					if len(self._ocmodel.vars[v].value) > ind:
						objective = objective.replace(v+'.value[i]', '%s' % (self._ocmodel.vars[v].value[ind]))
					objective = objective.replace(v+'[i]', 'x[%s]' % (self._ocmodel.vars[v].ind[ind]))
				if ind+1 >= 0 and ind+1 < len(self._ocmodel.vars[v].ind):
					if len(self._ocmodel.vars[v].value) > ind:
						objective = objective.replace(v+'.value[i+1]', '%s' % (self._ocmodel.vars[v].value[ind+1]))
					objective = objective.replace(v+'[i+1]', 'x[%s]' % (self._ocmodel.vars[v].ind[ind+1]))
				if ind-1 >= 0 and ind-1 < len(self._ocmodel.vars[v].ind):
					if len(self._ocmodel.vars[v].value) > ind:
						objective = objective.replace(v+'.value[i-1]', '%s' % (self._ocmodel.vars[v].value[ind-1]))
					objective = objective.replace(v+'[i-1]', 'x[%s]' % (self._ocmodel.vars[v].ind[ind-1]))
						
				if len(self._ocmodel.vars[v].value) > 0:
					objective = objective.replace(v+'.value', '%s' % (self._ocmodel.vars[v].value[0]))
				objective = objective.replace(v, 'x[%s]' % (self._ocmodel.vars[v].ind[0]))
				objective = objective.replace('dt', '%s' % (self._ocmodel.dt))
			
			temp_f_str.append(objective)
			
			
			# create gradient strings
			temp_temp_g_str = []
			for k in np.arange(self._ocmodel.nvars):
				if objective.find('x[%s]' % k) >= 0:
					temp_temp_g_str.append( str(sympy.diff( eval(objective),eval('x[%s]' % k) )).replace(', 0]',']') )
				else:
					temp_temp_g_str.append('0')
			
			temp_temp_g_str = ' , '.join(temp_temp_g_str)
			temp_temp_g_str = '['+temp_temp_g_str+']'
			temp_g_str.append(temp_temp_g_str)
			
		# combine the arrays into a single string
		temp_f_str = ' , '.join(temp_f_str)
		self.f_str = '['+temp_f_str+']'

		temp_g_str = ' , '.join(temp_g_str)
		self.g_str = '['+temp_g_str+']'
		

	def f(self,x):
		return eval(self.f_str)

	def g(self,x):
		return np.array(eval(self.g_str))



#!/usr/bin/env python3

import logging
import pymysql
import datetime
import numpy as np
import pyipopt
import parsenlp

logger = logging.getLogger('')


class Model:
	def __init__(self):
		"""
		define the general model variables and equations used in the
		systemidentification and the optimal control problem
		"""		

		# define model parameters
		parameters = {}
		parameters['C_op'] = Variable('C_op',[],0.1e6,100e6,10e6) 
		parameters['UA_op_amb'] = Variable('UA_op_amb',[],1,1000,100) 

		# define model measured states as parsenlp.Expressions without indices
		measured_states = {}
		measured_states['T_op'] = Variable('T_op[i]',['i'],-40,60,20) 

		# define model estimated states as parsenlp.Expressions without indices
		unmeasured_states = {}

		# define model inputs as parsenlp.Expressions without indices
		inputs = {}
		inputs['T_amb'] = Variable('T_amb[i]',['i'],-40,60,15)
		inputs['Q_sol'] = Variable('Q_sol[i]',['i'],0,100e3,1e3)
		inputs['Q_hea'] = Variable('Q_hea[i]',['i'],0,100e3,1e3)

		# define model state equations as parsenlp.Expressions without indices
		state_equations = {}
		state_equations['T_op'] = parsenlp.Expression('C_op*(T_op[i+1]-T_op[i])/dt - UA_op_amb*(T_amb[i]-T_op[i]) - Q_sol[i] - Q_hea[i]',['i']) 

		# add gradient expressions for the state equations

		self.parameters = parameters
		self.measured_states = measured_states
		self.unmeasured_states = unmeasured_states
		self.inputs = inputs
		self.state_equations = state_equations

class Variable(parsenlp.Expression):
	def __init__(self,string,indexnames,lowerbound,upperbound,value=None):
		parsenlp.Expression.__init__(self,string,indexnames)
		
		self.lowerbound = lowerbound
		self.upperbound = upperbound
		if value == None:
			self.value = 0.5*lowerbound + 0.5*upperbound
		else:
			self.value = value


class MPC:
	def __init__(self,homecon):

		self.homecon = homecon

		self.model = Model()
		systemidentification = Systemidentification(self)



class Systemidentification:
	def __init__(self,mpc):
		"""
		define the system identification model
		"""
		self.mpc = mpc
		self.homecon = self.mpc.homecon

		model = self.mpc.model

		logger.warning('Start defining system identification model')

		# define time
		self.dt = 3600
		self.t = np.arange(0,1*24*3600,self.dt)
		self.N = self.t.shape[0]


		nlp = parsenlp.Problem()
		
		# define parameters as the model measured states, and inputs and timestep
		logger.warning('Adding parameters')
		parameters = {}
		parameters['dt'] = np.array(nlp.add_parameter('dt',self.dt))

		for key in model.measured_states:
			var = model.measured_states[key]
			parameters[key] = np.empty((self.N), dtype=object)
			for i in range(self.N):
				parameters[key][i]  = nlp.add_parameter('mmnt_'+var.parse([[i]]),var.value)

		for key in model.inputs:
			var = model.inputs[key]
			parameters[key] = np.empty((self.N), dtype=object)
			for i in range(self.N):
				parameters[key][i]  = nlp.add_parameter(var.parse([[i]]),var.value)
		

		# define variables from model parameters and states
		logger.warning('Adding variables')
		variables = {}
		for key in model.parameters:
			var = model.parameters[key]
			variables[key] = np.array([nlp.add_variable(var.parse(),lowerbound=var.lowerbound,upperbound=var.upperbound,value=var.value)])
		
		for dic in [model.measured_states,model.unmeasured_states]:
			for key in dic:
				var = dic[key]
				variables[key] = np.empty((self.N), dtype=object)
				for i in range(self.N):
					variables[key][i]  = nlp.add_variable(var.parse([[i]]),lowerbound=var.lowerbound,upperbound=var.upperbound,value=var.value)
		
		# define constraints
		logger.warning('Adding constraints')
		constraints = {}
		for key in model.state_equations:
			expr = model.state_equations[key]
			constraints[key] = np.empty((self.N-1), dtype=object)
			for i in range(self.N-1):
				constraints[key][i] = nlp.add_constraint(expr.parse([[i]]),lowerbound=0.,upperbound=0.)
			
		# define objective
		logger.warning('Adding objective')
		objective = []
		for key in model.measured_states:
			var = model.measured_states[key]
			name = 'mmnt_'+var.string
			mmnt_name = 'mmnt_'+name
			objective.append('sum(('+name+'-'+mmnt_name+')**2,i)')

		nlp.set_objective(parsenlp.Expression('+'.join(objective),['i'],[range(self.N)]).parse()) 

		# create an initial guess
		self.initialguess = nlp.get_values()

		self.parameters = parameters
		self.variables = variables		
		self.constraints = constraints
		self.nlp = nlp

		logger.warning('System identification model ready')

	def __call__(self):
		"""
		run the system identification
		"""

		logger.warning('Start system identification')

		# get the data start time
		now = datetime.datetime.utcnow();
		minute = int(np.floor(int(now.strftime('%M'))/15)*15)
		enddate = now.replace(minute=minute,second=0, microsecond=0)
		epoch = datetime.datetime(1970,1,1)

		starttimestamp = int( (enddate - datetime.datetime(1970,1,1)).total_seconds() ) -self.t[-1]
		time = starttimestamp + self.t

		logger.warning('Loading data')
		# get the required data from the database
		parameter_values = {}

		parameter_values['dt'] = self.dt
		parameter_values['T_amb'] = _load_measurement(self,'knxcontrol.weather.current.temperature',time)	
		Tl    = _load_measurement(self,'livingzone.temperature',time)
		Ts    = _load_measurement(self,'sleepingzone.temperature',time)	
		Tb    = _load_measurement(self,'bathrooms.temperature',time)	
		parameter_values['T_op']  = np.mean( np.concatenate((Tl,Ts,Tb),axis=1) ,axis=1)

		Pgb   = _load_measurement(self,'knxcontrol.heat_production.gasboiler.power',time)
		Php   = _load_measurement(self,'knxcontrol.heat_production.heatpump.power',time)
		parameter_values['Q_hea'] = 0.9*Pgb + 3*Php  # assumes constant efficiencies and cop

		Ql    = _load_measurement(self,'livingzone.irradiation',time)
		Qs    = _load_measurement(self,'sleepingzone.irradiation',time)
		Qb    = _load_measurement(self,'bathrooms.irradiation',time)
		parameter_values['Q_sol'] = Ql + Qs + Qb

		# set the parameter values
		for par,par_val in zip(self.parameters,parameter_values):
			for p,v in zip(par,par_val):
				p.value = v
		
		# set an initial guess for the temperature equal to the measured temperature
		for i in range(self.N):
			self.variables['T_op_sim'][i].value = parameter_values['T_op'][i]

		# update the initial guess
		self.initialguess = problem.get_solution()

		# start the optimization
		logger.warning('Start optimization')
		self.nlp.solve(self.initialguess)		

		# return values
		print( ['{:.1f}'.format(self.variables['T_op_sim'][i].value) for i in range(N)] )
		print( ['{:.1f}'.format(self.variables['T_op'][i].value) for i in range(N)] )
		print( 'UA_op_amb: {:.0f}, C_op: {:.0f}'.format(self.parameters['UA_op_amb'][0].value,self.parameters['C_op'][0].value) )



	def _load_measurement(self,itemstr,time):
		"""
		Loads measurement data from mysql and resamples it to the correct time
		Arguments:
		itemstr:     item string
		time:        time array
		"""

		ids = []
		try:
			for item in self.homecon._sh.match_items(itemstr):
				ids.append(item.conf['mysql_id'])
		except:
			logger.warning('Could not find any mysql_id for %s' % (itemstr))
			return np.array([])

		value = np.empty((self.N,1),dtype=np.float)

		con = pymysql.connect('localhost', 'knxcontrol', self.homecon._mysql_pass, 'knxcontrol')
		cur = con.cursor()

		for i,id in enumerate(ids):
			try:
				# get the data from mysql
				cur.execute("SELECT time,value FROM  measurement_average_quarterhour WHERE signal_id={0} AND time>={1} AND time<={2}".format(id,time[0]-self.dt,time[-1]+self.dt))		
				data = np.asarray(list(cur))
				temp = np.expand_dims(np.interp(time,data[:,0],data[:,1],left=data[0,1],right=data[-1,1]),axis=1)			
				value = np.concatenate((value,temp),axis=1)
			except:
				logger.warning('Not enough data for id:{0} in quarterhour measurements'.format(id) )

		con.commit()
		con.close()
		return value


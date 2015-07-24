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

		measured_states_mmnt = {}
		measured_states_mmnt['T_op_mmnt'] = Variable('T_op_mmnt[i]',['i'],-40,60,20) 

		# add measurement identifiers



		# define model estimated states as parsenlp.Expressions without indices
		unmeasured_states = {}

		# define model inputs as parsenlp.Expressions without indices
		inputs = {}
		inputs['T_amb'] = Variable('T_amb[i]',['i'],-40,60,15)
		inputs['Q_sol'] = Variable('Q_sol[i]',['i'],0,100e3,1e3)
		inputs['Q_hea'] = Variable('Q_hea[i]',['i'],0,100e3,1e3)

		# add measurement identifiers



		# define model state equations as parsenlp.Expressions without indices
		state_equations = {}
		state_equations['T_op'] = parsenlp.Expression('C_op * ( T_op[i+1] - T_op[i] ) / dt - UA_op_amb * ( T_amb[i] - T_op[i] ) - Q_sol[i] - Q_hea[i]',['i']) 
		
		state_equations_gradient = {}
		state_equations_gradient['T_op'] = {'C_op': '( T_op[i+1] - T_op[i] ) / dt',
                                            'UA_op_amb': '-( T_amb[i] - T_op[i] )',
                                            'T_op[i]': '-C_op / dt + UA_op_amb',
                                            'T_op[i+1]': 'C_op / dt',
                                            'T_amb[i]': '-UA_op_amb',
                                            'Q_sol[i]': '-1',
                                            'Q_hea[i]': '-1'}
                                    


		# add gradient expressions for the state equations

		self.parameters = parameters
		self.measured_states = measured_states
		self.measured_states_mmnt = measured_states_mmnt
		self.unmeasured_states = unmeasured_states
		self.inputs = inputs
		self.state_equations = state_equations
		self.state_equations_gradient = state_equations_gradient

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
		self.systemidentification = Systemidentification(self)



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
		nlp.add_parameter('dt',self.dt)

		for key in model.measured_states_mmnt:
			var = model.measured_states_mmnt[key]
			for i in range(self.N):
				nlp.add_parameter(var.parse([[i]]),var.value)

		for key in model.inputs:
			var = model.inputs[key]
			for i in range(self.N):
				nlp.add_parameter(var.parse([[i]]),var.value)
		

		# define variables from model parameters and states
		logger.warning('Adding variables')
		for key in model.parameters:
			var = model.parameters[key]
			np.array([nlp.add_variable(var.parse(),lowerbound=var.lowerbound,upperbound=var.upperbound,value=var.value)])
		
		for dic in [model.measured_states,model.unmeasured_states]:
			for key in dic:
				var = dic[key]
				for i in range(self.N):
					nlp.add_variable(var.parse([[i]]),lowerbound=var.lowerbound,upperbound=var.upperbound,value=var.value)
		
		# define constraints
		logger.warning('Adding constraints')
		for key in model.state_equations:
			expr = model.state_equations[key]
			
			for i in range(self.N-1):

				# parse the gradient dictionary
				gradientdict = {}
				for grad_key in model.state_equations_gradient[key]:
					gradientdict[ parsenlp.Expression(grad_key,['i'],[[i]]).parse() ] = parsenlp.Expression(model.state_equations_gradient[key][grad_key],['i'],[[i]]).parse()
				nlp.add_constraint(expr.parse([[i]]),gradientdict=gradientdict,lowerbound=0.,upperbound=0.,name='{0}[{1}]'.format(key,i))
			

		# define objective
		logger.warning('Adding objective')
		objective = []
		gradientdict = {}
		for key,mmnt_key in zip(model.measured_states,model.measured_states_mmnt):
			var = model.measured_states[key]
			mmnt_var = model.measured_states_mmnt[mmnt_key]
			name = var.string
			mmnt_name = mmnt_var.string
			objective.append('sum(('+name+'-'+mmnt_name+')**2,i)')

			# parse the gradient dictionary
			for i in range(self.N):
				gradientdict[ parsenlp.Expression(name,['i'],[[i]]).parse() ] = parsenlp.Expression('2*'+name+'-2*'+mmnt_name,['i'],[[i]]).parse() 
				gradientdict[ parsenlp.Expression(mmnt_name,['i'],[[i]]).parse() ] = parsenlp.Expression('2*'+mmnt_name+'-2*'+name,['i'],[[i]]).parse()

		nlp.set_objective(parsenlp.Expression('+'.join(objective),['i'],[range(self.N)]).parse(),gradientdict=gradientdict) 

		# create an initial guess
		self.nlp = nlp

		logger.warning('System identification model ready')

	def __call__(self):
		"""
		run the system identification
		"""

		logger.warning('Start system identification')

		model = self.mpc.model

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
		parameter_values['T_amb'] = self._load_measurement('knxcontrol.weather.current.temperature',time)	
		Tl    = self._load_measurement('leefruimtes.temperature',time)
		Ts    = self._load_measurement('slaapkamers.temperature',time)	
		Tb    = self._load_measurement('badkamers.temperature',time)	
		parameter_values['T_op_mmnt']  = np.mean( np.concatenate((Tl,Ts,Tb),axis=1) ,axis=1)
		logger.warning(parameter_values['T_op_mmnt'])

		Pgb   = self._load_measurement('knxcontrol.heat_production.gasboiler.power',time)
		Php   = self._load_measurement('knxcontrol.heat_production.heatpump.power',time)
		parameter_values['Q_hea'] = 0.9*Pgb + 3.0*Php  # assumes constant efficiencies and cop
		logger.warning(0.9*Pgb)
		logger.warning(3.0*Php)
		logger.warning(0.9*Pgb + 3.0*Php)

		Ql    = self._load_measurement('leefruimtes.irradiation',time)
		Qs    = self._load_measurement('slaapkamers.irradiation',time)
		Qb    = self._load_measurement('badkamers.irradiation',time)
		parameter_values['Q_sol'] = Ql + Qs + Qb
		logger.warning(parameter_values['Q_sol'])

		# set the parameter values
		self.nlp.parameters['dt'].value = self.dt
		for key in parameter_values:			
			for i,v in enumerate(parameter_values[key]):
				self.nlp.parameters[key][i].value = v
		
		# set an initial guess for the measured states equal to the measurements
		for key,mmnt_key in zip(model.measured_states,model.measured_states_mmnt):
			for i in range(self.N):
				self.nlp.variables[key][i].value = parameter_values[mmnt_key][i]

		# display all objective, gradient, constraints, ...
		#print( self.nlp.objective.evaluationstring )
		#print( self.nlp.objective.gradientevaluationstring )

		#for c in self.nlp.constraints['T_op']:
		#	print( c.evaluationstring )
		#	print( c.gradientevaluationstring )
		
		# start the optimization
		logger.warning('Start optimization')
		self.nlp.solve()

		# return values
		print( ['{:.1f}'.format(self.nlp.parameters['T_op_mmnt'][i].value) for i in range(self.N)] )
		print( ['{:.1f}'.format(self.nlp.variables['T_op'][i].value) for i in range(self.N)] )
		print( 'UA_op_amb: {:.0f}, C_op: {:.0f}'.format(self.nlp.parameters['UA_op_amb'][0].value,self.parameters['C_op'][0].value) )



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

		for id in ids:
			try:
				# get the data from mysql

				cur.execute("SELECT time,value FROM  measurements_average_quarterhour WHERE signal_id={0} AND time>={1} AND time<={2}".format(id,time[0]-self.dt,time[-1]+self.dt))		
				data = np.asarray(list(cur))
				logger.warning(itemstr)
				logger.warning(time)
				logger.warning(data)
				temp = np.expand_dims(np.interp(time,data[:,0],data[:,1],left=data[0,1],right=data[-1,1]),axis=1)			
				value = temp # np.concatenate((value,temp),axis=1)
			except:
				logger.warning('Not enough data for id:{0} in quarterhour measurements'.format(id) )

		con.commit()
		con.close()
		return value


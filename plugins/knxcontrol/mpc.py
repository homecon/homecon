#!/usr/bin/env python3

import logging
import pymysql
import datetime
import numpy as np
import pyipopt
import parsenlp

logger = logging.getLogger('')







class MPC:
	def __init__(self,homecon):

		self.homecon = homecon


		# model definition
		# define model parameters
		parameters = {}
		parameters['C_op'] = {'expression': parsenlp.Expression('C_op',[]),
                              'lowerbound':   0.1e6,
                              'upperbound': 100.0e6,
                              'initialvalue': 10e6}
 
		parameters['UA_op_amb'] = {'expression': parsenlp.Expression('UA_op_amb',[]),
                                   'lowerbound':    1,
                                   'upperbound': 1000,
                                   'initialvalue': 100}
		logger.debug(parameters)

		# define model measured states
		measured_states = {}
		measured_states['T_op'] = {'expression': parsenlp.Expression('T_op[i]',['i']),
								   'mmnt_key': 'T_op_mmnt',
                                   'mmnt_expression': parsenlp.Expression('T_op_mmnt[i]',['i']),
                                   'lowerbound': -40,
								   'upperbound':  60,
								   'initialvalue': 20,
								   'mysql_data_string': 'np.mean(('+','.join(['[{}]'.format(zone.temperature.conf['mysql_id']) for zone in self.homecon.zones])+'))' }
		logger.debug(measured_states)
		
		# define model unmeasured states
		unmeasured_states = {}
		logger.debug(unmeasured_states)

		# define model inputs
		inputs = {}
		inputs['T_amb'] = {'expression': parsenlp.Expression('T_amb[i]',['i']),
                           'lowerbound': -40,
						   'upperbound':  60,
                           'initialvalue':  12,
                           'mysql_data_string': '[{0}]'.format(self.homecon.weather.current.temperature.conf['mysql_id']) }

		inputs['Q_sol'] = {'expression': parsenlp.Expression('Q_sol[i]',['i']),
                           'lowerbound':   0,
						   'upperbound': 100e3,
                           'initialvalue': 0,
                           'mysql_data_string': 'np.sum(('+','.join(['[{}]'.format(zone.irradiation.conf['mysql_id']) for zone in self.homecon.zones])+'))' }


		inputs['Q_hea'] = {'expression': parsenlp.Expression('Q_hea[i]',['i']),
                           'lowerbound':   0,
						   'upperbound': 100e3,
                           'initialvalue': 0,
                           'mysql_data_string': '0.9 * [{0}] + 3.0 * [{1}]'.format(self.homecon.heat_production.gasboiler.power.conf['mysql_id'],self.homecon.heat_production.heatpump.power.conf['mysql_id']) }   

		logger.debug(inputs)	


		# define model state equations as parsenlp.Expressions without indices
		state_equations = {}
		state_equations['T_op'] = {}
		state_equations['T_op']['function'] = parsenlp.Expression('C_op * ( T_op[i+1] - T_op[i] ) / dt - UA_op_amb * ( T_amb[i] - T_op[i] ) - Q_sol[i] - Q_hea[i]',['i']) 
		state_equations['T_op']['gradient']  = {'C_op': '( T_op[i+1] - T_op[i] ) / dt',
                                                'UA_op_amb': '-( T_amb[i] - T_op[i] )',
                                                'T_op[i]': '-C_op / dt + UA_op_amb',
                                                'T_op[i+1]': 'C_op / dt',
                                                'T_amb[i]': '-UA_op_amb',
                                                'Q_sol[i]': '-1',
                                                'Q_hea[i]': '-1'}



		self.model = Model(self,parameters,measured_states,unmeasured_states,inputs,state_equations)


################################################################################
# Model class
################################################################################
class Model:
	def __init__(self,mpc,parameters,measured_states,unmeasured_states,inputs,state_equations):
		"""
		
		"""		

		self.mpc = mpc

		self.parameters = parameters
		self.measured_states = measured_states
		self.unmeasured_states = unmeasured_states
		self.inputs = inputs
		self.state_equations = state_equations


		self.create_identification_nlp()



	def create_identification_nlp(self):
		"""
		define the identification optimization
		"""
		logger.warning('Start defining system identification model')

		# define time
		self.identificationtimestep = 3600
		self.identificationtime = 1*24*3600

		dt = self.identificationtimestep 
		t = np.arange(0,self.identificationtime,dt)
		N = t.shape[0]

		nlp = parsenlp.Problem()
		
		# define parameters as the model measured states, and inputs and timestep
		# define variables from model parameters and states
		logger.warning('Adding parameters and variables')
		nlp.add_parameter('dt',dt)

		for key in self.measured_states:
			var = self.measured_states[key]
			for i in range(N):
				nlp.add_parameter(var['mmnt_expression'].parse([[i]]),var['initialvalue'])
				nlp.add_variable(var['expression'].parse([[i]]),lowerbound=var['lowerbound'],upperbound=var['upperbound'],value=var['initialvalue'])

		for key in self.unmeasured_states:
			var = self.unmeasured_states[key]
			for i in range(N):
				nlp.add_variable(var['expression'].parse([[i]]),lowerbound=var['lowerbound'],upperbound=var['upperbound'],value=var['initialvalue'])
		
		for key in self.inputs:
			var = self.inputs[key]
			for i in range(N):
				nlp.add_parameter(var['expression'].parse([[i]]),var['initialvalue'])
		
		for key in self.parameters:
			var = self.parameters[key]
			nlp.add_variable(var['expression'].parse(),lowerbound=var['lowerbound'],upperbound=var['upperbound'],value=var['initialvalue'])
		

		# define constraints
		logger.warning('Adding constraints')
		for key in self.state_equations:
			expr = self.state_equations[key]['function']
			
			for i in range(N-1):

				# parse the gradient dictionary
				gradientdict = {}
				for var in self.state_equations[key]['gradient']:
					gradientdict[ parsenlp.Expression(var,['i'],[[i]]).parse() ] = parsenlp.Expression(self.state_equations[key]['gradient'][var],['i'],[[i]]).parse()
				nlp.add_constraint(expr.parse([[i]]),gradientdict=gradientdict,lowerbound=0.,upperbound=0.,name='{0}[{1}]'.format(key,i))
			

		# define objective
		logger.warning('Adding objective')
		objective = []
		gradientdict = {}
		for key in self.measured_states:
			name      = self.measured_states[key]['expression'].string
			mmnt_name = self.measured_states[key]['mmnt_expression'].string
			objective.append('sum(('+name+'-'+mmnt_name+')**2,i)')

			# parse the gradient dictionary
			for i in range(N):
				gradientdict[ parsenlp.Expression(name,['i'],[[i]]).parse() ] = parsenlp.Expression('2*'+name+'-2*'+mmnt_name,['i'],[[i]]).parse() 
				gradientdict[ parsenlp.Expression(mmnt_name,['i'],[[i]]).parse() ] = parsenlp.Expression('2*'+mmnt_name+'-2*'+name,['i'],[[i]]).parse()

		nlp.set_objective(parsenlp.Expression('+'.join(objective),['i'],[range(N)]).parse(),gradientdict=gradientdict) 

		self.identification_nlp = nlp

		logger.warning('System identification model ready')


	def identify(self):
		"""
		run the system identification
		"""

		logger.warning('Start system identification')

		dt = self.identificationtimestep 
		t = np.arange(0,self.identificationtime,dt)
		N = t.shape[0]

		# get the data start time
		now = datetime.datetime.utcnow();
		minute = int(np.floor(int(now.strftime('%M'))/15)*15)
		enddate = now.replace(minute=minute,second=0, microsecond=0)
		epoch = datetime.datetime(1970,1,1)

		starttimestamp = int( (enddate - datetime.datetime(1970,1,1)).total_seconds() ) - t[-1]
		time = starttimestamp + t
		
		# get the required data from the database and set the parameter values and initial values for the measured states
		logger.warning('Loading data')
		self.identification_nlp.parameters['dt'].value = dt

		for key in self.measured_states:		
			values = self._load_data(self.measured_states[key]['mysql_data_string'],time)	
			mmnt_key = self.measured_states[key]['mmnt_key']
			for i,v in enumerate(values):
				self.identification_nlp.parameters[mmnt_key][i].value = v
				self.identification_nlp.variables[key][i].value = v

		for key in self.inputs:		
			values = self._load_data(self.inputs[key]['mysql_data_string'],time)	
			for i,v in enumerate(values):
				self.identification_nlp.parameters[key][i].value = v
				
		
		# start the optimization
		logger.warning('Start optimization')
		self.identification_nlp.solve()
		logger.warning('Finished optimization')

		# print values
		logger.warning( ['{:.1f}'.format(self.identification_nlp.parameters['T_op_mmnt'][i].value) for i in range(N)] )
		logger.warning( ['{:.1f}'.format(self.identification_nlp.variables['T_op'][i].value) for i in range(N)] )
		logger.warning( 'UA_op_amb: {:.0f}, C_op: {:.0f}'.format(self.identification_nlp.variables['UA_op_amb'].value,self.identification_nlp.variables['C_op'].value) )


	def create_validation_nlp(self):
		"""
		define the validation optimization
		"""
		

	def validate(self):
		"""
		compares the identified model with the most recent dataset
		"""

		# get inputs





	def control(self):
		"""
		solve the optimal control problem
		"""
		pass




	def _load_data(self,string,time):
		"""
		Loads measurement data from mysql and resamples it to the correct time

		Arguments:
		string:      a string that can be evaluated using mysqlids as [id] from the database as variables
		time:        numpy.array for times of which data should be returned

		Example:
		self._load_data('0.6 * [10] + 0.4 * [11]')
		or 
		self._load_data('np.sum( '([10],[11],[12])')
		"""

		# find the id's in string
		ids = []
		substring = string
		start = substring.find('[')	
		while start >= 0:
			substring = substring[start:]
			end = substring.find(']')
			if end>0:
				ids.append(int(substring[1:end]))	
				substring = substring[end+1:]
				start = substring.find('[')	
			else:
				start = -1

		if ids==[]:
			logger.warning('Could not find any mysql_id for in "{}"'.fromat(string))
	

		# get the data from mysql and put them in a dictionary
		values = {}
		con,cur = self.mpc.homecon.mysql.create_cursor()
		for id in ids:
			try:
				cur.execute("SELECT time,value FROM  measurements_average_quarterhour WHERE signal_id={0} AND time>={1} AND time<={2}".format(id,time[0]-self.dt,time[-1]+self.dt))		
				data = np.array(list(cur))
				values[id] = np.interp(time,data[:,0],data[:,1],left=data[0,1],right=data[-1,1])			
			except:
				logger.warning('Not enough data for id:{0} in quarterhour measurements'.format(id) )

		con.commit()
		con.close()


		# parse the string using the values
		value = []
		for i,t in enumerate(time):
			try:
				temp = string
				for id in ids:
					temp = temp.replace('[{}]'.format(id),'{}'.format(values[id][i]))

				value.append( eval(temp) )
			except:
				value.append(-1)


		return np.array(value)


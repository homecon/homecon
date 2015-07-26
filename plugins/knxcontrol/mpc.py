#!/usr/bin/env python3
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import logging
import pymysql
import datetime
import numpy as np
import copy
import parsenlp

logger = logging.getLogger('')







class MPC:
	def __init__(self,homecon):

		self.homecon = homecon
		self.item = self.homecon.item.mpc


		# model 1 definition ###################################################
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

		self.model1 = Model(self,parameters,measured_states,unmeasured_states,inputs,state_equations)




		# model choice #########################################################
		self.model = self.model1


################################################################################
# Model class
################################################################################
class Model:
	def __init__(self,mpc,parameters,measured_states,unmeasured_states,inputs,state_equations):
		"""
		
		"""		

		self.mpc = mpc
		self.item = self.mpc.item.model

		self.parameters = parameters
		self.measured_states = measured_states
		self.unmeasured_states = unmeasured_states
		self.inputs = inputs
		self.state_equations = state_equations


		self.create_identification_nlp()
		self.create_validation_nlp()


##### system identification ####################################################
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


	def create_validation_nlp(self):
		"""
		define the validation optimization
		"""
		# copy the identification nlp
		nlp = copy.copy(self.identification_nlp)

		# change the objective
		nlp.set_objective('0',gradientdict={}) 

		self.validation_nlp = nlp	

	
	def identify(self):
		"""
		run the system identification
		"""

		logger.warning('Start system identification')
		nlp = self.identification_nlp
		self.set_identification_data(nlp)

		# start the optimization
		logger.warning('Start optimization')
		nlp.solve()
		logger.warning('Finished optimization')

		# print values
		logger.warning( ['{0}: {1:.0f}'.format(key,nlp.variables[key].value) for key in self.parameters] )	


	def validate(self):
		"""
		compares the identified model with the most recent dataset
		"""

		logger.warning('Start model validation')
		nlp = self.validation_nlp
		self.set_identification_data(nlp)

		# change the parameter variables bounds so they are fixed
		for key in self.parameters:
			var = self.parameters[key]
			nlp.variables[key].lowerbound = nlp.variables[key].value
			nlp.variables[key].upperbound = nlp.variables[key].value

		logger.debug(nlp.variables['UA_op_amb'].lowerbound)
		logger.debug(nlp.variables['UA_op_amb'].upperbound)

		# start the optimization
		logger.warning('Start optimization')
		nlp.solve()
		logger.warning('Finished optimization')

		# print values
		for key in self.measured_states:
			mmnt_key = self.measured_states[key]['mmnt_key']
			logger.warning( ['{:.1f}'.format(var.value) for var in nlp.parameters[mmnt_key]] )
			logger.warning( ['{:.1f}'.format(var.value) for var in nlp.variables[key]] )
			logger.warning( 'rmse: {:.1f}'.format( sum([(var.value-mmnt_var.value)**2 for var,mmnt_var in zip(nlp.variables[key],nlp.parameters[mmnt_key])])**0.5 ) )

		# store the validation results in an item
		inputs = {}
		for key in self.inputs:
			inputs[key] = {'measurement': [var.value for var in nlp.parameters[key]]}

		unmeasured_states = {}
		for key in self.unmeasured_states:
			unmeasured_states[key] = {'simulation': [var.value for var in nlp.variables[key]]}

		measured_states = {}
		for key in self.measured_states:
			mmnt_key = self.measured_states[key]['mmnt_key']
			measured_states[key] = {'measurement': [var.value for var in nlp.parameters[mmnt_key]],
			                        'simulation':  [var.value for var in nlp.variables[key]]}

		result = {'inputs': inputs,
				  'measured_states': measured_states,
                  'unmeasured_states': unmeasured_states}
		logger.debug(result)

		self.item.validation.result(result)


	def set_identification_data(self,nlp):
		"""
		set the system identification data to a nlp
		"""

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
		nlp.parameters['dt'].value = dt

		for key in self.measured_states:		
			values = self._load_data(self.measured_states[key]['mysql_data_string'],time)	
			mmnt_key = self.measured_states[key]['mmnt_key']
			for i,v in enumerate(values):
				nlp.parameters[mmnt_key][i].value = v
				nlp.variables[key][i].value = v

		for key in self.inputs:		
			values = self._load_data(self.inputs[key]['mysql_data_string'],time)	
			for i,v in enumerate(values):
				nlp.parameters[key][i].value = v




##### optimal control ##########################################################
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
				cur.execute("SELECT time,value FROM  measurements_average_quarterhour WHERE signal_id={0} AND time>={1} AND time<={2}".format(id,time[0]-3600,time[-1]+3600))		
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


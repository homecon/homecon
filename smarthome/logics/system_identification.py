#!/usr/bin/python3

import pyipopt
import numpy as np
import pymysql
import datetime

con = pymysql.connect('localhost', 'knxcontrol', sh.knxcontrol.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()

# get measurement data ids
signal_id = {}

signal_id['zone'] = []
for child in sh.knxcontrol.building.children():
	if child.conf['item'] != '':
		cur.execute("SELECT id FROM  measurement_legend WHERE name=%s" %(child.temperature.id())
		for data in cur:
			signal_id['zone'].append(data['id'])
		
signal_id['fanspeed'] = []
for child in sh.knxcontrol.ventilation.fanspeed
	if child.conf['item'] != '':
		cur.execute("SELECT id FROM  measurement_legend WHERE name=%s" %(child.id())
		for data in cur:
				signal_id['fanspeed'].append(data['id'])

signal_id['heatrecovery'] = []
for child in sh.knxcontrol.ventilation.heatrecovery
	if child.conf['item'] != '':
		cur.execute("SELECT id FROM  measurement_legend WHERE name=%s" %(child.id())
		for data in cur:
				signal_id['heatrecovery'].append(data['id'])

signal_id['heat_production'] = []
for child in sh.knxcontrol.heat.production.children():
	if child.conf['item'] != '':
		cur.execute("SELECT id FROM  measurement_legend WHERE name=%s" %(child.power.id())
		for data in cur:
			signal_id['heat_production'].append(data['id'])
	
signal_id['heat_emission'] = []
for child in sh.knxcontrol.heat.emission.children():
	if child.conf['item'] != '':
		cur.execute("SELECT id FROM  measurement_legend WHERE name=%s" %(child.power.id())
		for data in cur:
			signal_id['heat_emission'].append(data['id'])
	
	
	
	
	
	
# define time
dt = 1800
t = np.arange(0,7*24*3600,dt)

#######################################################################################
# Model 1
#######################################################################################
if sh.knxcontrol.model==1:

	# system equations:
	# C*dT/dt = UA*(T_amb-T) + n_ven*fanspeed*(T_amb-T_set) + n_irr*P_irr + P_emi
	# P_emi = sum( n_pro(i)*P_pro(i) )
	# unknown parameters:
	# C, UA, n_ven, n_irr, n_pro(i)
	
	
		
# define signals
signal_id = {'T_amb': 1, 'T_zon': 15, 'V_flow_ven': 17, 'W_flow_tot': 9, 'W_flow_ahp': 10, 'Q_flow_gas': 11, 'Q_flow_irr': 19 }
signal_val = {}

now = datetime.datetime.utcnow()

# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol','admin' , 'knxcontrol')   #sh.building.mysql.conf['password']
cur = con.cursor(pymysql.cursors.DictCursor)

timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )
timestamp_start = timestamp - 3600 - t[-1]

for signal in signal_id:
	# get data from the database
	cur.execute("SELECT time,value FROM  measurements_quarterhouraverage WHERE signal_id=%s AND time>%s" %(signal_id[signal],timestamp_start))
	raw_time = []
	raw_value = []
	for data in cur:
		raw_time.append(data['time'])
		raw_value.append(data['value'])
	
	raw_time  = array(raw_time)
	raw_value = array(raw_value)
	
	avg_value = []
	# resample to the wanted timevector
	for i,tt in enumerate(t[:-1]):
		# average all values where timestamp_start+t[i] < raw_time < timestamp_start+t[i+1]
		avg_value.append(mean(  raw_value[where( (timestamp_start+t[i] < raw_time) & (raw_time <= timestamp_start+t[i+1]) )]  ))
		
	# add the values to a dictionary
	signal_val[signal] = array(avg_value)
	
con.close()
	
# condition signals for use in the optimisation
t = t[:-1]
signal_val['W_flow_int'] = signal_val['W_flow_tot'] - signal_val['W_flow_ahp']

###################################################################################################################################

# define input signals
T_zon = signal_val['T_zon']
T_amb = signal_val['T_amb'] 
T_set = 21*ones(t.shape[0])

Q_flow_irr = signal_val['Q_flow_irr'] 
V_flow_ven = signal_val['V_flow_ven'] 
W_flow_ahp = signal_val['W_flow_ahp'] 
Q_flow_gas = signal_val['Q_flow_gas'] 
W_flow_int = signal_val['W_flow_int'] 



# define constants
rc = 1004*1.22
n_gas = 0.90


# Variable indexing
S = 1               # number of states        j = 0..S-1
N = t.shape[0]      # number of timesteps     i = 0..N-1
M = 6               # number of parameters to be estimated   k=0..M-1

nvars = N*S + M     # number of variables
ncons = N-1         # number of constraints

# state(j,i) = x(i*S+j)
# param(k)   = x(S*N+k)

state_measurement = transpose(array([T_zon]));
state_index       = array([0]);


def combineintoarray(states,C,UA,n_ven,n_int,n_irr,n_ahp):
	x = concatenate((states.reshape((N*S)),array([C,UA,n_ven,n_int,n_irr,n_ahp])))
	return x
	
def splitintovalues(x):

	states = zeros((N,S))
	for j in arange(S):
		states[:,j] = x[j + arange(N)*S]
	
	C  = x[N*S + 0]
	UA = x[N*S + 1]
	n_ven = x[N*S + 2]
	n_int = x[N*S + 3]
	n_irr = x[N*S + 4]
	n_ahp = x[N*S + 5]
	
	return states,C,UA,n_ven,n_int,n_irr,n_ahp

	
# define weights for the objective function
weights = ones((N,state_measurement.shape[0]))
weights[0,:] = 10    # add larger weights to the initial timestep as it is assumed to be known
	

# define required function for ipopt
def objective(x, user_data = None):
    
	states,C,UA,n_ven,n_int,n_irr,n_ahp = splitintovalues(x)
	
	Res = zeros((N,state_measurement.shape[0]))
	for ind, j in enumerate(state_index):
		Res[:,ind] = power(states[:,j] - state_measurement[:,ind],2)
	
	return sum(Res*weights)
	
def gradient(x, user_data = None):

	states,C,UA,n_ven,n_int,n_irr,n_ahp = splitintovalues(x)
	T = states[:,0]
	
	Gra = zeros((nvars))
	for j in state_index:
		for i in arange(N):
			Gra[i*S+j] = (2*T[i]-2*T_zon[i])*weights[i,j]

	
	return Gra
	
def constraint(x, user_data = None):

	states,C,UA,n_ven,n_int,n_irr,n_ahp = splitintovalues(x)
	T = states[:,0]
	
	Con = zeros((ncons))

	for i in arange(N-1):
		Con[i] = -C*(T[i+1]-T[i])/dt  + UA*(T_amb[i]-T[i]) + n_ven*rc*V_flow_ven[i]/3600*(T_amb[i]-T_set[i]) + n_int*W_flow_int[i] + n_irr*Q_flow_irr[i] + n_ahp*W_flow_ahp[i] + n_gas*Q_flow_gas[i]

	return Con
	
nnzj = ncons*8
def jacobian(x, flag, user_data = None):
	

	states,C,UA,n_ven,n_int,n_irr,n_ahp = splitintovalues(x)
	T = states[:,0]
	
	row = []
	col = []	
	Jac = []	
	for i in arange(N-1):
		row.append(i)
		col.append(i)
		Jac.append(C/dt - UA)
		
		row.append(i)
		col.append(i+1)
		Jac.append(-C/dt)
		
		row.append(i)
		col.append(N*S+0)
		Jac.append(-(T[i+1]-T[i])/dt)
		
		row.append(i)
		col.append(N*S+1)
		Jac.append(T_amb[i]-T[i])
		
		row.append(i)
		col.append(N*S+2)
		Jac.append(rc*V_flow_ven[i]/3600*(T_amb[i]-T_set[i]))
		
		row.append(i)
		col.append(N*S+3)
		Jac.append(W_flow_int[i])
		
		row.append(i)
		col.append(N*S+4)
		Jac.append(Q_flow_irr[i])
		
		row.append(i)
		col.append(N*S+5)
		Jac.append(W_flow_ahp[i])
	
	if flag:
		return (array(row),array(col))
	else:
		return array(Jac)
	
nnzh = 0	
	
# variable bounds
x_L = combineintoarray(array([ones((N))*15]),1e6  ,10  ,0,0,0,0)
x_U = combineintoarray(array([ones((N))*30]),200e6,1000,1,1,2,5)	
x0 = (x_L+x_U)/2

# constraint bounds
c_L = zeros((ncons))
c_U = zeros((ncons))


# prepare ipopt
nlp = pyipopt.create(nvars, x_L, x_U, ncons, c_L, c_U, nnzj, nnzh, objective, gradient, constraint, jacobian)


x, zl, zu, constraint_multipliers, obj, status = nlp.solve(x0)
print()
print( 'solution: ' + str(x) )
print()
print()
print()

states,C,UA,n_ven,n_int,n_irr,n_ahp = splitintovalues(x)
T = states[:,0]
res = T-T_zon
print(res)
		
#logger.warning('Einde model parameter identificatie')
#sh.building.model.identify(False)

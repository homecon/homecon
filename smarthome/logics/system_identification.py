#!/usr/bin/python3
###########################################################################
# run system identification, execute every monday at 00:01
###########################################################################

import pyipopt
from numpy import *

# system equation:
# C*dT/dt = UA*(T_amb-T) + n_ven*rc*V_flow_ven/3600*(T_amb-T_set) + n_int*W_flow_int + n_irr*Q_flow_irr + n_hp*W_flow_ahp + n_gas*Q_flow_gas
# unknown parameters:
# C, UA, n_ven, n_int, n_irr, n_ahp

# define input signals for use in the test
dt = 1800
t = arange(0,24*3600,dt)
T_zon = 21+1*sin(2*pi*t/24/3600)
T_amb = 10+5*sin(2*pi*(t/3600-5)/24)
T_set = 21*ones(t.shape[0])

Q_flow_irr = maximum(0*ones(t.shape[0]),800*sin(2*pi*(t/3600-0)/24))
V_flow_ven = 150*ones(t.shape[0]) + maximum(0*ones(t.shape[0]),150*sin(2*pi*(t/3600-0)/24))
W_flow_ahp = maximum(0*ones(t.shape[0]),2000*sin(2*pi*(t/3600-12)/24))
Q_flow_gas = 0*ones(t.shape[0])
Q_flow_gas[32] = 10000
Q_flow_gas[33] = 10000
Q_flow_gas[34] = 10000

W_flow_int = 0*ones(t.shape[0])
W_flow_int[32:42] = 200


# define constants
rc = 1004*1.22
n_gas = 0.98


# Variable indexing
S = 1               # number of states        j = 0..S-1
N = t.shape[0]      # number of timesteps     i = 0..N-1
M = 6               # number of parameters to be estimated   k=0..M-1

nvars = N*S + M     # number of variables

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

	
x_test = combineintoarray(array([T_zon]),1000,400,1,1,1,1)
print(x_test)
print( )

# define required function for ipopt
def objective(x, user_data = None):
    
	states,C,UA,n_ven,n_int,n_irr,n_ahp = splitintovalues(x)
	
	Res = zeros((N,state_measurement.shape[0]))
	for ind, j in enumerate(state_index):
		Res[:,ind] = power(states[:,j] - state_measurement[:,ind],2)
	
	return sum(Res)
	
def gradient(x, user_data = None):

	states,C,UA,n_ven,n_int,n_irr,n_ahp = splitintovalues(x)
	T = states[:,0]
	
	Gra = zeros((1,nvars))
	for j in state_index:
		for i in arange(N):
			Gra[0,i*S+j] = 2*T[i]-2*T_zon[i]

	
	return Gra
	
def constraint(x, user_data = None):

	states,C,UA,n_ven,n_int,n_irr,n_ahp = splitintovalues(x)
	T = states[:,0]
	
	Con = zeros((N-1,1))

	for i in arange(N-1):
		Con[i] = -C*(T[i+1]-T[i])/dt  + UA*(T_amb[i]-T[i]) + n_ven*rc*V_flow_ven[i]/3600*(T_amb[i]-T_set[i]) + n_int*W_flow_int[i] + n_irr*Q_flow_irr[i] + n_ahp*W_flow_ahp[i] + n_gas*Q_flow_gas[i]

	return Con
	
def jacobian(x, user_data = None):

	states,C,UA,n_ven,n_int,n_irr,n_ahp = splitintovalues(x)
	T = states[:,0]
		
	Jac = zeros((N-1,nvars))	
	for i in arange(N-1):
		Jac[i,i] = C/dt - UA
		Jac[i,i+1] = -C/dt
		Jac[i,N*S+0] = -(T[i+1]-T[i])/dt
		Jac[i,N*S+1] = (T_amb[i]-T[i])
		Jac[i,N*S+2] = rc*V_flow_ven[i]/3600*(T_amb[i]-T_set[i])
		Jac[i,N*S+3] = W_flow_int[i]
		Jac[i,N*S+4] = Q_flow_irr[i]
		Jac[i,N*S+5] = W_flow_ahp[i]
		
	return Jac
	
	
# test functions	
print( 'objective: ' + str(objective(x_test)) )
print( 'gradient: ' + str(gradient(x_test)) )
print( 'constraint: ' + str(constraint(x_test)) )
print( 'jacobian: ' + str(jacobian(x_test)) )

# prpare ipopt



'''
import pymysql

now = datetime.datetime.utcnow()
localtime = datetime.datetime.now()

# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol', sh.building.mysql.conf['password'], 'knxcontrol')
cur = con.cursor(pymysql.cursors.DictCursor)

timestep = 30*60;
timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )
timestamp_orig = timestamp-7*24*60*60
timestamp_start = timestamp_orig

time = []

T_amb = []
wind = []
T_op1 = []
T_op2 = []
T_op3 = []

Q_flow_sol1 = []
Q_flow_sol2 = []
Q_flow_sol3 = []

Q_flow_vent1 = []
Q_flow_vent2 = []
Q_flow_vent3 = []

Q_flow_int1 = []
Q_flow_int2 = []
Q_flow_int3 = []

W_flow_heating = []
Q_flow_heating = []

logger.warning('Start model parameter identificatie')
# get timestep averaged data from mysql
while timestamp_start < timestamp:
	timestamp_end = timestamp_start + timestep;
	
	time.append(timestamp_start-timestamp_orig)
	
	cur.execute("SELECT AVG(signal1),AVG(signal7),AVG(signal10),AVG(signal11),   AVG(signal14),AVG(signal17),AVG(signal18),AVG(signal19),   AVG(signal22),AVG(signal25),AVG(signal26),AVG(signal27),   AVG(signal30),AVG(signal33),AVG(signal34),AVG(signal35) FROM measurements WHERE time>%s AND time <=%s" %(timestamp_start,timestamp_end))

	timestamp_start = timestamp_end
	
	for temp in cur:
	
		# assign data and create running averages with 30min data
		T_amb.append(temp['AVG(signal1)'])
		wind.append(temp['AVG(signal7)'])
		
		W_flow_heating.append(temp['AVG(signal10)'])
		Q_flow_heating.append(temp['AVG(signal11)'])
		
		T_op1.append(temp['AVG(signal14)'])
		Q_flow_vent1.append(temp['AVG(signal17)'])
		Q_flow_int1.append(temp['AVG(signal18)'])
		Q_flow_sol1.append(temp['AVG(signal19)'])
		
		T_op2.append(temp['AVG(signal22)'])
		Q_flow_vent2.append(temp['AVG(signal25)'])
		Q_flow_int2.append(temp['AVG(signal26)'])
		Q_flow_sol2.append(temp['AVG(signal27)'])
		
		T_op3.append(temp['AVG(signal30)'])
		Q_flow_vent3.append(temp['AVG(signal33)'])
		Q_flow_int3.append(temp['AVG(signal34)'])
		Q_flow_sol3.append(temp['AVG(signal35)'])

		
		
		
		
logger.warning('Einde model parameter identificatie')
		
#sh.building.model.identify(False)
'''
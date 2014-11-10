#!/usr/bin/python3
###########################################################################
# run system identification, execute every monday at 00:01
###########################################################################

import pyipopt
from numpy import *

# define input signals for use in the test
t = arange(0,24*3600,1800)
T = 21+1*sin(2*pi*t/24/3600)
T_amb = 10+5*sin(2*pi*(t/3600-5)/24)
T_set = 21*ones(t.shape[0])

Q_flow_irr = maximum(0*ones(t.shape[0]),800*sin(2*pi*(t/3600-0)/24))
V_flow_vent = 150*ones(t.shape[0]) + maximum(0*ones(t.shape[0]),150*sin(2*pi*(t/3600-0)/24))
W_flow_hp = maximum(0*ones(t.shape[0]),2000*sin(2*pi*(t/3600-12)/24))
Q_flow_gas = 0*ones(t.shape[0])
Q_flow_gas[32] = 10000
Q_flow_gas[33] = 10000
Q_flow_gas[34] = 10000

W_flow_int = 0*ones(t.shape[0])
W_flow_int[32:42] = 200

n_gas = 0.98

print(W_flow_int)


# Variable indexing
S = 1               # number of states        j = 0..S-1
N = t.shape[0]      # number of timesteps     i = 0..N-1
M = 6               # number of parameters to be estimated   k=0..M-1


# state(j,i) = x(i*S+j)
# param(k)   = x(S*N+k)

state_measurement = array([T]);
state_index       = array([0]);

x_test = concatenate((T,array([1, 2, 3])))

def objective(x, user_data = None):
    
	j = 0
	state_residual = array([  power(x[j+arange(N-1)*S] - state_measurement[:,0],2)  ])
	
	rmse = sum(state_residual[:,0])
	
	return rmse
	
def gradient(x, user_data = None):
    
	g = 
	j = 0
	state_residual = array([  x[j+arange(N-1)*S] - state_measurement[:,0]  ])
	
	rmse = sum(state_residual[:,0])
	
	return rmse	
	
	
	
	
	
	
	
print( objective(x_test) )








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
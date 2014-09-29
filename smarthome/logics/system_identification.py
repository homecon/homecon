###########################################################################
# run alarms, execute every monday at 00:01
###########################################################################
# function to run all alarms in the mysql database
# writes "action" to "item"

import pymysql

now = datetime.datetime.utcnow()
localtime = datetime.datetime.now()

# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol', 'ysUnGTQEadTsDnTD', 'knxcontrol')
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
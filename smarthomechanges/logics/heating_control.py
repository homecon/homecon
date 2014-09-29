import pymysql

now = datetime.datetime.utcnow()
timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

localtime = datetime.datetime.now()

# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol', 'ysUnGTQEadTsDnTD', 'knxcontrol')
cur = con.cursor()


for zone in sh.building.zones:

	zone_str = zone.id().split(".")
	zone_str = zone_str[-1]
		
	try:
		# get setpoint temperature from mysql
		cur.execute("SELECT day,hour,minute,setpoint FROM temperature_setpoints WHERE zone='%s'" %(zone_str))
		setpointtime = []
		setpointval = []

		for setpoint in cur:
			# create time array
			setpointval.append(setpoint[3])
			setpointtime.append( setpoint[0]+setpoint[1]/60+setpoint[2]/24/60 )
		
		# add extra point in beginning
		setpointtime = [-1] + setpointtime
		setpointval  = [setpointval[-1]] + setpointval
		
		# create localtime value
		localtimetemp = localtime.weekday()+localtime.hour/24+localtime.minute/24/60
		
		for i, j in enumerate(setpointtime):
			if j <= localtimetemp:
				T_set = setpointval[i]
	except:
		logger.warning('Could not get temperature setpoint for zone %s' %(zone_str))
		T_set = 21
			
	


	# calculate 15 min averages
	try:
		# get signal number
		item = zone.id()+'.heat_flow_internal'
		cur.execute("SELECT id FROM measurements_legend WHERE item='%s'" % ( item ))
		for temp in cur:
			id = temp[0]
		
		# get average from mysql
		timestamp_new = timestamp-15*60
		cur.execute("SELECT AVG(signal%s) FROM measurements WHERE time>%s" %(id,timestamp_new))
		for temp in cur:
			heat_flow_internal = temp[0]	
	except:
		logger.warning('average calculation failed')
		heat_flow_internal = zone.heat_flow_internal()
	
	
	# calculate wanted heatflow
	T_set_min = T_set-1
	T_set_max = max(T_set+3,25)
	
	T_op = zone.T_operational()
	
	if T_op < T_set_min:
		heat_flow_temperature = 20000 * (T_set_min-T_op) + 2000
	elif T_op < T_set:
		heat_flow_temperature = 2000 * (T_set-T_op)
	elif T_op > T_set_max:
		heat_flow_temperature = 20000 * (T_set_max-T_op)
	else:
		heat_flow_temperature = 0
	
	heat_flow_wanted = heat_flow_temperature+heat_flow_internal-zone.heat_flow_transmission()
	
	# ??????
	if T_op > T_set+2:
		heat_flow_irradiation_wanted = 0.5*zone.heat_flow_irradiation_min() + 0.5*zone.heat_flow_irradiation_max()
	elif T_op > T_set+3:
		heat_flow_irradiation_wanted = zone.heat_flow_irradiation_min()
	else:
		heat_flow_irradiation_wanted = zone.heat_flow_irradiation_max()
	
	if heat_flow_wanted > 0:
		# heating mode
		heat_flow_ventilation_wanted = zone.heat_flow_ventilation_max()
		heat_flow_heating_wanted     = max(0,heat_flow_wanted-heat_flow_ventilation_wanted-heat_flow_irradiation_wanted)
		heat_flow_cooling_wanted     = 0
	else:
		# cooling mode
		heat_flow_ventilation_wanted = zone.heat_flow_ventilation_min()
		heat_flow_heating_wanted     = 0
		heat_flow_cooling_wanted     = heat_flow_wanted + heat_flow_ventilation_wanted + heat_flow_ventilation_wanted;
		
		
	
	# set items
	zone.T_set(T_set)
	zone.heat_flow_temperature(heat_flow_temperature)
	zone.heat_flow_wanted(heat_flow_wanted)
	zone.heat_flow_irradiation_wanted(heat_flow_irradiation_wanted)
	zone.heat_flow_heating_wanted(heat_flow_heating_wanted)
	zone.heat_flow_cooling_wanted(heat_flow_cooling_wanted)
		
		
		
con.commit()	
con.close()
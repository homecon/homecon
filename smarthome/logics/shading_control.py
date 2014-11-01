###########################################################################
# control shades automatically, execute every 30 mins
###########################################################################
#
#
#
import pymysql

now = datetime.datetime.utcnow()

# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol', sh.building.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()

rain = sh.building.rain()
wind = sh.building.wind_velocity() > 10


# calculate 15 min averages of cloud_factor
try:

	# get signal number
	#item = 'building.irradiation.cloud_factor'
	#cur.execute("SELECT id FROM measurements_legend WHERE item='%s'" % ( item ))
	#for temp in cur:
	#	cloud_factor_id = temp[0]
	#logger.warning(cloud_factor_id)

	timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

	cloud_factor_id = 6
	# get 15 min average from mysql
	timestamp_new = timestamp-15*60
	cur.execute("SELECT AVG(value) FROM measurements WHERE signal_id=%s  time>%s" %(cloud_factor_id,timestamp_new))
	for temp in cur:
		cloud_factor_avg = temp[0]
	
	if sh.building.irradiation.cloud_factor()>0:
		averaging_factor = cloud_factor_avg/sh.building.irradiation.cloud_factor()
	else:
		averaging_factor = 1
		
except:
	logger.warning('average calculation failed')
	averaging_factor = 1




for zone in sh.building.zones:

	zone_str  = zone.id().split('.')
	zone_str = zone_str[-1]	
	

	# wanted irradiation heat flow
	heat_flow_irradiation_wanted = zone.heat_flow_irradiation_wanted()
	
	# create an array with maximum and minimum values of irradiation for all windows
	#create a list with all windows
	window_list = []
	window_shading_list = []
	window_noshading_list = []
	
	for room in sh.find_items('zone'):
		if room.conf['zone'] == zone_str:
			if hasattr(room, 'windows'):
				for window in room.windows.return_children():
					window_list.append(window)
					if hasattr(window, 'shading'):
						window_shading_list.append(window)
					else:
						window_noshading_list.append(window)
					
		
	# calculate the total minimum irradiation
	heat_flow_irradiation_total = 0
	for window in window_shading_list:
		heat_flow_irradiation_total = heat_flow_irradiation_total + averaging_factor*window.heat_flow_irradiation_max()*float(window.shading.conf['transmittance'])

		
	# add the irradiation of windows without shading
	for window in window_noshading_list:
		heat_flow_irradiation_total = heat_flow_irradiation_total + averaging_factor*window.heat_flow_irradiation_max()
	
	# add the irradiation of windows without autoshading
	window_shading_auto = []
	window_shading_active = []
	window_shading_inactive = []
	window_shading_override = []
	for window in window_shading_list:
		if (not window.shading.auto()) or window.shading.override() or window.heat_flow_irradiation_max()<50 or rain or wind:
			# x=1 -> f
			# x=0 -> 1    (1-x)*1+x*f    = 1 - x*(1-f)
			heat_flow_irradiation_total = heat_flow_irradiation_total + averaging_factor*window.heat_flow_irradiation_max()*(1-window.shading.pos()/255*(1-float(window.shading.conf['transmittance'])))
			if window.shading.override():
				window_shading_override.append(window)
			else:
				window_shading_inactive.append(window)
		else:	
			window_shading_auto.append(window)

			
	# sort the windows by maximum irradiation with the lowest values first
	window_shading_sorted = sorted(window_shading_auto, key=lambda x: x.heat_flow_irradiation_max())

	# add the difference between maximum and minimum irradiation to the total until the wanted level is reached
	for window in window_shading_sorted:
		heat_flow_irradiation_total = heat_flow_irradiation_total + averaging_factor*window.heat_flow_irradiation_max()*(1-float(window.shading.conf['transmittance']))
		if heat_flow_irradiation_total > heat_flow_irradiation_wanted:
			# the shading is active
			window_shading_active.append(window)
		else:
			# the shading is inactive
			window_shading_inactive.append(window)
		
		
	# determine the level of shading for the active windows
	heat_flow_irradiation_rest = heat_flow_irradiation_wanted-averaging_factor*sum(window.heat_flow_irradiation_max() for window in window_shading_inactive)
	heat_flow_irradiation_max = averaging_factor*sum(window.heat_flow_irradiation_max() for window in window_shading_active)
	heat_flow_irradiation_min = averaging_factor*sum(window.heat_flow_irradiation_max()*float(window.shading.conf['transmittance']) for window in window_shading_active)

	if averaging_factor*zone.heat_flow_irradiation_max() > 100:
		if (heat_flow_irradiation_max-heat_flow_irradiation_min) >0:
			shading_pos = 1-(heat_flow_irradiation_rest - heat_flow_irradiation_min)/(heat_flow_irradiation_max-heat_flow_irradiation_min)
		else:
			shading_pos = 0
	else:
		shading_pos = 0

		
	shading_pos = min(1,max(0,shading_pos))		


# calculate and set positions including exceptions and alarms ##############################################################

	for window in window_shading_active:
		shading = window.shading
						
		position = 0
		
		# automatically close shading via alarms
		# close at night alarm
		if float(window.shading.conf['close_at_night'])==1:
			if sh.building.shading.closed():
				position = 255
			
		# find alarms which apply to the current shading
		if hasattr(window.shading,'closed'):
			if window.shading.closed():
				position = 255
		
		# if the position after alarms is open the sun takes over
		if position == 0:
			position = 255*shading_pos
														
		# set positions	
		if (abs(shading.pos()-position)>0.2*255 or position == 1 or position == 0):
			shading.pos(position)
		
		
	for window in window_shading_inactive:
		shading = window.shading
						
		position = 0
		
		# automatically close shading via alarms
		# close at night alarm
		if float(window.shading.conf['close_at_night'])==1:
			if sh.building.shading.closed():
				position = 255
			
		# find alarms which apply to the current shading
		if hasattr(window.shading,'closed'):
			if window.shading.closed():
				position = 255
														
		# set positions	
		if (abs(shading.pos()-position)>0.2*255 or position == 255 or position == 0):
			shading.pos(position)
	
	

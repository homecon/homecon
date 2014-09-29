###########################################################################
# run alarms, execute every 1 mins
###########################################################################
# function to run all alarms in the mysql database
# writes "action" to "item"

import pymysql

now = sh.now();

# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol', 'ysUnGTQEadTsDnTD', 'knxcontrol')
cur = con.cursor(pymysql.cursors.DictCursor)

# get alarm data from mysql 
cur.execute("SELECT * FROM alarms WHERE hour=%s AND minute=%s" % (now.hour,now.minute))

for alarm in cur:
	# check if the alarm has to be executed today
	if (now.weekday() == 0 and alarm['mon']) or (now.weekday() == 1 and alarm['tue']) or (now.weekday() == 2 and alarm['wed']) or (now.weekday() == 3 and alarm['thu']) or (now.weekday() == 4 and alarm['fri']) or (now.weekday() == 5 and alarm['sat']) or (now.weekday() == 6 and alarm['sun']): 

		logger.warning( 'alarm id: '+ str(alarm['id']) )
		logger.warning( 'alarm item: '+ alarm['item'] )
		logger.warning( 'alarm action: '+ alarm['action'] )

		# find the items and set their values 
		items = alarm['item'].split(",")
		for item_str in items:
			item = sh.return_item(item_str)
			item(alarm['action'])












# # create alarms list
# alarms_list = sh.find_items('alarm_id')
# #for alarm_id in sh.match_items('*.alarm_id'):
# #	alarms_list.append(alarm_id.return_parent())

	
# # find alarms that need to be run
# for alarm in alarms_list:

	# parent = alarm.return_parent()
	
	# # get alarm data from mysql 
	# cur.execute("SELECT * FROM alarms WHERE id=%s" % (alarm.conf['alarm_id']))
	# row = cur.fetchall()
	# row = row[0]
	
	# now = sh.now();
	# if (now.weekday() == 0 and row['mon']) or (now.weekday() == 1 and row['tue']) or (now.weekday() == 2 and row['wed']) or (now.weekday() == 3 and row['thu']) or (now.weekday() == 4 and row['fri']) or (now.weekday() == 5 and row['sat']) or (now.weekday() == 6 and row['sun']): 

		# val_hour = row['hour']
		# val_minute = row['minute']
		
		# if row['sunset']:
			# val_hour = sh.sun.set().hour + val_hour
			# val_minute = sh.sun.set().minute + val_minute
			# now = datetime.utcnow()
			
		# elif row['sunrise']:
			# val_hour = sh.sun.rise().hour + val_hour
			# val_minute = sh.sun.rise().minute + val_minute
			# now = datetime.utcnow()
			
		# if now.hour == val_hour:
			# if now.minute == val_minute:
			
				# logger.warning( 'alarm id: '+ alarm.conf['alarm_id'] )
				
				# if hasattr(alarm, 'alarm_action'):
					# logger.warning( alarm.alarm_action() )
					# parent( alarm.alarm_action() )
				
				# else:					
					# logger.warning( alarm.conf['alarm_action'] )
					# if 'fade' in alarm.conf['alarm_action']:

						# fadelist = alarm.conf['alarm_action'].split(',');

						# val = int(fadelist[1])
						# step = val/255*5
						# timedelta = float(fadelist[2])*step/val
						
						# logger.warning(val)
						# logger.warning(step)
						# logger.warning(timedelta)
						
						
						# #sh.trigger('fader')
						# parent.fade(val, step, timedelta)
					# else:
						# # set the value of the alarm parent item to alarm_action
						# parent(float(alarm.conf['alarm_action']))
				
				

						
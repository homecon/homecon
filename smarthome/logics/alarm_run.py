###########################################################################
# run alarms, execute every 1 mins
###########################################################################
# function to run all alarms in the mysql database
# writes "action" to "item"

import pymysql

now = sh.now();

# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol', sh.building.mysql.conf['password'], 'knxcontrol')
cur = con.cursor(pymysql.cursors.DictCursor)

# get alarm data from mysql 
cur.execute("SELECT * FROM alarms WHERE hour=%s AND minute=%s" % (now.hour,now.minute))

for alarm in cur:
	# check if the alarm has to be executed today
	if (now.weekday() == 0 and alarm['mon']) or (now.weekday() == 1 and alarm['tue']) or (now.weekday() == 2 and alarm['wed']) or (now.weekday() == 3 and alarm['thu']) or (now.weekday() == 4 and alarm['fri']) or (now.weekday() == 5 and alarm['sat']) or (now.weekday() == 6 and alarm['sun']): 

		logger.warning( 'alarm id: '+ str(alarm['id']) )

		# get the action of this alarm
		actioncur = con.cursor(pymysql.cursors.DictCursor)
		actioncur.execute("SELECT * FROM alarm_actions WHERE id=%s" % (alarm['action_id']))
		
		for action in actioncur:
		
			logger.warning( 'alarm item: '+ action['item1'] )
			logger.warning( 'alarm action: '+ action['value1'] )

			# find the items and set their values 
			items = action['item1'].split(",")
			for item_str in items:
				item = sh.return_item(item_str)
				item(action['value1'])


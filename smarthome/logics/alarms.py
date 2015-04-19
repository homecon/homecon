######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of KNXControl.
#
#    KNXControl is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KNXControl is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

# function to run all alarms in the mysql database
# schedules item to be set to value as specified in action

import pymysql

now = sh.now();

# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol', sh.knxcontrol.mysql.conf['password'], 'knxcontrol')
cur = con.cursor(pymysql.cursors.DictCursor)

# get alarm data from mysql 
cur.execute("SELECT * FROM alarms WHERE hour=%s AND minute=%s" % (now.hour,now.minute))

for alarm in cur:
	# check if the alarm has to be executed today
	if (now.weekday() == 0 and alarm['mon']) or (now.weekday() == 1 and alarm['tue']) or (now.weekday() == 2 and alarm['wed']) or (now.weekday() == 3 and alarm['thu']) or (now.weekday() == 4 and alarm['fri']) or (now.weekday() == 5 and alarm['sat']) or (now.weekday() == 6 and alarm['sun']): 

		logger.warning( 'alarm id: '+ str(alarm['id']) )

		# get the action of this alarm
		actioncur = con.cursor(pymysql.cursors.DictCursor)
		actioncur.execute("SELECT * FROM actions WHERE id=%s" % (alarm['action_id']))
		
		for action in actioncur:
		
			# find the items and set their values 
			ind_list = ['1','2','3','4','5']
			for ind in ind_list:
				# each line can be a comma separated list of items
				if action['item'+ind]:
					item_str_list = action['item'+ind].split(",")
					
					for item_str in item_str_list:
						# find the time delay
						if int(action['delay'+ind]) < 1:
							item = sh.return_item(item_str)
							logger.warning( item_str )
							# check if the item exists
							#if item:
							item(action['value'+ind])
							logger.info( action['item'+ind]+' set to '+str(action['value'+ind]))
						else:
							triggertime = now + datetime.timedelta(seconds=int(action['delay'+ind]))
							sh.trigger(name='set_item',by='alarm'+str(alarm['id']),source=item_str,value=action['value'+ind],prio=2,dt=triggertime)
				
							logger.info( action['item'+ind]+' scheduled to become '+str(action['value'+ind])+' in '+str(action['delay'+ind])+' seconds')

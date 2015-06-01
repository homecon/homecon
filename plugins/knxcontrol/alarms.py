#!/usr/bin/env python3


import logging
import pymysql
import datetime

logger = logging.getLogger('')

class Alarms:
	def __init__(self,knxcontrol):
		"""
		Create an Alarms object
		"""

		self.knxcontrol = knxcontrol
		self._sh = knxcontrol._sh
		self._mysql_pass = knxcontrol._mysql_pass

		logger.warning("Alarms initialized")

	def run(self):
		now = self._sh.now()
	
		# connect to the mysql database
		con = pymysql.connect('localhost', 'knxcontrol', self._mysql_pass, 'knxcontrol')
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
									item = self._sh.return_item(item_str)
									logger.warning( item_str )
									logger.warning(item)
									for tmp in self._sh.return_items():
										logger.warning( tmp )

									# check if the item exists
									if item:
										item(action['value'+ind])
										logger.info( action['item'+ind]+' set to '+str(action['value'+ind]))
									else:
										logger.warning( 'item %s does not exist' % item_str )
								else:
									triggertime = now + datetime.timedelta(seconds=int(action['delay'+ind]))
									self._sh.trigger(name='set_item',by='alarm'+str(alarm['id']),source=item_str,value=action['value'+ind],prio=2,dt=triggertime)
				
									logger.info( action['item'+ind]+' scheduled to become '+str(action['value'+ind])+' in '+str(action['delay'+ind])+' seconds')






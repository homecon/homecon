#!/usr/bin/env python3
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import logging
import numpy as np
import pymysql
import threading
import types

import lib.item


from plugins.homecon.mysql import *
from plugins.homecon.alarms import *
from plugins.homecon.measurements import *
from plugins.homecon.weather import *
from plugins.homecon.zone import *
from plugins.homecon.mpc import *


logger = logging.getLogger('')

class HomeCon:

	def __init__(self, smarthome, mysql_pass='admin'):
		logger.info('HomeCon started')
		
		self._sh = smarthome
		self._mysql_pass = mysql_pass

		# test to add an item from within a plugin
		parent = None
		testpath = 'testitem'
		testitem = lib.item.Item(smarthome, parent, testpath, {})
		smarthome.add_item(testpath, testitem)
		#parent.__children.append(testitem)

		logger.warning(dir(testitem))		

		childpath = 'testitem.child'
		childitem = lib.item.Item(smarthome, testitem, childpath, {})
		smarthome.add_item(childpath, childitem)
		testitem._Item__children.append(childitem)


		self.item = None

		self.sh_listen_items = {}

		self.zones = []
		self.weather = None

		self.lat  = float(self._sh._lat)
		self.lon  = float(self._sh._lon)
		self.elev = float(self._sh._elev)

		#code for adding items for homecon and from mysql will come here
		# 
        #for attr, value in config.items():
        #    if isinstance(value, dict):
        #        child_path = self._path + '.' + attr
        #        try:
        #            child = Item(smarthome, self, child_path, value)
		#"""
        #Arguments:
        #smarthome: the smarthome object
        #parent: the parent item
        #config: a dict with key value pairs of config attributes or child items
		#
        #Example:
        #item = Item(smarthome,parentitem,'sh.firstfloor.living.window.shading',{'transmittance':'0.3','move':{'type':'bool','knx_dpt':'1','knx_send':'2/1/5'}})
        #"""
        #        except Exception as e:
        #            logger.error("Item {}: problem creating: {}".format(child_path, e))
        #        else:
        #            vars(self)[attr] = child
        #            smarthome.add_item(child_path, child)
        #            self.__children.append(child)



	def run(self):

		for item in self._sh.return_items():
			print(item.id())


		# called once after the items have been parsed
		self.alive = True
		
		self.item = self._sh.homecon

		self.energy = self.item.energy
		self.ventilation = self.item.ventilation
		self.heat_production = self.item.heat_production
	

		# create objects
		self.mysql = Mysql(self)
		self.alarms = Alarms(self)
		self.measurements = Measurements(self)
		self.weather = Weather(self)

		# zone objects
		for item in self.find_item('zone'):
			logger.warning(item)
			self.zones.append( Zone(self,item) )

		logger.warning('New objects created')


 		# schedule low_level_control
		self._sh.scheduler.add('HomeCon_update', self.low_level_control, prio=2, cron='* * * *')

		# schedule alarms
		self._sh.scheduler.add('Alarm_run', self.alarms.run, prio=1, cron='* * * *')

		# schedule measurements
		self._sh.scheduler.add('Measurements_minute', self.measurements.minute, prio=2, cron='* * * *')
		self._sh.scheduler.add('Measurements_average_quarterhour', self.measurements.quarterhour, prio=5, cron='1,16,31,46 * * *')
		self._sh.scheduler.add('Measurements_average_week', self.measurements.week, prio=5, cron='2 0 * 0')
		self._sh.scheduler.add('Measurements_average_month', self.measurements.month, prio=5, cron='2 0 1 *')
		
		# schedule forecast loading
		self._sh.scheduler.add('Weater_forecast', self.weather.forecast, prio=5, cron='1 * * *')



		# create the mpc objects
		self.mpc = MPC(self)
		self.mpc.model.identify()
		self.mpc.model.validate()

		logger.warning('Initialization Complete')


	def stop(self):
		self.alive = False


	def parse_item(self, item):
		# called once while parsing the items
		# find the items in sh_listen and
		if 'sh_listen' in item.conf:
			listenitems = self.find_items_in_str(item.conf['sh_listen'])
			for listenitem in listenitems:
				if listenitem in self.sh_listen_items:
					self.sh_listen_items[listenitem].append(item)
				else:
					self.sh_listen_items[listenitem] = [item]
		
		return self.update_item
	


	def update_item(self, item, caller=None, source=None, dest=None):
		# called each time an item changes

		########################################################################
		# evaluate expressions in sh_listen
		if item.id() in self.sh_listen_items:
			for dest_item in self.sh_listen_items[item.id()]:
				try:
					dest_item( eval( dest_item.conf['sh_listen'].replace('sh.','self._sh.') ) )
				except:
					logger.warning('Could not parse \'%s\' to %s' % (dest_item.conf['sh_listen'],dest_item.id()))

		########################################################################
		# check if shading override values need to be set
		if item in self._sh.match_items('*.shading.set_override'):
			window = item.return_parent().conf['homeconobject']
			window.shading_override()

		if item in self._sh.match_items('*.shading.value'):
			if caller!='KNX' and caller != 'Logic':
				window = item.return_parent().conf['homeconobject']
				window.shading_override()

		########################################################################
		# check for rain
		if item.id() == 'homecon.weather.current.precipitation':
			for zone in self.zones:
				zone.shading_control()

		########################################################################
		# check for model identify
		if item.id() == 'homecon.mpc.model.identification':
			self.mpc.model.identify()

		########################################################################
		# check for model validation
		if item.id() == 'homecon.mpc.model.validation':
			self.mpc.model.validate()



	def parse_logic(self, logic):
		pass


	def low_level_control(self):
		"""
		Update all values dependent on time
		Run every minute
		"""
		logger.warning('low level control')
		
		self.weather.update()

		# set controls
		for zone in self.zones:
			#zone.irradiation.setpoint(500)
			#zone.emission.setpoint(0)

			zone.shading_control()








	def find_item(self,homeconitem):
		"""
		function to find items with a certain homecon attribute
		"""
		items = []
		for item in self._sh.find_items('homeconitem'):
			if item.conf['homeconitem'] == homeconitem:
				items.append(item)

		return items
		

	def find_items_in_str(self,searchstr):
		"""
		function to find all items in a string. It looks for instances starting with "sh." and ending with "()"
		"""
		items = []
		tempstr = searchstr
		while len(tempstr)>0:
			try:
				start = tempstr.index('sh.')+3
				tempstr = tempstr[start:]
				try:
					end  = tempstr.index('()')
					items.append(tempstr[:end])
					tempstr = tempstr[end:]
				except:
					tempstr = ''
			except:
				tempstr = ''
	
		return items


			


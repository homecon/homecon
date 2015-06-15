#!/usr/bin/python3
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

import logging
import numpy as np
from plugins.knxcontrol.window import *

logger = logging.getLogger('')

class Zone():
	def __init__(self,knxcontrol,item):
		self.knxcontrol = knxcontrol
		self.item = item
		self.item.conf['knxcontrolobject'] = self

		self.windows = []
		self.emission = []

		for item in self.knxcontrol._sh.find_children(self.item, 'knxcontrolitem'):
			if item.conf['knxcontrolitem']== 'window':
				self.windows.append( Window(knxcontrol,self,item) )

		
		self.irradiation = self.item.irradiation
		self.emission = self.item.emission

		

	def irradiation_max(self,average=False):
		"""
		calculates the maximum zone irradiation
		will be bound to all zone items
		"""
		return sum([window.irradiation_max(average=average) for window in self.windows])


	def irradiation_min(self,average=False):
		"""
		calculates the minimum zone irradiation
		will be bound to all zone items
		"""
		return sum([window.irradiation_min(average=average) for window in self.windows])	

	def irradiation_est(self,average=False):
		"""
		calculates the estimated zone irradiation and sets it to the appropriate item
		will be bound to all zone items
		"""
		value = sum([window.irradiation_est(average=average) for window in self.windows])

		# set the irradiation item
		self.irradiation( value )
		return value


	def shading_control(self):
		"""
		Function tries to control the shading so the actual solar gains to the zone match the setpoint
		"""
		#logger.warning('automatic shading control for zone: '+ self.item.id())
		irradiation_set = self.item.irradiation.setpoint()

		# close shadings until the setpoint is reached
		# try to keep as many shadings completely open, to maintain view through the windows
		# so start with the windows with the highest difference between max and min
		
		# create an array of irradiation difference for all windows
		differ = [w.irradiation_max(average=True)-w.irradiation_min(average=True) for w in self.windows]
		windows = sorted(self.windows, key=lambda w: w.irradiation_max(average=True)-w.irradiation_min(average=True), reverse=True)

		# get old shading positions
		newpos = []
		oldpos = []
		for window in windows:
			if window.shading != None:
				newpos.append(0)
				oldpos.append( (window.shading.value()-float(window.shading.conf['open_value']))/(float(window.shading.conf['closed_value'])-float(window.shading.conf['open_value'])) )
			else:
				newpos.append(-1)
				oldpos.append(-1)

		# calculate new shading positions
		for idx,window in enumerate(windows):
			oldirradiation = sum( [w.irradiation_max(average=True)*(1-p)+w.irradiation_min(average=True)*p for w,p in zip(windows,newpos)] )
		
			if oldirradiation <= irradiation_set:
				break

			if window.shading != None:
				if window.shading.closed():
					newpos[idx] = 1
				elif not window.shading.auto():
					newpos[idx] = 0
				elif self.knxcontrol.weather.current.precipitation() and ('open_when_raining' in window.shading.conf):
					newpos[idx] = 0
				elif window.shading.override():
					newpos[idx] = (window.shading.value()-float(window.shading.conf['open_value']))/(float(window.shading.conf['closed_value'])-float(window.shading.conf['open_value']))
				else:
					newpos[idx] = 1
					newirradiation = sum([w.irradiation_max(average=True)*(1-p)+w.irradiation_min(average=True)*(p) for w,p in zip(windows,newpos)])
					newpos[idx] = min(1,max(0,(irradiation_set - oldirradiation)/(newirradiation - oldirradiation)))

		# set all shading positions
		for idx,window in enumerate(windows):
			if window.shading != None:
				if not window.shading.override():
					if abs( newpos[idx]-oldpos[idx]) > 0.2 or newpos[idx]==0.0 or newpos[idx]==1.0:
						# only actually set the shading position if the change is larger than 20% or it is closed or open
						window.shading.value( float(window.shading.conf['open_value'])+newpos[idx]*(float(window.shading.conf['closed_value'])-float(window.shading.conf['open_value'])) )


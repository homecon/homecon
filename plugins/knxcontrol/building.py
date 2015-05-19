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
import datetime
import numpy as np

logger = logging.getLogger('')

class Building:
	def __init__(self,knxcontrol):

		self.knxcontrol = knxcontrol
		self._sh = knxcontrol._sh
		self.item = self._sh.return_item('knxcontrol.building')

		self.zone = []
		for item in self.item.return_children():
			self.zone.append(Zone(self.knxcontrol,item))
		
		logger.warning('Building initialized')


	def update_irradiation(self):
		"""
		Update all values depentand on the solar irradiation
		"""
		for zone in self.zone:
			zone.irradiation()


	def control(self):
		"""
		Execute control actions
		"""
		for zone in self.zone:
			zone.shading_control()

class Zone:
	def __init__(self,knxcontrol,item):

		self.knxcontrol = knxcontrol
		self._sh = knxcontrol._sh
		self.weather = knxcontrol.weather
		self.item = item

		self.name = self.item.id().split('.')[-1]

		self.window = []

		# create objects belonging to the zone
		for room in self._sh.find_items('zone'):
			if room.conf['zone'] == self.name:
				if hasattr(room, 'windows'):
					for item in room.windows.return_children():
						# create window objects
						self.window.append(Window(self.knxcontrol,item))

	def irradiation_max(self,average=False):
		"""
		calculates the maximum zone irradiation
		"""
		return sum([window.irradiation_max(average=average) for window in self.window])

	def irradiation_min(self,average=False):
		"""
		calculates the minimum zone irradiation
		"""
		return sum([window.irradiation_min(average=average) for window in self.window])		

	def irradiation(self,average=False):
		"""
		calculates the estimated zone irradiation and sets it to the appropriate item
		"""
		value = sum([window.irradiation(average=average) for window in self.window])
		self.item.irradiation.power( value )
		return value


	def shading_control(self):
		"""
		Function tries to control the shading so the actual solar gains to the zone match the setpoint
		"""
		logger.warning('automatic shading control for zone: '+ self.name)
		irradiation_set = self.item.irradiation.setpoint()

		# close shadings until the setpoint is reached
		# try to keep as many shadings completely open, to maintain view through the windows
		# so start with the windows with the highest difference between max and min
		# create an array of irradiation difference for all windows

		differ = [w.irradiation_max(average=True)-w.irradiation_min(average=True) for w in self.window]
		windows = sorted(self.window, key=lambda x: x.irradiation_max(average=True)-x.irradiation_min(average=True), reverse=True)
		newpos = []
		oldpos = []

		# get old shading positions
		for window in windows:
			if window.has_shading:
				newpos.append(0)
				oldpos.append((window.shading.value()-window.shading_open_value)/(window.shading_closed_value-window.shading_open_value))
			else:
				newpos.append(-1)
				oldpos.append(-1)

		# calculate new shading positions
		for idx,window in enumerate(windows):
			oldirradiation = sum( [w.irradiation_max(average=True)*(1-p)+w.irradiation_min(average=True)*p for w,p in zip(windows,newpos)] )
			
			if oldirradiation <= irradiation_set:
				break

			if window.has_shading:
				if window.shading.closed():
					newpos[idx] = 1 
				elif window.shading.override():
					newpos[idx] = (window.shading.value()-window.shading_open_value)/(window.shading_closed_value-window.shading_open_value)
				else:
					newpos[idx] = 1
					newirradiation = sum([w.irradiation_max(average=True)*(1-p)+w.irradiation_min(average=True)*(p) for w,p in zip(windows,newpos)])
					newpos[idx] = min(1,max(0,(irradiation_set - oldirradiation)/(newirradiation - oldirradiation)))

		# set all shading positions
		logger.warning(newpos)
		for idx,window in enumerate(windows):
			if window.has_shading:
				if not window.shading.override():
					if abs( newpos[idx]-oldpos[idx]) > 0.1 or newpos[idx]==window.shading_closed_value or newpos[idx]==window.shading_open_value:
						# only actually set the shading position if the change is larger than 10% or it is closed or open
						window.shading.value( window.shading_open_value+newpos[idx]*(window.shading_closed_value-window.shading_open_value) )




class Window:
	def __init__(self,knxcontrol,item):
		self._sh = knxcontrol._sh
		self.weather = knxcontrol.weather


		self.item = item
		if 'orientation' in self.item.conf:
			self.orientation = float(self.item.conf['orientation'])*np.pi/180
		else:
			self.orientation = 0
		if 'tilt' in self.item.conf:
			self.tilt = float(self.item.conf['tilt'])*np.pi/180
		else:
			self.tilt = np.pi/2
		if 'area' in self.item.conf:
			self.area = float(self.item.conf['area'])
		else:
			self.area = 1
		if 'transmittance' in self.item.conf:
			self.transmittance = float(self.item.conf['transmittance'])
		else:
			self.transmittance = 0.5


		if hasattr(self.item, 'shading'):
			self.has_shading = True
			self.shading = self.item.shading

			if 'open_value' in self.shading.conf:
				self.shading_open_value = float(self.shading.conf['open_value'])
			else:
				self.shading_open_value = 0.0

			if 'closed_value' in self.shading.conf:
				self.shading_closed_value = float(self.shading.conf['closed_value'])
			else:
				self.shading_closed_value = 255.0

			if 'transmittance' in self.shading.conf:
				self.shading_transmittance = float(self.shading.conf['transmittance'])
			else:
				self.shading_transmittance = 0.0

		else:
			self.has_shading = False


	def irradiation_open(self,average=False):
		"""
		Returns the irradiation through a window when the shading is open
		"""
		return self.area*self.transmittance*self.weather.incidentradiation(self.orientation,self.tilt,average=average)

	def irradiation_closed(self,average=False):
		"""
		Returns the irradiation through a window when the shading is closed if there is shading
		"""
		if self.has_shading:
			shading = self.shading_transmittance
		else:
			shading = 1.0

		return self.irradiation_open(average=average)*shading

	def irradiation_max(self,average=False):
		"""
		Returns the maximum amount of irradiation through the window
		It checks the closed flag indicating the shading must be closed
		And the override flag indicating the shading position is fixed
		"""
		if self.has_shading:
			if self.shading.closed():
				return self.irradiation_closed(average=average)
			elif self.shading.override():
				return self.irradiation(average=average)
			else:
				return self.irradiation_open(average=average)
		else:
			return self.irradiation_open(average=average)

	def irradiation_min(self,average=False):
		"""
		Returns the minimum amount of irradiation through the window
		It checks the closed flag indicating the shading must be closed
		And the override flag indicating the shading position is fixed
		"""
		if self.has_shading:
			if self.shading.override():
				return self.irradiation(average=average)
			else:
				return self.irradiation_closed(average=average)
		else:
			return self.irradiation_open(average=average)

	def irradiation(self,average=False):
		"""
		Returns the estimated actual irradiation through the window
		"""
		if self.has_shading:
			shading = (self.shading.value()-self.shading_open_value)/(self.shading_closed_value-self.shading_open_value)
			return self.irradiation_open(average=average)*(1-shading) + self.irradiation_closed(average=average)*shading
		else:
			return self.irradiation_open(average=average)


class Measurement:
	def __init__(self,smarthome,expression):
		"""
		Not used for now


		Define a measurement from an expression containing items
		ex.
		temperature = Measurement('0.5*sh.living.measurements.temperature_door() + 0.5*sh.study.measurements.temperature()')
		"""
		self._sh = smarthome

		# parse the expression so the sh. in the beginning of an item is replaced with self._sh
		# self.expression = eval( expression.replace('sh.','self._sh.') ) whould not allow for items to end with 'sh'
		tempstr = expression
		self.expression = ''
		while len(tempstr)>0:
			try:
				start = tempstr.index('sh.')+3
				self.expression += temstr[:start].replace('sh.','self._sh.')
				tempstr = tempstr[start:]
				try:
					end = tempstr.index('()')
					self.expression += tempstr[:end]
					tempstr = tempstr[end:]
				except:
					self.expression += tempstr
					tempstr = ''
			except:
				self.expression += tempstr
				tempstr = ''

	def id(self):
		return ''
		
	def __call__(self):
		return eval(self.expression)


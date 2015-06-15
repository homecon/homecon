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
import threading

logger = logging.getLogger('')

class Window():
	def __init__(self,knxcontrol,zone,item):
		self.knxcontrol = knxcontrol
		self.zone = zone
		self.item = item
		self.item.conf['knxcontrolobject'] = self

		self.shading = None
		for item in self.knxcontrol._sh.find_children(self.item, 'knxcontrolitem'):
			if item.conf['knxcontrolitem']== 'shading':
				self.shading = item
				self.shading.conf['knxcontrolobject'] = self
		

	def irradiation_open(self,average=False):
		"""
		Returns the irradiation through a window when the shading is open
		"""
		return float(self.item.conf['area'])*float(self.item.conf['transmittance'])*self.knxcontrol.weather.incidentradiation(surface_azimuth=float(self.item.conf['orientation'])*np.pi/180,surface_tilt=float(self.item.conf['tilt'])*np.pi/180,average=average)


	def irradiation_closed(self,average=False):
		"""
		Returns the irradiation through a window when the shading is closed if there is shading
		"""
		if self.shading != None:
			shading = float(self.shading.conf['transmittance'])
		else:
			shading = 1.0
		return self.irradiation_open(average=average)*shading

	def irradiation_max(self,average=False):
		"""
		Returns the maximum amount of irradiation through the window
		It checks the closed flag indicating the shading must be closed
		And the override flag indicating the shading position is fixed
		"""

		if self.shading != None:
			if self.shading.closed():
				return self.irradiation_closed(average=average)
			elif self.shading.override() or not self.shading.auto():
				return self.irradiation_est(average=average)
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
		if self.shading != None:
			if self.shading.override() or not self.shading.auto():
				return self.irradiation_est(average=average)
			else:
				return self.irradiation_closed(average=average)
		else:
			return self.irradiation_open(average=average)

	def irradiation_est(self,average=False):
		"""
		Returns the estimated actual irradiation through the window
		"""
		if self.shading != None:
			shading = (self.shading.value()-float(self.shading.conf['open_value']))/(float(self.shading.conf['closed_value'])-float(self.shading.conf['open_value']))
			return self.irradiation_open(average=average)*(1-shading) + self.irradiation_closed(average=average)*shading
		else:
			return self.irradiation_open(average=average)

	def shading_override(self):
		self.shading.override(True)
		logger.warning('Overriding %s control'%self.shading)

		# release override after 4h
		def release():
			self.shading.override(False)
			logger.warning('Override of %s control released'%self.shading)
		
		threading.Timer(4*3600,release).start()

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
		"""
		return sum([window.irradiation_max(average=average) for window in self.windows])

	def irradiation_min(self,average=False):
		"""
		calculates the minimum zone irradiation
		"""
		return sum([window.irradiation_min(average=average) for window in self.windows])	

	def irradiation_est(self,average=False):
		"""
		calculates the estimated zone irradiation and sets it to the appropriate item
		"""
		value = sum([window.irradiation_est(average=average) for window in self.windows])

		# set the irradiation item
		self.irradiation( value )
		return value


	def shading_control(self):
		"""
		Function tries to control the shading so the actual solar gains to the zone match the setpoint
		"""
		
		irradiation_set = self.item.irradiation.setpoint()

		# close shadings until the setpoint is reached
		# try to keep as many shadings completely open, to maintain view through the windows
		# so start with the windows with the highest difference between max and min
		
		# create an array of irradiation difference for all windows
		differ = [w.irradiation_open(average=True)-w.irradiation_closed(average=True) for w in self.windows]
		windows = sorted(self.windows, key=lambda w: w.irradiation_open(average=True)-w.irradiation_closed(average=True), reverse=True)


		# get old shading positions
		pos_new = []
		pos_old = []
		irradiation_open = []
		irradiation_closed = []
		for window in windows:
			if window.shading != None:
				pos_new.append(0)
				pos_old.append( (window.shading.value()-float(window.shading.conf['open_value']))/(float(window.shading.conf['closed_value'])-float(window.shading.conf['open_value'])) )
			else:
				pos_new.append(-1)
				pos_old.append(-1)

	
			irradiation_open.append( window.irradiation_open(average=True) )
			irradiation_closed.append( window.irradiation_closed(average=True) )
		tolerance = 100		

		# set position min/max values
		pos_min = []
		pos_max = []
		for window in windows:
			if window.shading != None:
				if self.knxcontrol.item.weather.current.precipitation() and ('open_when_raining' in window.shading.conf):
					pos_min.append( 0 )
					pos_max.append( 0 )
				elif window.shading.closed():
					pos_min.append( 1 )
					pos_max.append( 1 )
				elif (not window.shading.auto()) or window.shading.override():
					pos_min.append( window.shading_value2pos() )
					pos_max.append( window.shading_value2pos() )
				else:
					pos_min.append( 0 )
					pos_max.append( 1 )	
			else:
				pos_min.append(0)
				pos_max.append(0)
			
		# calculate new shading positions
		irradiation = sum([(1-pos_min[idx])*irradiation_open[idx]+(pos_min[idx])*irradiation_closed[idx] for idx,w in enumerate(windows)])

		for idx,window in enumerate(windows):
			logger.warning(irradiation)
			
			irradiation_temp = irradiation - ( (pos_max[idx]-pos_min[idx])*irradiation_open[idx] + (pos_min[idx]-pos_max[idx])*irradiation_closed[idx] )

			if abs(irradiation-irradiation_set) > tolerance and irradiation-irradiation_temp > 1:
				# to avoid devisions by zero
				pos_new[idx] = (irradiation-irradiation_set)/(irradiation-irradiation_temp)
		
			pos_new[idx] = min(pos_max[idx],max(pos_min[idx],pos_new[idx]))

			# update irradiation
			irradiation = irradiation - irradiation_open[idx] + (1-pos_new[idx])*irradiation_open[idx] + (pos_new[idx])*irradiation_closed[idx]

			
		# set shading positions which are auto and not override
		for idx,window in enumerate(windows):
			if window.shading != None:
				# only actually set the shading position if
				# it is set to closed
				condition1 = window.shading.closed()
				# it is set to open when raining and it rains
				condition2 = self.knxcontrol.item.weather.current.precipitation() and ('open_when_raining' in window.shading.conf)
				# auto is set and override is not set and if the change is larger than 20% or it is closed or open
				condition3 = window.shading.auto() and (not window.shading.override()) and abs(pos_new[idx]-pos_old[idx]) > 0.2
				if condition1 or condition2 or condition3:
					window.shading.value( window.shading_pos2value(pos_new[idx]) )

		
		# estimate the new value for irradiation and set it
		self.irradiation_est()

		logger.warning(  'automatic shading control for zone: {0}, setpoint: {1:.1f}, estimate: {2:.1f}'.format( self.item.id(),self.irradiation.setpoint(),self.irradiation_est(average=True) )  )		
		az,al = self.knxcontrol.weather.sunposition()
		cl = self.knxcontrol.item.weather.current.irradiation.clouds()
		logger.warning(  'azimuth: {0:.0f}, altitude: {1:.0f}, clouds: {2:.2f}'.format(az*180./np.pi,al*180./np.pi,cl)  )
		logger.warning(  ', '.join(['{0} pos: {1:.1f} min: {2:.1f} max:{3:.1f} irr: {4:.1f}'.format(w.item.id(),p,pmin,pmax,w.irradiation_est()) for w,p,pmin,pmax in zip(windows,pos_new,pos_min,pos_max)])  )



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

		self.temperature = self.item.temperature
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

		irradiation_set = self.irradiation.setpoint()

		logger.warning( 'automatic shading control for zone: {0}, setpoint: {1:.1f}'.format( self.item.id(),self.irradiation.setpoint() )  )

		# create an array of irradiation difference for all windows
		windows = sorted(self.windows, key=lambda w: w.item.conf['area'], reverse=True)

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

		# get old shading positions updated them with the new extreme values
		pos_old = []
		pos_new = []
		irradiation_open = []
		irradiation_closed = []
		for window,pmin,pmax in zip(windows,pos_min,pos_max):
			if window.shading != None:
				p = window.shading_value2pos()
				p = min(pmax,max(pmin,p))				
				pos_old.append( p )
				pos_new.append( p )
			else:
				pos_old.append(0)
				pos_new.append(0)
		
			irradiation_open.append( window.irradiation_open(average=True) )
			irradiation_closed.append( window.irradiation_closed(average=True) )

				
		# calculate the irradiation with the old shading positions updated with the current min and max
		irradiation = sum([(1-p)*irr_open+(p)*irr_closed for p,irr_open,irr_closed in zip(pos_old,irradiation_open,irradiation_closed)])

		# calculate new shading positions
		lower_shading = False
		raise_shading = False
		if irradiation < tolerance:
			# set all shades to their minimum value
			pos_new = pos_min
			logger.warning('go to minimum')
		else:
			if irradiation < irradiation_set-tolerance:
				# raise more shades
				raise_shading = True
				irradiation_set_move = irradiation_set+0.75*tolerance
				logger.warning('raising')
			elif irradiation > irradiation_set+tolerance:
				# lower more shades
				lower_shading = True
				irradiation_set_move = irradiation_set-0.75*tolerance
				logger.warning('lowering')
			else: 
				# do nothing
				logger.warning('do nothing')

			if lower_shading or raise_shading:
				if lower_shading:
					windowloop = enumerate(windows)
				else:
					windowloop = enumerate(reversed(windows))

				for i,window in windowloop:

					# maximum and minimum possible irradiation by changing this window only
					irradiation_max = irradiation - ((1-pos_old[i])*irradiation_open[i]+(pos_old[i])*irradiation_closed[i]) + ((1-pos_min[i])*irradiation_open[i]+(pos_min[i])*irradiation_closed[i])
					irradiation_min = irradiation - ((1-pos_old[i])*irradiation_open[i]+(pos_old[i])*irradiation_closed[i]) + ((1-pos_max[i])*irradiation_open[i]+(pos_max[i])*irradiation_closed[i])

					# to avoid devisions by zero
					if abs(irradiation_max-irradiation_min) > 1:
						pos_new[i] = (irradiation_max-irradiation_set_move)/(irradiation_max-irradiation_min)
						pos_new[i] = min(pos_max[i],max(pos_min[i],pos_new[i]))
			
					logger.warning('window: {0}, pos_old: {1:.1f}, irr: {2}, irr_max:{3}, irr_min:{4}, pos_new: {5:.1f}'.format(window.item.id(),pos_old[i],irradiation,irradiation_max,irradiation_min,pos_new[i]))

					# update the irradiation value
					irradiation = irradiation - ((1-pos_old[i])*irradiation_open[i]+(pos_old[i])*irradiation_closed[i]) +  ((1-pos_new[i])*irradiation_open[i]+(pos_new[i])*irradiation_closed[i])

					if abs(irradiation - irradiation_set_move) < 0.1*tolerance:
						break



		# set shading positions which are auto and not override
		for i,window in enumerate(windows):
			if window.shading != None:
				# only actually set the shading position if
				# it is set to closed
				condition1 = window.shading.closed()
				# it is set to open when raining and it rains
				condition2 = self.knxcontrol.item.weather.current.precipitation() and ('open_when_raining' in window.shading.conf)
				# auto is set and override is not set and if the change is larger than 20% or it is closed or open
				condition3 = window.shading.auto() and (not window.shading.override()) and (abs(pos_new[i]-pos_old[i]) > 0.2 or pos_new[i]==0 or pos_new[i]==1)
				if condition1 or condition2 or condition3:
					window.shading.value( window.shading_pos2value(pos_new[i]) )

		
		# estimate the new value for irradiation and set it
		self.irradiation_est()

		#logger.warning(  ', '.join(['{0} pos: {1:.1f} min: {2:.1f} max:{3:.1f} irr: {4:.1f}'.format(w.item.id(),p,pmin,pmax,w.irradiation_est()) for w,p,pmin,pmax in zip(windows,pos_new,pos_min,pos_max)])  )
		logger.warning( 'estimate: {2:.1f}'.format( self.item.id(),self.irradiation.setpoint(),self.irradiation_est(average=True) )  )		


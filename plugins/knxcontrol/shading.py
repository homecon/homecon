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


class Shading:
	def __init__(self,smarthome):
		self._sh = smarthome
		

		# make a list with all windows
		self.window = []

		for zone in self._sh.knxcontrol.building:
			zone_str  = zone.id().split('.')
			zone_str = zone_str[-1]

			self.window['zone_str'] = []
			self.window_shading['zone_str'] = []
			self.window_noshading['zone_str'] = []

			for room in self._sh.find_items('zone'):
				if room.conf['zone'] == zone_str:
					if hasattr(room, 'windows'):
						for window in room.windows.return_children():
							# create window objects
							self.window.append(Window(self._sh,window))

	def set_positions(self):
		"""
		try to set the positions of all shadings so the actual zone irradiation equals the zone irradiation setpoint
		
		"""


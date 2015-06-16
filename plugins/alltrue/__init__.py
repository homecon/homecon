#!/usr/bin/env python3
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

logger = logging.getLogger('')


class AllTrue:
	def __init__(self,smarthome):
		self._sh = smarthome

	def run(self):
		self.alive = True
		logger.info('AllTrue initialized')

	def stop(self):
		self.alive = False

	def parse_item(self, item):
		# called once while parsing the items
		if 'alltrue_item' in item.conf or 'anytrue_item' in item.conf:
			return self.check

	def check(self, item, caller=None, source=None, dest=None):
		"""
		finds all items with the same alltrue_master attribute,
		checks if the alltrue_condition is true for all items
		and sets the item with the alltrue_id to true or false accordingly
		"""

		# alltrue
		if 'alltrue_item' in item.conf:
			master_str = item.conf['alltrue_item']
			master_item = self._sh.return_item(item.conf['master_str'])

			condition = True
			if master_item != None:
				for it in self._sh.find_items('alltrue_item'):
					if it.conf['alltrue_master'] == master_str:
						val = float(it())
						# evaluate the condition
						if not eval(str(val) + master_item.conf['alltrue_condition']):
							condition = False
							break
			
				master_item(condition)

		# anytrue
		if 'anytrue_item' in item.conf:
			master_str = item.conf['anytrue_item']
			master_item = self._sh.return_item(master_str)

			condition = False
			if master_item != None:
				for it in self._sh.find_items('anytrue_item'):
					if it.conf['anytrue_item'] == master_str:
						val = float(it())
						# evaluate the condition
						if eval(str(val) + master_item.conf['anytrue_condition']):
							condition = True
							break
			
				master_item(condition)


	def parse_logic(self, logic):
		pass

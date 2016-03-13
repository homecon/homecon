#!/usr/bin/python3
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
import json

import lib.item

logger = logging.getLogger('')




def create_item(smarthome,config_string):
	"""
	Adds a items to smarthome from a configuration string
	Throws an exception when the item parent does not exist

	Arguments:
	smarthome: the smarthome object
	config_string: json string configuring the item
	
	Example:
	create_item(smarthome,'{"path":"firstfloor.living.window","type":"window","config": {"area":"2.1","transmittance":"0.6","shading":{"transmittance":"0.3","move":{"knx_dpt":"1","knx_send":"2/1/5"}}})	
	"""
	path = config_string['path']
	item_type = config_string['type']
	config = json.loads(config_string['config'])

	# parse special types
	if item_type == 'zone': 
		# a zone item
		pass




	elif item_type == 'window':
		# a window item
		pass





	else:
		if item_type != '':
			# add the type to config
			config['type'] = item_type

		# it is a default item
		_add_item(smarthome,path,config)





def _add_item(smarthome,path,config={}):
	"""
	Adds a low level item to smarthome.
	Throws an exception when the item parent does not exist

	Arguments:
	smarthome: the smarthome object
	path: the item path
	config: a dict with key value pairs of config attributes or child items
	
	Example:
	_add_item(smarthome,'firstfloor.living.window.shading.move',{'type':'bool','knx_dpt':'1','knx_send':'2/1/5'})
	"""

	# split the path to find the parent	
	parentpath = '.'.join( path.split('.')[:-1] )

	if parentpath == '':
		parent = None
	else:
		parent = smarthome.return_item(parentpath)
		if parent == None:
			raise Exception( 'Error: parent does not exist. {}'.format(path) )

	item = lib.item.Item(smarthome, parent, path, config)
	smarthome.add_item(path, item)

	if parent != None:
		parent._Item__children.append(item)


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




def update_item(sh,db,config_string):
	"""
	Updates or creates an item from a configuration string and adds it to the database

	Arguments:
	sh: the smarthome object
	db: the database object
	item_config: string, item configuration string
	
	Example:
	update_item(sh,db,'{"path":"firstfloor.living.window","type":"window","config": '{"area":"2.1","transmittance":"0.6","children":{"shading":{"transmittance":"0.3","move":{"knx_dpt":"1","knx_send":"2/1/5"}}}}')
	"""
	# parse the config string
	config = json.loads(config_string)
	item_path = item_config['path']
	item_type = item_config['type']
	item_config = json.loads(item_config['config'])

	# check if the item exists in the database
	db_items = db.GET('item_config','path={}'.format(item_path))
	db_added = False
	if len(db_items)==0:
		# add the item to the database
		db.POST('item_config',{'path':json.dumps(item_path),'type':json.dumps(item_type),'config':json.dumps(item_config)})
		db_added = True


	# update the item in smarthome
	update_smarthome_item(sh,item_path,item_type,item_config)


	# update the item in the database
	if not db_added:
		db.PUT('item_config','path={}'.format(item_path),{'path':json.dumps(item_path),'type':json.dumps(item_type),'config':json.dumps(item_config)})




def update_smarthome_item(sh,item_path,item_type,item_config):
	"""
	Adds a items to smarthome from a configuration dictionary
	Throws an exception when the item parent does not exist

	Arguments:
	sh: the smarthome object
	item_path: string
	item_type: string
	item_config: dict of json string, item configuration  as retrieved from the database
	
	Example:
	create_item(smarthome,'firstfloor.living.window','window','{"area":"2.1","transmittance":"0.6","children":{"shading":{"transmittance":"0.3","children":{"move":{"knx_dpt":"1","knx_send":"2/1/5"}}}}}')	
	"""

	# parse item_config
	if isinstance(item_config, str):
		item_config = json.loads(item_config)
		
	# get the item children configuration
	item_children = {}
	if 'children' in item_config:
		item_children = item_config['children']
		del item_config['children']

	# add the type to config
	if item_type != '':
		item_config['type'] = item_type


	# check if the item exists in smarthome
	item = sh.return_item(item_path)
	if not item == None:
		# delete the item and re add it
		# deleting the item is required to reconfigure the plugin_method_triggers
		# of all plugins
		_delete_item(item)



	# parse special types
	if item_type == 'heatedzone':
		########################################################################
		# a heated zone item
		########################################################################
		# default config attributes
		default_config = {'floor_area': '100.0', 'exterior_wall_area':'300.0', 'volume':'250.0'}
		# create the item
		item = _add_item(sh,item_path,config=default_config.update(item_config))


	elif item_type == 'unheatedzone':
		########################################################################
		# a unheated zone item
		########################################################################
		# default config attributes
		default_config = {'floor_area': '100.0', 'exterior_wall_area':'300.0', 'volume':'250.0'}
		# create the item
		item = _add_item(sh,item_path,config=default_config.update(item_config))


	elif item_type == 'window':
		########################################################################
		# a window item
		########################################################################
		# default config attributes
		default_config = {'area': '1.0', 'orientation':'0.0', 'tilt':'90.0', 'transmittance':'0.6'}
		# create the item
		item = _add_item(sh,item_path,config=default_config.update(item_config))

		# add a shading item
		child_config = {}
		if 'shading' in item_children:
			child_config = item_children['shading']
			
		update_smarthome_item(sh,item_path+'.shading','shading',child_config)


	elif item_type == 'shading':
		########################################################################
		# a shading item
		########################################################################
		# default config attributes
		default_config = {'transmittance':'0.3'}
		# create the item
		item = _add_item(sh,item_path,config=default_config.update(item_config))

		# add a move item
		child_config = {}
		if 'move' in item_children:
			child_config = item_children['move']

		update_smarthome_item(sh,item_path+'.move','',child_config)

		# add a stop item
		child_config = {}
		if 'stop' in item_children:
			child_config = item_children['stop']

		update_smarthome_item(sh,item_path+'.stop','',child_config)

		# add a value item
		child_config = {}
		if 'value' in item_children:
			child_config = item_children['value']

		update_smarthome_item(sh,item_path+'.value','',child_config)

		# add a value_status item
		child_config = {}
		if 'value_status' in item_children:
			child_config = item_children['value_status']

		update_smarthome_item(sh,item_path+'.value_status','',child_config)

		# add a auto item
		child_config = {}
		if 'auto' in item_children:
			child_config = item_children['auto']

		update_smarthome_item(sh,item_path+'.auto','',child_config)

		# add a override item
		child_config = {}
		if 'override' in item_children:
			child_config = item_children['override']

		update_smarthome_item(sh,item_path+'.override','',child_config)

		# add a closed item
		child_config = {}
		if 'closed' in item_children:
			child_config = item_children['closed']

		update_smarthome_item(sh,item_path+'.closed','',child_config)




		
		
def _delete_item(item):
	"""
	Deletes a low level item and its children from smarthome
	"""
	_sh = item._sh
	path = item.id()

	# run through all children and delete them
	for child in item.return_children():
		_delete_item(child)

	# delete the item itself
	# as the items are protected in the smarthome class this hacky construction is required
	ind = _sh._SmartHome__items.index(path)
	del _sh._SmartHome__items[ind]  # path list
	del _sh._SmartHome__item_dict[path]  # key = path

	if item in _sh._SmartHome__children:
		ind = _sh._SmartHome__children.index(item) 
		del _sh._SmartHome__children[ind] # item list



def _add_item(sh,path,config={}):
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
		parent = sh.return_item(parentpath)
		if parent == None:
			raise Exception( 'Error: parent does not exist. {}'.format(path) )

	item = lib.item.Item(sh, parent, path, config)
	sh.add_item(path, item)

	if parent != None:
		parent._Item__children.append(item)

	return item


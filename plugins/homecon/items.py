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


def set_items(homecon):
	add_test_item(homecon)


def add_test_item(homecon):

	smarthome = homecon._sh

	# test to add an item from within a plugin
	parent = None
	testpath = 'testitem'
	testitem = lib.item.Item(smarthome, parent, testpath, {'homeconitem':'ok'})
	smarthome.add_item(testpath, testitem)
	#parent.__children.append(testitem)

	childpath = 'testitem.child'
	childitem = lib.item.Item(smarthome, testitem, childpath, {'homeconitem':'ok'})
	smarthome.add_item(childpath, childitem)
	testitem._Item__children.append(childitem)



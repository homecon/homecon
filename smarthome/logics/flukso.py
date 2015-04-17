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

#!/usr/bin/python3

# find flukso items and populate them from the flukso api
from urllib.request import urlopen

# run through the flukso items
for item in sh.flukso.return_children():
	
	try:
		# get data from the flukso api
		response = urlopen( 'http://%s:8080/sensor/%s?version=1.0&unit=%s&interval=minute' % (sh.flukso.conf['ip'],item.conf['sensor'],item.conf['unit']) )
	
		line = response.read().decode("utf-8")

		# split line into array and replace nan with 0
		if line:
			exec("data = " + line.replace("\"nan\"","0"))
			#exec("data = " + line.replace("\"nan\"","float('nan')"))
	
			# check if there are measurements in the array
			values = [row[1] for row in data]
			if len(values)>0:
				# calculate the average of all values and set item to this value
				item(sum(values)/len(values))

	except:
		logger.warning('Could not read flukso api for sensor %s' % (item.conf['sensor']) )

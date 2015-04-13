from urllib.request import urlopen


# run through the flukso items
for item in sh.flukso.return_children():

	# get data from the flukso api
	response = urlopen('http://'+sh.flukso.conf['ip']+':8080/sensor/'+item.conf['sensor']+'?version=1.0&unit='+item.conf['unit']+'&interval=minute')
	
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

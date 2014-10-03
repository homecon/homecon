import pymysql

now = datetime.datetime.utcnow();
# remove seconds from time and add :00
now.replace( second=0, microsecond=0)

# convert time to seconds from epoch
timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol', 'ysUnGTQEadTsDnTD', 'knxcontrol')
cur = con.cursor()

# add a row to the measurements table
cur.execute( "INSERT INTO measurements(time) VALUES (%s)" % (timestamp)  )
con.commit()


legend = con.cursor()
legend.execute("SELECT id,item FROM measurements_legend WHERE item <> ''")

# run through all items with a mysql_id attribute
for measurement in legend:

	item = sh.return_item(measurement[1])
	
	# add the value to the database
	try :
		cur.execute( "UPDATE measurements SET signal%s=%f WHERE time=%s" % (measurement[0],item(),timestamp)  )
	except:
		logger.warning('could not add value to database: ' + measurement[1])
		
con.commit()	
con.close()

import pymysql

now = datetime.datetime.utcnow();
# remove seconds from time and add :00
now.replace( second=0, microsecond=0)


# connect to the mysql database
con = pymysql.connect('localhost', 'knxcontrol', sh.building.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()


# convert time to seconds from epoch
timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )


legend = con.cursor()
legend.execute("SELECT id,item FROM measurements_legend WHERE item <> ''")

# create mysql querry
query = "INSERT INTO measurements (signal_id,time,value) VALUES "


# run through legend
for measurement in legend:
	try:
		item = sh.return_item(measurement[1])
		query = query + "(%s,%s,%f)," % (measurement[0],timestamp,item())
	except:
		logger.warning( "legend entry "+measurement[0]+": "+ measurement[1]+", is not an item")
	
query = query[:-1]

# try to execute query
try :
	cur.execute( query )
except:
	logger.warning("could not add measurements to database")
	
con.commit()	
con.close()

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
query1 = "INSERT INTO measurements (time"
query2 = "VALUES (%s" % (timestamp)

# run through legend
for measurement in legend:
	item = sh.return_item(measurement[1])
	query1 = query1 + ",signal%s" % (measurement[0])
	query2 = query2 + ",%f" % (item())
	
query = query1 + ") " + query2 + ")"

# try to execute query
try :
	cur.execute( query )
except:
	logger.warning("could not add measurements to database")
	
con.commit()	
con.close()

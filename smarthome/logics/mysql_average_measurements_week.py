###########################################################################
# week average measurements run every monday at 00:01
###########################################################################
# calculate the total over the past week of all measurement signals in the database legend and add them to the database
# executes every monday at 00:01
import pymysql
import datetime

# get the last monday's date
today = sh.now()
today = today.replace( hour=0 ,minute=0, second=0, microsecond=0)

epoch = datetime.datetime(1970,1,1).replace(tzinfo=sh.utcinfo())

monday = today + datetime.timedelta(days=-today.weekday())
monday = monday.astimezone( sh.utcinfo() )

startdate = monday - datetime.timedelta(weeks=1)
endddate  = monday

starttimestamp = int( (startdate - epoch).total_seconds() )
endtimestamp = int( (endddate - epoch).total_seconds() )

# connect to database
con = pymysql.connect('localhost', 'knxcontrol', sh.building.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()

cur.execute("INSERT INTO measurements_weekaverage(year,week,timestamp) VALUES ('%s','%s','%s')" % (endddate.isocalendar()[0],endddate.isocalendar()[1],starttimestamp))


cur.execute("SELECT * FROM measurements_legend")

for measurement in cur:

	signalcur = con.cursor()
	
	signalcur.execute("SELECT AVG(signal%i) FROM measurements WHERE time >= '%s' AND time < '%s'" % (measurement[0],starttimestamp,endtimestamp))
	row = signalcur.fetchall()
	if (row[0][0] is None):
		avg = 0
	else:
		avg = row[0][0]
		
	signalcur.execute("UPDATE measurements_weekaverage SET signal%s=%f WHERE timestamp=%s" % (measurement[0],avg,starttimestamp))
	
	
con.commit()
con.close()
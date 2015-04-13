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
con = pymysql.connect('localhost', 'knxcontrol', sh.knxcontrol.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()

query = "INSERT INTO measurement_average_week(signal_id,time,value) VALUES "

cur.execute("SELECT * FROM measurement_legend")

for measurement in cur:

	signalcur = con.cursor()
	
	signalcur.execute("SELECT AVG(value) FROM measurement WHERE signal_id=%s AND time >= '%s' AND time < '%s'" % (measurement[0],starttimestamp,endtimestamp))
	row = signalcur.fetchall()
	if (row[0][0] is None):
		avg = 0
	else:
		avg = row[0][0]
		
	query = query + "(%s,%s,%f),"  % (measurement[0],starttimestamp,avg)	
	
query = query[:-1]	
cur.execute(query)
	
con.commit()
con.close()

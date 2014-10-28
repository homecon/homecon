###########################################################################
# month average measurements run every 1st of month at 00:01
###########################################################################
# calculate the total over the past month of all measurement signals in the database legend and add them to the database
import pymysql
import datetime

# get the last monday's date
today = sh.now()
first = today.replace(day=1, hour=0 ,minute=0, second=0, microsecond=0)
first = first.astimezone( sh.utcinfo() )

epoch = datetime.datetime(1970,1,1).replace(tzinfo=sh.utcinfo())

startdate = first - datetime.timedelta(month=1)
endddate  = first

starttimestamp = int( (startdate - epoch).total_seconds() )
endtimestamp = int( (endddate - epoch).total_seconds() )

# connect to database
con = pymysql.connect('localhost', 'knxcontrol', sh.building.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()

query = "INSERT INTO measurements_monthaverage(signal_id,time,value) VALUES "

cur.execute("SELECT * FROM measurements_legend")

for measurement in cur:

	signalcur = con.cursor()
	
	signalcur.execute("SELECT AVG(value) FROM measurements WHERE signal_id=%s AND time >= '%s' AND time < '%s'" % (measurement[0],starttimestamp,endtimestamp))
	row = signalcur.fetchall()
	if (row[0][0] is None):
		avg = 0
	else:
		avg = row[0][0]
		
	query = query + "(%s,%s,%f), "  % (measurement[0],starttimestamp,avg)	
	
query = query[:-1]	
cur.execute(query)
	
	
con.commit()
con.close()
###########################################################################
# quarterhour average measurements run every 15 minutes
###########################################################################
import pymysql
import datetime

# get the last monday's date
now = sh.now().replace(second=0, microsecond=0)

epoch = datetime.datetime(1970,1,1).replace(tzinfo=sh.utcinfo())


startdate = now - datetime.timedelta(minutes=15)
endddate  = now

starttimestamp = int( (startdate - epoch).total_seconds() )
endtimestamp = int( (endddate - epoch).total_seconds() )

# connect to database
con = pymysql.connect('localhost', 'knxcontrol', sh.knxcontrol.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()

query = "INSERT INTO measurement_average_quarterhour(signal_id,time,value) VALUES "

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

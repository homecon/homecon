###########################################################################
# backup the measurement data of the last week
###########################################################################
#!/usr/bin/python
# Original file by : Rahul Kumar
# Website: http://tecadmin.net


import os
import time
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

# MySQL database details to which backup to be done. Make sure below user having enough privileges to take databases backup. 

DB_HOST = 'localhost'
DB_USER = 'knxcontrol'
DB_USER_PASSWORD = sh.knxcontrol.mysql.conf['password']
DB_NAME = 'knxcontrol'
BACKUP_PATH = sh.knxcontrol.mysql.conf['backupdir']

if BACKUP_PATH:
	# Getting current datetime to create separate backup folder like "12012013-071334".
	DATETIME = time.strftime('%Y%m%d')

	# Starting actual database backup process.
	logger.warning(BACKUP_PATH)
	dumpcmd = "mysqldump -u " + DB_USER + " -p" + DB_USER_PASSWORD + " --skip-add-drop-table " + DB_NAME + " measurement measurement_average_quarterhour measurement_average_week measurement_average_month" + " --where='time>="+str(starttimestamp)+" AND time <"+str(endtimestamp)+"' > " + BACKUP_PATH + "/" + DB_NAME + "_measurements_" + DATETIME  + ".sql"
	os.system(dumpcmd)

	logger.info("Measurements backup created")

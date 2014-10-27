#!/usr/bin/python
# Original file by : Rahul Kumar
# Website: http://tecadmin.net


import os
import time
import datetime

# MySQL database details to which backup to be done. Make sure below user having enough privileges to take databases backup. 

DB_HOST = 'localhost'
DB_USER = 'knxcontrol'
DB_USER_PASSWORD = sh.building.mysql.conf['password']
DB_NAME = 'knxcontrol'
BACKUP_PATH = sh.building.mysql.conf['backupdir']

if BACKUP_PATH:
	# Getting current datetime to create separate backup folder like "12012013-071334".
	DATETIME = time.strftime('%Y%m%d')

	# Starting actual database backup process.
	logger.warning(BACKUP_PATH)
	dumpcmd = "mysqldump -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + DB_NAME + "alarm_actions alarms data measurements_legend temperature_setpoints users" + " > " + BACKUP_PATH + "/" + DB_NAME + "_" + DATETIME  + ".sql"
	os.system(dumpcmd)

	logger.warning("Database backup created")

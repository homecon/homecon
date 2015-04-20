# Create entries in measurements_legend for items that must be logged when they are present
#
#
#


import pymysql

con = pymysql.connect('localhost', 'knxcontrol', sh.building.mysql.conf['password'], 'knxcontrol')
cur = con.cursor()

query = "UPDATE data (latitude,longitude,elevation) VALUES (%f,%f,%f) WHERE id=1" % (sh._lat(),sh._lon(),sh._elev())


# try to execute query
try:
	cur.execute( query )
except:
	logger.warning("could not add data to database")
	logger.warning(query)
	
con.commit()	
con.close()

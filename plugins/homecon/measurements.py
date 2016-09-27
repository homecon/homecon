#!/usr/bin/env python3

import logging
import pymysql
import datetime
import numpy as np

logger = logging.getLogger('')

class Measurements:

    def __init__(self,database):
        """

        """

        self._db = database

        self.measurements = {}
        self.maxmeasurementslen = 60*24*7
        logger.warning('Measurements initialized')
        
        self.ws_commands = {
            'measurements': self._ws_measurements,
        }

    def save(self,item):
        """
        stores the current value of an item in the database

        Parameters
        ----------
        item : smarthome item
            the item to store
        """
        
        success = False
        try:
            value = float(item())
            path = item.id()
        except:
            pass

        else:
            # get the current utc timestamp
            now = datetime.datetime.utcnow()
            timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )

            self._db.measurements_POST(time=timestamp,path=path,value=value)
            
            # update the series if required
            if path in self.measurements:

                if len(self.measurements[path]['data']) >= self.maxmeasurementslen:
                    self.measurements[path]['data'].pop(0)

                self.measurements[path]['data'].append( (timestamp,value,) )

            # send the series to the connected clients
            # ???
            success = True

        return success


    def load_measurements(self,path):
        """
        loads a series into memory
        """

        success = False
        if not path in self.series:
            item = self._db.item_GET(path=path)

            if not item==None:
                dbdata = self._db.measurements_GET(path=path)
                data = []
                for m in dbdata[::-1]:
                    data.append( (m['time'],m['value'],) )

                self.measurements[path] = {'label':item['label'], 'description':item['description'], 'unit':item['unit'], 'data':data}
                success = True

        return success



    ############################################################################
    # websocket commands
    ############################################################################

    def _ws_measurements(self,client,data,tokenpayload):

        success = False

        if tokenpayload and tokenpayload['permission']>=1 and 'path' in data:

            if not data['path'] in self.measurements:
                success = self.load_measurements(data['path'])

            val = self.measurements[data['path']]
            success = True


        if success:
            logger.debug("Client {} requested measurements for {}".format(client.addr,data['path']))
            return {'cmd':'measurements', 'val':item}
        else:
            logger.debug("Client {} tried to request measurements".format(client.addr))
            return {'cmd':'measurements', 'val':None}












    def quarterhour(self):
        """
        Calculate 15 minute average of the past 15 minutes and store in MySQL
        """
        # get the last 15 minutes date
        now = datetime.datetime.now(self._sh.tzinfo())
        minute = int(np.floor(int(now.strftime('%M'))/15)*15)
        now = now.replace(minute=minute,second=0, microsecond=0).astimezone( self._sh.utcinfo() )

        startdate = now - datetime.timedelta(minutes=15)
        endddate  = now

        self._set_average_values('measurements_average_quarterhour',startdate,endddate)
        
        
    def week(self):
        """
        Calculate week average of the past week and store in MySQL
        """
        # get the last monday's date
        now = datetime.datetime.now(self._sh.tzinfo())
        now = now.replace( hour=0 ,minute=0, second=0, microsecond=0)

        monday = now + datetime.timedelta(days=-now.weekday())
        monday = monday.astimezone( self._sh.utcinfo() )

        startdate = monday - datetime.timedelta(weeks=1)
        endddate  = monday

        self._set_average_values('measurements_average_week',startdate,endddate)

        
    def month(self):
        """
        calculate month average of the past month and store in MySQL
        """
        # get the last 1st of month date
        now = datetime.datetime.now(self._sh.tzinfo())

        startdate = now.replace( month=(now.month-1) % 12 + 1,day=1, hour=0 ,minute=0, second=0, microsecond=0).astimezone( self._sh.utcinfo() )
        enddate   = now.replace( day=1, hour=0 ,minute=0, second=0, microsecond=0).astimezone( self._sh.utcinfo() )

        self._set_average_values('measurements_average_week',startdate,enddate)    
        

    def _set_average_values(self,table,startdate,endddate):
        """
        Set some average values in MySQL
        
        Arguments:
        table:              string, name of a MySQL table to set result in
        startdate:          datetime with local timezone to start averaging
        endddate:              datetime with local timezone to end averaging
        """
        
        # convert datetimes to timestamps
        epoch = datetime.datetime(1970,1,1).replace(tzinfo=self._sh.utcinfo())
        
        starttimestamp = int( (startdate - epoch).total_seconds() )
        endtimestamp = int( (endddate - epoch).total_seconds() )

        # connect to database
        con,cur = homecon.mysql.create_cursor()

        # build query
        query = "INSERT INTO %s(signal_id,time,value) VALUES " % (table)

        cur.execute("SELECT * FROM measurements_legend")
        for measurement in cur:
            signalcur = con.cursor()
            signalcur.execute("SELECT AVG(value) FROM measurements WHERE signal_id=%s AND time >= '%s' AND time < '%s'" % (measurement[0],starttimestamp,endtimestamp))
            row = signalcur.fetchall()
            if (row[0][0] is None):
                avg = 0
            else:
                avg = row[0][0]
        
            query = query + "(%s,%s,%f),"  % (measurement[0],starttimestamp,avg)    
    
        # execute query
        query = query[:-1]
        try:
            cur.execute(query)
        except:
            logger.warning("could not add average measurements to database")

        con.commit()
        con.close()



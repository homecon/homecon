#!/usr/bin/env python3
######################################################################################
#    Copyright 2016 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import logging
import threading
import types
import lib
import os

from . import database
from . import authentication
from . import settings
from . import items
from . import websocket

"""
import numpy as np
import dateutil.tz

from . import items
from . import mysql
from . import alarms
from . import measurements
from . import weather
from . import building
from . import mpc
"""


logger = logging.getLogger('')

class HomeCon:

    def __init__(self,smarthome,jwt_secret='jwt_secret',db_name='homecon',db_user='homecon',db_pass='db_pass'):
        """
        initialize
        """

        logger.info('HomeCon started')

        self.ws_commands = {}

        # set basic attributes
        self._sh = smarthome
        self._db = database.Mysql(db_name,db_user,db_pass)
        self._auth = authentication.Authentication(self._db,jwt_secret)
        self._settings = settings.Settings(self._sh,self._db)

        self._ws = websocket.WebSocket(self._sh, self._auth, ip='127.0.0.1', port=9024)


        """
        # prepare other attributes
        #self.item = None
        self.alarms = None
        self.weather = None
        self.measurements = None
        self.zones = []
        

        self.sh_listen_items = {}
        """

    def run(self):
        """
        called once after the items have been parsed
        """

        self.alive = True
        self._ws.run() # not needed?

        # initialize the dynamic items
        self._items = items.Items(self._sh,self._db)
        logger.debug('HomeCon items created')


        # add the websocket commands from the different modules
        self._ws.add_commands(self._auth.ws_commands)
        self._ws.add_commands(self._items.ws_commands)
        self._ws.add_commands(self._settings.ws_commands)

        
        """
        config = self._db.GET_JSON( 'config','id=\'1\'' )[0]['config']
        
        ########################################################################
        # configure position from the database
        ########################################################################
        self._sh._lat = config['lat']
        self._sh._lon = config['lon']
        self._sh._elev = config['elev']

        self._sh.sun = lib.orb.Orb('sun', self._sh._lon, self._sh._lat, self._sh._elev)
        self._sh.moon = lib.orb.Orb('moon', self._sh._lon, self._sh._lat, self._sh._elev)


        ########################################################################
        # configure timezone from the database
        ########################################################################
        tz = config['tz']
        tzinfo = dateutil.tz.gettz(tz)
        if tzinfo is not None:
            TZ = tzinfo
            self._sh._tz = tz
            self._sh.tz = tz
            os.environ['TZ'] = tz
        else:
            logger.warning('Problem parsing timezone: {}. Using UTC.'.format(tz))


        ########################################################################
        # configure homeconitems
        #######################################################################
        items.update_smarthome_item(self._sh,'homecon','',{})

        # controls
        items.update_smarthome_item(self._sh,'homecon.controls','',{})
        items.update_smarthome_item(self._sh,'homecon.controls.update_item','bool',{})
        items.update_smarthome_item(self._sh,'homecon.controls.update_item.config','str',{})
        items.update_smarthome_item(self._sh,'homecon.controls.delete_item','bool',{})
        items.update_smarthome_item(self._sh,'homecon.controls.delete_item.path','str',{})

        # actions
        items.update_smarthome_item(self._sh,'homecon.actions','',{})

        # alarms
        items.update_smarthome_item(self._sh,'homecon.alarms','',{})

        # weather
        items.update_smarthome_item(self._sh,'homecon.weather','',{})
        items.update_smarthome_item(self._sh,'homecon.weather.current','',{})
        items.update_smarthome_item(self._sh,'homecon.weather.current.temperature','num',{'quantity':'Temperature','unit':'degC','label':'Ambient','description':'ambient temperature','measurement':True})
        items.update_smarthome_item(self._sh,'homecon.weather.current.humidity','num',{'quantity':'Percentage','unit':'pct','label':'Ambient','description':'ambient relative humidity','measurement':True})
        items.update_smarthome_item(self._sh,'homecon.weather.current.irradiation','',{})
        items.update_smarthome_item(self._sh,'homecon.weather.current.irradiation.horizontal','num',{'quantity':'Heat flux','unit':'W/m2','label':'global horizontal','description':'global horizontal irradiation'})
        items.update_smarthome_item(self._sh,'homecon.weather.current.irradiation.clouds','num',{'quantity':'Percentage','unit':'pct','label':'Clouds','description':'cloud cover','measurement':True})
        items.update_smarthome_item(self._sh,'homecon.weather.current.precipitation','num',{'quantity':'Boolean','unit':'-','label':'Rain','description':'rain','measurement':True})
        items.update_smarthome_item(self._sh,'homecon.weather.current.wind','',{})
        items.update_smarthome_item(self._sh,'homecon.weather.current.wind.speed','num',{'quantity':'Velocity magnitude','unit':'m/s','label':'Speed','description':'wind speed','measurement':True})
        items.update_smarthome_item(self._sh,'homecon.weather.current.wind.direction','num',{'quantity':'Angle','unit':'deg','label':'Direction','description':'wind direction','measurement':True})
        items.update_smarthome_item(self._sh,'homecon.weather.prediction','',{})        
        items.update_smarthome_item(self._sh,'homecon.weather.prediction.detailed','list',{})
        items.update_smarthome_item(self._sh,'homecon.weather.prediction.daily','list',{})

        # mpc
        items.update_smarthome_item(self._sh,'homecon.mpc','',{})
        items.update_smarthome_item(self._sh,'homecon.mpc.model','',{})
        items.update_smarthome_item(self._sh,'homecon.mpc.model.type','str',{})
        items.update_smarthome_item(self._sh,'homecon.mpc.model.identification','bool',{})
        items.update_smarthome_item(self._sh,'homecon.mpc.model.identification.result','dict',{})


        ########################################################################
        # configure items from the database
        ########################################################################
        logger.debug('Adding items from database')
        db_item_config =  self._db.GET('item_config')
        db_item_config.sort( key=lambda item_config: len(item_config['path']) )

        for item in db_item_config:
            items.update_smarthome_item(self._sh,item['path'],item['type'],item['config'])
            
        # test
        #self._sh.scheduler.add('sync_items', self.sync_items, prio=2, cycle='100')


        # print all items for testing
        for item in self._sh.return_items():
            print(item.id())


        ########################################################################
        # create objects after all items have been parsed
        ########################################################################
        #self.alarms = alarms.Alarms(self)
        #self.weather = weather.Weather(self)
        #self.measurements = measurements.Measurements(self)
        

        # zone objects
        for item in self.find_item('zone'):
            logger.warning(item)
            self.zones.append( building.Zone(self,item) )

        logger.warning('New objects created')

        


         # schedule low_level_control
        #self._sh.scheduler.add('HomeCon_update', self.low_level_control, prio=2, cron='* * * *')

        # schedule measurements
        #self._sh.scheduler.add('Measurements_minute', self.measurements.minute, prio=2, cron='* * * *')
        #self._sh.scheduler.add('Measurements_average_quarterhour', self.measurements.quarterhour, prio=5, cron='1,16,31,46 * * *')
        #self._sh.scheduler.add('Measurements_average_week', self.measurements.week, prio=5, cron='2 0 * 0')
        #self._sh.scheduler.add('Measurements_average_month', self.measurements.month, prio=5, cron='2 0 1 *')
        
        # schedule forecast loading
        #self._sh.scheduler.add('Weater_forecast', self.weather.forecast, prio=5, cron='1 * * *')



        # create the mpc objects
        #self.mpc = MPC(self)
        #self.mpc.model.identify()
        #self.mpc.model.validate()

        logger.warning('Initialization Complete')
        """

    def stop(self):
        """
        stop
        """

        self.alive = False
        self._ws.stop()

    def parse_item(self, item):
        """
        called once while parsing the items
        """
        
        logger.warning(item)


        self._ws.parse_item(item)



        """
        ########################################################################
        # add default attributes to all items
        ########################################################################
        if not 'quantity' in item.conf:
            item.conf['quantity'] = ''

        if not 'unit' in item.conf:
            item.conf['unit'] = ''

        if not 'label' in item.conf:
            item.conf['label'] = ''

        if not 'description' in item.conf:
            item.conf['description'] = ''

        if not 'persistent' in item.conf:
            item.conf['persistent'] = '0'


        ########################################################################
        # add or update the item to or from the database
        ########################################################################
        db_items = self._db.GET( 'items','path=\'{}\''.format(item.id()) )
        item_data = {'path':item.id(),'quantity':item.conf['quantity'],'unit':item.conf['unit'],'label':item.conf['label'],'description':item.conf['description'],'persistent':item.conf['persistent'],'value':str(item())}

        if db_items == []:
            self._db.POST( 'items', item_data)
        else:
            if item.conf['persistent'] == '1':
                # update the value
                db_item = db_items[0]
                item(db_item['value']) 
                item_data['value'] = str(item())

            self._db.PUT( 'items','path=\'{}\''.format(item.id()),item_data )


        ########################################################################
        # find the items in sh_listen and
        ########################################################################
        if 'sh_listen' in item.conf:
            listenitems = self.find_items_in_str(item.conf['sh_listen'])
            for listenitem in listenitems:
                if listenitem in self.sh_listen_items:
                    self.sh_listen_items[listenitem].append(item)
                else:
                    self.sh_listen_items[listenitem] = [item]
        """
        return self.update_item
    

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        called each time an item changes
        """

        """
        ########################################################################
        # update the value in the database
        ########################################################################
        self._db.PUT( 'items','path=\'{}\''.format(item.id()),{'value':str(item())} )

        ########################################################################
        # update the value in the measurement database
        ########################################################################    
        if 'measurement' in item.conf and item.conf['measurement']:
            now = datetime.datetime.utcnow()
            timestamp = int( (now - datetime.datetime(1970,1,1)).total_seconds() )
            # get the item id from the database
            item_id = self._db.GET( 'items','path=\'{}\''.format(item.id()) )['id']

            self._db.POST( 'measurements',{'item_id':item_id,'time':timestamp,'value':item()} )
 

        ########################################################################
        # evaluate expressions in sh_listen
        ########################################################################
        if item.id() in self.sh_listen_items:
            for dest_item in self.sh_listen_items[item.id()]:
                try:
                    dest_item( eval( dest_item.conf['sh_listen'].replace('sh.','self._sh.') ) )
                except:
                    logger.warning('Could not parse \'%s\' to %s' % (dest_item.conf['sh_listen'],dest_item.id()))

        ########################################################################
        # check if shading override values need to be set
        #if item in self._sh.match_items('*.shading.set_override'):
        #    window = item.return_parent().conf['homeconobject']
        #    window.shading_override()

        #if item in self._sh.match_items('*.shading.value'):
        #    if caller!='KNX' and caller != 'Logic':
        #        window = item.return_parent().conf['homeconobject']
        #        window.shading_override()

        ########################################################################
        # check for rain
        if item.id() == 'homecon.weather.current.precipitation':
            pass
            #for zone in self.zones:
            #    zone.shading_control()

        ########################################################################
        # check for model identify
        if item.id() == 'homecon.mpc.model.identification':
            pass
            #self.mpc.model.identify()

        ########################################################################
        # check for model validation
        if item.id() == 'homecon.mpc.model.validation':
            pass
            #self.mpc.model.validate()
        """


    def parse_logic(self, logic):


        self._ws.parse_logic(logic)



    def low_level_control(self):
        """
        Update all values dependent on time
        Run every minute
        """
        pass
        #logger.warning('low level control')
        
        # check for alarms
        #self.alarms.run()

        # update weather calculations
        #self.weather.update()

        # set controls
        #for zone in self.zones:
            #zone.irradiation.setpoint(500)
            #zone.emission.setpoint(0)

        #    zone.shading_control()








    def find_item(self,homeconitem,parent=None):
        """
        function to find items with a certain homecon attribute
        """
        items = []
        if parent == None:
            itemiterator = self._sh.find_items('homeconitem')
        else:
            itemiterator = self._sh.find_children(parent, 'homeconitem')

        for item in itemiterator:
            if item.conf['homeconitem'] == homeconitem:
                items.append(item)

        return items
        

    def find_items_in_str(self,searchstr):
        """
        function to find all items in a string. It looks for instances starting with "sh." and ending with "()"
        """
        items = []
        tempstr = searchstr
        while len(tempstr)>0:
            try:
                start = tempstr.index('sh.')+3
                tempstr = tempstr[start:]
                try:
                    end  = tempstr.index('()')
                    items.append(tempstr[:end])
                    tempstr = tempstr[end:]
                except:
                    tempstr = ''
            except:
                tempstr = ''
    
        return items


            


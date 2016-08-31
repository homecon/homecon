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

import unittest
import subprocess
import time
import os
import shutil
import pymysql
import sys

# allow imports from the parent folder
sys.path.insert(0, os.path.abspath('..'))

class HomeConTestCase(unittest.TestCase):
    
    smarthomedir = '../../../../smarthome'
    homecondir = '..'
    logfile = os.path.join(smarthomedir,'var/log/smarthome.log')

    if not os.path.exists('log'):
        os.mkdir('log')

    

    @classmethod
    def setUpClass(cls):
        """
        Executed before the tests
        Set up smarthome and homecon
        """
        print('\nSetting up test environment')

        # copy the homecon plugin to the smarthome plugins folder
        if os.path.exists(os.path.join(cls.smarthomedir,'plugins','homecon')):
            shutil.rmtree(os.path.join(cls.smarthomedir,'plugins','homecon'))

        shutil.copytree(cls.homecondir, os.path.join(cls.smarthomedir,'plugins','homecon') )

        # setup the config files for testing
        f = open(os.path.join(cls.smarthomedir,'etc/smarthome.conf'), 'w')
        f.write('lat = 50.894914\nlon = 4.341551\nelev = 100\ntz = \'Europe/Brussels\'')
        f.close()

        f = open(os.path.join(cls.smarthomedir,'etc/plugin.conf'), 'w')
        f.write('[homecon]\n    class_name = HomeCon\n    class_path = plugins.homecon\n    db = homecon_test\n    db_user=homecon_test\n    db_pass=passwordusedfortesting')
        f.close()

        f = open(os.path.join(cls.smarthomedir,'etc/logic.conf'), 'w').close()


    @classmethod
    def tearDownClass(cls):
        """
        Executed after the tests
        Return smarthome to its original state
        """
        print('\nTearing down test environment')

        # undo changes to the smarthome repo
        os.remove(os.path.join(cls.smarthomedir,'etc/smarthome.conf'))
        os.remove(os.path.join(cls.smarthomedir,'etc/plugin.conf'))
        os.remove(os.path.join(cls.smarthomedir,'etc/logic.conf'))

        shutil.rmtree(os.path.join(cls.smarthomedir,'plugins','homecon'))


    def create_database_connection(self):
        con = pymysql.connect('localhost', 'homecon_test', 'passwordusedfortesting', 'homecon_test')
        cur = con.cursor()

        return con,cur


    def clear_database(self):
        con,cur = self.create_database_connection()
        cur.execute('SHOW TABLES')
        result = cur.fetchall()

        for table in result:
            cur.execute('DROP TABLE {}'.format(table[0]))

        con.commit()
        con.close()

    def start_smarthome(self):
        """
        starts smarthome
        """
        self.fnull = open(os.devnull, 'w')
        self.sh_process = subprocess.Popen(['python', os.path.join(self.smarthomedir,'bin/smarthome.py'), '-d'], stdout=self.fnull, stderr=subprocess.STDOUT)

    def stop_smarthome(self):
        """
        stop smarthome
        """
        self.sh_process.terminate()
        time.sleep(1) # stopping smarthome takes some time
        self.fnull.close()


    def setUp(self):
        """
        Executed before every test

        clear the smarthome log file
        start smarthome
        """

        # clear the log file
        open(self.logfile, 'w').close()

        # clear the database
        self.clear_database()

    def tearDown(self):
        """
        Executed after every test

        stop smarthome
        copy the smarthome log file
        check the log file for errors
        """
        
        # stop smarthome if it is still running
        try:
            self.stop_smarthome()
        except:
            pass

        # copy the log file
        shutil.copyfile(self.logfile, 'log/{}_{}_smarthome.log'.format(self.__class__.__name__,self._testMethodName))

        # clear the database
        self.clear_database()

        # check if there are errors in the log file
        with open(self.logfile) as f:
            errors = []
            for l in f:
                if ' ERROR ' in l:
                    errors.append(l)

            self.assertEqual(len(errors),0,msg='\n' + '\n'.join(errors))




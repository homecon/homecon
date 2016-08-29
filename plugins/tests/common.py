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


class HomeConTestCase(unittest.TestCase):
    
    smarthomedir = '../../../smarthome'
    homecondir = '../homecon'
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



    def setUp(self):
        """
        Executed before every test

        clear the smarthome log file
        start smarthome
        """

        # clear the log file
        open(self.logfile, 'w').close()

        # start smarthome
        self.fnull = open(os.devnull, 'w')
        self.sh_process = subprocess.Popen(['python', os.path.join(self.smarthomedir,'bin/smarthome.py'), '-d'], stdout=self.fnull, stderr=subprocess.STDOUT)


    def tearDown(self):
        """
        Executed after every test

        stop smarthome
        copy the smarthome log file
        check the log file for errors
        """
        
        # stop smarthome
        self.sh_process.terminate()
        time.sleep(1) # stopping smarthome takes some time
        self.fnull.close()

        # copy the log file
        shutil.copyfile(self.logfile, 'log/{}_{}_smarthome.log'.format(self.__class__.__name__,self._testMethodName))

        # check if there are errors in the log file
        with open(self.logfile) as f:
            errors = []
            for l in f:
                if ' ERROR ' in l:
                    errors.append(l)

            self.assertEqual(len(errors),0,msg='\n' + '\n'.join(errors))



import unittest
import subprocess
import time
import os
import shutil


FNULL = open(os.devnull, 'w')

class HomeConTestCase(unittest.TestCase):
    
    smarthomedir = '../../../smarthome'
    os.mkdir('log')
    logfile = os.path.join(smarthomedir,'var/log/smarthome.log')

    @classmethod
    def setUpClass(cls):
        print('\nSetting up test environment')
        # copy the homecon plugin to the smarthome plugins folder

        # setup the config files for testing
        f = open(os.path.join(cls.smarthomedir,'etc/smarthome.conf'), 'w')
        f.write('lat = 50.894914\nlon = 4.341551\nelev = 100\ntz = \'Europe/Brussels\'')
        f.close()

        f = open(os.path.join(cls.smarthomedir,'etc/plugin.conf'), 'w')
        f.close()

        f = open(os.path.join(cls.smarthomedir,'etc/logic.conf'), 'w').close()


    @classmethod
    def tearDownClass(cls):
        print('\nTearing down test environment')
        
        # undo changes to the smarthome repo
        os.remove(os.path.join(cls.smarthomedir,'etc/smarthome.conf'))
        os.remove(os.path.join(cls.smarthomedir,'etc/plugin.conf'))
        os.remove(os.path.join(cls.smarthomedir,'etc/logic.conf'))



    def setUp(self):
        # clear the log file
        open(self.logfile, 'w').close()

        # start smarthome
        self.sh_process = subprocess.Popen(['python', os.path.join(self.smarthomedir,'bin/smarthome.py'), '-d'], stdout=FNULL, stderr=subprocess.STDOUT)


    def tearDown(self):
        self.sh_process.terminate()
        time.sleep(1)

        # copy the log file
        shutil.copyfile(self.logfile, 'log/{}_{}_smarthome.log'.format(self.__class__.__name__,self._testMethodName))



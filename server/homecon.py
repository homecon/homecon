#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import inspect
import time
import asyncio
import logging


import core
import plugins



################################################################################
# create the logger
################################################################################

logFormatter = logging.Formatter('%(asctime)s    %(threadName)-15.15s %(levelname)-8.8s    %(message)s')
logger = logging.getLogger()

basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if not os.path.exists( os.path.join(basedir,'log')):
    os.makedirs(os.path.join(basedir,'log'))

if not 'homecon.fileHandler' in [lh.name for lh in logger.handlers]:
    fileHandler = logging.FileHandler(os.path.join(basedir,'log/homecon.log'))
    fileHandler.setFormatter(logFormatter)
    fileHandler.set_name('homecon.fileHandler')
    logger.addHandler(fileHandler)



################################################################################
# HomeCon object
################################################################################
class HomeCon(object): 
    def __init__(self,debug=False):
        """
        initialize a homecon object
        """

        ########################################################################
        # set logging properties
        ########################################################################
        if debug:
            logger.setLevel(logging.DEBUG)
            if not 'homecon.consoleHandler' in [lh.name for lh in logger.handlers]:
                consoleHandler = logging.StreamHandler()
                consoleHandler.setFormatter(logFormatter)
                consoleHandler.set_name('homecon.consoleHandler')
                logger.addHandler(consoleHandler)

        else:
            logger.setLevel(logging.INFO)

        logging.info('HomeCon started')


        ########################################################################
        # create the event loop
        ########################################################################
        self._loop = asyncio.get_event_loop()


        ########################################################################
        # start core components
        ########################################################################
        self.states = core.states.States(self)
        self.websocket = core.websocket.Websocket(self)
        

        ########################################################################
        # start plugins
        ########################################################################
        self.plugins = []
        self.start_plugin('knx')  # this should be done dynamically from the database


        logging.info('HomeCon Initialized')



    def start_plugin(self,name,package='plugins'):
        """
        Starts a plugin

        this attempts to load the plugin with the correct format by name from
        the plugins folder

        Parameters
        ----------
        name : string
            the filename of the plugin
    
        package : string
            package where to find the plugin, defaults to 'plugins'

        """
        pluginmodule = __import__('{}.{}'.format(package,name), fromlist=[name])
        pluginclass = getattr(pluginmodule, name.capitalize())
        
        plugininstance = pluginclass(self)
        self.plugins.append(plugininstance)


    def fire(self,event):
        logging.debug(event)
        self._loop.call_soon_threadsafe(self.listen,event)


    def listen(self,event):
        """
        listen for events in all plugins
        """
        for plugin in self.plugins:
            self._loop.call_soon_threadsafe(plugin._listen, event)


    def main(self):
        # Start the event loop
        logging.debug('Starting event loop')
        self._loop.run_forever()
        #self._loop.close()


    def stop(self):
        logging.info('Stopping HomeCon')
        
        # cancel all tasks
        for task in asyncio.Task.all_tasks():
            task.cancel()

        # stop the websocket
        self.websocket.stop()

        logging.info('Homecon stopped\n\n')


if __name__ == '__main__':
    hc = HomeCon(debug=True)
    hc.main()
    hc.stop()


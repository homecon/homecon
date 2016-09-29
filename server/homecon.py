#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import inspect
import time
import asyncio
import logging


import core
import plugins



class HomeCon(object): 
    def __init__(self,debug=False):
        """
        initialize a homecon object
        """

        ########################################################################
        # create the logger
        ########################################################################
        logFormatter = logging.Formatter('%(asctime)s    %(threadName)-15.15s %(levelname)-5.5s    %(message)s')
        self.logger = logging.getLogger()
        if debug:
            self.logger.setLevel(logging.DEBUG)

            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            self.logger.addHandler(consoleHandler)

        else:
            self.logger.setLevel(logging.INFO)


        basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        if not os.path.exists( os.path.join(basedir,'log')):
            os.makedirs(os.path.join(basedir,'log'))
        fileHandler = logging.FileHandler(os.path.join(basedir,'log/homecon.log'))
        fileHandler.setFormatter(logFormatter)
        self.logger.addHandler(fileHandler)

        logging.info('HomeCon started')


        ########################################################################
        # create the event loop
        ########################################################################
        self._loop = asyncio.get_event_loop()



        ########################################################################
        # start plugins
        ########################################################################
        self.plugins = []


        # core plugins
        self.start_plugin('server',package='core')
        self.start_plugin('states',package='core')
        
        
        # optional plugins
        self.start_plugin('knx')  # this should be done dynamically from the database



        self.logger.info('HomeCon Initialized')



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
        self._loop.call_soon_threadsafe(self.listen,event)


    def listen(self,event):
        """
        listen for events in all plugins
        """
        for plugin in self.plugins:
            self._loop.call_soon_threadsafe(plugin._listen, event)


    def main(self):

        # Start the event loop
        self._loop.run_forever()
        self._loop.close()



if __name__ == '__main__':
    hc = HomeCon(debug=True)
    hc.main()

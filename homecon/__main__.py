#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import inspect
import traceback


def runserver():

    ################################################################################
    # parse arguments
    ################################################################################
    kwargs = {}
    if 'debug' in sys.argv:
        kwargs['loglevel'] = 'debug'
        kwargs['printlog'] = True

    if 'debugdb' in sys.argv:
        kwargs['loglevel'] = 'debugdb'
        kwargs['printlog'] = True

    if 'daemon' in sys.argv:
        kwargs['printlog'] = False

    if 'demo' in sys.argv:
        kwargs['demo'] = True

        # clear the demo database
        basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        try:
            os.remove(os.path.join(basedir,'demo_homecon.db'))
        except:
            pass
        try:
            os.remove(os.path.join(basedir,'demo_homecon_measurements.db'))
        except:
            pass


    ################################################################################
    # start the webserver in a different thread
    ################################################################################
    from . import httpserver

    httpserverthread = httpserver.HttpServerThread()

    if not 'nohttp' in sys.argv:
        httpserverthread.start()




    ################################################################################
    # start homecon
    ################################################################################
    from . import homecon

    print('Starting HomeCon')
    print('Press Ctrl + C to stop')
    print('')

    try:
        hc = homecon.HomeCon(**kwargs)

        if 'demo' in sys.argv:
            from . import demo
            
            demo.prepare_database()
            demo.emulatorthread.start()
            demo.forecastthread.start()
            demo.responsethread.start()

        hc.main()

    except:
        httpserverthread.stop()
        print('Stopping HomeCon')
        #hc.stop()

        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        print('\n'*3)



if __name__ == '__main__':
    runserver()


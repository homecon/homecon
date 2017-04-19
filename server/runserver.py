#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import traceback
import datetime

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

if 'demo' in sys.argv:
    kwargs['demo'] = True

    # clear the demo database
    try:
        os.remove('demo_homecon.db')
    except:
        pass
    try:
        os.remove('demo_homecon_measurements.db')
    except:
        pass


################################################################################
# start the webserver in a different thread
################################################################################
import web

httpserverthread = web.HttpServer()

if not 'nohttp' in sys.argv:
    httpserverthread.start()




################################################################################
# start homecon
################################################################################
import homecon.homecon as homecon

print('Starting HomeCon')
print('Press Ctrl + C to stop')
print('')

try:
    hc = homecon.HomeCon(**kwargs)

    if 'demo' in sys.argv:
        import homecon.demo
        
        homecon.demo.prepare_database()
        homecon.demo.emulatorthread.start()
        homecon.demo.forecastthread.start()
        homecon.demo.responsethread.start()

    hc.main()

except:
    httpserverthread.stop()
    print('Stopping HomeCon')
    #hc.stop()

    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    print('\n'*3)


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

if 'demo' in sys.argv:
    
    # backup the database
    timestring = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    try:
        os.rename('homecon.db','homecon_backup{}.db'.format(timestring))
        os.rename('homecon_measurements.db','homecon_measurements_backup{}.db'.format(timestring))
        restore = True
    except:
        restore = False

    kwargs['demo'] = True
    



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

    hc.main()

except Exception as e:

    print('Stopping HomeCon')
    #hc.stop()

    if 'demo' in sys.argv:
        # restore the databases
        os.remove('homecon.db')
        os.remove('homecon_measurements.db')
        if restore:
            os.rename('homecon_backup{}.db'.format(timestring),'homecon.db')
            os.rename('homecon_measurements_backup{}.db'.format(timestring),'homecon_measurements.db')

    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    print('\n'*3)


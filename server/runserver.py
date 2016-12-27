#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import homecon.homecon as homecon
import sys


# parse arguments
kwargs = {}
if 'debug' in sys.argv:
    kwargs['loglevel'] = 'debug'
    kwargs['printlog'] = True

if 'demo' in sys.argv:
    kwargs['demo'] = True



# start homecon
print('Starting HomeCon')
print('Press Ctrl + C to stop')
print('')
hc = homecon.HomeCon(**kwargs)
try:
    hc.main()
except KeyboardInterrupt:
    hc.stop()


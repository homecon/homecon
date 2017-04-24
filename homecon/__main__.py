#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import inspect
import traceback


# the current file directory
basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def main():
    """
    Main entrypoint

    """

    if 'install' in sys.argv:
        ################################################################################
        # Install non python dependencies
        ################################################################################
        from .util import install

        # set a static ip address
        if not '--nostaticip' in sys.argv: 
            setip = False
            for arg in sys.argv:
                if arg.startswith( '--ip='):
                    ip = arg[5:]
                    setip = True
                    break

            if not setip:
                # use dialogs
                setip = input('Do you want to set a static ip address (yes): ')
                if setip in ['','yes','y']:
                    setip = True
                    rawip = input('Enter the desired static ip address (192.168.1.234): ')
                    if rawip == '':
                        ip = '192.168.1.234'
                    else:
                        ip = rawip

                elif setip in ['no','n']:
                    setip = False
                else:
                    raise Exception('{} is not a valid answer, yes/y/no/n'.format(setip))

            if setip:
                print('#'*80+'\nSetting static ip address\n'+'#'*80)
                install.set_static_ip(ip)


        # install ipopt
        if not '--noipopt' in sys.argv:
            if not install.solver_available('ipopt'):
                print('#'*80+'\nInstalling IPOPT\n'+'#'*80)
                install.install_ipopt()


        # install glpk
        if not '--noglpk' in sys.argv:    
            if not install.solver_available('glpk'):
                print('#'*80+'\nInstalling GLPK\n'+'#'*80)
                install.install_ipopt()



    else:
        ################################################################################
        # Run homecon
        ################################################################################

        hc_kwargs = {}
        if 'debug' in sys.argv:
            hc_kwargs['loglevel'] = 'debug'
            hc_kwargs['printlog'] = True

        if 'debugdb' in sys.argv:
            hc_kwargs['loglevel'] = 'debugdb'
            hc_kwargs['printlog'] = True

        if 'daemon' in sys.argv:
            hc_kwargs['printlog'] = False

        if 'demo' in sys.argv:
            hc_kwargs['demo'] = True

            # clear the demo database
            try:
                os.remove(os.path.join(basedir,'demo_homecon.db'))
            except:
                pass
            try:
                os.remove(os.path.join(basedir,'demo_homecon_measurements.db'))
            except:
                pass


        app_kwargs = {}
        if 'appsrc' in sys.argv:
            app_kwargs['documentroot'] = os.path.abspath(os.path.join(basedir,'..','app'))


        ################################################################################
        # start the webserver in a different thread
        ################################################################################
        from . import httpserver

        httpserverthread = httpserver.HttpServerThread(**app_kwargs)

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
            hc = homecon.HomeCon(**hc_kwargs)

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
    main()


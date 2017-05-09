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
        from . import __install__


        if not '--nofolders' in sys.argv:
            print('### Creating the Homecon folders')
            __install__.create_data_folders()


        # set a static ip address
        if not '--nostaticip' in sys.argv:

            setip = False
            for arg in sys.argv:
                if arg.startswith( '--ip='):
                    ip = arg[5:]
                    print('### Setting static ip address')
                    print('requires sudo and is not implemented')
                    #__install__.set_static_ip(ip)
                    break

            if not setip:
                # use dialogs
                setip = input('Do you want to set a static ip address (yes): ')
                if setip in ['','yes','y']:
                    print('### Setting static ip address')
                    print('requires sudo and is not implemented')
                    #__install__.set_static_ip()

                elif setip in ['no','n']:
                    pass
                else:
                    raise Exception('{} is not a valid answer, yes/y/no/n'.format(setip))


        # patch pyutilib
        if not '--nopatchpyutilib' in sys.argv:
            print('### Patching the pytuilib')
            __install__.patch_pyutilib()

        # install bonmin
        if not '--nobonmin' in sys.argv:
            if not __install__.solver_available('bonmin'):
                print('### Installing BONMIN')
                __install__.install_bonmin()

        # install ipopt
        if not '--noipopt' in sys.argv:
            if not __install__.solver_available('ipopt'):
                print('### Installing IPOPT')
                __install__.install_ipopt()

        # install glpk
        if not '--noglpk' in sys.argv:
            if not __install__.solver_available('glpk'):
                print('### Installing GLPK')
                print('installation does not work locally yet and is omitted')
                #__install__.install_glpk()



    else:
        ################################################################################
        # Run homecon
        ################################################################################

        hc_kwargs = {}
        app_kwargs = {}

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
                os.remove(os.path.join(sys.prefix,'lib/homecon/demo_homecon.db'))
            except:
                pass
            try:
                os.remove(os.path.join(sys.prefix,'lib/homecon/demo_homecon_measurements.db'))
            except:
                pass

        for arg in sys.argv:
            if arg.startswith( '--port='):
                app_kwargs['port'] = int(arg[7:])
                break

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


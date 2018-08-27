#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import inspect
import traceback
import logging

from logging.handlers import TimedRotatingFileHandler


logger = logging.getLogger(__name__)


# the current file directory
base_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def main():
    """
    Main entry point
    """

    # configure logging
    os.makedirs(os.path.join(sys.prefix, 'var', 'log', 'homecon'), exist_ok=True)
    logFormatter = logging.Formatter('%(asctime)s %(levelname)7.7s  %(processName)-12.12s  %(name)-28.28s %(message)s')
    if 'homecon.file_handler' not in [lh.name for lh in logger.handlers]:
        file_handler = TimedRotatingFileHandler(os.path.join(sys.prefix, 'var', 'log', 'homecon', 'homecon.log'),
                                                when="midnight")
        file_handler.setFormatter(logFormatter)
        file_handler.set_name('homecon.file_handler')
        logging.root.handlers.append(file_handler)

    if '--printlog' in sys.argv:
        if 'homecon.console_handler' not in [lh.name for lh in logger.handlers]:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logFormatter)
            console_handler.set_name('homecon.console_handler')
            logging.root.handlers.append(console_handler)

    for arg in sys.argv:
        level = 'INFO'
        if arg.startswith('--loglevel='):
            level = arg[11:]
            break
    logging.root.setLevel(getattr(logging, level))

    for arg in sys.argv:
        level = 'INFO'
        if arg.startswith('--dbloglevel='):
            level = arg[13:]
            break
    logging.getLogger('homecon.core.database').setLevel(getattr(logging, level))

    for arg in sys.argv:
        level = 'INFO'
        if arg.startswith('--httploglevel='):
            level = arg[13:]
            break
    logging.getLogger('homecon.httpserver').setLevel(getattr(logging, level))

    if 'configure' in sys.argv:
        ################################################################################
        # Install non python dependencies
        ################################################################################
        from . import configure

        if not '--nofolders' in sys.argv:
            print('### Creating the Homecon folders')
            configure.create_data_folders()

        # set a static ip address
        if not '--nostaticip' in sys.argv:

            setip = False
            for arg in sys.argv:
                if arg.startswith( '--ip='):
                    ip = arg[5:]
                    print('### Setting static ip address')
                    configure.set_static_ip(ip)
                    break

            if not setip:
                # use dialogs
                setip = input('Do you want to set a static ip address (yes): ')
                if setip in ['','yes','y']:
                    print('### Setting static ip address')
                    configure.set_static_ip()

                elif setip in ['no','n']:
                    pass
                else:
                    raise Exception('{} is not a valid answer, yes/y/no/n'.format(setip))

        # create an initscript
        if not '--noinitscript' in sys.argv:
            scriptname='homecon'
            for arg in sys.argv:
                if arg.startswith('--initscriptname='):
                    scriptname = arg[17:]
                    break

            configure.set_init_script(scriptname=scriptname)

        # patch pyutilib
        # if not '--nopatchpyutilib' in sys.argv:
        #     print('### Patching the pytuilib')
        #     configure.patch_pyutilib()

        # install knxd
        # if not '--noknxd' in sys.argv:
        #     print('### Installing knxd')
        #     configure.install_knxd()

        # install bonmin
        #if not '--nobonmin' in sys.argv:
        #    if not configure.solver_available('bonmin'):
        #        print('### Installing BONMIN')
        #        configure.install_bonmin()

        # install ipopt
        if not '--noipopt' in sys.argv:
            if not configure.solver_available('ipopt'):
                print('### Installing IPOPT')
                configure.install_ipopt()

        # install glpk
        # if not '--noglpk' in sys.argv:
        #     if not configure.solver_available('glpk'):
        #         print('### Installing GLPK')
        #         print('installation does not work locally yet and is omitted')
        #         configure.install_glpk()

        # install knxd
        if not '--noknxd' in sys.argv:
            print('### Installing knxd')
            configure.install_knxd()

    else:
        ################################################################################
        # Run HomeCon
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
                os.remove(os.path.join(sys.prefix, 'lib/homecon/demo_homecon.db'))
            except:
                pass
            try:
                os.remove(os.path.join(sys.prefix, 'lib/homecon/demo_homecon_measurements.db'))
            except:
                pass

        for arg in sys.argv:
            if arg.startswith('--port='):
                app_kwargs['port'] = int(arg[7:])
                break

        if 'appsrc' in sys.argv:
            app_kwargs['document_root'] = os.path.abspath(os.path.join(base_path, '..', 'app'))

        ################################################################################
        # start the webserver in a different thread
        ################################################################################
        from homecon.httpserver import HttpServer
        http_server = HttpServer(**app_kwargs)

        if 'nohttp' not in sys.argv:
            http_server.start()

        ################################################################################
        # start HomeCon
        ################################################################################
        from homecon.homecon import HomeCon

        print('\nStarting HomeCon\nPress Ctrl + C to stop\n')
        try:
            hc = HomeCon(**hc_kwargs)

            if 'demo' in sys.argv:
                from homecon import demo
                
                demo.prepare_database()
                demo.emulatorthread.start()
                demo.forecastthread.start()
                demo.responsethread.start()

            hc.start()
        except KeyboardInterrupt:
            print('\nStopping HomeCon\n')
            hc.stop()
            http_server.stop()

        except:
            print('Stopping HomeCon')
            hc.stop()
            http_server.stop()

            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
            print('\n'*3)

if __name__ == '__main__':
    main()


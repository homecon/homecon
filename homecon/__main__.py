#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import traceback
import logging

from argparse import ArgumentParser
from logging.handlers import TimedRotatingFileHandler


logger = logging.getLogger(__name__)


# the current file directory
base_path = os.path.dirname(os.path.abspath(__file__))


def main(printlog=False, loglevel='INFO', dbloglevel='INFO', httploglevel='INFO',
         demo=False, appsrc=False, appport=None, serve_app=True,
         configure=False, create_folders=True,
         set_static_ip=True, ip=None,
         run_init_script=True, init_script_name='homecon',
         install_ipopt=True, install_knxd=True):
    """
    Main entry point.
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

    if printlog:
        if 'homecon.console_handler' not in [lh.name for lh in logger.handlers]:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logFormatter)
            console_handler.set_name('homecon.console_handler')
            logging.root.handlers.append(console_handler)

    logging.root.setLevel(getattr(logging, loglevel))
    logging.getLogger('homecon.core.database').setLevel(getattr(logging, dbloglevel))
    logging.getLogger('homecon.httpserver').setLevel(getattr(logging, httploglevel))

    if configure:
        ################################################################################
        # Install non python dependencies
        ################################################################################
        from . import configure

        if create_folders:
            print('### Creating the Homecon folders')
            configure.create_data_folders()

        # set a static ip address
        if set_static_ip:

            setip = False

            if ip is not None:
                print('### Setting static ip address')
                configure.set_static_ip(ip)
                setip = True

            if not setip:
                # use dialogs
                setip = input('Do you want to set a static ip address (yes): ')
                if setip in ['', 'yes', 'y']:
                    print('### Setting static ip address')
                    configure.set_static_ip()

                elif setip in ['no', 'n']:
                    pass
                else:
                    raise Exception('{} is not a valid answer, yes/y/no/n'.format(setip))

        # create an initscript
        if run_init_script:
            configure.set_init_script(scriptname=init_script_name)

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
        if install_ipopt:
            if not configure.solver_available('ipopt'):
                print('### Installing IPOPT')
                configure.install_ipopt()

        # install cbc
        # if not '--noglpk' in sys.argv:
        #     if not configure.solver_available('glpk'):
        #         print('### Installing GLPK')
        #         print('installation does not work locally yet and is omitted')
        #         configure.install_glpk()

        # install knxd
        if install_knxd:
            print('### Installing knxd')
            configure.install_knxd()

    else:
        ################################################################################
        # Run HomeCon
        ################################################################################
        app_kwargs = {}

        if demo:
            from homecon.demo import initialize
            initialize()


            # prepare_database()
            # emulatorthread.start()
            # forecastthread.start()
            # responsethread.start()

        if appport is not None:
            app_kwargs['port'] = appport

        if appsrc:
            app_kwargs['document_root'] = os.path.abspath(os.path.join(base_path, '..', 'app'))

        if serve_app:
            from homecon.httpserver import HttpServer
            http_server = HttpServer(**app_kwargs)
            http_server.start()

        ################################################################################
        # start HomeCon
        ################################################################################
        from homecon.homecon import HomeCon

        print('\nStarting HomeCon\nPress Ctrl + C to stop\n')
        try:
            hc = HomeCon()
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

    parser = ArgumentParser(description='Generate all energy market records')
    parser.add_argument('-l', '--loglevel', type=str, choices=['INFO', 'DEBUG'], default='INFO')
    parser.add_argument('--dbloglevel', type=str, choices=['INFO', 'DEBUG'], default='INFO')
    parser.add_argument('--httploglevel', type=str, choices=['INFO', 'DEBUG'], default='INFO')
    parser.add_argument('--demo', action='store_true')
    parser.add_argument('--printlog', action='store_true')
    parser.add_argument('--noapp', dest='serve_app', action='store_false')
    parser.add_argument('--appsrc', action='store_true')
    parser.add_argument('--appport', type=str, default=None)
    parser.add_argument('--configure', action='store_true')
    parser.add_argument('--nofolders', dest='create_folders', action='store_false')
    parser.add_argument('--nostaticip', dest='set_static_ip', action='store_false')
    parser.add_argument('--ip', type=str, default=None)
    parser.add_argument('--noinitscript', dest='run_init_script', action='store_false')
    parser.add_argument('--initscriptname', dest='init_script_name', type=str, default='homecon')
    parser.add_argument('--noipopt', dest='install_ipopt', action='store_false')
    parser.add_argument('--noknxd', dest='install_knxd', action='store_false')

    kwargs = vars(parser.parse_args())

    main(**kwargs)


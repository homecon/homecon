#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import logging
from logging.handlers import TimedRotatingFileHandler

from argparse import ArgumentParser
from app.server import HttpServer, _document_root, _address, _port


logger = logging.getLogger(__name__)


def main(printlog=False, loglevel='INFO', **kwargs):
    # configure logging
    os.makedirs(os.path.join(sys.prefix, 'var', 'log', 'homecon'), exist_ok=True)
    logFormatter = logging.Formatter('%(asctime)s %(levelname)7.7s  %(processName)-12.12s  %(name)-28.28s %(message)s')
    if 'homecon_app.file_handler' not in [lh.name for lh in logger.handlers]:
        file_handler = TimedRotatingFileHandler(os.path.join(sys.prefix, 'var', 'log', 'homecon', 'homecon_app.log'),
                                                when="midnight")
        file_handler.setFormatter(logFormatter)
        file_handler.set_name('homecon_app.file_handler')
        logging.root.handlers.append(file_handler)

    if printlog:
        if 'homecon_app.console_handler' not in [lh.name for lh in logger.handlers]:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logFormatter)
            console_handler.set_name('homecon_app.console_handler')
            logging.root.handlers.append(console_handler)

    logging.root.setLevel(getattr(logging, loglevel))
    logging.getLogger('homecon_app.httpserver').setLevel(getattr(logging, loglevel))

    http_server = HttpServer(**kwargs)
    http_server.start()


if __name__ == '__main__':

    parser = ArgumentParser(description='Generate all energy market records')
    parser.add_argument('--printlog', action='store_true')
    parser.add_argument('-l', '--loglevel', type=str, choices=['INFO', 'DEBUG'], default='INFO')
    parser.add_argument('--address', type=str, default=_address)
    parser.add_argument('--port', type=str, default=_port)
    parser.add_argument('--document_root', type=str, default=_document_root)

    kwargs = vars(parser.parse_args())

    main(**kwargs)

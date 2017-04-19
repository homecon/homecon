#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class PolymerRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        logging.debug('GET {}'.format(self.path))

        if '.' in self.path:
            abspath = os.path.abspath(os.path.join('..','app',self.path[1:]))

        else:
            # return index.html
            abspath = os.path.abspath(os.path.join('..','app','index.html'))


        _, ext = os.path.splitext(abspath)
        ext = ext.lower()
        content_type = {
            '.css': 'text/css',
            '.gif': 'image/gif',
            '.html': 'text/html',
            '.jpeg': 'image/jpeg',
            '.jpg': 'image/jpg',
            '.js': 'text/javascript',
            '.png': 'image/png',
            '.text': 'text/plain',
            '.txt': 'text/plain',
        }

        # If it is a known extension, set the correct
        # content type in the response.
        if ext in content_type:

            if os.path.exists(abspath):

                self.send_response(200)  # OK
                self.send_header('Content-type', content_type[ext])
                self.end_headers()


                with open(abspath,'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404,'File Not Found: %s' % self.path)

        return



def run():
    try:
        print('starting server...')

        # Server settings
        server_address = ('0.0.0.0', 12300)
        httpd = HTTPServer(server_address, PolymerRequestHandler)
        print('running server...')
        httpd.serve_forever()
    except:
        print('\nshutting down server...')

run()

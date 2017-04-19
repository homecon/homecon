#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import threading
import http.server
import inspect


basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class HttpRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        #logging.debug('GET {}'.format(self.path))

        if '.' in self.path:
            # if an extension is supplied return the file
            abspath = os.path.abspath(os.path.join(basedir,'..','app',self.path[1:]))

        else:
            # else return index.html
            abspath = os.path.abspath(os.path.join(basedir,'..','app','index.html'))


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

        # If it is a known extension, set the correct content type
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



class HttpServerThread(threading.Thread):
    def __init__(self, address='0.0.0.0',port=12300):
        super().__init__()

        self.name = 'HttpServer'
        self.address = address
        self.port = port


    def run(self):        
        self.httpd = http.server.HTTPServer((self.address, self.port), HttpRequestHandler)
        print('Running the HomeCon http server at {}:{}'.format(self.address,self.port))
        self.httpd.serve_forever()


    def stop(self):
        try:
            self.httpd.shutdown()
            self.httpd.socket.close()
            print('HomeCon http server stopped')
        except:
            pass



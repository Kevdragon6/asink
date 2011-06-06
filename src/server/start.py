#!/usr/bin/env python

#    Copyright (C) 2011 Aaron Lindsay <aaron@aclindsay.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import multiprocessing
import re

#fixup python include path, so we can include other project directories
sys.path.append(os.path.join(os.getcwd(), "../"))

from database import Database
from handlers import api, web

NUM_PROCESSES = 1 #keep it simple for starters

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.do_GET()
    def do_GET(self):
        if re.match("^/api/?$", self.path):
            api(self)
        else:
            web(self)

def serve(server):
    global database
    database = Database()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

def start_server(host, port):
    server = HTTPServer((host, port), Handler)
    processes = []

    for i in range(NUM_PROCESSES-1):
        processes.append(multiprocessing.Process(target=serve, args=(server,)))
        processes[i].start()
    serve(server)

if __name__ == "__main__":
    start_server('localhost', 8080)

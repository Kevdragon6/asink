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
import logging
import tornado.ioloop
import tornado.web

#fixup python include path, so we can include other project directories
sys.path.append(os.path.join(os.getcwd(), "../"))

from database import Database
from handlers import WebHandler, EventsHandler, PollingHandler

application = tornado.web.Application([
    (r"/", WebHandler),
    (r"/api/?", EventsHandler),
    (r"/api/updates/([0-9]+)", PollingHandler),
])

def setup_logging():
    #TODO set this to go to a configurable file, and make logging level configurable
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

if __name__ == "__main__":
    setup_logging()
    application.listen(8080)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

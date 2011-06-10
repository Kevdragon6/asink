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

import json
import tornado.web
import threading

from shared import events
from database import Database

local = threading.local()
local.database = Database()

class WebHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Web interface not yet implemented, sorry\n")

class EventsHandler(tornado.web.RequestHandler):
    """Handle HTTP requests send to <hostname:port>/api endpoint -
    namely update and delete events for files."""
    def post(self):
        try:
            j = self.get_argument("data")
            data = json.loads(j)
            query = "INSERT INTO events VALUES (NULL,?,?,?,?,?,?,?)"
            event = events.Event(0)
            for e in data:
                event.fromseq(e)
                local.database.execute(query, event.totuple()[1:])
            local.database.commit()
            #TODO see if there are any long-polling connections waiting on input from
                #this user. If there are, write these events out to them, and close
                #those connections
        except Exception as e:
            print type(e)
            print e.args
            print e
            raise tornado.web.HTTPError(400)

class PollingHandler(tornado.web.RequestHandler):
    def get(self, lastrev):
        #TODO - actually get their userid here
        userid = 0
        #TODO check and see if there are already updates waiting on this user.
            #If there are, return them and don't mess with keeping this connection
            #around.
        self.write("Hello, world "+str(lastrev))

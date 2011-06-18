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
import logging

from shared import events
from database import Database

local = threading.local()
local.database = Database()

class WebHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Web interface not yet implemented, sorry\n")

class UpdatesMixin(object):
    waiters = {}
    waiters_lock = threading.Lock() #TODO make locking per-userid
    def wait_for_updates(self, userid, callback):
        cls = UpdatesMixin
        cls.waiters_lock.acquire()
        if userid in cls.waiters:
            cls.waiters[userid].append(callback)
        else:
            cls.waiters[userid] = [callback]
        cls.waiters_lock.release()
    def updates_ready(self, userid, events):
        cls = UpdatesMixin
        cls.waiters_lock.acquire()
        if userid in cls.waiters:
            for callback in cls.waiters[userid]:
                callback(events)
            cls.waiters[userid] = []
        cls.waiters_lock.release()


class EventsHandler(tornado.web.RequestHandler, UpdatesMixin):
    """Handle HTTP requests sent to <hostname:port>/api endpoint -
    namely update and delete events for files."""
    def post(self):
        #TODO - actually get their userid here
        userid = 0
        try:
            j = self.get_argument("data")
            data = json.loads(j)
            query = "INSERT INTO events VALUES (NULL,?,?,?,?,?,?,?)"
            event = events.Event(0)
            for e in data:
                event.fromseq(e)
                local.database.execute(query, event.totuple()[1:])
                e[0] = local.database.lastrowid()
            self.updates_ready(userid, data) #send updates to any waiting
                #long-polling connections
        except:
            raise tornado.web.HTTPError(400)

class PollingHandler(tornado.web.RequestHandler, UpdatesMixin):
    """Handle long-polling HTTP requests sent to
    <hostname:port>/api/updates/<lastrev> endpoint"""
    @tornado.web.asynchronous
    def get(self, lastrev):
        #TODO - actually get their userid here
        userid = 0
        #check and see if there are already updates waiting on this user. If
        #there are, return them and don't mess with keeping this connection
        #around.
        logging.info("Update request w/ ip=%s, userid=%s, lastrev=%s" %
                     (self.request.remote_ip, userid, lastrev))
        res = local.database.execute("""SELECT * FROM events WHERE user=? AND
                                     rev > ? ORDER BY rev ASC""", (userid, lastrev))
        events = []
        for e in res:
            events.append(e)
        if len(events) > 0:
            logging.debug("%s events already available, returning those" %
                          len(events))
            self.on_new_events(events)
        else:
            logging.debug("No events available, blocking")
            self.wait_for_updates(userid, self.async_callback(self.on_new_events))

    def on_new_events(self, events):
        if self.request.connection.stream.closed():
            return
        self.write(json.dumps(events))
        self.finish()

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

import threading
import Queue
import urllib2
import json

from shared import events
from database import Database

POLLING_TIMEOUT = 10 #number of seconds to wait for a response

class Receiver(threading.Thread):
    stopped = False
    def stop(self):
        self.stopped = True
    def run(self):
        self.database = Database()
        while not self.stopped:
            response = urllib2.urlopen("http://localhost:8080/api/updates/"+str(self.get_last_rev()), None, POLLING_TIMEOUT)
            #events = json.loads(response.read())
            events = []
            if len(events) > 0:
                self.handle_events(events)
    def get_last_rev(self):
        return 0 #TODO implement me
    def handle_events(self, events):
        for e in events:
            event = Event(0)
            event.fromseq(e)
            print "received", event

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
import urllib
import urllib2
import json

from shared import events

MAX_TO_QUEUE = 100  #The maximum number of events to queue before sending them to
                    #the server

class Sender(threading.Thread):
    stopped = False
    to_send = [] #list of events to send to the server
    def stop(self):
        self.stopped = True
    def run(self):
        while not self.stopped:
           try:
                self.handle_event(self.wuhs_queue.get(True, 0.2))
           except Queue.Empty:
               if len(self.to_send) > 0:
                   self.handle_event(None, True)

    def handle_event(self, event, finalize=False):
        if event:
            print "sending", event
            self.to_send.append(event.tolist())
        if finalize or len(self.to_send) >= MAX_TO_QUEUE:
            j = json.dumps(self.to_send)
            urlencoded = urllib.urlencode({"data": j})
            urllib2.urlopen("http://localhost:8080/api", urlencoded).read()
            self.to_send = []

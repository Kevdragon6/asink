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

class Hasher(threading.Thread):
    stopped = False
    def set_queue(self, queue):
        self.queue = queue
    def stop(self):
        self.stopped = True
    def run(self):
        while not self.stopped:
           try:
                self.handle_event(self.queue.get(True, 0.2))
           except Queue.Empty:
                pass
    def handle_event(self, event):
        j = json.dumps([event.tolist()])
        print urllib2.urlopen("http://localhost:8080/api", j).read()

        #if delete, send to server right away
        #else if update
            #hash file, see if it matches any pre-existing stored files
                #if so, put event in queue to be sent to server
            #otherwise, put in queue to be uploaded
                #when done, put it in queue to be sent to server

        print event

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
from httplib import BadStatusLine

from shared import events
from database import Database
from config import Config

POLLING_TIMEOUT = 10 #number of seconds to wait for a response

class Receiver(threading.Thread):
    stopped = False
    def stop(self):
        self.stopped = True
    def run(self):
        self.database = Database()
        while not self.stopped:
            try:
                host = "http://%s:%s" % (Config().get("server", "host"),
                                        Config().get("server", "port"))
                response = urllib2.urlopen(host+"/api/updates/"+str(self.get_last_rev()), None, POLLING_TIMEOUT)
                events = json.loads(response.read())
                if len(events) > 0:
                    self.handle_events(events)
            except urllib2.URLError:
                pass
            except BadStatusLine:
                pass
    def get_last_rev(self):
        return 0 #TODO implement me
    def handle_events(self, es):
        for e in es:
            event = events.Event(0)
            event.fromseq(e)
            #make sure we don't already have this event
            res = self.database.execute("SELECT * FROM events WHERE rev=?",
                                  (event.rev,))
            oldEvent = next(res, None)
            if oldEvent is not None:
                ev2 = events.Event(0)
                ev2.fromseq(oldEvent)
                print event
                print ev2
                if ev2 != event:
                    #TODO handle error where event exists but isn't
                    #consistent
                    print "Error: events have same revision, but don't match"
                return

            #if we've reached here, the event doesn't exist exactly in the local
            #database. Check if it exists, just w/ a rev of 0, or whether it is
            #completely new, and therefore originated remotely

            res = self.database.execute("""SELECT * FROM events WHERE rev=0 AND
                                        user=? AND type=? AND hash=? AND
                                        localpath=? AND modified=? AND
                                        storagepath=? AND permissions=?""",
                                        event.totuple()[1:])
            localEvent = next(res, None)
            #if this originated as a local event, update the rev, and re-store it
            if localEvent is not None:
                self.database.execute("""UPDATE events SET rev=? WHERE rev=0 AND
                                        user=? AND type=? AND hash=? AND
                                        localpath=? AND modified=? AND
                                        storagepath=? AND permissions=?""",
                                        event.totuple())
            #otherwise, pass it on to the downloader 
            else:
                self.database.execute("""INSERT INTO events VALUES
                                      (?,?,?,?,?,?,?,?)""", event.totuple())
                self.rd_queue.put(event)

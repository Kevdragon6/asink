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
from os import path
import logging

from shared.events import EventType
from config import Config
from database import Database

class Uploader(threading.Thread):
    stopped = False
    def stop(self):
        self.stopped = True
        self.hu_queue.put(None)
    def run(self):
        self.database = Database()
        while not self.stopped:
            event = self.hu_queue.get(True)
            if event:
                self.handle_event(event)

    def handle_event(self, event):
        src = path.join(Config().get("core", "cachedir"), event.hash)

        needsUpload = False
        if event.type & EventType.DELETE is 0:
            res = self.database.execute("SELECT * FROM events WHERE hash=? AND rev!=0",
                                       (event.hash,))
            needsUpload = next(res, None) is None

        #add event to the database
        self.database.execute("INSERT INTO events VALUES (0,?,?,?,?,?,?,?)",
                              event.totuple()[1:])

        if needsUpload:
            try:
                event.storagekey = self.storage.put(src, event.hash)
                #TODO handle failure of storage.put (will throw exception if fails)
                self.wuhs_queue.put(event)
            except Exception as e:
                logging.error("Error uploading file: "+str(event)+"\n"+e.message)
        else:
            self.wuhs_queue.put(event)

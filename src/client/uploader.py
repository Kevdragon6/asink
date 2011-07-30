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

import os
import stat
import Queue
import logging
import threading
from itertools import izip
from tempfile import mkstemp
from shutil import copy2, move

from hasher import hash
from config import Config
from database import Database
from shared.events import Event, EventType

MAX_TO_QUEUE = 100  #The maximum number of uploads to queue before uploading them

class Uploader(threading.Thread):
    stopped = False
    to_upload = []

    def stop(self):
        self.stopped = True

    def run(self):
        self.database = Database()
        while not self.stopped:
            try:
                self.handle_event(self.queue.get(True, 0.2))
            except Queue.Empty:
                if len(self.to_upload) > 0:
                    self.upload()
            if len(self.to_upload) >= MAX_TO_QUEUE:
                self.upload()

    def upload(self):
        try:
            keys = self.storage.putm(((localpath, event.hash) for event, localpath in self.to_upload))
            #TODO handle failure of storage.put (will throw exception if fails)

            for s, key in izip(self.to_upload, keys):
                event, tmppath = s
                event.storagekey = key

                #add event to the database
                self.database.execute("INSERT INTO events VALUES (0,?,?,?,?,?,?,?)",
                                      event.totuple()[1:])

                #move tmp file to hash-named file in cache directory
                cachepath = os.path.join(Config().get("core", "cachedir"), event.hash)
                move(tmppath, cachepath)

                self.sender_queue.put(event)

            self.to_upload = []
        except Exception as e:
            logging.error("Uploader failed: "+str(type(e))+": "+e.message)

    def handle_event(self, event):
        try:
            if event.type & EventType.UPDATE:
                self.handle_update_event(event)
            elif event.type & EventType.DELETE:
                self.handle_delete_event(event)
        except Exception as e:
            logging.error("Uploader failed: "+str(event)+"\n"+e.message)
            logging.error(str(type(e))+": "+e.message)

    def handle_update_event(self, event):
        filepath = os.path.join(Config().get("core", "syncdir"), event.path)

        #first, copy the file over to a temporary directory, get its hash,
        #upload it, and then move it to the filename with that hash value
        handle, tmppath = mkstemp(dir=Config().get("core", "cachedir"))
        os.close(handle) #we don't really want it open, we just want a good name
        try:
            copy2(filepath, tmppath)
        except IOError:
            logging.warning("Dropping update event because file was deleted before we could upload it: %s" % (str(event)))
            return

        #get the mode of the file
        stats = os.stat(filepath)
        event.permissions = str(stat.S_IMODE(stats.st_mode))

        #hash the temporary file
        event.hash = hash(tmppath)[0]
        logging.debug("HASHED  "+str(event))

        #make sure the most recent version of this file doesn't match this one
        #otherwise it's pointless to re-upload it
        res = self.database.execute("""SELECT * FROM events WHERE localpath=?
                                    AND rev != 0 ORDER BY rev DESC LIMIT 1""", (event.path,))
        latest = next(res, None)
        if latest is not None:
            e = Event(0)
            e.fromseq(latest)
            if e.hash == event.hash:
                #returning because hashes are equal
                #but first, remove the temporary file in the cache
                os.remove(tmppath)
                return

        res = self.database.execute("SELECT * FROM events WHERE hash=? AND rev!=0",
                                   (event.hash,))
        sameHash = next(res, None)
        #if this file isn't already uploaded, add it to the list to upload, and
        #upload them in a batch when we have a chance
        if sameHash is None:
            self.to_upload.append((event, tmppath))
            return

        e = Event(0)
        e.fromseq(sameHash)
        event.storagekey = e.storagekey

        #add event to the database
        self.database.execute("INSERT INTO events VALUES (0,?,?,?,?,?,?,?)",
                              event.totuple()[1:])

        #move tmp file to hash-named file in cache directory
        cachepath = os.path.join(Config().get("core", "cachedir"), event.hash)
        move(tmppath, cachepath)

        self.sender_queue.put(event)

    def handle_delete_event(self, event):
        #if the file doesn't exist and we're a delete event, just drop it
        res = self.database.execute("""SELECT * FROM events WHERE localpath=? 
                                    LIMIT 1""", (event.path,))
        exists = next(res, None)
        if exists is None:
            return

        res = self.database.execute("""SELECT * FROM events WHERE localpath=?
                                    AND rev != 0 ORDER BY rev DESC LIMIT 1""", (event.path,))
        latest = next(res, None)
        if latest is not None:
            e = Event(0)
            e.fromseq(latest)
            if e.type & EventType.DELETE:
                #returning because it was already deleted
                return

        #add event to the database
        self.database.execute("INSERT INTO events VALUES (0,?,?,?,?,?,?,?)",
                              event.totuple()[1:])

        self.sender_queue.put(event)

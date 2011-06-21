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
import logging
from tempfile import mkstemp
from shutil import copy2, move
from os import path, remove, makedirs, close, rmdir

from shared import events
from config import Config
from database import Database

class Downloader(threading.Thread):
    stopped = False
    def stop(self):
        self.stopped = True
        self.queue.put(None)
    def run(self):
        self.database = Database()
        while not self.stopped:
            event = self.queue.get(True)
            if event:
                self.handle_event(event)

    def handle_event(self, event):
        dst = path.join(Config().get("core", "syncdir"), event.path)
        cachepath = path.join(Config().get("core", "cachedir"), event.hash)

        #Check to see if this event's time is later than the latest
        #modification time we have locally seen for this file. If it's not,
        #simply return
        res = self.database.execute("SELECT * FROM events WHERE localpath=? and modified>?",
                                    (event.path, event.time))
        newerEvent = next(res, None)
        if newerEvent is not None:
            return #receiver has already added this event to the database

        #TODO make sure deleted files are cached locally if they're not yet
            #stored online
        if event.type & events.EventType.DELETE != 0:
            try:
                self.recursive_delete(dst)
            except: #OSError from file not existing
                logging.error("could not remove "+event.path)
            return

        try:
            #ensure file isn't already cached
            if not path.exists(cachepath):
                #create temporary file to download it to
                handle, tmppath = mkstemp(dir=Config().get("core", "cachedir"))
                close(handle) #we don't really want it open, we just want a good name

                self.storage.get(tmppath, event.hash, event.storagekey)
                #TODO handle failure of storage.get (will throw exception if fails)

                #move temp file to hashed cache file
                move(tmppath, cachepath)

            #move file from cache directory to actual file system
            #by way of another tmp file
            handle, tmppath = mkstemp(dir=Config().get("core", "cachedir"))
            close(handle) #we don't really want it open, we just want a good name
            copy2(cachepath, tmppath)

            #make sure directory exists first
            dirname = path.dirname(dst)
            if not path.isdir(dirname):
                makedirs(dirname)

            move(tmppath, dst)
        except Exception as e:
            logging.error("Could not download file: "+str(event))
            logging.error(str(type(e))+": "+e.message)

    def recursive_delete(self, filepath):
        syncdir = Config().get("core", "syncdir")
        remove(filepath)
        logging.debug("removed "+ filepath)
        try:
            dirpath = path.dirname(filepath)
            while dirpath != syncdir and len(dirpath) > len(syncdir):
                rmdir(dirpath)
                dirpath = path.dirname(dirpath)
        except OSError:
            pass

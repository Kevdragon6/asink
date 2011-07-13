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

import Queue
import logging
import threading
from itertools import izip
from tempfile import mkstemp
from shutil import copy2, move
from os import path, remove, makedirs, close, rmdir, chmod

from hasher import hash
from config import Config
from database import Database
from shared.events import EventType

MAX_TO_QUEUE = 100  #The maximum number of downloads to queue before downloading them

class Downloader(threading.Thread):
    stopped = False
    to_download = []

    def stop(self):
        self.stopped = True

    def run(self):
        self.database = Database()
        while not self.stopped:
            try:
                self.handle_event(self.queue.get(True, 0.2))
            except Queue.Empty:
                if len(self.to_download) > 0:
                    self.download()
            except Exception as e:
                logging.error("Unexpected exception: "+str(e))
            if len(self.to_download) >= MAX_TO_QUEUE:
                self.download()

    def download(self):
        syncdir = Config().get("core", "syncdir")
        cachedir = Config().get("core", "cachedir")

        #make all the temporary files for the downloads
        tmppaths = []
        for e in self.to_download:
            handle, tmppath = mkstemp(dir=cachedir)
            close(handle) #we don't really want it open, we just want a good name
            tmppaths.append(tmppath)

        #now, actually download all the files
        self.storage.getm(((tmppath, event.hash, event.storagekey) for tmppath,
                          event in izip(tmppaths, self.to_download)))
        #TODO handle failure of storage.get (will throw exception if fails)

        #now, move all the downloaded files to the cache
        for tmppath, event in izip(tmppaths, self.to_download):
            h = hash(tmppath)[0]
            if h != event.hash:
                logging.error("    DOWN: hash doesn't match downloaded file event: "+str(event))
                logging.error("        : offending hash: "+h)
                continue #TODO handle this error somehow?

            #set the permissions, if we have them
            if len(event.permissions.strip()) > 0:
                chmod(tmppath, int(event.permissions))

            #move temp file to hashed cache file
            cachepath = path.join(cachedir, event.hash)
            move(tmppath, cachepath)

            dst = path.join(Config().get("core", "syncdir"), event.path)
            self.cache_to_asink_dir(cachepath, dst)

        self.to_download = []

    def handle_event(self, event):
        #Check to see if this event's time is later than the latest
        #modification time we have locally seen for this file. If it's not,
        #simply return
        res = self.database.execute("SELECT * FROM events WHERE localpath=? and modified>?",
                                    (event.path, event.time))
        newerEvent = next(res, None)
        if newerEvent is not None:
            return #receiver has already added this event to the database

        if event.type & EventType.UPDATE:
            self.handle_update_event(event)
        elif event.type & EventType.DELETE:
            self.handle_delete_event(event)

    def handle_update_event(self, event):
        try:
            #if file isn't cached, fetch it from remote server
            dst = path.join(Config().get("core", "syncdir"), event.path)
            cachepath = path.join(Config().get("core", "cachedir"), event.hash)
            if not path.exists(cachepath):
                self.to_download.append(event)
            else:
                self.cache_to_asink_dir(cachepath, dst)

        except Exception as e:
            logging.error("Could not download file: "+str(event))
            logging.error(str(type(e))+": "+e.message)

    def cache_to_asink_dir(self, cachepath, dst):
        #move file from cache directory to actual file system
        #by way of another tmp file
        handle, tmppath = mkstemp(dir=Config().get("core", "cachedir"))
        close(handle) #we don't really want it open, we just want a good name
        copy2(cachepath, tmppath)

        #make sure directory exists first
        dirname = path.dirname(dst)
        if not path.isdir(dirname):
            makedirs(dirname, 0755)

        move(tmppath, dst)

    def handle_delete_event(self, event):
        #TODO make sure deleted files are cached locally if they're not yet stored online
        try:
            to_delete = path.join(Config().get("core", "syncdir"), event.path)
            self.recursive_delete(to_delete)
        except: #OSError from file not existing
            logging.error("could not remove "+event.path)

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

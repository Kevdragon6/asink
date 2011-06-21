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
import logging
from os import path, walk

from shared.events import Event, EventType
from config import Config
import util

class Indexer(threading.Thread):
    stopped = False
    def stop(self):
        self.stopped = True
    def run(self):
        for root, dirs, files in walk(Config().get("core", "syncdir")):
            if self.stopped:
                return
            for file in files:
                filepath = path.join(root, file)
                relpath = path.relpath(filepath, Config().get("core", "syncdir"))
                try:
                    e = Event(EventType.UPDATE | EventType.LOCAL)
                    e.path = relpath
                    e.time = path.getmtime(filepath) + util.time_diff()
                    self.hasher_queue.put(e, True)
                except OSError:
                    logging.warning("Couldn't get a modification time for "
                                    +filepath+". Ignoring file")
        #TODO later go through and update all the files that exist here, but have
        #been removed from the database? This *shouldn't* be necessary, but
        #perhaps it would be nice to do some preventative maintenance.

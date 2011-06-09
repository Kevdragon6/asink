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

import pyinotify
from Queue import Queue
from time import time

from config import Config
from shared.events import Event, EventType

mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM # watched events

class EventHandler(pyinotify.ProcessEvent):
    def enqueue_modify(self, path):
        e = Event(EventType.UPDATE | EventType.LOCAL)
        e.path = path
        e.time = time()
        self.wh_queue.put(e, True)
    def enqueue_delete(self, path):
        e = Event(EventType.DELETE | EventType.LOCAL)
        e.path = path
        e.time = time()
        self.wus_queue.put(e, True)
    def process_IN_CREATE(self, event):
        self.enqueue_modify(event.pathname)
    def process_IN_MODIFY(self, event):
        self.enqueue_modify(event.pathname)
    def process_IN_DELETE(self, event):
        self.enqueue_delete(event.pathname)
    def process_IN_MOVED_TO(self, event):
        self.enqueue_modify(event.pathname)
    def process_IN_MOVED_FROM(self, event):
        self.enqueue_delete(event.pathname)

def start_watching(wh_queue, wus_queue):
    global notifier, wm
    wm = pyinotify.WatchManager()  # Watch Manager
    eh = EventHandler()
    eh.wh_queue = wh_queue
    eh.wus_queue = wus_queue

    notifier = pyinotify.ThreadedNotifier(wm, eh)
    notifier.start()

    add_watched_dir(Config().syncdir)

def add_watched_dir(directory):
    global wm
    wm.add_watch(directory, mask, rec=True, auto_add=True)

def remove_watched_dir(wd):
    global wm
    wm.rm_watch(wd)

def stop_watching():
    global notifier
    notifier.stop()

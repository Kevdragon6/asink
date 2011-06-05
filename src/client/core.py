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
import time

import events

class CoreEventLoop(threading.Thread):
    stopped = False
    def set_event_queue(self, queue):
        self.queue = queue
    def stop(self):
        self.stopped = True
    def run(self):
        while not self.stopped:
            try:
                self.handle_event(self.queue.get(False))
            except Queue.Empty:
                pass
    def handle_event(self, event):
        print event

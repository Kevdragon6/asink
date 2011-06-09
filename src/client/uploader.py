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
from shutil import copyfile, copymode, copystat
from os import path

from shared import events

class Uploader(threading.Thread):
    stopped = False
    def stop(self):
        self.stopped = True
    def run(self):
        while not self.stopped:
           try:
                self.handle_event(self.hu_queue.get(True, 0.2))
           except Queue.Empty:
                pass
    def handle_event(self, event):
        #fake uploader for now by 'uploading' to local directory by hash
        src = event.path
        dst = path.join("/home/aclindsa/asink_scratch", event.hash)
        try:
            copyfile(src, dst)
            copymode(src, dst)
            copystat(src, dst)
            self.wus_queue.put(event)
        except:
            print "Error uploading file:"
            print event,

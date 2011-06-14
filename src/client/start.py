#!/usr/bin/env python

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
import signal
import sys
import time
from Queue import Queue

#fixup python include path, so we can include other project directories
sys.path.append(os.path.join(os.getcwd(), "../"))

import constants
from config import Config
import watcher
from hasher import Hasher
from uploader import Uploader
from sender import Sender

from receiver import Receiver
from downloader import Downloader

def main():
    global hasher, uploader, sender, receiver, downloader
    setup_signals()

    #TODO implement this
    #start pyinotify listener, but just queue events until after indexing and syncing is done
    #start long-polling w/ server for changes coming down, but    "    "    "
    #pull changes from server
    #run initial indexer
    #begin handling incoming inotify events, and longpolling info from server

    #create all threads which will be used to process events
    hasher = Hasher()
    uploader = Uploader()
    sender = Sender()
    receiver = Receiver()
    downloader = Downloader()

    #create and set up queues which are used to pass events between threads
    wh_queue = Queue()
    hasher.wh_queue = wh_queue
    #set on watcher when initialized

    hu_queue = Queue()
    hasher.hu_queue = hu_queue
    uploader.hu_queue = hu_queue

    wuhs_queue = Queue()
    watcher.wuhs_queue = wuhs_queue
    uploader.wuhs_queue = wuhs_queue
    hasher.wuhs_queue = wuhs_queue
    sender.wuhs_queue = wuhs_queue

    rd_queue = Queue()
    receiver.rd_queue = rd_queue
    downloader.rd_queue = rd_queue

    #start all threads
    watcher.start_watching(wh_queue, wuhs_queue)
    hasher.start()
    uploader.start()
    sender.start()
    receiver.start()
    downloader.start()

    #sleep until signaled, which will call sig_handler
    while True:
        time.sleep(86400) #= 24 hours just for fun

def setup_signals():
    signal.signal(signal.SIGABRT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

def sig_handler(signum, frame):
    global hasher, uploader, sender, receiver
    receiver.stop() #stop the receiver first, because it could take a while to
        #finish its last poll
    watcher.stop_watching()
    hasher.stop()
    uploader.stop()
    sender.stop()
    downloader.stop()
    Config().write() #write any changes to the config out to the config file
    sys.exit(0)

if __name__ == "__main__":
    main()

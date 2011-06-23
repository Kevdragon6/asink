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
import logging
from Queue import Queue

#fixup python include path, so we can include other project directories
sys.path.append(os.path.join(os.getcwd(), "../"))

import constants
from config import Config

from storage.ssh import SSHStorage
from storage.s3 import S3Storage

import watcher
from indexer import Indexer
from hasher import Hasher
from uploader import Uploader
from sender import Sender
from receiver import Receiver
from downloader import Downloader

def main():
    global indexer, hasher, uploader, sender, receiver, downloader
    setup_logging()
    setup_signals()

    #TODO implement this
    #start pyinotify listener, but just queue events until after indexing and syncing is done
    #start long-polling w/ server for changes coming down, but    "    "    "
    #pull changes from server
    #run initial indexer
    #begin handling incoming inotify events, and longpolling info from server

    #create all threads which will be used to process events
    indexer = Indexer()
    hasher = Hasher()
    uploader = Uploader()
    sender = Sender()
    receiver = Receiver()
    downloader = Downloader()

    #create and set up queues which are used to pass events between threads
    hasher_queue = Queue()
    indexer.hasher_queue = hasher_queue
    hasher.queue = hasher_queue
    #set on watcher when initialized

    uploader_queue = Queue()
    hasher.uploader_queue = uploader_queue
    uploader.queue = uploader_queue

    sender_queue = Queue()
    uploader.sender_queue = sender_queue
    sender.queue = sender_queue

    downloader_queue = Queue()
    receiver.downloader_queue = downloader_queue
    downloader.queue = downloader_queue

    #setup storage provider
    storage = setup_storage()
    uploader.storage = storage.clone()
    downloader.storage = storage

    #start all threads
    watcher.start_watching(hasher_queue)
    indexer.start()
    hasher.start()
    uploader.start()
    sender.start()
    receiver.start()
    downloader.start()

    #sleep until signaled, which will call sig_handler
    while True:
        time.sleep(86400) #= 24 hours just for fun

def setup_logging():
    #TODO log to a file
    #TODO make log level a config option
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

def setup_storage():
    method = Config().get("core", "storagemethod")
    if method == "ssh":
        host = Config().get("ssh", "host")
        port = Config().get("ssh", "port")
        username = Config().get("ssh", "username")
        basepath = Config().get("ssh", "basepath")
        return SSHStorage(host, username, basepath, port)
    elif method == "s3":
        host = Config().get("s3", "host")
        bucket = Config().get("s3", "bucket")
        id = Config().get("s3", "id")
        secretkey = Config().get("s3", "secretkey")
        return S3Storage(host, bucket, id, secretkey)
    #TODO handle error if method isn't valid or setup right

def setup_signals():
    signal.signal(signal.SIGABRT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

def sig_handler(signum, frame):
    global indexer, hasher, uploader, sender, receiver
    receiver.stop() #stop the receiver first, because it could take a while to
        #finish its last poll
    watcher.stop_watching()
    indexer.stop()
    hasher.stop()
    uploader.stop()
    sender.stop()
    downloader.stop()
    Config().write() #write any changes to the config out to the config file
    sys.exit(0)

if __name__ == "__main__":
    main()

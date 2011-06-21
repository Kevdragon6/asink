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

import urllib2
from time import time
import logging

from config import Config

last_synced = 0
current_diff = float(Config().get("core", "timediff"))
#current_diff = server time - client time
#So, to get server time from client time, add diff to client time

def measure_diff():
    host = "http://%s:%s" % (Config().get("server", "host"),
                            Config().get("server", "port"))
    try:
        begin = time()
        response = urllib2.urlopen(host+"/api/timesync").read()
        end = time()
        return float(response) - (begin+end)/2.0
    except urllib2.URLError:
        pass
    return None

def time_diff():
    global current_diff, last_synced
    #sync every 10 minutes
    if last_synced < (time() - 600):
        diffs = []
        for i in range(10):
            diff = measure_diff()
            if diff is not None:
                diffs.append(diff)
        if len(diffs) > 0:
            current_diff = sum(diffs) / len(diffs)
            last_synced = time()
            Config().set("core", "timediff", current_diff)
            logging.info("time diff with server updated to "+str(current_diff)+" seconds")

    return current_diff

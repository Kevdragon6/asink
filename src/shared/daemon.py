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
import sys
from time import sleep
import atexit
import logging
from signal import SIGTERM

pid_file = "" #holds the name of file holding our pid

def daemonize(pid_filename, daemon_fn):
    """Daemonize the current process, store the new pid in pid_filename, and
    call daemon_fn() to continue execution."""
    global pid_file
    pid_file = pid_filename
    try:
        #fork off a process, kill the parent
        if os.fork() > 0:
            os._exit(0)
    except:
        logging.error("Failed to fork new process.")
        os._exit(0)

    os.chdir("/")
    os.setsid()  #start a new session, with this as the session leader
    os.umask(0)  #reset file creation mask

    #fork again
    try:
        if os.fork() > 0:
            os._exit(0)
    except:
        logging.error("Failed to fork new process.")
        os._exit(0)

    #flush all terminal 'files' and redirect them to /dev/null
    sys.stdout.flush()
    sys.stderr.flush()
    null = os.open('/dev/null', os.O_RDWR)
    os.dup2(null, sys.stdin.fileno())
    os.dup2(null, sys.stdout.fileno())
    os.dup2(null, sys.stderr.fileno())
    os.close(null)

    #store our current pid in the given pidfile
    atexit.register(rm_pid_file) #delete pid file when current process exits
    pid = os.getpid()
    try:
        with open(pid_file,'w') as f:
            f.write(str(pid))
            f.close()
    except:
        logging.error("Failed to create pid file at %s" %
                         (pid_filename))
        os._exit(0)

    #run the function with "real work" in it
    daemon_fn()

def rm_pid_file():
    global pid_file
    os.remove(pid_file)

def aengelize(pid_filename):
    """Make the daemonized process represented by the given filename 'go to
    heaven'."""
    try:
        with open(pid_filename,'r') as f:
            pid = int(f.read().strip())
            f.close()
    except Exception as e:
        logging.error("""Failed to open pid file at %s. Process
                         already exited?""" % (pid_filename))
        logging.error(type(e))
        logging.error(e.message)
        sys.exit(0)

    #kill process
    try:
        #try to kill process for 11 seconds
        for i in range(0,110):
            os.kill(pid, SIGTERM)
            sleep(0.1)
        logging.error("Failed to stop process")
    except OSError, err:
        if str(err).find("No such process") > 0:
            os.remove(pid_filename)
        else:
            logging.error("Failed to stop process")
            sys.exit(1)

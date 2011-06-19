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

from os import path
import subprocess
import logging
from copy import deepcopy

class SSHStorage:
    """Provides an ssh-based backing store. Assumes username has key-based
       passwordless login setup on the remote machine"""
    def __init__(self, host, username, basepath, port=22):
        self.host = host
        self.username = username
        self.basepath = basepath
        self.port = port

    def put(self, localpath, hash):
        """Stores the file designated by localpath on the ssh server. Returns a
           string key the calling application should pass to get() to retrieve
           the file."""
        dst = path.join(self.basepath, hash)
        args = ['scp', '-P', str(self.port), localpath, "%s@%s:%s" %
                            (self.username, self.host, dst)]
        logging.debug(str(args))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if len(err) > 0:
            logging.error(err)
        return ""   #return empty key, because the hash and path are enough for us to
                    #retrieve the file

    def get(self, localpath, hash, key):
        """Gets the file which was stored earlier with this localpath, hash, and
           which returned this key from the put method."""
        src = path.join(self.basepath, hash)
        args = ['scp', '-P', str(self.port), "%s@%s:%s" % (self.username,
                            self.host, src), localpath]
        logging.debug(str(args))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if len(err) > 0:
            logging.error(err)

    def clone(self):
        """Provide a clone of this storage object so others can use it"""
        return deepcopy(self)

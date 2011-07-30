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

import logging
import subprocess
from time import time
from copy import deepcopy
from itertools import izip
from hashlib import sha256
from os import path, makedirs
from shutil import copy2, rmtree

class SSHStorage:
    """Provides an ssh-based backing store. Assumes username has key-based
       passwordless login setup on the remote machine"""
    def __init__(self, host, username, basepath, port=22):
        self.host = host
        self.username = username
        self.basepath = basepath
        self.port = port

    def putm(self, files):
        """Stores multiple files on the server. 'files' is a sequence containing
        localpath, hash pairs (in a tuple or other sequence) which would be
        passed to put() normally. It is safe to assume that all the files being
        uploaded have unique base filenames."""
        keys = []
        hashfn = sha256()
        upload_list = []
        hashes = []
        #generate string for uploading files and hash of all files
        for localpath, hash in files:
            keys.append("") #add empty key, because we don't need keys for SSH
            hashfn.update(localpath+":"+hash+":") #add to the hash used to make the dirname
            upload_list.append(localpath) #add to the string used to upload files
            hashes.append(hash)
        #come up with directory name to temporarily upload the files to
        dirname = path.join(self.basepath, hashfn.hexdigest() + "-" + str(time()))
        #create that directory
        self.shell(['ssh', '-p', str(self.port), "%s@%s" %
                            (self.username, self.host), 'mkdir', dirname])
        #upload all files to that directory
        args = ['scp', '-P', str(self.port)] + upload_list + ["%s@%s:%s" %
                            (self.username, self.host, dirname)]
        self.shell(args)
        mv_list = []
        #build up the string with the move commands
        for localpath, hash in izip(upload_list, hashes):
            mv_list.append("mv "+path.join(path.join(self.basepath, dirname), path.basename(localpath))+" "+path.join(self.basepath,hash)+";")
        #move all those files to their proper locations and delete the tmp directory
        self.shell(['ssh', '-p', str(self.port), "%s@%s" %
                            (self.username, self.host)] + mv_list + ['rmdir', dirname])
        return keys

    def put(self, localpath, hash):
        """Stores the file designated by localpath on the ssh server. Returns a
           string key the calling application should pass to get() to retrieve
           the file."""
        dst = path.join(self.basepath, hash)
        args = ['scp', '-P', str(self.port), localpath, "%s@%s:%s" %
                            (self.username, self.host, dst)]
        self.shell(args)
        return ""   #return empty key, because the hash and path are enough for us to
                    #retrieve the file

    def getm(self, files):
        """Gets multiple files, stored as a sequence of sequences, in much
        the same way as putm."""
        download_list = []
        pathes = []
        hashes = []
        hashfn = sha256()
        localpath_ex = "" #example of local path (used to find which directory it
        #is safe for us to create another directory in
        user_and_host = "%s@%s:" % (self.username, self.host)
        for localpath, hash, key in files:
            download_list.append(user_and_host+path.join(self.basepath, hash))
            hashfn.update(localpath+":"+hash+":")
            hashes.append(hash)
            pathes.append(localpath)
            localpath_ex = localpath
        #make local directory to hold downloaded files
        dirname = path.join(path.dirname(localpath_ex), hashfn.hexdigest() + "-" + str(time()))
        makedirs(dirname, 0755)
        #scp files into local directory
        args = ['scp', '-P', str(self.port)] + download_list + [dirname]
        self.shell(args)
        #copy them all to their corresponding localpath places before removing the directory
        for localpath, hash in izip(pathes, hashes):
            copy2(path.join(dirname, hash), localpath)
        rmtree(dirname)

    def get(self, localpath, hash, key):
        """Gets the file which was stored earlier with this localpath, hash, and
           which returned this key from the put method."""
        src = path.join(self.basepath, hash)
        args = ['scp', '-P', str(self.port), "%s@%s:%s" % (self.username,
                            self.host, src), localpath]
        self.shell(args)

    def clone(self):
        """Provide a clone of this storage object so others can use it"""
        return deepcopy(self)

    def shell(self, args):
        logging.debug(str(args))
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if len(err) > 0:
            logging.error(err)
        return out

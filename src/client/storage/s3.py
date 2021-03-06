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

from copy import deepcopy
from hashlib import sha1
import logging
import time
import base64
import hmac
import mimetypes
from httplib import HTTPConnection, HTTPSConnection
import os

class S3Storage:
    """Provides an s3-based backing store. Based on the documentation available
    online at
    http://docs.amazonwebservices.com/AmazonS3/latest/dev/index.html?RESTAuthentication.html"""
    def __init__(self, host, bucket, id, secret_key, https=True):
        self.host = host
        self.bucket = bucket
        self.id = id
        self.secret_key = secret_key
        self.use_https = https

        #TODO make sure bucket works

    def putm(self, files):
        """Stores multiple files on the server. 'files' is a sequence containing
        localpath, hash pairs (in a tuple or other sequence) which would be
        passed to put() normally. It is safe to assume that all the files being
        uploaded have unique base filenames."""
        keys = []
        for localpath, hash in files:
            keys.append(self.put(localpath, hash))
        return keys

    def put(self, localpath, hash, event=None):
        """Stores the file designated by localpath on the s3 server. Returns a
           string key the calling application should pass to get() to retrieve
           the file. It is safe to assume that all the files being uploaded have
           unique base filenames."""
        content_type = "text/plain"
        try:
            content_type = mimetypes.guess_type(event.path)[0]
        except:
            pass
        content_length = os.stat(localpath).st_size
        date = time.strftime("%a, %d %b %Y %X GMT", time.gmtime())
        canonicalized_resource = "/%s/%s" % (self.bucket, hash)

        signature = get_signature("PUT", "", content_type, date, "", canonicalized_resource, self.secret_key)

        body = open(localpath, "rb")
        headers = {"Date": date,
                   "Content-Type": content_type,
                   "authorization": "AWS %s:%s" % (self.id, signature)}
        conn = HTTPSConnection(self.host) if self.use_https else HTTPConnection(self.host)
        conn.request("PUT", canonicalized_resource, body, headers)
        response = conn.getresponse()
        body.close()
        if response.status is not 200:
            logging.error("S3 response: %d: %s\n%s" % (response.status,
                                          response.reason, response.read()))
        return ""

    def getm(self, files):
        """Gets multiple files, stored as a sequence of sequences, in much
        the same way as putm"""
        for localpath, hash, key in files:
            self.get(localpath, hash, key)

    def get(self, localpath, hash, key, event=None):
        """Gets the file which was stored earlier with this localpath, hash, and
           which returned this key from the put method."""
        date = time.strftime("%a, %d %b %Y %X GMT", time.gmtime())
        canonicalized_resource = "/%s/%s" % (self.bucket, hash)
        signature = get_signature("GET", "", "", date, "", canonicalized_resource, self.secret_key)
        headers = {"Date": date,
                   "authorization": "AWS %s:%s" % (self.id, signature)}
        conn = HTTPSConnection(self.host) if self.use_https else HTTPConnection(self.host)
        conn.request("GET", canonicalized_resource, "", headers)
        response = conn.getresponse()
        if response.status is not 200:
            logging.error("S3 response: %d: %s\n%s" % (response.status,
                                          response.reason, response.read()))
            return
        with open(localpath,'wb') as f:
            for chunk in iter(lambda: response.read(2**15), ''):
                f.write(chunk)
            f.close()

    def clone(self):
        """Provide a clone of this storage object so others can use it"""
        return deepcopy(self)

def get_signature(http_verb, content_md5, content_type, date,
                    canonicalized_headers, canonicalized_resource, secret_key):
    string_to_sign = "%s\n%s\n%s\n%s\n%s%s" % (http_verb, content_md5,
                                               content_type, date,
                                               canonicalized_headers,
                                               canonicalized_resource)
    sha_hmac = hmac.new(secret_key, string_to_sign, sha1)
    signature = sha_hmac.digest()
    return base64.b64encode(signature)

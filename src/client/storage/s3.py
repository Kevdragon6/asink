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
from hashlib import sha1, md5
import logging
import time
import base64
import hmac
import mimetypes
import urllib2

class S3Storage:
    """Provides an s3-based backing store. Based on the documentation available
    online at
    http://docs.amazonwebservices.com/AmazonS3/latest/dev/index.html?RESTAuthentication.html"""
    def __init__(self, host, bucket, id, secret_key):
        self.host = host
        self.bucket = bucket
        self.id = id
        self.secret_key = secret_key

    def put(self, localpath, hash, event=None):
        """Stores the file designated by localpath on the ssh server. Returns a
           string key the calling application should pass to get() to retrieve
           the file."""
        url = "https://%s.%s/%s" % (self.bucket, self.host, hash)
        content_type = "text/plain"
        try:
            content_type = mimetypes.guess_type(event.path)[0]
        except:
            pass
        content_length = os.stat(localpath).st_size
        date = time.strftime("%a, %d %b %Y %X GMT", time.gmtime())
        md5 = md5hash(localpath)
        canonicalized_resource = "/%s/%s" % (self.bucket, hash)

        signature = get_signature("PUT", md5, content_type, date, "", canonicalized_resource, self.secret_key)

        request = urllib2.Request(url, yield_bytes(localpath))
        request.add_header('Date', date)
        request.add_header('Content-Type', content_type)
        request.add_header('Content-Length', content_length)
        request.add_header('Authorization', "AWS %s:%s" % (self.id, signature))
        request.get_method = lambda: 'PUT'
        response = urllib2.urlopen(request)
        logging.info("S3 response"+response.read())
        return ""

    def get(self, localpath, hash, key, event=None):
        """Gets the file which was stored earlier with this localpath, hash, and
           which returned this key from the put method."""

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

def yield_bytes(filename):
    with open(filename,'rb') as f:                                                                    
        for chunk in iter(lambda: f.read(2**15), ''):
             yield chunk

def md5hash(filename):
    fn = md5()
    with open(filename,'rb') as f:                                                                    
        for chunk in iter(lambda: f.read(2**15), ''):
             fn.update(chunk)
    return fn.hexdigest()

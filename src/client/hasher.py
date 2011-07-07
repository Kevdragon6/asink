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

import hashlib

blocksize = 2**15 #seems to be the fastest chunk size on my laptop

def hash(filename, hashfns=[hashlib.sha256]):
    fns = []
    for f in hashfns:
        fns.append(f())
    with open(filename,'rb') as ifile:
        for chunk in iter(lambda: ifile.read(blocksize), ''):
            for f in fns:
                f.update(chunk)
    return [f.hexdigest() for f in fns]

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

#fixup python include path, so we can include other project directories
sys.path.append(os.path.join(os.getcwd(), "../"))

import yappi
from client.start import main

yappi.start(True)
try:
    main()
except:
    pass
for it in yappi.get_stats(yappi.SORTTYPE_TSUB,
                          yappi.SORTORDER_DESCENDING,
                          yappi.SHOW_ALL):
    print it
yappi.stop()

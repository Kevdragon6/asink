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

import json

from shared import events

def web(r):
    r.send_response(200)
    r.end_headers()
    r.wfile.write("Web interface not yet implemented, sorry!\n")

def api(r):
    data = None
    try:
        length = int(r.headers['Content-Length'])
        j = r.rfile.read(length)
        data = json.loads(j)
    except:
        r.send_response(400)
        r.end_headers()
        return

    for e in data:
        event = events.Event(0)
        event.fromlist(e)
        print event
    r.send_response(200)
    r.end_headers()
    r.wfile.write("API YAAAYA!\n")

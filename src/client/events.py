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

class EventType:
    #describe the change to the file
    UPDATE = 1 #used for create as well
    DELETE = 2
    #describe where this change originated
    LOCAL  = 4
    REMOTE = 8
    
class Event:
    type = EventType.UPDATE
    rev = 0   #revision number this corresponds to, 0 if local change only
    hash = "" #hex of sha hash
    time = 0  #unix timestamp
    path = "" #local path to file
    storagepath = "" #path or info related to storage
    permissions = "" #permissions of file as of this change

    def __init__(self, event_type):
        self.type = event_type
    def __str__(self):
        s = ""
        if self.type & EventType.UPDATE:
            s += "Update "
        else:
            s += "Delete "
        s += self.path
        s += " at " + str(self.time)
        if self.type & EventType.LOCAL:
            s += " (local)"
        else:
            s += " (remote)"
        return s

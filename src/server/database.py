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

import sqlite3

def cursor_generator(cursor):
    results = cursor.fetchmany()
    while results:
        for result in results:
            yield result
        results = cursor.fetchmany()

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("asink.db")
        self.cursor = self.conn.cursor()
        self.ensure_installed()
    def execute(self, query, args):
        self.cursor.execute(query, args)
        return cursor_generator(self.cursor)
    def commit(self):
        self.conn.commit()
    def rollback(self):
        self.conn.rollback()
    def close(self):
        self.conn.close()
    def ensure_installed(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files';")
        if self.cursor.fetchone() is None:
            self.cursor.execute("""CREATE TABLE files (
                rev INTEGER,
                user INTEGER,
                hash TEXT,
                modified INTEGER,
                localpath TEXT,
                storagepath TEXT,
                permissions INTEGER,
                action INTEGER,
                status INTEGER)""")
            #make index on rev and localpath
            self.cursor.execute("CREATE INDEX IF NOT EXISTS revidx on files (rev)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS pathidx on files (localpath)")

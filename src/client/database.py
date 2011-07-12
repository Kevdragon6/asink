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

from config import Config
import logging
import sqlite3

def cursor_generator(cursor):
    results = cursor.fetchmany()
    while results:
        for result in results:
            yield result
        results = cursor.fetchmany()

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config().get("core", "dbfile"))
        self.cursor = self.conn.cursor()
        self.ensure_installed()
    def execute(self, query, args):
        for i in range(1000):
            try:
                self.cursor.execute(query, args)
                self.commit()
                return cursor_generator(self.cursor)
            except sqlite3.OperationalError as e:
                if i is 9:
                    raise
                logging.error("sqlite3.OperationalError while running query:\n"
                              +query+" with args "+str(args))
                self.rollback()
                self.close()
                self.__init__()
    def commit(self):
        self.conn.commit()
    def rollback(self):
        self.conn.rollback()
    def close(self):
        self.conn.close()
    def ensure_installed(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events';")
        if self.cursor.fetchone() is None:
            self.cursor.execute("""CREATE TABLE events (
                rev INTEGER,
                user INTEGER,
                type INTEGER,
                hash TEXT,
                localpath TEXT,
                modified INTEGER,
                storagekey TEXT,
                permissions INTEGER)""")
            #make index on rev and localpath
            self.cursor.execute("CREATE INDEX IF NOT EXISTS revidx on events (rev)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS pathidx on events (localpath)")

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
import sqlite3

import constants
from config import Config

def main():
    config = Config(constants.configfile)
    #make sure directories exist
    if not os.path.isdir(constants.dotdir):
        os.mkdir(constants.dotdir)
    if not os.path.isdir(config.syncdir):
        os.mkdir(config.syncdir)

    #create database and table
    conn = sqlite3.connect(config.dbfile)
    c = conn.cursor()

    #create 'files' table if it doesn't already exist
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files';")
    if c.fetchone() is None: 
        c.execute("""CREATE TABLE files (
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
        c.execute("CREATE INDEX IF NOT EXISTS revidx on files (rev)")
        c.execute("CREATE INDEX IF NOT EXISTS pathidx on files (localpath)")

    config.write() #write the config back out, so that if it didn't exist, it does now

if __name__ == "__main__":
    main()

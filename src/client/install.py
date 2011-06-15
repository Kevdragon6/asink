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
from database import Database

def main():
    #make sure directories exist
    if not os.path.isdir(constants.dotdir):
        os.mkdir(constants.dotdir)
    cachedir = os.path.join(constants.dotdir, "cache")
    if not os.path.isdir(cachedir):
        os.mkdir(cachedir)
    syncdir = Config().get("core", "syncdir")
    if not os.path.isdir(syncdir):
        os.mkdir(syncdir)

    #create the database object so it will automatically create its database
    database = Database()

    Config().write() #write the config back out, so that if it didn't exist, it does now

if __name__ == "__main__":
    main()

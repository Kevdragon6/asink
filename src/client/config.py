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
import logging
import ConfigParser

import constants

class _Config:
    #name of config file backing this object
    config_filename = constants.configfile

    #options that will be read
    syncdir = os.path.join(constants.homedir, "Asink")
    dbfile = os.path.join(constants.dotdir, "fileinfo.db")
    server = "localhost"
    port = 8080

    def __init__(self):
        self.parser = ConfigParser.SafeConfigParser()
        read = self.parser.read(self.config_filename)
        if self.config_filename in read:
            self.parse()
        #assume defaults if file doesn't exist

    def parse(self):
        try:
            self.syncdir = self.parser.get('core', 'syncdir')
            self.dbfile = self.parser.get('core', 'dbfile')
            self.server = self.parser.get('core', 'server')
            self.port = self.parser.getint('core', 'port')
        except:
            logging.warning("Config file at "+self.config_filename+" improperly formatted. Using default config options.")

    def write(self, second_try = False):
        try:
            self.parser.set('core', 'syncdir', self.syncdir)
            self.parser.set('core', 'dbfile', self.dbfile)
            self.parser.set('core', 'server', self.server)
            self.parser.set('core', 'port', str(self.port))
        except:
            if not second_try:
                try:
                    self.parser.add_section('core')
                except ConfigParser.DuplicateSectionError:
                    pass
                self.write(True)
        with open(self.config_filename, 'wb') as configfile:
                self.parser.write(configfile)

#make Config class a singleton so we don't have a million instances of it
_config_singleton = _Config()
def Config():
    return _config_singleton

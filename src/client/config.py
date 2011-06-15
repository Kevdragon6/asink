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

defaults = {"core.syncdir" : os.path.join(constants.homedir, "Asink"),
            "core.dbfile" : os.path.join(constants.dotdir, "events.db"),
            "core.storagemethod" : "ssh",

            #Asink server options
            "server.host" : "localhost",
            "server.port" : 8080,

            #SSH-related options (only necessary if core.storagemethod is ssh)
            "ssh.host" : "localhost",
            "ssh.port" : 22,
            "ssh.username" : "asinkuser",
            "ssh.basepath" : "/opt/asink"
           }

class _Config:
    #name of config file backing this object
    config_filename = constants.configfile

    def __init__(self):
        self.parser = ConfigParser.SafeConfigParser()
        read = self.parser.read(self.config_filename)

    def write(self):
        with open(self.config_filename, 'wb') as configfile:
                self.parser.write(configfile)

    def get(self, section, option):
        try:
            return self.parser.get(section, option)
        except:
            wholeoption = section+"."+option
            if wholeoption in defaults:
                self.set(section, option, defaults[wholeoption]) #if it gets
                    #read, it must be important, so we should write it out to the
                    #config file for the user to change if they want
                return defaults[wholeoption]
            else:
                return None

    def set(self, section, option, value):
        try:
            self.parser.set(section, option, str(value))
        except:
            try:
                self.parser.add_section(section)
                self.parser.set(section, option, str(value))
            except ConfigParser.DuplicateSectionError:
                print "config.py: ConfigParser.DuplicateSectionError occurred. It shouldn't have."

#make Config class a singleton so we don't have a million instances of it
_config_singleton = _Config()
def Config():
    return _config_singleton

#!/usr/bin/env python

import os
import re

import argparse
import shlex

from model.setting import Setting
from helper import output
import environment


class Settings:

    __settings=[]

    def __init__(self):
        # Expand settings filename, so that ~ is the real users home path
        self.__SETTINGS_FILENAME=environment.TMUX_CSSH_CONFIG_FILENAME

        # Load settings
        self.load()
    # End def

    def load(self):
        # Clear list
        self.__settings=[]

        try:
            # Open file
            fileHandle=open(self.__SETTINGS_FILENAME, 'r')

            # Read file
            while True:
                line=fileHandle.readline()
                if not line: break;

                # Split/interpret line
                lineParts=re.match(r'^(.*?):(.*)$', line)

                if lineParts:
                    # Add new setting to list
                    settingObject=Setting()
                    settingObject.setKey(lineParts.group(1))
                    settingObject.setValue(lineParts.group(2))

                    self.__settings.append(settingObject)
                # End if
            # End while

            # Close file
            fileHandle.close()
        except IOError:
            output.error(self.__SETTINGS_FILENAME+' can\'t be opened/read.')
        # End try/except
    # End def

    def save(self):
        try:
            fileHandle=open(self.__SETTINGS_FILENAME, 'w')

            if fileHandle:
                for setting in self.__settings:
                    fileHandle.write(setting.getKey()+':'+setting.getValue()+os.linesep)
                # Close file

                fileHandle.close()
            # End if
        except IOError:
            output.error(self.__SETTINGS_FILENAME+' can\'t be opened/written.')
        # End if
    # End def

    def yieldSettings(self):
        for settingObject in self.__settings:
            yield settingObject
        # End for
    # End def

    def __getitem__(self, itemPos):
        if itemPos>=0 and itemPos<len(self.__settings):
            return self.__settings[itemPos]
        else:
            return None
        # End if
    # End def

    def __delitem__(self, itemPos):
        if itemPos>=0 and itemPos<len(self.__settings):
            del self.__settings[itemPos]

            self.save()
        # End if
    # End def

    def add(self, object):
        if object is not None:
            self.__settings.append(object)

            self.save()
        # End if
    # End def

    def __setitem__(self, key, value):
        if key>=0 and key<len(self.__settings):
            self.__settings[key]=value

            self.save()
        # End if
    # End def

    def __len__(self):
        return len(self.__settings)
    # End def

    def getParsedParametersFromSettingObject(self, settingPos=None, settingObject=None):
        if (settingPos is not None and settingPos>=0 and settingPos<len(self.__settings)) or \
                (settingObject is not None):
            # Get and initialize argument parser
            parser=argparse.ArgumentParser()
            # User
            parser.add_argument('-u', '--user', type=str, nargs=1, action='store', dest='user')
            # Certificate / Identity file
            parser.add_argument('-c', '--certificate', type=str, nargs=1, action='store', dest='certificateIdentity')
            parser.add_argument('-i', '--identity', type=str, nargs=1, action='store', dest='certificateIdentity')
            # SSH Server Connection String
            parser.add_argument('-sc', '--ssh-server-connect-string', type=str, nargs=1, action='append', dest='sshConnectString')
            # Additional ssh parameters
            parser.add_argument('-sa', '--ssh_args', type=str, nargs=1, action='store', dest='additionalSSHArgs')
            # TMUX Session name
            parser.add_argument('-ts', '--tmux-session-name', type=str, nargs=1, action='store', dest='tmuxSessionName')
            # Set epoch time
            parser.add_argument('-set', '--set-epoch-time', action='store_true', dest='setEpochTime')
            # New session
            parser.add_argument('-ns', '--new-session', action='store_true', dest='newSession')
            # Quiet mode
            parser.add_argument('-q', '--quiet', action='store_true', dest='quietMode')
            # SSH Connect String Filename
            parser.add_argument('-f', '--filename', type=str, nargs=1, action='append', dest='filename')
            # Config Setting
            parser.add_argument('-cs', '--config-setting', type=str, nargs=1, action='append', dest='configSetting')
            # Don't clusterize/synchronize panes
            parser.add_argument('-dc', '-ds', '--dont-clusterize', '--dont-synchronize', action='store_false', default=True, dest='synchronizePanes')

            # Other parameters go to -sc

            # Parse value of settings
            settingValueString=None

            # From setting pos
            if settingPos is not None:
                settingValueString=self.__settings[settingPos].getValue()
            # End if

            # From setting object
            if settingObject is not None:
                settingValueString=settingObject.getValue()
            # End if

            # Parse setting value
            args=None

            if settingValueString is not None:
                preArgs=shlex.split(settingValueString)

                # Walk throug all found/splitted parameters, see "workaround" below
                for i in range(0, len(preArgs)):
                    # Workaround, so that argparse don't try to interpret the -sa argument as tmux-cssh parameters
                    if i>0 and preArgs[i-1]=='-sa':
                        preArgs[i]=' '+preArgs[i]
                        continue
                    # End if
                # End for

                # Parser known and unknown arguments
                args, unknownArgs=parser.parse_known_args(preArgs)

                # Transfer unknown arguments, like tmux-cssh-help defines, to -sc-list
                if len(unknownArgs)>0:
                    # Create list
                    if args.sshConnectString is None:
                        args.sshConnectString=[]
                    # End if

                    # Transfer list
                    [ args.sshConnectString.append([x]) for x in unknownArgs ]
                # End if
            # End if

            return args
        else:
            return None
        # End if
    # End def

# End class
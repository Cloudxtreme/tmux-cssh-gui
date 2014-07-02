#!/usr/bin/env python

import os

import ConfigParser

import environment

class Config:

    __CONFIG_FILENAME = None

    SECTION_WINDOW = 'window'
    OPTION_WINDOW_SIZE_X = 'size-x'
    OPTION_WINDOW_SIZE_Y = 'size-y'
    OPTION_WINDOW_POSITION_X = 'position-x'
    OPTION_WINDOW_POSITION_Y = 'position-y'
    OPTION_WINDOW_START_MINIMIZED ='start-minimized'

    SECTION_TERMINAL = 'terminal-emulator'
    OPTION_TERMINAL_COMMAND = 'cmnd'
    OPTION_TERMINAL_PARAMETER = 'params'

    def __init__(self):
        # Expand settings filename, so that ~ is the real users home path
        self.__CONFIG_FILENAME=environment.APP_CONFIG_FILE
        self.__CONFIG_FILENAME=os.path.expanduser(self.__CONFIG_FILENAME)

        # Init config-parser
        self.__configParser=ConfigParser.ConfigParser()
        # Read config file
        self.__configParser.read(self.__CONFIG_FILENAME)
    # End def

    def __save(self):
        fh=open(self.__CONFIG_FILENAME, 'w')
        self.__configParser.write(fh)
        fh.close()
    # End def

    def get(self, section, option):
        cp=self.__configParser

        if cp.has_section(section) and cp.has_option(section, option):
            return cp.get(section, option)
        else:
            return None
        # End if
    # End def

    def set(self, section, option, value):
        cp=self.__configParser

        # Create section, if it not exist
        if not cp.has_section(section):
            cp.add_section(section)
        # End if

        # Set value to section/option-pair
        cp.set(section, option, value)

        # Save config
        self.__save()
    # End def

    def getBool(self, section, option):
        cp=self.__configParser

        if cp.has_section(section) and cp.has_option(section, option):
            return cp.getboolean(section, option)
        else:
            return None
        # End if
    # End def

# End class
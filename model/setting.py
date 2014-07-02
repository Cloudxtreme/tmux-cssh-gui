#!/usr/bin/env python

class Setting:

    def __init__(self, key=None, value=None):
        self.__key=key
        self.__value=value
    # End def

    def setKey(self, key):
        self.__key=key
    # End def

    def getKey(self):
        return self.__key
    # End def

    def setValue(self, value):
        self.__value=value
    # End def

    def getValue(self):
        return self.__value
    # End def

# End class
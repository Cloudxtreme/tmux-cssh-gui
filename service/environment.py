#!/usr/bin/env python

import os

# Name of application
APP_NAME = 'TMUX-CSSH GUI'

# Version of application
APP_VERSION = '1.0.1-0'

# App's website
APP_WEBSITE = 'https://github.com/dennishafemann/tmux-cssh-gui'

# App's license
APP_LICENSE_TEXT = APP_NAME+' is under Apache 2 license. Take a look on the webpages.'

# App's config file
APP_CONFIG_FILE = os.path.expanduser('~/.tmux-cssh-gui')

# Relative directory path for glade-gui-files
NAME_GLADE_XML_PATH=os.path.abspath(os.path.dirname(__file__))+'/../glade/'

# TMUX-CSSH config filename
TMUX_CSSH_CONFIG_FILENAME=os.path.expanduser('~/.tmux-cssh')

# TMUX-CSSH execute command
TMUX_CSSH_COMMAND = '/usr/local/bin/tmux-cssh'

# Terminal-Emulator default values
TERMINAL_EMULATOR_CMND = '/usr/bin/x-terminal-emulator'
TERMINAL_EMULATOR_PARAMETER = '-e'

# Author's name
AUTHOR_NAME = ['Dennis Hafemann']

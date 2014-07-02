#!/usr/bin/env python

import gtk, gtk.glade

from service import environment

class EntryDlg:

    # Constant: glade-xml-path
    __NAME_MAIN_WINDOW_GLADE_XML = 'entry_dialog.glade'

    def __init__(self, labeltext="", defaultvalue="", parentWindow=None):
        # Read glade file
        self.__gladeXML=gtk.glade.XML(environment.NAME_GLADE_XML_PATH+self.__NAME_MAIN_WINDOW_GLADE_XML)

        # Connect signals to self
        self.__gladeXML.signal_autoconnect(self)

        # Get window object
        self.__window=self.__gladeXML.get_widget("windowEntryDialog")

        # Titel
        #self.__entryDlg.set_title(vTitle.encode("utf8"))

        # Set label text
        self.__gladeXML.get_widget("lDescription").set_text(labeltext)

        # Button
        self.__bOk=self.__gladeXML.get_widget("bOk")
        self.__bOk.set_sensitive(True if defaultvalue!="" else False)

        self.__bCancel=self.__gladeXML.get_widget("bCancel")

        # Set default value
        self.__fEntry=self.__gladeXML.get_widget("fEntry")
        self.__fEntry.set_text(defaultvalue)
    # End def

    def Run(self):
        rtn=self.__fEntry.get_text() if self.__window.run()==1 else None
        self.destroy()
        return rtn
    # End def

    def destroy(self):
        self.__window.destroy()
        del self.__window
    # End def

    def on_fEntry_changed(self, *params):
        text=self.__fEntry.get_text()
        self.__bOk.set_sensitive(True if text!="" else False)
    # End def

    def on_bOk_clicked(self, view):
        self.__window.response(1)
    # End def

    def on_bCancel_clicked(self, view):
        self.__window.response(2)
    # End def

# End class
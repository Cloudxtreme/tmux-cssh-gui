#!/usr/bin/env python


import gtk
import gtk.glade
import subprocess
import shlex

from service import environment
from model.setting import Setting
from service.settings import Settings
from service.config import Config
from gui.entrydlg import EntryDlg

class TMUXCSSHGUI:

    # Constant: Name of main window
    __NAME_MAIN_WINDOW_GLADE_XML = 'main.glade'
    __NAME_MAIN_WINDOW = 'windowMain'
    __NAME_BEDITSETTING = 'bEditSetting'
    __NAME_BRUNSETTING = 'bRunSetting'
    __NAME_BREMOVESETTING = 'bRemoveSetting'
    __NAME_NONE_SELECTED_LABEL = 'lChooseInfo'
    __NAME_SETTINGS_FORM = 'vboxSettingsForm'
    __NAME_VBOX_SC = 'vboxSC'
    __NAME_VBOX_FILENAME = 'vboxFilename'
    __NAME_VBOX_CONFIGSETTINGS = 'vboxConfigSettings'

    # Constant: Name of treeview list holding the settings
    __NAME_TREEVIEW_SETTINGS_LIST = 'treeviewSettings'

    __windowStateMaximized=False

    def __init__(self):
        """Constructor"""

        # Initialize configs
        self.__config=Config()

        # Read glade file
        self.__gladeXML=gtk.glade.XML(environment.NAME_GLADE_XML_PATH+self.__NAME_MAIN_WINDOW_GLADE_XML)

        # Connect signals to self
        self.__gladeXML.signal_autoconnect(self)

        # Get treeview list for settings
        self.__treeviewSettings=self.__gladeXML.get_widget(self.__NAME_TREEVIEW_SETTINGS_LIST)

        # Create render for displaying the text
        renderer=gtk.CellRendererText()

        # Create column
        column=gtk.TreeViewColumn('Settings name/key', renderer)
        column.set_attributes(renderer, text=0)

        # Add column to list
        self.__treeviewSettings.append_column(column)

        # Create list
        self.__liststoreSettings=gtk.ListStore(str)

        # Add list to treeview list
        self.__treeviewSettings.set_model(self.__liststoreSettings)

        # Show main window
        self.__windowMain=self.__gladeXML.get_widget(self.__NAME_MAIN_WINDOW)

        # Size
        windowSizeX=self.__config.get(Config.SECTION_WINDOW, Config.OPTION_WINDOW_SIZE_X)
        windowSizeY=self.__config.get(Config.SECTION_WINDOW, Config.OPTION_WINDOW_SIZE_Y)

        if  windowSizeX is not None and windowSizeY is not None:
            self.__windowMain.resize(int(windowSizeX), (int(windowSizeY)))
        # End if

        # Position
        windowPositionX=self.__config.get(Config.SECTION_WINDOW, Config.OPTION_WINDOW_POSITION_X)
        windowPositionY=self.__config.get(Config.SECTION_WINDOW, Config.OPTION_WINDOW_POSITION_Y)

        if  windowPositionX is not None and windowPositionY is not None:
            self.__windowMain.move(int(windowPositionX), int(windowPositionY))
        # End if

        # Check, if window should be started minimized
        startMinimized=self.__config.getBool(Config.SECTION_WINDOW, Config.OPTION_WINDOW_START_MINIMIZED)

        if startMinimized is None or not startMinimized:
            # Set default value
            self.__config.set(Config.SECTION_WINDOW, Config.OPTION_WINDOW_START_MINIMIZED, False)
            # Show window
            self.__windowMain.show()
        # End if

        # Get several gui components
        # Menu items
        self.__miEdit=self.__gladeXML.get_widget('menuItemEdit')
        self.__miRemove=self.__gladeXML.get_widget('menuItemRemove')

        # Settings-list button area
        self.__bEditSetting=self.__gladeXML.get_widget(self.__NAME_BEDITSETTING)
        self.__bRemoveSetting=self.__gladeXML.get_widget(self.__NAME_BREMOVESETTING)
        self.__bRunSetting=self.__gladeXML.get_widget(self.__NAME_BRUNSETTING)

        # Form area
        self.__noneSelectedLabel=self.__gladeXML.get_widget(self.__NAME_NONE_SELECTED_LABEL)
        self.__settingsForm=self.__gladeXML.get_widget(self.__NAME_SETTINGS_FORM)

        # Boxes for server connection string -sc
        self.__vboxSC=self.__gladeXML.get_widget(self.__NAME_VBOX_SC)
        self.__vboxFilename=self.__gladeXML.get_widget(self.__NAME_VBOX_FILENAME)
        self.__vboxConfigSettings=self.__gladeXML.get_widget(self.__NAME_VBOX_CONFIGSETTINGS)

        # Create and setup systray-icon/.menu
        self.__systrayIcon=gtk.StatusIcon()
        self.__systrayIcon.set_from_stock(gtk.STOCK_ABOUT)
        self.__systrayIcon.connect('activate', self.on_systrayIcon_activate)
        self.__systrayIcon.connect('popup-menu', self.on_systrayIcon_popup_menu)
        self.__systrayIcon.set_title(environment.APP_NAME)
        self.__systrayIcon.set_tooltip(environment.APP_NAME)

        # Load settings
        self.__loadSettings()
    # End def

    def __loadSettings(self):
        # Initialize settings-service-object
        self.__serviceSettings=Settings()

        # Update settings list in gui
        self.__updateGUISettingsList()
    # End def

    def __updateGUISettingsList(self):
        # Reset internal selection
        self.__currentSelectedSetting=None

        # Clear list
        self.__liststoreSettings.clear()

        # Insert items
        for settingEntry in self.__serviceSettings.yieldSettings():
            self.__liststoreSettings.append([settingEntry.getKey()])
        # End for
    # End def

    def __updateGUI(self):
        # Update list
        self.__updateGUISettingsList()

        # Form area
        self.__switchFormVisibility()
    # End def

    def on_destroy(self, object):
        # Call quit
        self.__quit()
    # End def

    def __quit(self):
        # Actually quit
        gtk.main_quit()
    # End def

    def __runSetting(self, position):
        cmnd=self.__config.get(Config.SECTION_TERMINAL, Config.OPTION_TERMINAL_COMMAND)
        params=self.__config.get(Config.SECTION_TERMINAL, Config.OPTION_TERMINAL_PARAMETER)

        if cmnd is None and params is None:
            cmnd=environment.TERMINAL_EMULATOR_CMND
            self.__config.set(Config.SECTION_TERMINAL, Config.OPTION_TERMINAL_COMMAND, cmnd)

            params=environment.TERMINAL_EMULATOR_PARAMETER
            self.__config.set(Config.SECTION_TERMINAL, Config.OPTION_TERMINAL_PARAMETER, params)

            dlg=gtk.MessageDialog(self.__windowMain, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                u'Terminal-Emulator-Command not set yet. Edit the config-file ('+environment.APP_CONFIG_FILE+'). Setting default.')
            dlg.run()
            dlg.destroy()
        # End if

        # Command and parameters available
        if cmnd and params:
            setting=self.__serviceSettings[position];

            subprocess.Popen(cmnd+' '+params+' "'+environment.TMUX_CSSH_COMMAND+' '+setting.getValue()+'" ', shell=True)
        # End if

    # End def

    def on_treeviewSettings_cursor_changed(self, treeviewObject):
        self.__settingSelected=True

        # Get selected rows from treeview object
        selectedRows=treeviewObject.get_selection().get_selected_rows()[1]

        # Clear current settings selection
        self.__currentSelectedSetting=None

        if len(selectedRows)>0:
            # Get selected row number for settings-object
            selectedRow=selectedRows[0][0]

            # Fill form
            if selectedRow>=0 and selectedRow<len(self.__serviceSettings):
                self.__currentSelectedSetting=selectedRow
                self.__showFormFromSettingsObject(self.__serviceSettings[selectedRow])
            else:
                self.__showFormFromSettingsObject(None)
            # End if
        # End if

        self.__settingSelected=False
    # End def

    def on_treeviewSettings_row_activated(self, *params):
        self.__runSetting(self.__currentSelectedSetting)
    # End def

    def __switchFormVisibility(self):
        # Setting activated in list
        if self.__currentSelectedSetting is None:
            # Menu items
            self.__miEdit.set_sensitive(False)
            self.__miRemove.set_sensitive(False)

            # Button area in Settings-List
            self.__bEditSetting.set_sensitive(False)
            self.__bRemoveSetting.set_sensitive(False)
            self.__bRunSetting.set_sensitive(False)

            # Form area
            self.__noneSelectedLabel.show()
            self.__settingsForm.hide()
        # No setting activated
        else:
            # Menu items
            self.__miEdit.set_sensitive(True)
            self.__miRemove.set_sensitive(True)

            # Button area in Settings-List
            self.__bEditSetting.set_sensitive(True)
            self.__bRemoveSetting.set_sensitive(True)
            self.__bRunSetting.set_sensitive(True)

            # Form area
            self.__noneSelectedLabel.hide()
            self.__settingsForm.show()
        # End if
    # End def

    def __showFormFromSettingsObject(self, settingObject):
        # Switch form visibility
        self.__switchFormVisibility()

        # Get array with parsed settings from setting object
        settingsFromObject=self.__serviceSettings.getParsedParametersFromSettingObject(settingObject=settingObject)

        # Add user to form
        fUser=self.__gladeXML.get_widget('fUser')
        fUser.set_text(settingsFromObject.user[0].strip() if settingsFromObject.user is not None else '')

        # Add certificate/identity to form
        fIdentity=self.__gladeXML.get_widget('fCertificateIdentity')
        if fIdentity.get_filename() is not None:
            fIdentity.unselect_filename(fIdentity.get_filename())
        # End if

        if settingsFromObject.certificateIdentity is not None:
            fIdentity.set_filename(settingsFromObject.certificateIdentity[0])
        # End if

        # Add server connection strings to form
        # Remove old
        for vboxSCChildren in self.__vboxSC.get_children():
            self.__vboxSC.remove(vboxSCChildren)
        # End for

        # Add new
        if settingsFromObject.sshConnectString is not None:
            for serverConnectionString in settingsFromObject.sshConnectString:
                self.__addSCItem(serverConnectionString[0])
            # End for
        # End if

        # Add additional ssh args to form
        fAdditionalSSHArguments=self.__gladeXML.get_widget('fAdditionalSSHArguments')
        fAdditionalSSHArguments.set_text(settingsFromObject.additionalSSHArgs[0].strip() if settingsFromObject.additionalSSHArgs is not None else '')

        # Add TMUX Session name to form
        fTMUXSessionName=self.__gladeXML.get_widget('fTMUXSessionName')
        fTMUXSessionName.set_text(settingsFromObject.tmuxSessionName[0].strip() if settingsFromObject.tmuxSessionName is not None else '')

        # Add Epoch time to form
        cbSetEpochTime=self.__gladeXML.get_widget('cbSetEpochTime')
        cbSetEpochTime.set_active(settingsFromObject.setEpochTime)

        # Add new session to form
        cbNewSession=self.__gladeXML.get_widget('cbNewSession')
        cbNewSession.set_active(settingsFromObject.newSession)

        # Add quiet mode to form
        cbQuietMode=self.__gladeXML.get_widget('cbQuietMode')
        cbQuietMode.set_active(settingsFromObject.quietMode)

        # Add filenames to form
        # Remove old
        for vboxFilenameChildren in self.__vboxFilename.get_children():
            self.__vboxFilename.remove(vboxFilenameChildren)
        # End for

        # Add new
        if settingsFromObject.filename is not None:
            for filename in settingsFromObject.filename:
                self.__addFilenameItem(filename[0])
            # End for
        # End if

        # Add config settings to form
        # Remove old
        for vboxConfigSettingsChildren in self.__vboxConfigSettings.get_children():
            self.__vboxConfigSettings.remove(vboxConfigSettingsChildren)
        # End for

        # Add new
        if settingsFromObject.configSetting is not None:
            for configSetting in settingsFromObject.configSetting:
                self.__addConfigSettingItem(configSetting[0])
            # End for
        # End if
    # End def

    def __saveFormData(self):
        if not self.__settingSelected and self.__currentSelectedSetting is not None:
            # Get current setting
            setting=self.__serviceSettings[self.__currentSelectedSetting]

            # Gather settings from form
            valueArray=[]

            # Set epoch time
            f=self.__gladeXML.get_widget('cbSetEpochTime')
            if f.get_active(): valueArray.append('-set')

            # New session
            f=self.__gladeXML.get_widget('cbNewSession')
            if f.get_active(): valueArray.append('-ns')

            # Quiet mode
            f=self.__gladeXML.get_widget('cbQuietMode')
            if f.get_active(): valueArray.append('-q')

            # TMUX Session name
            f=self.__gladeXML.get_widget('fTMUXSessionName')
            if f.get_text().strip(): valueArray.append('-ts "'+f.get_text().strip()+'"')

            # SSH user name
            f=self.__gladeXML.get_widget('fUser')
            if f.get_text().strip(): valueArray.append('-u "'+f.get_text().strip()+'"')

            # Certificate / Identity
            f=self.__gladeXML.get_widget('fCertificateIdentity')
            if f.get_filename() is not None: valueArray.append('-c "'+f.get_filename()+'"')

            # Additional SSH arguments
            f=self.__gladeXML.get_widget('fAdditionalSSHArguments')
            if f.get_text().strip(): valueArray.append('-sa "'+f.get_text().strip()+'"')

            # Server connection strings, -sc
            self.__addValuesFromVBox(valueArray, self.__vboxSC, '-sc')

            # Filenames with server connection strings, -f
            self.__addValuesFromVBox(valueArray, self.__vboxFilename, '-f')

            # Config settings -cs
            self.__addValuesFromVBox(valueArray, self.__vboxConfigSettings, '-cs')

            # Store to settings
            setting.setValue(' '.join(valueArray))
            self.__serviceSettings[self.__currentSelectedSetting]=setting

            # Save settings
            # already saved with [...]-__setitem__
            #self.__serviceSettings.save()
        # End if
    # End def

    def __addValuesFromVBox(self, valueArray, vbox, parameterShortcut):
        # Walk through all hbox children
        for childHBOX in vbox.get_children():
            # Get HBOX children
            childHBOXChildren=childHBOX.get_children()

            if len(childHBOXChildren)>0:
                # Get second child of hbox, for it's the actually value
                f=childHBOXChildren[1]
                # Entry field
                if type(f)==gtk.Entry and f.get_text().strip(): valueArray.append(parameterShortcut+' "'+f.get_text().strip()+'"')
                # FileChooseButton
                if type(f)==gtk.FileChooserButton and f.get_filename() is not None: valueArray.append(parameterShortcut+' "'+f.get_filename()+'"')
                # Combobox field
                if type(f)==gtk.ComboBoxEntry and f.get_active_text().strip(): valueArray.append(parameterShortcut+' "'+f.get_active_text().strip()+'"')
            # End if
        # End for
    # End def

    def on_bAddSetting_clicked(self, view):
        settingName=EntryDlg(labeltext="Insert the name of the new setting:").Run()

        # Not empty, add config setting
        if settingName and settingName is not None:
            # Create and add setting
            setting=Setting()
            setting.setKey(settingName)
            setting.setValue('')

            self.__serviceSettings.add(setting)

            # Refresh list
            self.__updateGUI()

            # Set new item as selected
            self.__treeviewSettings.set_cursor(len(self.__liststoreSettings)-1)
        # End if
    # End def

    def on_bEditSetting_clicked(self, view):
        # Get setting
        setting=self.__serviceSettings[self.__currentSelectedSetting];

        dlg=EntryDlg(labeltext="Insert the new name of the setting:", defaultvalue=setting.getKey(), parentWindow=self.__windowMain)
        settingName=dlg.Run()
        del dlg

        # Not empty, add config setting
        if settingName and settingName is not None:
            # Update setting
            setting.setKey(settingName)

            self.__serviceSettings[self.__currentSelectedSetting]=setting

            # Refresh list
            self.__updateGUI()
        # End if
    # End def

    def on_bRemoveSetting_clicked(self, view):
        # Get setting
        setting=self.__serviceSettings[self.__currentSelectedSetting];

        # Create and display confirm dialog
        dlg=gtk.MessageDialog(self.__windowMain, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, u'Do you want to remove the config setting \''+setting.getKey()+'\' ?')
        response=dlg.run()
        dlg.destroy()

        # Ok, delete setting
        if response==gtk.RESPONSE_OK:
            # Delete
            del self.__serviceSettings[self.__currentSelectedSetting]

            # Refresh list
            self.__updateGUI()
        # End if
    # End def

    def on_bRunSetting_clicked(self, view):
        self.__runSetting(self.__currentSelectedSetting)
    # End def

    def __addSCItem(self, value=""):
        # Create new Hbox
        hbox=gtk.HBox(False, 5)

        # Add label to hbox
        lLabel=gtk.Label('-sc')
        lLabel.set_property('width-request', 50)
        lLabel.set_property('xalign', 0)
        lLabel.show()
        hbox.pack_start(lLabel, False)

        # Add entry field to hbox
        fEntry=gtk.Entry()
        fEntry.set_text(value)
        fEntry.connect('focus-out-event', self.on_formitem_changed)
        fEntry.show()
        hbox.pack_start(fEntry)

        # Add remove button to hbox
        bRemove=gtk.Button('X')
        bRemove.connect('clicked', self.on_remove_item, self.__vboxSC, hbox)
        bRemove.show();
        hbox.pack_start(bRemove, False)

        # Show hbox
        hbox.show()

        self.__vboxSC.add(hbox)

        # Focus entry field
        if not value: fEntry.grab_focus()
    # End def

    def on_bAddSC_clicked(self, view):
        self.__addSCItem()
    # End def

    def on_remove_item(self, view, *data):
        # Remove hbox from vbox
        if len(data)>0:
            vbox=data[0]
            hbox=data[1]

            vbox.remove(hbox)

            self.__saveFormData()
        # End if
    # End def

    def on_formitem_changed(self, *params):
        if not self.__settingSelected:
            self.__saveFormData()
        # End if
    # End def

    def __addFilenameItem(self, value=''):
        # Create new hbox
        hbox=gtk.HBox(False, 5)

        # Add label to hbox
        lLabel=gtk.Label('-f')
        lLabel.set_property('width-request', 50)
        lLabel.set_property('xalign', 0)
        lLabel.show()
        hbox.pack_start(lLabel, False)

        # Add entry field to hbox
        fFilename=gtk.FileChooserButton('File for -sc items')
        fFilename.set_filename(value)
        fFilename.connect('file-set', self.on_formitem_changed)
        fFilename.show()
        hbox.pack_start(fFilename)

        # Add remove button to hbox
        bRemove=gtk.Button('X')
        bRemove.connect('clicked', self.on_remove_item, self.__vboxFilename, hbox)
        bRemove.show();
        hbox.pack_start(bRemove, False)

        # Show hbox
        hbox.show()

        self.__vboxFilename.add(hbox)

        # Focus file field
        if not value: fFilename.grab_focus()
    # End def

    def on_bAddFilename_clicked(self, view):
        self.__addFilenameItem()
    # End def

    def __addConfigSettingItem(self, value=''):
        # Create new hbox
        hbox=gtk.HBox(False, 5)

        # Add label to hbox
        lLabel=gtk.Label('-cs')
        lLabel.set_property('width-request', 50)
        lLabel.set_property('xalign', 0)
        lLabel.show()
        hbox.pack_start(lLabel, False)

        # Add entry field to hbox
        cbConfigSettings=gtk.combo_box_entry_new_text()
        cbConfigSettings.append_text('')
        cbConfigSettings.set_active(0)

        # Fill with available settings
        counter=1
        for setting in self.__serviceSettings.yieldSettings():
            cbConfigSettings.append_text(setting.getKey())

            # Activate entry
            if setting.getKey()==value:
                cbConfigSettings.set_active(counter)
            # End f

            counter=counter+1
        # End for

        cbConfigSettings.connect('changed', self.on_formitem_changed)
        cbConfigSettings.connect('focus-out-event', self.on_formitem_changed)
        cbConfigSettings.show()
        hbox.pack_start(cbConfigSettings)

        # Add remove button to hbox
        bRemove=gtk.Button('X')
        bRemove.connect('clicked', self.on_remove_item, self.__vboxConfigSettings, hbox)
        bRemove.show();
        hbox.pack_start(bRemove, False)

        # Show hbox
        hbox.show()

        self.__vboxConfigSettings.add(hbox)

        # Focus entry field
        if not value: cbConfigSettings.grab_focus()
    # End def

    def on_bAddConfigSetting_clicked(self, view):
        self.__addConfigSettingItem()
    # End def

    def on_windowMain_window_state_event(self, view, event):
        self.__windowStateMaximized=(view.get_window().get_state() & gtk.gdk.WINDOW_STATE_MAXIMIZED)==gtk.gdk.WINDOW_STATE_MAXIMIZED
    # End def

    def on_windowMain_check_resize_event(self, *params):
        # Save size
        size=self.__windowMain.get_size()
        self.__config.set(Config.SECTION_WINDOW, Config.OPTION_WINDOW_SIZE_X, size[0])
        self.__config.set(Config.SECTION_WINDOW, Config.OPTION_WINDOW_SIZE_Y, size[1])

        # Save position
        position=self.__windowMain.get_position()
        self.__config.set(Config.SECTION_WINDOW, Config.OPTION_WINDOW_POSITION_X, position[0])
        self.__config.set(Config.SECTION_WINDOW, Config.OPTION_WINDOW_POSITION_Y, position[1])
    # End def

    def on_menuItemAdd_activate(self, view):
        self.on_bAddSetting_clicked(None)
    # End def

    def on_menuItemEdit_activate(self, view):
        self.on_bEditSetting_clicked(None)
    # End def

    def on_menuItemRemove_activate(self, view):
        self.on_bRemoveSetting_clicked(None)
    # End def

    def on_menuItemQuit_activate(self, view):
        self.__quit()
    # End def

    def on_menuItemAbout_activate(self, view):
        dlg=gtk.AboutDialog()
        dlg.set_name(environment.APP_NAME)
        dlg.set_version(environment.APP_VERSION)
        dlg.set_website(environment.APP_WEBSITE)
        dlg.set_authors(environment.AUTHOR_NAME)
        dlg.set_license(environment.APP_LICENSE_TEXT)
        dlg.run()
        dlg.destroy()
        del dlg
    # End def

    def on_systrayIcon_activate(self, icon):
        menu=gtk.Menu()

        for i in range(0, len(self.__serviceSettings)):
            # Get setting object
            settingEntry=self.__serviceSettings[i]

            # Create and add menu item
            item=gtk.MenuItem(settingEntry.getKey())
            item.set_use_underline(False)
            item.connect('activate', self.on_systrayIcon_setting_activate, i)
            item.show()

            menu.append(item)
        # End for

        menu.popup(None, None, None, 0, 0, self.__systrayIcon)
    # End def

    def on_systrayIcon_popup_menu(self, icon, eventButton, eventTime):
        menu=self.__gladeXML.get_widget('popmenuSystray')
        menu.popup(None, None, None, eventButton, eventTime, self.__systrayIcon)
    # End def

    def on_systrayIcon_setting_activate(self, view, *params):
        self.__runSetting(params[0])
    # End def

    def on_menuitemShowHideMainwindow_activate(self, view):
        if self.__windowMain.props.visible:
            self.__windowMain.hide()
        else:
            self.__windowMain.show()
        # End if

        self.__config.set(Config.SECTION_WINDOW, Config.OPTION_WINDOW_START_MINIMIZED, not self.__windowMain.props.visible)
    # End def

    def on_bClearCertificateIdentity_clicked(self, view):
        fIdentity=self.__gladeXML.get_widget('fCertificateIdentity')

        if fIdentity.get_filename() is not None:
            fIdentity.unselect_filename(fIdentity.get_filename())
            self.__saveFormData()
        # End if
    # End def

# End class
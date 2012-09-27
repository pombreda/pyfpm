#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
#
#                   Outils - tools.py
#
# Commencé le : 02 septembre 2012
#
# TODO : Faire une fonction pour remplir une combobox
#
########################################################################
#
# Copyright (C) gaetan gourdin 2011 <bouleetbil@frogdev.info>
#
# pyfpm is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfpm is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK not found.")

import os, sys, codecs

from string import strip
from ConfigParser import SafeConfigParser

import pacmang2.libpacman
from pacmang2.libpacman import *

#can quit program with ctrl-C
import signal
signal.signal(signal.SIGINT,signal.SIG_DFL)

#global
#change it for 0 before release a new tarball
devel_mode=1
homedir = os.path.expanduser('~')
fileconfig=homedir+"/.pyfpm"

if devel_mode==1:
    UI_PYFPM = "pyfpm.ui"
    UI_PYFPMCONF = "pyfpm-configuration.ui"
    LOGO = "data/logo.png"
    UI_SPLASH = "splash.ui"
    UI_PYFUN = "pyfun.ui"
    UI_PYINST = "pyfpminstall.ui"
    PYFPM_INST = "pyfpminstall.py"
    PYFPM_FUN = "pyfun.py"
    PYFPMCONF = "pyfpm-configuration.py"
    PICTURE_NOT_AVAILABLE = "data/screenshot_not_available.png"
    #for enable some trace
    pacmang2.libpacman.printconsole=1
    pacmang2.libpacman.debug=0
else:
    UI_PYFPM = "/usr/share/pyfpm/ui/pyfpm.ui"
    UI_SPLASH = "/usr/share/pyfpm/ui/splash.ui"
    UI_PYFUN ="/usr/local/share/pyfpm/ui/pyfun.ui"
    UI_PYINST= "/usr/share/pyfpm/pyfpminstall.py"
    PYFPM_FUN= "/usr/share/pyfpm/pyfun.py"
    PYFPM_INST="/usr/share/pyfpm/pyfpminstall.py"
    PYFPMCONF="/usr/share/pyfpm/pyfpm-configuration.py"
    UI_PYFPMCONF = "/usr/share/pyfpm/ui/pyfpm-configuration.ui"
    PICTURE_NOT_AVAILABLE="/usr/share/pyfpm/screenshot_not_available.png"


def draw():
    try :
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
            print_debug("draw gdk")
        #Delaying 100ms until the next iteration
        import time
        time.sleep(0.1)
    except:
        e = sys.exc_info()[1]
        print "window closed"
        print e

def check_user():
    if not os.geteuid()==0:
        return 0
    return 1

def print_info(text):
    dialog=Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, text)
    dialog.run()
    dialog.destroy()

def print_question(text):
    bo_ok=0
    dialog=Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, text)
    result=dialog.run()
    if result==Gtk.ResponseType.YES:
        bo_ok=1
    dialog.destroy()
    return bo_ok

def sysexec(cmd):
    os.system(cmd)

class configuration:
    def Exist(self):
        if os.path.exists("pyfpm.config") == False:
            result = self.Write('en','gksu','0')
            if result == False:
                print "pyFPM have not write the conf file ..."

    def Read(self,option):
        config = SafeConfigParser()
        self.Exist()
        config.read("pyfpm.config")
        return config.get("pyfpm", option)

    def Write(self,lang,command,offline):
        try :
            config = open("pyfpm.config", "w")
            # FIXME : Ecriture du fichier de conf pas optimisée
            config.write("[pyfpm]\nlang = " + str(lang) + "\nsu_command = " + str(command) + "\noffline = " + str(offline) + "\n")
            config.close()
            return True
        except:
            return False

class pypacmang2:
    def initPacman(self):
        #init pacman
        pacman_init()
        pacman_init_database()
        pacman_register_all_database()

    def pacman_finally(self):
        pacman_finally()

    def listFindElement(self,array,element):
        bo_find=0
        for el in array :
            if element==el :
                bo_find=1
                break
        return bo_find

    def PacmanGetGrp(self):
        db=db_list[0]
        tab_GRP=[]
        for db in db_list :
            i=pacman_db_getgrpcache(db)
            while i != 0:
                grp = pacman_list_getdata(i)
                if self.listFindElement(tab_GRP,pointer_to_string(grp))==0:
                    tab_GRP.append(pointer_to_string(grp))
                i=pacman_list_next(i)
        tab_GRP.sort()
        return tab_GRP

    def GetPkgFromGrp(self,groupname):
        tab_pkgs=[]
        for db in db_list:
            pm_group = pacman_db_readgrp (db, groupname)
            i = pacman_grp_getinfo (pm_group, PM_GRP_PKGNAMES)
            while i != 0:
                pkg = pacman_db_readpkg (db, pacman_list_getdata(i))
                if self.listFindElement(tab_pkgs,pkg)==0:
                    tab_pkgs.append(pkg)
                i=pacman_list_next(i)
        tab_pkgs.sort()
        return tab_pkgs

class divers():
    def getATrad(sef, word):
        """
        Get a traduction from the *.ini file
        """
        config = configuration()
        lang = config.Read("lang")
        try:
            trad = SafeConfigParser()
            trad.read("lang/" + lang + ".ini")

            return trad.get("traduction", word)
        except:
            return word

    def isUTF8(self, text):
        try:
            text = unicode(text, 'UTF-8', 'strict')
            return True
        except UnicodeDecodeError:
            return False

    def inList(self, liste, name):
        exist = 0
        for row in liste:
            if name == row:
                exist = row
                break
        return exist

    def countList(self, liste):
        count = 0
        for row in liste:
            count += 1
        return count

    def fillCommand(self, combobox):
        # Default applications
        config = configuration()
        configCommand = config.Read("su_command")
        default = ['gksu', 'kdsu']
        indice = 0

        if self.inList(default, configCommand) == 0:
            default.append(configCommand)
        for row in default:
            if os.path.exists("/usr/bin/" + row) == True:
                combobox.append_text(row)
            # FIXME : Ne marche qu'avec l'indice 0
            if configCommand == row:
                combobox.set_active(indice)
            indice += 1

    def information(self, title, text):
        """
        An information window
        """
        message = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, text)
        message.set_title(title)
        message.set_default_response(gtk.RESPONSE_OK)
        message.run()
        message.destroy()

class packages:
    def progressInstall(*args):
        """
        Change the progress bar
        """
        print_debug("fpm_progress_install")
        i = 1
        percent = 0
        event = 0
        count = 0
        str_label = ""
        progress = 0
        for arg in args:
            if i == 1:
                if arg != None:
                    event = arg
            #if i == 2:
            #   packagename = pointer_to_string(arg)
            if i == 3:
                if arg != None:
                    percent = arg
            elif i == 4:
                if arg != None:
                    count = arg
            else:
                pass
            i = i + 1
        try :
            progress = float(float(percent)/100)
            print_debug(progress)
        except :
            pass
        if event == PM_TRANS_PROGRESS_ADD_START:
            if count > 1:
                str_label = "Installing packages..."
            else:
                str_label = "Installing package..."
            updateGUI(str_label,progress)
        elif event == PM_TRANS_PROGRESS_UPGRADE_START:
            if count > 1:
                str_label = "Upgrading packages..."
            else:
                str_label = "Upgrading package..."
            updateGUI(str_label,progress)
        elif event == PM_TRANS_PROGRESS_REMOVE_START:
            if count > 1:
                str_label = "Removing packages..."
            else:
                str_label = "Removing package..."
            updateGUI(str_label,progress)
        elif event == PM_TRANS_PROGRESS_CONFLICTS_START:
            if count > 1:
                str_label = "Checking packages for file conflicts..."
            else:
                str_label = "Checking package for file conflicts..."
            updateGUI(str_label,progress)
        else:
            pass
        if str_label != "":
            print_debug(str_label)
        print_debug("fpm_progress_install finish")

    def progressUpdate(*args):
        print_debug("fpm_progress_update")

    def progressEvent(*args):
        print_debug("fpm_progress_event")
        try:
            i = 1
            data1 = None
            data2 = None
            for arg in args:
                if i == 1:
                    if arg != None:
                        event = arg
                elif i == 2:
                    if arg != None:
                        data1 = arg
                elif i == 3:
                    if arg != None:
                        data2 = arg
                else:
                    pass
                i = i + 1

            print_debug(event)
            print_debug(data1)
            print_debug(data2)
        except :
            pass

        if event != PM_TRANS_EVT_RETRIEVE_START and event != PM_TRANS_EVT_RESOLVEDEPS_START and event != PM_TRANS_EVT_RESOLVEDEPS_DONE:
            bo_download = 0
        str_label = ""
        progress = 0
        if event == PM_TRANS_EVT_CHECKDEPS_START:
            str_label = "Checking dependencies"
            progress = 1
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_FILECONFLICTS_START:
            str_label = "Checking for file conflicts"
            progress = 1
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_RESOLVEDEPS_START:
            str_label = "Resolving dependencies"
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_INTERCONFLICTS_START:
            str_label = "Looking for inter-conflicts"
            progress = 1
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_INTERCONFLICTS_DONE:
            str_label = "Done"
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_ADD_START:
            str_label = "Installing"
            progress = 1
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_ADD_DONE:
            str_label = "Package installation finished"
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_UPGRADE_START:
            str_label = "Upgrading " # + pointer_to_string(pacman_pkg_getinfo(data1, PM_PKG_NAME))
            progress = 1
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_UPGRADE_DONE:
            str_label = "Package upgrade finished"
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_REMOVE_START:
            str_label = "removing"
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_REMOVE_DONE:
            str_label = "Package removal finished"
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_INTEGRITY_START:
            str_label = "Checking package integrity"
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_INTEGRITY_DONE:
            str_label = "Done"
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_SCRIPTLET_INFO:
            str_label = pointer_to_string(data1)
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_SCRIPTLET_START:
            str_label = str_data1
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_SCRIPTLET_DONE:
            str_label = "Done"
            updateGUI(str_label,progress)
        elif event == PM_TRANS_EVT_RETRIEVE_START:
            str_label = "Retrieving packages...\nPlease wait..."
            bo_download = 1
            progress = 1
            updateGUI(str_label,progress)
        else:
            pass
        print_debug(str_label)
        print_debug("fpm_progress_event finish")

    def updateGUI(self, str_label, progress):
        """
        Update progressbar
        """
        if str_label == "":
            return
        if str_label == label_what.get_text() and progress == progressbar_install.get_fraction():
            return
        self.statusbar.push(1,str_label)
        self.progress.set_fraction(progress)
        draw()

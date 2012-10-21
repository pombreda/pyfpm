#!/usr/bin/python
# -*- coding: utf-8 -*-

########################################################################
#
#                   pyfpm par PacMiam
#                   version 0.1a
#
# Gestionnaire de paquets pour la distribution GNU/Linux
# Frugalware basé sur le travail de Gaetan Gourdin.
#
# Commencé le : 23 aout 2012
#
# TODO : Fenêtre de préférences avec choix de la langue (50%)
# TODO : Afficher les paquets installés, a mettre à jour, etc
# TODO : Mettre une couleur spécifique dans le treeview des packages
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

import os, sys, urllib, codecs, time, pango

from string import strip
from tools import *

import pacmang2.libpacman
from pacmang2.libpacman import *

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK not found.")

divers = divers()
config = configuration()
pypacman = pypacmang2()

# Création du fichier de configuration si inexistant
config.Exist()
# Initialisation du module pacman
pypacman.initPacman()

########################################################################

class INTERFACE:
    def __init__(self):
        self.name = "pyFPM"
        self.version = "0.0.1"
        self.width = 800
        self.height = 600
        self.packageSelected = ""
        self.instPkgList = []
        self.listInstall = []
        self.listRemove = []

        # Fenêtre principale
        self.mainwindow = gtk.Window()
        self.mainwindow.set_title(divers.getATrad("title") + " - " + self.name)
        self.mainwindow.set_size_request(self.width, self.height)
        self.mainwindow.set_resizable(True)
        self.mainwindow.set_position(gtk.WIN_POS_CENTER)

        # Grilles pour les éléments de la fenêtre
        self.main_table = gtk.Table(3,4)
        self.groups_packages = gtk.HPaned()
        self.packages_notebook = gtk.VPaned()

        if (self.mainwindow):
            self.mainwindow.connect("destroy", gtk.main_quit)

        # Menu, toolbar et barre de recherche
        self.menu = gtk.MenuBar()
        self.toolbar = gtk.Toolbar()

        # Menu
        self.menu_action = gtk.MenuItem(label=divers.getATrad("action"))
        self.menu_action_list = gtk.Menu()
        self.menu_action_clean = gtk.ImageMenuItem(divers.getATrad("clean_cache"))
        self.menu_action_clean.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
        self.menu_action_clean.connect("activate", self.cleanCache)
        self.menu_action_update = gtk.ImageMenuItem(divers.getATrad("update_database"))
        self.menu_action_update.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU))
        self.menu_action_update.connect("activate", self.updateDatabase)
        self.menu_action_check = gtk.ImageMenuItem(divers.getATrad("check_update"))
        self.menu_action_check.set_image(gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU))
        self.menu_action_check.connect("activate", self.checkUpdate)
        self.menu_action_quit = gtk.ImageMenuItem(divers.getATrad("quit"))
        self.menu_action_quit.set_image(gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU))
        self.menu_action_quit.connect("activate", self.destroy)
        self.menu.add(self.menu_action)
        self.menu_action_list.add(self.menu_action_clean)
        self.menu_action_list.add(self.menu_action_update)
        self.menu_action_list.add(self.menu_action_check)
        self.menu_action_list.add(self.menu_action_quit)
        self.menu_action.set_submenu(self.menu_action_list)

        self.menu_edit = gtk.MenuItem(label=divers.getATrad("edit"))
        self.menu_edit_list = gtk.Menu()
        self.menu_edit_clear_changes = gtk.ImageMenuItem(divers.getATrad("clear_changes"))
        self.menu_edit_clear_changes.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
        self.menu_edit_clear_changes.connect("activate", self.resetSelect)
        self.menu_edit_preference = gtk.ImageMenuItem(divers.getATrad("preferences"))
        self.menu_edit_preference.set_image(gtk.image_new_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU))
        self.menu_edit_preference.connect("activate", self.preferences)
        self.menu.add(self.menu_edit)
        self.menu_edit_list.add(self.menu_edit_clear_changes)
        self.menu_edit_list.add(self.menu_edit_preference)
        self.menu_edit.set_submenu(self.menu_edit_list)

        self.menu_help = gtk.MenuItem(label=divers.getATrad("help"))
        self.menu_help_list = gtk.Menu()
        self.menu_help_about = gtk.ImageMenuItem(divers.getATrad("about"))
        self.menu_help_about.set_image(gtk.image_new_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU))
        self.menu_help_about.connect("activate", self.about)
        self.menu.add(self.menu_help)
        self.menu_help_list.add(self.menu_help_about)
        self.menu_help.set_submenu(self.menu_help_list)

        # Toolbar
        self.toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.toolbar.insert_stock(gtk.STOCK_APPLY, divers.getATrad("apply_pkg"), None, self.applyChange, None, 0)
        self.toolbar.insert_stock(gtk.STOCK_REFRESH, divers.getATrad("refresh_pkg"), None, self.updateDatabase, None, 2)
        self.toolbar.insert_space(3)
        self.search_entry = gtk.Entry()
        # TODO : Ajouter l'action d'effacer l'entry via le bouton
        self.search_entry.set_icon_from_stock(1, gtk.STOCK_CLEAR)
        self.search_entry.connect("activate", self.search, gtk.RESPONSE_OK)
        self.toolbar.insert_widget(self.search_entry, divers.getATrad("write_search"), None, 4)
        self.toolbar.insert_stock(gtk.STOCK_FIND, divers.getATrad("search"), None, self.search, None, 5)
        self.toolbar.insert_space(6)
        self.toolbar.insert_stock(gtk.STOCK_QUIT, divers.getATrad("quit"), None, self.destroy, None, 7)

        # Statusbar
        self.statusbox = gtk.HBox()
        self.statusbar = gtk.Statusbar()
        self.progress = gtk.ProgressBar()
        self.statusbox.pack_start(self.progress, expand=False)
        self.statusbox.pack_start(self.statusbar)

        # List view - Groups
        self.groups_list = gtk.ListStore(str)
        self.groups = gtk.TreeView(self.groups_list)
        self.groups.set_headers_visible(False)
        self.groups.set_size_request(180,0)
        self.groups.set_search_column(0)

        self.groups_nom = gtk.TreeViewColumn(divers.getATrad("groups"))
        self.groups_nom.set_sort_column_id(0)
        self.groups.append_column(self.groups_nom)
        self.groups_cellule_nom = gtk.CellRendererText()
        self.groups_nom.pack_start(self.groups_cellule_nom, True)
        self.groups_nom.set_attributes(self.groups_cellule_nom, text=0)

        self.groups_scroll = gtk.ScrolledWindow()
        self.groups_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.groups_scroll.add(self.groups)

        # List view - Packages
        self.packages_list = gtk.ListStore(int, str, str)
        self.packages = gtk.TreeView(self.packages_list)
        self.packages.set_size_request(0,300)
        self.packages.set_search_column(1)
        self.packages_list.set_sort_column_id(1,gtk.SORT_ASCENDING) # Trie la liste de paquet alphabetiquement

        self.packages_checkbox = gtk.TreeViewColumn(" ")
        self.packages_checkbox.set_sort_column_id(0)
        self.packages_nom = gtk.TreeViewColumn(divers.getATrad("name"))
        self.packages_nom.set_min_width(300)
        self.packages_nom.set_sort_column_id(1)
        self.packages_version = gtk.TreeViewColumn(divers.getATrad("version"))
        self.packages_version.set_sort_column_id(2)

        self.packages.append_column(self.packages_checkbox)
        self.packages.append_column(self.packages_nom)
        self.packages.append_column(self.packages_version)

        self.packages_cellule_checkbox = gtk.CellRendererToggle()
        self.packages_cellule_checkbox.set_property('active', 1)
        self.packages_cellule_checkbox.set_property('activatable', True)
        self.packages_cellule_checkbox.connect('toggled', self.toggled, self.packages)
        self.packages_cellule_nom = gtk.CellRendererText()
        self.packages_cellule_version = gtk.CellRendererText()

        self.packages_checkbox.pack_start(self.packages_cellule_checkbox, True)
        self.packages_nom.pack_start(self.packages_cellule_nom, True)
        self.packages_version.pack_start(self.packages_cellule_version, True)

        self.packages_checkbox.add_attribute(self.packages_cellule_checkbox, 'active', 0)
        self.packages_nom.add_attribute(self.packages_cellule_nom, 'text', 1)
        self.packages_version.add_attribute(self.packages_cellule_version, 'text', 2)

        self.packages_scroll = gtk.ScrolledWindow()
        self.packages_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.packages_scroll.add(self.packages)

        # Notebook
        self.notebook = gtk.Notebook()

        # Information sur le paquet
        self.information_text = gtk.TreeView()
        self.information_text.set_headers_visible(False)
        self.information_text.set_hover_selection(True)
        self.info_store = gtk.TreeStore(str,str)
        self.info_column = gtk.TreeViewColumn()
        self.info_cell = gtk.CellRendererText()
        self.info_cell.set_property('weight', pango.WEIGHT_BOLD)
        self.info_column2 = gtk.TreeViewColumn()
        self.info_cell2 = gtk.CellRendererText()
        self.info_column.pack_start(self.info_cell, True)
        self.info_column.add_attribute(self.info_cell, "text", 0)
        self.info_column2.pack_start(self.info_cell2, True)
        self.info_column2.add_attribute(self.info_cell2, "text", 1)
        self.information_text.append_column(self.info_column)
        self.information_text.append_column(self.info_column2)
        self.information_text.set_model(self.info_store)
        self.information_scroll = gtk.ScrolledWindow()
        self.information_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.information_scroll.add(self.information_text)

        # Fichiers contenus dans le paquet
        self.file_text = gtk.TextView()
        self.file_text.set_editable(False)
        self.file_text.set_cursor_visible(False)
        self.file_scroll = gtk.ScrolledWindow()
        self.file_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.file_scroll.add(self.file_text)
        # Journal de changements sur le paquet
        self.changelog_text = gtk.TextView()
        self.changelog_text.set_editable(False)
        self.changelog_text.set_cursor_visible(False)
        self.changelog_scroll = gtk.ScrolledWindow()
        self.changelog_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.changelog_scroll.add(self.changelog_text)

        self.notebook_information = gtk.Label(divers.getATrad("informations"))
        self.notebook.append_page(self.information_scroll, self.notebook_information)
        self.notebook_files = gtk.Label(divers.getATrad("files"))
        self.notebook.append_page(self.file_scroll, self.notebook_files)
        self.notebook_changelog = gtk.Label(divers.getATrad("changelog"))
        self.notebook.append_page(self.changelog_scroll, self.notebook_changelog)

        # Intégration des éléments dans les grilles
        self.groups_frame = gtk.Frame(divers.getATrad("groups"))
        self.groups_frame.add(self.groups_scroll)
        self.groups_scroll.set_border_width(4)
        self.groups_frame.set_border_width(4)
        self.packages_frame = gtk.Frame(divers.getATrad("packages_list"))
        self.packages_frame.add(self.packages_scroll)
        self.packages_scroll.set_border_width(4)
        self.packages_frame.set_border_width(4)
        self.details_frame = gtk.Frame(divers.getATrad("details"))
        self.details_frame.add(self.notebook)
        self.notebook.set_border_width(4)
        self.details_frame.set_border_width(4)
        # 1 - main_table
        self.main_table.attach(self.menu, 0, 3, 0, 1, yoptions=gtk.FILL)
        self.main_table.attach(self.toolbar, 0, 3, 1, 2, yoptions=gtk.FILL)
        self.main_table.attach(self.groups_packages, 0, 3, 2, 3)
        self.main_table.attach(self.statusbox, 0, 3, 3, 4, yoptions=gtk.FILL)
        # 2 - packages_notebook
        self.packages_notebook.add1(self.packages_frame)
        self.packages_notebook.add2(self.details_frame)
        # 3 - groups_packages
        self.groups_packages.add1(self.groups_frame)
        self.groups_packages.add2(self.packages_notebook)

        # Fonctions
        self.init_Grp()

        # Ajout de la grille principale dans la fenêtre principale
        self.mainwindow.add(self.main_table)

        # On affiche l'interface et on cache la barre de progrès tant
        # que l'on ne l'utilise pas.
        self.mainwindow.show_all()
        self.progress.hide()

        # Focus sur la zone de recherche
        self.search_entry.grab_focus()

        # Sélection du groupe
        self.groups_selection = self.groups.get_selection()
        self.groups_selection.connect('changed', self.selection_grp, self.groups_list)

        # Sélection du paquet
        self.packages_selection = self.packages.get_selection()
        self.packages_selection.connect('changed', self.selection_pkg, self.packages_list)

        # Fonction pour l'ouverture de page internet
        self.info_selection = self.information_text.get_selection()
        self.information_text.connect('row-activated', self.gotourl)

    ####################################################################
    #                           Windows
    ####################################################################

    def about(self, widget, *event):
        """
        About window
        """
        about = gtk.AboutDialog()
        about.set_program_name(self.name)
        about.set_version(self.version)
        about.set_comments(divers.getATrad("about_desc"))
        about.set_copyright("Copyright (c) 2012\nGaetan Gourdin\nAurélien Lubert")
        about.set_license("Ce programme est un logiciel libre, vous pouvez le redistribuer\net/ou le modifier conformément aux dispositions de la Licence Publique\nGénérale GNU, telle que publiée par la Free Software Foundation.")
        logo = gtk.gdk.pixbuf_new_from_file("logo.png")
        about.set_logo(logo)
        about.run()
        about.destroy()

    def preferences(self, widget, *event):
        """
        Preferences window
        """
        preferences = gtk.Dialog(divers.getATrad("preferences"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_APPLY, gtk.RESPONSE_APPLY))
        preferences.set_has_separator(False)
        preferences.set_default_response(gtk.RESPONSE_OK)

        frameTool = gtk.Frame(divers.getATrad("tools"))
        frameTool.set_border_width(4)
        grilleTool = gtk.HBox()
        grilleTool.set_border_width(4)
        preferences.vbox.pack_start(frameTool)
        frameMisc = gtk.Frame(divers.getATrad("misc"))
        frameMisc.set_border_width(4)
        grilleMisc = gtk.Table(2,2)
        grilleMisc.set_border_width(4)
        preferences.vbox.pack_start(frameMisc)

        labelTool = gtk.Label(divers.getATrad("choose_su") + " ")
        labelTool.set_alignment(0,0.5)
        entryTool = gtk.combo_box_entry_new_text()
        # FIXME : Si fichier vide problème
        divers.fillCommand(entryTool)

        grilleTool.pack_start(labelTool)
        grilleTool.pack_start(entryTool)
        frameTool.add(grilleTool)

        labelLang = gtk.Label(divers.getATrad("lang"))
        labelLang.set_alignment(0,0.5)
        # TODO : Faire en sorte de récupérer l'ensemble des fichiers de traduction
        tabLang = ['fr','en']
        comboLang = gtk.combo_box_new_text()
        i = 0
        for entry in tabLang:
            comboLang.append_text(entry)
            if entry == config.Read("lang"):
                comboLang.set_active(i)
            i += 1
        checkboxOffLine = gtk.CheckButton(divers.getATrad("offline"))
        try:
            checkboxOffLine.set_active(int(config.Read("offline")))
        except:
            checkboxOffLine.set_active(0)
        grilleMisc.attach(labelLang, 0, 1, 0, 1)
        grilleMisc.attach(comboLang, 1, 2, 0, 1, xoptions=gtk.FILL)
        grilleMisc.attach(checkboxOffLine, 0, 2, 1, 2, xoptions=gtk.FILL)
        frameMisc.add(grilleMisc)

        preferences.show_all()
        reponse = preferences.run()
        if reponse == gtk.RESPONSE_OK:
            command = str(entryTool.get_active_text())
            lang = str(comboLang.get_active_text())
            offline = checkboxOffLine.get_active()
            if offline == True:
                offline = 1
            else:
                offline = 0
            config.Write(lang,command,offline)
        preferences.destroy()

    def applyChange(self,*args):
        '''
        Install/remove applications
        '''
        if divers.countList(self.listInstall) != 0 or divers.countList(self.listRemove) != 0:
            installWindow = gtk.Dialog(divers.getATrad("apply_pkg"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
            installWindow.set_has_separator(True)
            installWindow.set_default_response(gtk.RESPONSE_OK)
            installWindow.set_size_request(280,300)

            installText = gtk.TreeView()
            installText.set_headers_visible(False)
            installText.set_hover_selection(True)
            installStore = gtk.TreeStore(str)
            installColumn = gtk.TreeViewColumn()
            installCell = gtk.CellRendererText()
            installColumn.pack_start(installCell, True)
            installColumn.add_attribute(installCell, "text", 0)
            installText.append_column(installColumn)
            installText.set_model(installStore)
            installScroll = gtk.ScrolledWindow()
            installScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            installScroll.add(installText)

            if divers.countList(self.listInstall) != 0:
                viewColumn = installStore.append(None, [divers.getATrad("install_pkg")])
                for row in self.listInstall:
                    installStore.append(viewColumn, [row])
            if divers.countList(self.listRemove) != 0:
                viewColumn = installStore.append(None, [divers.getATrad("remove_pkg")])
                for row in self.listRemove:
                    installStore.append(viewColumn, [row])

            installWindow.vbox.pack_start(installScroll)

            installWindow.show_all()
            installWindow.run()
            installWindow.destroy()
        else:
            divers.information(divers.getATrad("apply_pkg"),divers.getATrad("no_change"))

    def cleanCache(self,*args):
        '''
        Clean cache
        '''
        sysexec(config.Read("su_command") + " python " + PYFPM_INST + " cleancache")
        self.init_Grp()

    def updateDatabase(self,*args):
        '''
        Update database
        '''
        sysexec(config.Read("su_command") + " python " + PYFPM_INST + " updatedb")
        self.init_Grp()

    def checkUpdate(self,*args):
        '''
        Check update
        '''
        sysexec("python " + PYFPM_FUN)
        self.init_Grp()

    def search(self,*args):
        # FIXME : Impossible d'empêcher la recherche quand l'entry est vide
        if self.search_entry.get_text != '':
            self.packages_list.clear()
            search = self.search_entry.get_text()
            print "'" + search + "'"
            self.print_info_statusbar(divers.getATrad("search_package") + " " + search)
            pkgs = pacman_search_pkg(search)
            if len(pkgs) == 0:
                return
            pacman_trans_release()
            self.pkgtoListsore(pkgs)

    def clearEntry(self,*args):
        self.search_entry.set_text("")

    ####################################################################
    #                          Functions
    ####################################################################

    def init_Grp(self):
        """
        Write the groups into the groups list
        """
        self.groups_list.clear()
        tab_grp = pypacman.PacmanGetGrp()
        for grp in tab_grp :
            self.groups_list.append([grp])

    def pkgtoListsore(self, pkgs):
        """
        Write the packages into the packages list
        """
        bo_inst = 0
        self.instPkgList = []
        self.packages_list.clear()
        # Read packages list
        for pkg in pkgs:
            # If package is allready install
            if pacman_package_intalled(pacman_pkg_get_info(pkg,PM_PKG_NAME),pacman_pkg_get_info(pkg,PM_PKG_VERSION)) == 1:
                if divers.inList(self.listRemove, pacman_pkg_get_info(pkg,PM_PKG_NAME)) == 0:
                    bo_inst = 1
                else:
                    bo_inst = 0
                if self.verifyPkgInst(pacman_pkg_get_info(pkg,PM_PKG_NAME), pacman_pkg_get_info(pkg,PM_PKG_VERSION)) == False:
                    # Pour éviter les doublons, le paquet est ajouté dans la liste instPkgList
                    self.instPkgList.append([pacman_pkg_get_info(pkg,PM_PKG_NAME),pacman_pkg_get_info(pkg,PM_PKG_VERSION)])
                    self.packages_list.append([bo_inst,pacman_pkg_get_info(pkg,PM_PKG_NAME),pacman_pkg_get_info(pkg,PM_PKG_VERSION)])
            else:
                if divers.inList(self.listInstall, pacman_pkg_get_info(pkg,PM_PKG_NAME)) == 0:
                    bo_inst = 0
                else:
                    bo_inst = 1
                self.packages_list.append([bo_inst,pacman_pkg_get_info(pkg,PM_PKG_NAME),pacman_pkg_get_info(pkg,PM_PKG_VERSION)])
        pkgs.sort()
        self.eraseData()

    def eraseData(self):
        """
        Reset package data area
        """
        self.info_column.set_title("")
        self.info_store.clear()
        textbuffer = self.changelog_text.get_buffer()
        textbuffer.set_text("")

    def resetSelect(self, *arg):
        """
        Reset the install and remove packages lists
        """
        # FIXME : Le faire uniquement si les deux listes ne sont pas vides
        self.listInstall = []
        self.listRemove = []
        self.groups_selection = self.groups.get_selection()
        self.selection_grp(self.groups_selection, self.groups_list)

    def verifyPkgInst(self, pkgname, pkgver):
        """
        Verify if a package is allready install
        """
        value = False
        for index in self.instPkgList:
            if index[0] == pkgname and index[1] == pkgver:
                # Package exist
                value = True
                break
        return value

    def selection_grp(self, selection, model):
        sel = selection.get_selected()
        if sel == ():
            return

        treeiter = sel[1]
        model = self.groups.get_model()
        grpselected = model.get_value(treeiter, 0)
        self.show_group(grpselected)
        return True

    def selection_pkg(self, selection, model):
        sel = selection.get_selected()
        if sel == ():
            return

        treeiter = sel[1]
        try :
            pkgname, pkgver = model.get(treeiter, 1, 2)
            self.show_package(pkgname, pkgver)
        except :
            # not a problem
            return True
        return True

    def gotourl(self, widget, *event):
        self.information_text.get_model()
        try :
            pkgname, pkgver = model.get(self.info_selection[1], 1, 2)
            print pkgver
        except :
            # not a problem
            return True
        return True

    def show_group(self, grp):
        self.print_info_statusbar(divers.getATrad("read_grp") + " " + grp)
        pkgs = pypacman.GetPkgFromGrp(grp)
        self.pkgtoListsore(pkgs)

    def show_package(self, pkgname, pkgver):
        self.print_info_statusbar(divers.getATrad("read_pkg") + " " + pkgname)
        bo_find = 0
        try:
            pkgs = pacman_search_pkg(pkgname)
            self.packageSelected = pkgname
            for pkg in pkgs:
                if pacman_pkg_get_info(pkg,PM_PKG_NAME) == pkgname and pacman_pkg_get_info(pkg,PM_PKG_VERSION) == pkgver:
                    bo_find = 1
                    self.show_packagedetails(pkgname, pkgver, pkg)
                    break
        except:
            pass
        if bo_find == 0:
            # nobuild package or not in fdb read local information
            pkg = pacman_db_readpkg(db_list[0], pkgname)
            self.show_packagedetails(pkgname, pkgver, pkg)

    def show_packagedetails(self, pkgname, pkgver, pkg):
        """
        Show the package informations
        """
        text = ""
        pkgl = None

        # Erase data
        self.info_store.clear()

        if pacman_package_intalled(pkgname,pkgver) == 1:
            pkgl = pacman_db_readpkg (db_list[0], pkgname)

        # Main informations
        self.info_store.append(None, [divers.getATrad("name"), pkgname])
        self.info_store.append(None, [divers.getATrad("version"), pkgver])
        self.info_store.append(None, [divers.getATrad("description"), pacman_pkg_get_info(pkg,PM_PKG_DESC)])
        if pkgl <> None:
            self.info_store.append(None, [divers.getATrad("url"), pointer_to_string(pacman_pkg_get_info(pkgl,PM_PKG_URL))])
            #~ gtk.LinkButton("http://www.pygtk.org/", "PyGtk")
            self.info_store.append(None, ["SHA1SUMS\t\t", pacman_pkg_get_info(pkg,PM_PKG_SHA1SUM)])

        # Depends
        if pacman_package_intalled(pkgname,pkgver) == 1:
            deps = pacman_pkg_getinfo(pkg, PM_PKG_DEPENDS)
            while deps != 0:
                text += pointer_to_string(pacman_list_getdata(deps))
                deps = pacman_list_next(deps)
                if deps != 0:
                    text += ", "    # Evite d'avoir une virgule à la fin de la liste
            viewColumn = self.info_store.append(None, [divers.getATrad("depends"), text])

        text = ""
        # Files
        textbuffer = self.file_text.get_buffer()
        if pacman_package_intalled(pkgname,pkgver) == 1:
            i = pacman_pkg_getinfo(pkgl, PM_PKG_FILES)
            while i != 0:
                text = text + "  /" + pointer_to_string(pacman_list_getdata(i)) + "\n"
                i = pacman_list_next(i)
        textbuffer.set_text(text)
        text = ""

        # Changelog
        # FIXME : Les changelog apparaissent avec iso-8859-15 mais conservent les problèmes d'accents
        textbuffer = self.changelog_text.get_buffer()
        fileChangeLog = PM_ROOT + PM_DBPATH + "/" + repo_list[0] + "/" + pkgname + "-" + pkgver + "/changelog"
        if os.path.exists(fileChangeLog) == True:
            file = codecs.open(fileChangeLog,"r","iso-8859-15")
            for line in file:
                if line <> "":
                    text += line
            file.close()
        else:
            text = divers.getATrad("no_changelog")
        textbuffer.set_text(text)

    def download(self,url,where):
        """
        Copy the contents of a file from a given URL
        to a local file.
        """
        try :
            webFile = urllib.urlopen(url)
            localFile = open(where, 'w')
            localFile.write(webFile.read())
            webFile.close()
            localFile.close()
        except :
            pass

    def print_info_statusbar(self, text):
        """
        Write a new text in the statusbar
        """
        self.statusbar.push(0,text)

    def toggled(self, cell_renderer, col, treeview):
        """
        Change status of the package checkbox
        """
        model = treeview.get_model()
        model[col][0] = not model[col][0]
        rowR = divers.inList(self.listRemove, model[col][1])
        rowI = divers.inList(self.listInstall, model[col][1])

        if model[col][0] == 0:
            # Uncheck
            if pacman_package_intalled(model[col][1],model[col][2]) == 1:
                if rowR == 0:
                    self.listRemove.append(model[col][1])
            else:
                if rowI != 0:
                    self.listInstall.remove(rowI)
        else:
            # Check
            if pacman_package_intalled(model[col][1],model[col][2]) == 1:
                if rowR != 0:
                    self.listRemove.remove(rowR)
            else:
                if rowI == 0:
                    self.listInstall.append(model[col][1])

    def destroy(window, self):
        pypacman.pacman_finally()
        gtk.main_quit()

def main():
    pyfpm = INTERFACE()
    gtk.main()

if __name__ == "__main__":
    sys.exit(main())

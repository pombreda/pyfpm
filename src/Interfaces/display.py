#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions permettant de créer l'interface
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys, pango, codecs, urllib, gettext

gettext.bindtextdomain('pyfpm', 'lang')
gettext.textdomain('pyfpm')
_ = gettext.gettext

try:
    import pygtk, gtk
except ImportError:
    sys.exit(_("pygtk was not found"))

from . import preferences
from Functions import package, config, files

# Initialisation des modules
Preferences = preferences.Preferences()
Package = package.Package()
File = files.File()
Config = config.Config()


class Interface (object):
    """
    Ensemble des fonctions de la fenêtre principale
    """

    def __init__(self):
        """
        Initialisation de la fenêtre principale
        """

        self.listeGroupesProhibes = ['-extensions','adesklets-desklets','amsn-plugins','avidemux-plugin-cli','avidemux-plugin-gtk','avidemux-plugin-qt','chroot-core','core','cinnamon-desktop','devel-core','directfb-drivers','e17-apps','e17-misc','fatrat-plugins','firefox-extensions','geda-suite','gift-plugins','gnome-minimal','hk_classes-drivers','jdictionary-plugins','kde-apps','kde-build','kde-core','kde-doc','kde-docs','kde-minimal','kde-runtime','lxde-desktop','lxde-extra','pantheon-desktop','misc-fonts','phonon-backend','pidgin-plugins','qt4-libs','sawfish-scripts','seamonkey-addons','thunderbird-extensions','tuxcmd-plugins','wmaker-dockapps','xfce4-core','xfce4-goodies','xorg-apps','xorg-core','xorg-data','xorg-doc','xorg-drivers','xorg-fonts','xorg-libs','xorg-proto','xorg-util']

        self.paquetSelectionne = ""

        self.listeInstallationPacman = []
        self.listeSuppressionPacman = []
        self.listeMiseAJourPacman = []

        self.recherche_mode = False
        self.recherche_nom = ""

        # ------------------------------------------------------------------
        #       Fenetre
        # ------------------------------------------------------------------

        self.fenetre = gtk.Window()
        self.grille = gtk.Table(1,4)
        self.grilleSelectionDepots = gtk.Table(1,2)
        self.grilleDepotGroupes = gtk.Table(1,2)
        self.grilleColonnePaquets = gtk.Table(2,1)
        self.grillePaquetsInformations = gtk.VPaned()

        self.barreStatus = gtk.Statusbar()

        # ------------------------------------------------------------------
        #       Menu
        # ------------------------------------------------------------------

        self.menu = gtk.MenuBar()
        self.menu_action = gtk.MenuItem(label=_("Action"))
        self.menu_action_list = gtk.Menu()
        self.menu_action_install = gtk.ImageMenuItem(_("Apply changes"))
        self.menu_action_clean = gtk.ImageMenuItem(_("Clean cache"))
        self.menu_action_update = gtk.ImageMenuItem(_("Update databases"))
        self.menu_action_check = gtk.ImageMenuItem(_("Check update"))
        self.menu_action_quit = gtk.ImageMenuItem(_("Quit"))
        self.menu_edit = gtk.MenuItem(label=_("Edit"))
        self.menu_edit_list = gtk.Menu()
        self.menu_edit_clear_changes = gtk.ImageMenuItem(_("Reset installation list"))
        self.menu_edit_preference = gtk.ImageMenuItem(_("Preferences"))
        self.menu_help = gtk.MenuItem(label=_("Help"))
        self.menu_help_list = gtk.Menu()
        self.menu_help_about = gtk.ImageMenuItem(_("About"))

        # ------------------------------------------------------------------
        #       Barre d'outils
        # ------------------------------------------------------------------

        self.outils = gtk.Toolbar()
        self.texteRecherche = gtk.Entry()

        # ------------------------------------------------------------------
        #       Liste des dépôts
        # ------------------------------------------------------------------

        self.labelSelectionDepots = gtk.Label(_("Select a group"))
        self.listeSelectionDepots = gtk.combo_box_new_text()

        # ------------------------------------------------------------------
        #       Colonnes des groupes
        # ------------------------------------------------------------------

        #~ self.zoneGroupes = gtk.Frame(Lang.translate("list_groups"))
        self.listeColonneGroupes = gtk.ListStore(str)
        self.colonneGroupes = gtk.TreeView(self.listeColonneGroupes)
        self.colonneGroupesNom = gtk.TreeViewColumn(_("Groups"))
        self.celluleGroupesNom = gtk.CellRendererText()
        self.defilementGroupes = gtk.ScrolledWindow()

        # ------------------------------------------------------------------
        #       Colonnes des paquets
        # ------------------------------------------------------------------

        #~ self.zonePaquets = gtk.Frame(Lang.translate("packages_list"))
        self.listeColonnePaquets = gtk.ListStore(int, str, str, str, str)
        self.colonnePaquets = gtk.TreeView(self.listeColonnePaquets)
        self.colonnePaquetsCheckbox = gtk.TreeViewColumn(" ")
        self.cellulePaquetsCheckbox = gtk.CellRendererToggle()
        self.colonnePaquetsImage = gtk.TreeViewColumn(" ")
        self.cellulePaquetsImage = gtk.CellRendererPixbuf()
        self.colonnePaquetsNom = gtk.TreeViewColumn(_("Package name"))
        self.cellulePaquetsNom = gtk.CellRendererText()
        self.colonnePaquetsVersionActuelle = gtk.TreeViewColumn(_("Actual version"))
        self.cellulePaquetsVersionActuelle = gtk.CellRendererText()
        self.colonnePaquetsVersionDisponible = gtk.TreeViewColumn(_("Available version"))
        self.cellulePaquetsVersionDisponible = gtk.CellRendererText()
        self.defilementPaquets = gtk.ScrolledWindow()

        # ------------------------------------------------------------------
        #       Informations sur le paquet
        # ------------------------------------------------------------------

        self.zoneInformations = gtk.Notebook()

        self.labelInformations = gtk.Label(_("Informations"))
        self.listeInformations = gtk.TreeView()
        self.colonneLabelInformations = gtk.TreeViewColumn()
        self.celluleLabelInformations = gtk.CellRendererText()
        self.colonneValeurInformations = gtk.TreeViewColumn()
        self.celluleValeurInformations = gtk.CellRendererText()
        self.contenuInformations = gtk.TreeStore(str,str)
        self.defilementInformations = gtk.ScrolledWindow()

        self.labelPaquet = gtk.Label(_("Package"))
        self.listePaquet = gtk.TreeView()
        self.colonneLabelPaquet = gtk.TreeViewColumn()
        self.celluleLabelPaquet = gtk.CellRendererText()
        self.colonneValeurPaquet = gtk.TreeViewColumn()
        self.celluleValeurPaquet = gtk.CellRendererText()
        self.contenuPaquet = gtk.TreeStore(str,str)
        self.defilementPaquet = gtk.ScrolledWindow()

        self.labelFichiers = gtk.Label(_("Files"))
        #~ self.listeFichiers = gtk.TextView()
        self.listeFichiers = gtk.TreeView()
        self.colonneFichiers = gtk.TreeViewColumn()
        self.celluleFichiers = gtk.CellRendererText()
        self.contenuFichiers = gtk.TreeStore(str)
        self.defilementFichiers = gtk.ScrolledWindow()

        self.labelJournal = gtk.Label(_("Changelog"))
        self.listeJournal = gtk.TextView()
        self.defilementJournal = gtk.ScrolledWindow()

        self.labelFrugalbuild = gtk.Label(_("FrugalBuild"))
        self.listeFrugalbuild = gtk.TextView()
        self.defilementFrugalbuild = gtk.ScrolledWindow()


    def mainWindow (self, devMode = False):
        """
        Fenêtre principale
        """

        self.developementMode = devMode

        longueur = Config.readConfig("screen", "width")
        hauteur = Config.readConfig("screen", "height")

        # Vérifie que la fenêtre n'a pas une taille inférieur à 800x600
        if int(longueur) >= 800 and int(hauteur) >= 600:

            # ------------------------------------------------------------------
            #       Fenetre
            # ------------------------------------------------------------------

            self.fenetre.set_title(_("Install and Remove packages"))
            self.fenetre.set_default_size(int(longueur), int(hauteur))
            self.fenetre.set_resizable(True)
            self.fenetre.set_position(gtk.WIN_POS_CENTER)

            # ------------------------------------------------------------------
            #       Menu
            # ------------------------------------------------------------------

            self.fenetre.connect("destroy", gtk.main_quit)
            self.fenetre.connect("check-resize", self.resize)

            self.menu_action_install.set_image(gtk.image_new_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU))
            self.menu_action_install.connect("activate", self.installWindow, self)

            self.menu_action_clean.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
            self.menu_action_clean.connect("activate", Package.cleanCache, self)

            self.menu_action_update.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU))
            self.menu_action_update.connect("activate", Package.updateDatabase, self)

            self.menu_action_check.set_image(gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU))
            self.menu_action_check.connect("activate", self.updateWindow)

            self.menu_action_quit.set_image(gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU))
            self.menu_action_quit.connect("activate", self.closeWindow)

            self.menu.add(self.menu_action)

            self.menu_action_list.add(self.menu_action_install)
            self.menu_action_list.add(self.menu_action_clean)
            self.menu_action_list.add(self.menu_action_update)
            self.menu_action_list.add(self.menu_action_check)
            self.menu_action_list.add(self.menu_action_quit)

            self.menu_action.set_submenu(self.menu_action_list)

            self.menu_edit_clear_changes.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
            self.menu_edit_clear_changes.connect("activate", self.erasePackage)

            self.menu_edit_preference.set_image(gtk.image_new_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU))
            self.menu_edit_preference.connect("activate", Preferences.runPreferences, self)

            self.menu.add(self.menu_edit)

            self.menu_edit_list.add(self.menu_edit_clear_changes)
            self.menu_edit_list.add(self.menu_edit_preference)

            self.menu_edit.set_submenu(self.menu_edit_list)
            self.menu_help_about.set_image(gtk.image_new_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU))
            self.menu_help_about.connect("activate", self.aboutWindow)

            self.menu.add(self.menu_help)

            self.menu_help_list.add(self.menu_help_about)

            self.menu_help.set_submenu(self.menu_help_list)

            # ------------------------------------------------------------------
            #       Barre d'outils
            # ------------------------------------------------------------------

            self.outils.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            self.outils.set_style(gtk.TOOLBAR_ICONS)

            self.outils.insert_stock(gtk.STOCK_APPLY, _("Apply changes"), None, self.installWindow, self, 0)
            self.outils.insert_stock(gtk.STOCK_REFRESH, _("Update databases"), None, Package.updateDatabase, self, 2)
            self.outils.insert_space(3)
            self.texteRecherche.set_icon_from_stock(1, gtk.STOCK_CLEAR)
            self.texteRecherche.connect("activate", self.search, gtk.RESPONSE_OK)
            self.texteRecherche.connect("icon-press", self.eraseSearch)
            self.texteRecherche.grab_focus()
            self.outils.insert_widget(self.texteRecherche, _("Write your search here"), None, 4)
            self.outils.insert_stock(gtk.STOCK_FIND, _("Search"), None, self.search, None, 5)
            self.outils.insert_space(6)
            self.outils.insert_stock(gtk.STOCK_PREFERENCES, _("Preferences"), None, Preferences.runPreferences, self, 7)
            self.outils.insert_stock(gtk.STOCK_QUIT, _("Quit"), None, self.closeWindow, None, 8)

            # ------------------------------------------------------------------
            #       Liste des dépôts
            # ------------------------------------------------------------------

            # Ajout des dépôts
            self.addRepos()

            self.labelSelectionDepots.set_alignment(0.05,0.5)
            self.listeSelectionDepots.connect('changed', self.changeRepo, self)
            self.grilleSelectionDepots.set_border_width(2)

            # ------------------------------------------------------------------
            #       Colonnes des groupes
            # ------------------------------------------------------------------

            #~ self.listeColonneGroupes.clear()

            # Ajout des groupes en fonction du dépôt initial
            self.addGroups()

            self.colonneGroupes.set_headers_visible(True)
            self.colonneGroupes.set_size_request(180,0)
            self.colonneGroupes.set_search_column(0)

            self.colonneGroupesNom.set_sort_column_id(0)
            self.colonneGroupesNom.pack_start(self.celluleGroupesNom, True)
            self.colonneGroupesNom.add_attribute(self.celluleGroupesNom, 'text', 0)
            self.colonneGroupes.append_column(self.colonneGroupesNom)

            self.defilementGroupes.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.defilementGroupes.add(self.colonneGroupes)
            self.defilementGroupes.set_border_width(2)
            self.defilementGroupes.set_resize_mode(gtk.RESIZE_PARENT)

            self.selectionGroupe = self.colonneGroupes.get_selection()
            self.selectionGroupe.connect('changed', self.selectGroup, self.listeColonneGroupes)
            self.grilleDepotGroupes.set_border_width(4)

            # ------------------------------------------------------------------
            #       Colonnes des paquets
            # ------------------------------------------------------------------

            self.listeColonnePaquets.clear()
            self.listeColonnePaquets.set_sort_column_id(2, gtk.SORT_ASCENDING)

            self.colonnePaquets.set_headers_visible(True)
            self.colonnePaquets.set_search_column(2)

            self.colonnePaquetsCheckbox.set_sort_column_id(0)
            self.colonnePaquetsImage.set_sort_column_id(1)
            self.colonnePaquetsNom.set_min_width(300)
            self.colonnePaquetsNom.set_sort_column_id(2)
            self.colonnePaquetsVersionActuelle.set_sort_column_id(3)
            self.colonnePaquetsVersionDisponible.set_sort_column_id(4)

            self.cellulePaquetsCheckbox.set_property('active', 1)
            self.cellulePaquetsCheckbox.set_property('activatable', True)
            self.cellulePaquetsCheckbox.connect('toggled', self.checkPackage, self.colonnePaquets)

            self.colonnePaquetsCheckbox.pack_start(self.cellulePaquetsCheckbox, True)
            self.colonnePaquetsCheckbox.add_attribute(self.cellulePaquetsCheckbox, 'active', 0)
            self.colonnePaquetsImage.pack_start(self.cellulePaquetsImage, False)
            self.colonnePaquetsImage.add_attribute(self.cellulePaquetsImage, 'stock_id', 1)
            self.colonnePaquetsNom.pack_start(self.cellulePaquetsNom, True)
            self.colonnePaquetsNom.add_attribute(self.cellulePaquetsNom, 'text', 2)
            self.colonnePaquetsVersionActuelle.pack_start(self.cellulePaquetsVersionActuelle, True)
            self.colonnePaquetsVersionActuelle.add_attribute(self.cellulePaquetsVersionActuelle, 'text', 3)
            self.colonnePaquetsVersionDisponible.pack_start(self.cellulePaquetsVersionDisponible, True)
            self.colonnePaquetsVersionDisponible.add_attribute(self.cellulePaquetsVersionDisponible, 'text', 4)

            self.colonnePaquets.append_column(self.colonnePaquetsCheckbox)
            self.colonnePaquets.append_column(self.colonnePaquetsImage)
            self.colonnePaquets.append_column(self.colonnePaquetsNom)
            self.colonnePaquets.append_column(self.colonnePaquetsVersionActuelle)
            self.colonnePaquets.append_column(self.colonnePaquetsVersionDisponible)

            self.defilementPaquets.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.defilementPaquets.add(self.colonnePaquets)
            self.defilementPaquets.set_border_width(4)

            self.selectionPaquet = self.colonnePaquets.get_selection()
            self.selectionPaquet.connect('changed', self.selectPackage, self.listeColonnePaquets)

            #~ self.zonePaquets.add(self.defilementPaquets)
            #~ self.zonePaquets.set_border_width(4)

            # ------------------------------------------------------------------
            #       Informations sur le paquet
            # ------------------------------------------------------------------

            self.listeInformations.set_headers_visible(False)
            self.listeInformations.set_hover_selection(False)

            self.celluleLabelInformations.set_property('weight', pango.WEIGHT_BOLD)

            self.colonneLabelInformations.pack_start(self.celluleLabelInformations, True)
            self.colonneLabelInformations.add_attribute(self.celluleLabelInformations, "text", 0)
            self.colonneValeurInformations.pack_start(self.celluleValeurInformations, True)
            self.colonneValeurInformations.add_attribute(self.celluleValeurInformations, "text", 1)

            self.celluleValeurInformations.set_property('wrap-mode', pango.WRAP_WORD)
            self.celluleValeurInformations.set_property('editable', True)

            self.listeInformations.append_column(self.colonneLabelInformations)
            self.listeInformations.append_column(self.colonneValeurInformations)
            self.listeInformations.set_model(self.contenuInformations)

            self.defilementInformations.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.defilementInformations.add(self.listeInformations)
            self.defilementInformations.set_border_width(4)

            self.listePaquet.set_headers_visible(False)
            self.listePaquet.set_hover_selection(False)

            self.celluleLabelPaquet.set_property('weight', pango.WEIGHT_BOLD)

            self.colonneLabelPaquet.pack_start(self.celluleLabelPaquet, True)
            self.colonneLabelPaquet.add_attribute(self.celluleLabelPaquet, "text", 0)
            self.colonneValeurPaquet.pack_start(self.celluleValeurPaquet, True)
            self.colonneValeurPaquet.add_attribute(self.celluleValeurPaquet, "text", 1)

            self.celluleValeurPaquet.set_property('wrap-mode', pango.WRAP_WORD)
            self.celluleValeurPaquet.set_property('editable', True)

            self.listePaquet.append_column(self.colonneLabelPaquet)
            self.listePaquet.append_column(self.colonneValeurPaquet)
            self.listePaquet.set_model(self.contenuPaquet)

            self.defilementPaquet.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.defilementPaquet.add(self.listePaquet)
            self.defilementPaquet.set_border_width(4)

            #~ self.listeFichiers.set_editable(False)
            #~ self.listeFichiers.set_cursor_visible(False)

            #~ self.defilementFichiers.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            #~ self.defilementFichiers.add(self.listeFichiers)
            #~ self.defilementFichiers.set_border_width(4)

            self.listeFichiers.set_headers_visible(False)
            self.listeFichiers.set_hover_selection(False)

            self.colonneFichiers.pack_start(self.celluleFichiers, True)
            self.colonneFichiers.add_attribute(self.celluleFichiers, "text", 0)

            self.celluleFichiers.set_property('editable', False)

            self.listeFichiers.append_column(self.colonneFichiers)
            self.listeFichiers.set_model(self.contenuFichiers)

            self.defilementFichiers.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.defilementFichiers.add(self.listeFichiers)
            self.defilementFichiers.set_border_width(4)

            self.listeJournal.set_editable(False)
            self.listeJournal.set_cursor_visible(False)

            self.defilementJournal.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.defilementJournal.add(self.listeJournal)
            self.defilementJournal.set_border_width(4)

            self.listeFrugalbuild.set_editable(False)
            self.listeFrugalbuild.set_cursor_visible(False)

            self.defilementFrugalbuild.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.defilementFrugalbuild.add(self.listeFrugalbuild)
            self.defilementFrugalbuild.set_border_width(4)

            self.zoneInformations.set_tab_pos(gtk.POS_LEFT)
            self.zoneInformations.append_page(self.defilementInformations, self.labelInformations)
            self.zoneInformations.append_page(self.defilementPaquet, self.labelPaquet)
            self.zoneInformations.append_page(self.defilementFichiers, self.labelFichiers)
            self.zoneInformations.append_page(self.defilementJournal, self.labelJournal)

            # Affiche la zone "FrugalBuild" uniquement si l'option est activé
            if self.developementMode:
                self.zoneInformations.append_page(self.defilementFrugalbuild, self.labelFrugalbuild)

            self.zoneInformations.set_border_width(4)
            self.zoneInformations.set_resize_mode(gtk.RESIZE_PARENT)

            # ------------------------------------------------------------------
            #       Intégration des widgets
            # ------------------------------------------------------------------

            # Liste des dépôts
            self.grilleSelectionDepots.attach(self.labelSelectionDepots, 0, 1, 0, 1, yoptions=gtk.FILL)
            self.grilleSelectionDepots.attach(self.listeSelectionDepots, 0, 1, 1, 2, yoptions=gtk.FILL)
            self.grilleDepotGroupes.attach(self.grilleSelectionDepots, 0, 1, 0, 1, yoptions=gtk.FILL)

            # Liste des groupes
            self.grilleDepotGroupes.attach(self.defilementGroupes, 0, 1, 1, 2)

            # Liste des paquets
            self.grilleColonnePaquets.attach(self.grilleDepotGroupes, 0, 1, 0, 1, xoptions=gtk.FILL)
            self.grilleColonnePaquets.attach(self.grillePaquetsInformations, 1, 2, 0, 1)

            # Informations des paquets
            #~ self.grillePaquetsInformations.add1(self.zonePaquets)
            self.grillePaquetsInformations.add1(self.defilementPaquets)
            self.grillePaquetsInformations.add2(self.zoneInformations)

            # Grille principale
            self.grille.attach(self.menu, 0, 1, 0, 1, yoptions=gtk.FILL)
            self.grille.attach(self.outils, 0, 1, 1, 2, yoptions=gtk.FILL)
            self.grille.attach(self.grilleColonnePaquets, 0, 1, 2, 3)
            self.grille.attach(self.barreStatus, 0, 1, 3, 4, yoptions=gtk.FILL)

            self.fenetre.add(self.grille)
            self.fenetre.show_all()

            self.getUpdateList()
        else:
            try:
                self.informationWindow(_("Error"), _("Window is under limit size"))
            except:
                pass

            sys.exit("[ERROR] - " + _("Window is under limit size"))


    def runWindow (self):
        """
        Affiche l'interface
        """

        gtk.main()


    def closeWindow (self, interface):
        """
        Termine pyFPM
        """

        gtk.main_quit()


    def getUpdateList (self):
        """
        Récupérer la liste des mises à jour
        """

        self.printDebug("DEBUG", _("Get the update packages list"))

        if len(self.listeMiseAJourPacman) > 0:
            self.listeMiseAJourPacman = []

        listePaquetsMiseAJour = Package.getUpdateList()

        if listePaquetsMiseAJour > 0:
            for element in listePaquetsMiseAJour:
                self.listeMiseAJourPacman.append(element)

        # Affiche les mises à jour si l'option est activé
        if Config.readConfig("pyfpm", "startupdate") == "true":
            self.updateWindow()


    def addRepos (self):
        """
        Récupère les dépots disponible sur le système
        """

        listeDepot = Package.getRepoList()

        # Met le dépôt du système en choix principal
        index = Package.getIndexFromRepo()

        # Intègre les dépôts dans la liste
        for element in listeDepot:
            if element == "local":
                element = _("Installed packages")

            self.listeSelectionDepots.append_text(element)

        # Met le dépôt du système en actif
        self.listeSelectionDepots.set_active(index)


    def changeRepo (self, *args):
        """
        Permet de changer de dépôt
        """

        self.listeColonnePaquets.clear()
        self.listeColonneGroupes.clear()
        self.addGroups()

        self.updateStatusbar(_("Change repository to %s") % str(self.listeSelectionDepots.get_active_text()))


    def updateStatusbar (self, texte):
        """
        Changer le texte inscrit dans la barre inférieur
        """

        self.barreStatus.push(0, str(texte))


    def eraseInterface (self):
        """
        Efface l'ensemble de l'interface
        """

        modele = self.listeSelectionDepots.get_model()
        modele.clear()
        self.listeSelectionDepots.set_model(modele)

        self.listeColonneGroupes.clear()
        self.listeColonnePaquets.clear()

        self.contenuInformations.clear()
        self.contenuPaquet.clear()

        self.updateStatusbar("")


    def resize (self, *args):
        """
        Redimensionne la largueur de celluleValeur afin que le texte
        s'adapte à la fenêtre
        """

        self.celluleValeurInformations.set_property("wrap-width", self.fenetre.get_size()[0]/2)
        self.celluleValeurPaquet.set_property("wrap-width", self.fenetre.get_size()[0]/2)
        self.colonnePaquetsNom.set_min_width(self.fenetre.get_size()[0]/2)
        self.colonnePaquets.set_size_request(0, self.fenetre.get_size()[1]/2)


    @staticmethod
    def refresh ():
        """
        Rafraichit l'interface quand des changements ont lieux
        """

        try :
            while gtk.events_pending():
                gtk.main_iteration_do(False)
        except:
            pass


    def addGroups (self):
        """
        Ajouter les groupes dans l'interface
        """

        self.listeColonnePaquets.clear()
        ensembleGroupes = Package.getGroupsList(self.listeSelectionDepots.get_active())

        for nom in ensembleGroupes:
            # Affiche les groupes secondaires si l'option est activé
            if Config.readConfig("pyfpm", "useprohibategroups") == "false":
                if not nom in self.listeGroupesProhibes:
                    self.listeColonneGroupes.append([nom])
            else:
                self.listeColonneGroupes.append([nom])

        self.printDebug("DEBUG", str(len(self.listeColonneGroupes)) + " groups append")


    def selectGroup (self, selection, modele):
        """
        Récupère les informations concernant le groupe actuellement
        sélectionné.
        """

        try:
            choix = selection.get_selected()
            treeiter = choix[1]

            modele = self.colonneGroupes.get_model()

            nomGroupe = modele.get_value(treeiter, 0)

            self.recherche_mode = False
            self.recherche_nom = ""

            self.getPackages(nomGroupe)
        except:
            return True


    def getPackages (self, nomGroupe):
        """
        Obtenir les paquets correspondant au groupe sélectionné
        """

        paquets = Package.getPackagesList(self.listeSelectionDepots.get_active(), nomGroupe)
        self.addPackages(paquets)

        self.printDebug("DEBUG", str(len(paquets)) + " packages append")


    def addPackages (self, paquets, recherche = False):
        """
        Ajoute les paquets dans l'interface
        """

        objetTrouve = 0
        n = 0
        self.listeColonnePaquets.clear()

        listePaquetsInstalles = Package.getInstalledList()

        # Supprime le mode de tri des colonnes
        modeleColonnePaquets = self.colonnePaquets.get_model()
        modeleColonnePaquets.set_default_sort_func(lambda *args: -1)
        modeleColonnePaquets.set_sort_column_id(-1, gtk.SORT_ASCENDING)

        self.colonnePaquets.set_model(None)
        self.colonnePaquets.freeze_child_notify()

        for element in paquets:
            # Une recherche n'est pas composé de la même manière qu'une sélection normal
            if not recherche:
                paquet = Package.getPackageInfo(element)
            elif recherche:
                paquet = Package.getPackageInfo(element[1])

            nomPaquet = paquet.get("name")
            versionPaquet = paquet.get("version")

            #~ if nomPaquet in listePaquetsInstalles:
            if Package.checkPackageInstalled(nomPaquet, versionPaquet):
                # Le paquet est installé dans la version correspondante
                objetTrouve = 1
                image = " "
                nouvelleVersion = " "
            elif str(nomPaquet) in self.listeMiseAJourPacman or str(nomPaquet) in listePaquetsInstalles:
                # Le paquet peut être mis à jour
                objetTrouve = 1
                if str(nomPaquet) in self.listeInstallationPacman:
                    # Le paquet est dans la liste des paquets à installer
                    image = gtk.STOCK_ADD
                elif str(nomPaquet) in self.listeMiseAJourPacman:
                    image = gtk.STOCK_REFRESH
                elif str(nomPaquet) in listePaquetsInstalles:
                    image = gtk.STOCK_REDO

                # On récupère la valeur de la version de mise à jour
                nouvelleVersion = versionPaquet
                pointerPaquet = Package.getPackagePointer(nomPaquet)
                paquetInstalle = Package.getPackageInfo(pointerPaquet)
                versionPaquet = paquetInstalle.get("version")
            else:
                # Le paquet n'est pas installé
                objetTrouve = 0
                image = " "
                nouvelleVersion = " "

            if nomPaquet in self.listeInstallationPacman:
                # Le paquet est dans la liste des paquets à installer
                objetTrouve = 1
                if not nomPaquet in self.listeMiseAJourPacman:
                    image = gtk.STOCK_ADD
            elif nomPaquet in self.listeSuppressionPacman:
                # Le paquet est dans la liste des paquets à supprimer
                objetTrouve = 0
                image = gtk.STOCK_REMOVE

            if recherche and len(Package.getRepoList()) > 2:
                # Dans le cas d'une recherche on préfixe avec [<nom_dépôt>]
                nomPaquet = "[" + element[0] + "] " + nomPaquet

            modeleColonnePaquets.append([objetTrouve, image, nomPaquet, versionPaquet, nouvelleVersion])

            n += 1
            if (n / 100 == 1):
                self.updateStatusbar(_("Load packages"))
                self.refresh()
                n = 0

        self.colonnePaquets.set_model(modeleColonnePaquets)
        self.colonnePaquets.thaw_child_notify()
        self.refresh()
        self.updateStatusbar(_("%s packages were found") % str(len(self.listeColonnePaquets)))


    def selectPackage (self, selection, modele):
        """
        Récupère les informations concernant le paquet actuellement
        sélectionné.
        """

        choix = selection.get_selected()

        if choix == ():
            return

        tableau = choix[1]

        try :
            nomPaquet, versionPaquet = modele.get(tableau, 2, 3)
            self.getPackageInfo(nomPaquet, versionPaquet)
        except :
            return True

        return True


    def getPackageInfo (self, nomPaquet, versionPaquet):
        """
        Obtient les détails du paquet
        """

        objetTrouve = 0
        depotRecherche = ""
        modeRecherche = False

        if nomPaquet.find("]") != -1:
            # Dans le cas d'une recherche, il est nécessaire d'enlever le préfixe [<nom_dépôt>]
            depotRecherche = nomPaquet[nomPaquet.find("[") + 1:nomPaquet.find("]")].strip()
            nomPaquet = nomPaquet[nomPaquet.find("]") + 1:].strip()
            modeRecherche = True

        self.updateStatusbar(_("Get informations about %s") % nomPaquet)

        texte = ""

        self.contenuInformations.clear()
        self.contenuPaquet.clear()
        self.contenuFichiers.clear()

        # Récupère les informations depuis local si le paquet est installé
        if Package.checkPackageInstalled(nomPaquet, versionPaquet):
            depot = 0
        else:
            if not modeRecherche:
                depot = int(self.listeSelectionDepots.get_active())
            else:
                # Il s'agit d'une recherche donc on prend le dépot entre []
                depot = Package.getRepoList().index(depotRecherche)

        # Récupération des informations
        pointerPaquet = Package.getPackagePointer(nomPaquet, depot)
        infoPaquet = Package.getPackageInfo(pointerPaquet)

        self.contenuInformations.append(None, [_("Name"), infoPaquet.get("name")])
        self.contenuInformations.append(None, [_("Version"), infoPaquet.get("version")])

        # [TODO] - Améliorer l'affichage
        self.contenuInformations.append(None, [_("Description"), infoPaquet.get("description").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").encode('ascii', 'replace')])

        # Liste des groupes
        groupes = infoPaquet.get("groups")
        if len(groupes) > 0:
            self.contenuInformations.append(None, [_("Groups"), ', '.join(groupes)])

        # Affichage du SHA1SUMS du paquet
        if infoPaquet.get("name") in self.listeMiseAJourPacman:
            self.contenuPaquet.append(None, [_("SHA1SUMS"), Lang.translate("package_update_available")])
        else:
            if self.listeSelectionDepots.get_active() != 0:
                depot = self.listeSelectionDepots.get_active()
            else:
                listeDepot = Package.getIndexFromRepo()

            self.contenuPaquet.append(None, [_("SHA1SUMS"), str(Package.getSha1sums(infoPaquet.get("name"), int(depot)))])

        # Affiche des informations supplémentaires si le paquet est installé
        if Package.checkPackageInstalled(nomPaquet, versionPaquet):
            self.contenuInformations.append(None, [_("url"), str(infoPaquet.get("url"))])

            self.contenuPaquet.append(None, [_("Install date"), str(infoPaquet.get("install_date"))])
            self.contenuPaquet.append(None, [_("Size"), str(format(float(long(infoPaquet.get("size"))/1024)/1024, '.2f')) + " MB"])
            self.contenuPaquet.append(None, [_("Packager"), str(infoPaquet.get("packager").encode('ascii', 'replace'))])
        else:
            self.contenuPaquet.append(None, [_("Compress size"), str(format(float(long(infoPaquet.get("compress_size"))/1024)/1024, '.2f')) + " MB"])
            self.contenuPaquet.append(None, [_("Uncompress size"), str(format(float(long(infoPaquet.get("uncompress_size"))/1024)/1024, '.2f')) + " MB"])

        # Liste des dépendances
        depends = infoPaquet.get("depends")
        if len(depends) > 0:
            self.contenuInformations.append(None, [_("Depends"), ', '.join(depends)])

        # Liste des paquets ajoutés
        provides = infoPaquet.get("provides")
        if len(provides) > 0:
            self.contenuPaquet.append(None, [_("Provides"), ', '.join(provides)])

        # Liste des paquets remplacés
        replaces = infoPaquet.get("replaces")
        if len(replaces) > 0:
            self.contenuPaquet.append(None, [_("Replaces"), ', '.join(replaces)])

        # Liste des dépendances inverses
        required = infoPaquet.get("required_by")
        if len(required) > 0:
            self.contenuPaquet.append(None, [_("Required_by"), ', '.join(required)])

        # Liste des paquets en conflit
        conflits = infoPaquet.get("conflits")
        if len(conflits) > 0:
            self.contenuPaquet.append(None, [_("Conflits"), ', '.join(conflits)])

        # Liste des fichiers inclus dans le paquet
        if Package.checkPackageInstalled(nomPaquet, versionPaquet):
            listeFichiers = Package.getFileFromPackage(nomPaquet)
            #~ chemin = []
            #~ racine = self.contenuFichiers.append(None, ['/'])
            for element in listeFichiers:
                self.contenuFichiers.append(None, ['/' + str(element)])
                #~ chaine = element.split('/')
                #~ if len(chaine[len(chaine - 1)] == 0):
                    #~ if len(chaine) == 1:
                        # Dossier de niveau 1
                        #~ self.contenuFichiers.append(racine, ['/' + str(chaine[len(chaine - 1)])])

        else:
            self.contenuFichiers.append(None, [_("No info")])

        # Changelog du paquet
        texte = ""
        texteBuffer = self.listeJournal.get_buffer()

        if Package.checkPackageInstalled(nomPaquet, versionPaquet):
            try:
                listeDepot = Package.getRepoList()
                journal = "/var/lib/pacman-g2/" + listeDepot[0] + "/" + nomPaquet + "-" + versionPaquet + "/changelog"
                if os.path.exists(journal) == True:
                    file = codecs.open(journal, "r", "iso-8859-15")
                    for element in file:
                        if element != "":
                            texte += "\t" + element
                    file.close()
                else:
                    texte = "\t" + _("No file found")
            except:
                texte = "\t" + _("Error")
        else:
            texte = "\t" + _("No info")

        texteBuffer.set_text(texte)

        # Si le mode développement est actif, le frugalbuild est récupéré
        #~ if self.developementMode:
            #~ texte = ""
            #~ texteBuffer = self.listeFrugalbuild.get_buffer()

            #~ try:
                #~ if self.getFrugalBuild(nomPaquet, infoPaquet.get("groups")):
                    #~ if os.path.exists("/tmp/frugalbuild") == True:
                        #~ file = codecs.open("/tmp/frugalbuild", "r", "utf-8")
                        #~ for element in file:
                            #~ if element != "":
                                #~ texte += " " + element
                        #~ file.close()
            #~ except:
                #~ texte = " " + _("No file found")

            #~ texteBuffer.set_text(texte)


    def getFrugalBuild (self, nomPaquet, listeGroupes):
        """
        Récupère le FrugalBuild via le git de Frugalware
        """

        listeDepot = Package.getRepoList()

        if "frugalware" in listeDepot:
            index = "frugalware-stable"
        elif "frugalware-current" in listeDepot:
            index = "frugalware-current"

        listeGroupesProhibes = ['-extensions','adesklets-desklets','amsn-plugins','avidemux-plugin-cli','avidemux-plugin-gtk','avidemux-plugin-qt','chroot-core','core','cinnamon-desktop','devel-core','directfb-drivers','e17-apps','e17-misc','fatrat-plugins','firefox-extensions','geda-suite','gift-plugins','gnome-minimal','hk_classes-drivers','jdictionary-plugins','kde-apps','kde-build','kde-core','kde-doc','kde-docs','kde-minimal','kde-runtime','lxde-desktop','lxde-extra','pantheon-desktop','misc-fonts','phonon-backend','pidgin-plugins','qt4-libs','sawfish-scripts','seamonkey-addons','thunderbird-extensions','tuxcmd-plugins','wmaker-dockapps','xfce4-core','xfce4-goodies','xorg-apps','xorg-core','xorg-data','xorg-doc','xorg-drivers','xorg-fonts','xorg-libs','xorg-proto','xorg-util']

        for element in listeGroupes:
            if not element in listeGroupesProhibes:
                nomGroupe = element
                break

        #~ url = "http://www7.frugalware.org/pub/frugalware/" + index + "/source/" + nomGroupe + "/" + nomPaquet + "/FrugalBuild"

        #~ try:
            #~ if File.verifierErreurUrl(url) == 1:
                #~ fichierFB = urllib.urlopen(url)
                #~ fichierLocal = open("/tmp/frugalbuild", 'w')
                #~ fichierLocal.write(fichierFB.read())
                #~ fichierFB.close()
                #~ fichierLocal.close()
                #~ Event.printDebug("DEBUG", _("Download complete") + " " + url)
                #~ resultat = True
            #~ else:
                #~ Event.printDebug("ERROR", _("Download failed with 404 error") + " " + url)
        #~ except:
            #~ Event.printDebug("ERROR", _("Download failed") + " " + url)
            #~ resultat = False
            #~ pass

        return resultat


    def checkPackage (self, cell_renderer, colonne, liste):
        """
        Permet de gérer les paquets à installer/desinstaller via deux
        tableau qui se mettent à jour en fonction du cochage.
        """

        # On met la checkbox à la valeur contraire (1 -> 0, 0 -> 1)
        modele = liste.get_model()
        modele[colonne][0] = not modele[colonne][0]

        nomPaquet = modele[colonne][2]

        if nomPaquet.find("]") != -1:
            # Dans le cas d'une recherche, il est nécessaire d'enlever le préfixe [<nom_dépôt>]
            nomPaquet = nomPaquet[nomPaquet.find("]") + 1:].strip()

        elementAjouter = self.checkData(self.listeInstallationPacman, nomPaquet)
        elementEnlever = self.checkData(self.listeSuppressionPacman, nomPaquet)

        listePaquetsInstalles = Package.getInstalledList()

        if modele[colonne][0] == 0:
            # Le paquet en question à été décoché
            if Package.checkPackageInstalled(nomPaquet, modele[colonne][3]) :
                # Le paquet en question est installé
                if elementEnlever == 0:
                    # Le paquet est mis dans la liste des paquets à supprimer
                    self.listeSuppressionPacman.append(nomPaquet)
                    modele[colonne][1] = gtk.STOCK_REMOVE
            else:
                if elementAjouter != 0:
                    # Le paquet est enlevé de la liste des paquets à installer
                    self.listeInstallationPacman.remove(elementAjouter)
                    modele[colonne][1] = " "

        else:
            # Le paquet en question à été coché
            if Package.checkPackageInstalled(nomPaquet, modele[colonne][3]):
                # Le paquet en question est installé
                if elementEnlever != 0:
                    # Le paquet est enlevé de la liste des paquets à supprimer
                    self.listeSuppressionPacman.remove(elementEnlever)
                    if modele[colonne][2] in self.listeMiseAJourPacman:
                        modele[colonne][1] = gtk.STOCK_REFRESH
                    elif len(modele[colonne][4]) > 1:
                        modele[colonne][1] = gtk.STOCK_REDO
                    else:
                        modele[colonne][1] = " "
            else:
                if elementAjouter == 0:
                    # Le paquet est mis dans la liste des paquets à installer
                    self.listeInstallationPacman.append(nomPaquet)
                    modele[colonne][1] = gtk.STOCK_ADD


    def erasePackage (self, *args):
        """
        Remet à zéro la liste des paquets à installer et désinstaller
        """

        self.listeInstallationPacman = []
        self.listeSuppressionPacman  = []

        try:
            self.selectionGroupe = self.colonneGroupes.get_selection()
            self.selectionnerGroupe(self.selectionGroupe, self.listeColonneGroupes)
        except:
            pass

        self.updateStatusbar(_("Clear changes done"))


    def search (self, *args):
        """
        Affiche l'ensemble des paquets correspondant à la recherche
        """

        # La recherche n'est possible que si la chaine est non nulle et différente de celle précédement utilisée
        if len(self.texteRecherche.get_text()) > 0 and self.texteRecherche.get_text() != self.recherche_nom:
            self.listeColonnePaquets.clear()
            objetRechercher = self.texteRecherche.get_text()

            paquets = Package.searchPackage(objetRechercher)

            self.printDebug("INFO", _("%(nbr)s search package for %(search)s") % {'nbr': str(len(paquets)), 'search': objetRechercher})
            self.updateStatusbar(_("%(nbr)s search package for %(search)s") % {'nbr': str(len(paquets)), 'search': objetRechercher})

            self.recherche_mode = True
            self.recherche_nom = objetRechercher

            if len(paquets) > 0:
                # Si la liste contient des paquets on lance l'ajout dans l'interface
                self.addPackages(paquets, recherche = True)

            # On efface le critère de recherche
            #~ self.eraseSearch()

            try:
                path, colonne = self.colonneGroupes.get_cursor()
                self.colonneGroupes.get_selection().unselect_path(path)
            except:
                pass


    def eraseSearch (self, *args):
        """
        Efface la zone de recherche
        """

        self.texteRecherche.set_text("")


    def checkData (self, liste, donnee):
        """
        Vérifie si donnee est dans liste
        """

        objetTrouve = 0

        for element in liste:
            if donnee == element:
                objetTrouve = element
                break

        return objetTrouve


    def checkUser (self):
        """
        Verifie quel utilisateur est en train d'utiliser pyFPM
        """

        if not os.geteuid() == 0:
            return 0

        return 1


    def printDebug (self, typeErreur, erreur):
        """
        Affiche une sortie terminal
        """

        modeDebug = True

        if typeErreur == "DEBUG":
            color = "\033[0;32m"
        elif typeErreur == "ERROR":
            color = "\033[0;34m"
        elif typeErreur == "INFO":
            color = "\033[0;36m"
        else:
            color = "\033[0m"

        if modeDebug or typeErreur != "INFO":
            print (str(color) + "[" + typeErreur + "]\t\033[0m" + str(erreur))


# ------------------------------------------------------------------------------------------------------------
#
#                Fenêtres supplémentaires
#
# ------------------------------------------------------------------------------------------------------------

    def aboutWindow (self, widget, *event):
        """
        Affiche la fenêtre A propos commune à toutes les applications
        """

        about = gtk.AboutDialog()
        logo = gtk.gdk.pixbuf_new_from_file("./data/icons/96x96/pyfpm.png")

        about.set_program_name("pyFPM")
        about.set_version("(Inky)")
        about.set_comments(_("A pacman-g2 front-end for Frugalware Linux"))
        about.set_copyright("(C) 2012-2013 Frugalware Developer Team (GPL)")
        about.set_authors(["Gaetan Gourdin (bouleetbil)", "Aurélien Lubert (PacMiam)"])
        about.set_artists(["Aurélien Lubert (PacMiam)"])
        about.set_translator_credits("fr_FR - Anthony Jorion (Pingax)")
        about.set_license("Ce programme est un logiciel libre, vous pouvez le redistribuer et/ou le modifier conformément aux dispositions de la Licence Publique Générale GNU, telle que publiée par la Free Software Foundation.")
        about.set_wrap_license(True)
        about.set_website("http://www.frugalware.org")
        about.set_logo(logo)

        about.run()

        about.destroy()


    def informationWindow (self, titre, texte):
        """
        Affiche une fenêtre d'information
        """

        information = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, texte)

        information.set_title(titre)
        information.set_default_response(gtk.RESPONSE_OK)

        information.run()

        information.destroy()


    def installWindow (self, widget, *event):
        """
        Affiche les modifications à effectuer sur les paquets
        """

        listeDepot = Package.getRepoList()

        # Récupère l'index du dépôt initial
        if "frugalware" in listeDepot:
            index = listeDepot.index("frugalware")
        elif "frugalware-current" in listeDepot:
            index = listeDepot.index("frugalware-current")

        if self.recherche_mode == False:
            # On réaffiche les paquets du groupe sélectionné
            self.selectionGroupe = self.colonneGroupes.get_selection()
            self.selectGroup(self.selectionGroupe, self.listeColonneGroupes)
        else:
            # Dans le cas d'une recherche, on réaffiche l'ensemble
            self.texteRecherche.set_text(self.recherche_nom)
            self.search()

        if len(self.listeInstallationPacman) != 0 or len(self.listeSuppressionPacman):
            # On tri les paquets des deux listes
            self.listeInstallationPacman.sort()
            self.listeSuppressionPacman.sort()

            fenetre = gtk.Dialog(_("pyFPM"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_APPLY, gtk.RESPONSE_APPLY))
            texteFenetre = gtk.Label(_("Changements to do"))

            grilleInstallation = gtk.Table(1,3)
            zoneInstallation = gtk.Frame(_("To install packages"))
            listeInstallation = gtk.TreeStore(str, str)
            colonnesInstallation = gtk.TreeView()
            colonneInstallationNom = gtk.TreeViewColumn()
            colonneInstallationTaille = gtk.TreeViewColumn()
            celluleInstallationNom = gtk.CellRendererText()
            celluleInstallationTaille = gtk.CellRendererText()
            defilementInstallation = gtk.ScrolledWindow()
            tailleInstallation = gtk.Label("")
            self.verifierDependancesInstallation = gtk.CheckButton(_("Skip check dependances"))
            self.seulementTelecharger = gtk.CheckButton(_("Download only"))

            grilleSuppression = gtk.Table(1,3)
            zoneSuppression = gtk.Frame(_("To remove packages"))
            listeSuppression = gtk.TreeStore(str, str)
            colonnesSuppression = gtk.TreeView()
            colonneSuppressionNom = gtk.TreeViewColumn()
            celluleSuppressionNom = gtk.CellRendererText()
            colonneSuppressionTaille = gtk.TreeViewColumn()
            celluleSuppressionTaille = gtk.CellRendererText()
            defilementSuppression = gtk.ScrolledWindow()
            tailleSuppression = gtk.Label("")
            self.verifierDependancesSuppression = gtk.CheckButton(_("Skip check dependances"))

            fenetre.set_default_response(gtk.RESPONSE_OK)
            fenetre.set_size_request(400, 400)

            texteFenetre.set_alignment(-1, 0.5)

            colonnesInstallation.set_headers_visible(False)
            colonnesInstallation.set_hover_selection(True)
            colonnesInstallation.expand_all()

            colonneInstallationNom.pack_start(celluleInstallationNom, True)
            colonneInstallationNom.add_attribute(celluleInstallationNom, "text", 0)

            colonneInstallationTaille.pack_start(celluleInstallationTaille, True)
            colonneInstallationTaille.add_attribute(celluleInstallationTaille, "text", 1)

            colonnesInstallation.append_column(colonneInstallationNom)
            colonnesInstallation.append_column(colonneInstallationTaille)
            colonnesInstallation.set_model(listeInstallation)

            defilementInstallation.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            defilementInstallation.add(colonnesInstallation)
            defilementInstallation.set_border_width(4)

            grilleInstallation.attach(defilementInstallation, 0, 1, 0, 1)
            grilleInstallation.attach(tailleInstallation, 0, 1, 1, 2, yoptions=gtk.FILL, xoptions=gtk.FILL)
            grilleInstallation.attach(self.verifierDependancesInstallation, 0, 1, 2, 3, yoptions=gtk.FILL)
            grilleInstallation.attach(self.seulementTelecharger, 0, 1, 3, 4, yoptions=gtk.FILL)
            grilleInstallation.set_border_width(4)

            zoneInstallation.add(grilleInstallation)
            zoneInstallation.set_border_width(4)

            colonnesSuppression.set_headers_visible(False)
            colonnesSuppression.set_hover_selection(True)
            colonnesSuppression.expand_all()

            colonneSuppressionNom.pack_start(celluleSuppressionNom, True)
            colonneSuppressionNom.add_attribute(celluleSuppressionNom, "text", 0)

            colonneSuppressionTaille.pack_start(celluleSuppressionTaille, True)
            colonneSuppressionTaille.add_attribute(celluleSuppressionTaille, "text", 1)

            colonnesSuppression.append_column(colonneSuppressionNom)
            colonnesSuppression.append_column(colonneSuppressionTaille)
            colonnesSuppression.set_model(listeSuppression)

            defilementSuppression.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            defilementSuppression.add(colonnesSuppression)
            defilementSuppression.set_border_width(4)

            grilleSuppression.attach(defilementSuppression, 0, 1, 0, 1)
            grilleSuppression.attach(tailleSuppression, 0, 1, 1, 2, yoptions=gtk.FILL, xoptions=gtk.FILL)
            grilleSuppression.attach(self.verifierDependancesSuppression, 0, 1, 2, 3, yoptions=gtk.FILL)
            grilleSuppression.set_border_width(4)

            zoneSuppression.add(grilleSuppression)
            zoneSuppression.set_border_width(4)

            fenetre.vbox.pack_start(texteFenetre, expand=False)

            if len(self.listeInstallationPacman) != 0:
                # S'il y a des paquets à installer, on affiche la zone Installation
                valeurInstallation = 0
                for element in self.listeInstallationPacman:
                    if element.find("]") != -1:
                        # Dans le cas d'une recherche, il est nécessaire d'enlever le préfixe [<nom_dépôt>]
                        element = element[element.find("]") + 1:].strip()

                    paquet = Package.getPackagePointer(element, index)
                    infoPaquet = Package.getPackageInfo(paquet)

                    # Le nom de la taille à récupérer est différent si le paquet
                    # est installé ou pas
                    if Package.checkPackageInstalled(infoPaquet.get("name"), infoPaquet.get("version")):
                        size = "size"
                    else:
                        size = "compress_size"

                    listeInstallation.append(None, [element, str(format(float(long(infoPaquet.get(size))/1024)/1024, '.2f')) + " MB"])

                    valeurInstallation += float(long(infoPaquet.get(size))/1024)/1024

                tailleInstallation.set_text(_("Total size : %s MB") % str(format(valeurInstallation, '.2f')))
                fenetre.vbox.pack_start(zoneInstallation)

            if len(self.listeSuppressionPacman) != 0:
                # S'il y a des paquets à supprimer, on affiche la zone Suppression
                valeurSuppression = 0
                for element in self.listeSuppressionPacman:
                    if element.find("]") != -1:
                        # Dans le cas d'une recherche, il est nécessaire d'enlever le préfixe [<nom_dépôt>]
                        element = element[element.find("]") + 1:].strip()

                    paquet = Package.getPackagePointer(element, index)
                    infoPaquet = Package.getPackageInfo(paquet)
                    listeSuppression.append(None, [element, str(format(float(long(infoPaquet.get("size"))/1024)/1024, '.2f')) + " MB"])

                    valeurSuppression += float(long(infoPaquet.get("size"))/1024)/1024

                tailleSuppression.set_text(_("Total size : %s MB") % str(format(valeurSuppression, '.2f')))
                fenetre.vbox.pack_start(zoneSuppression)

            fenetre.show_all()
            choix = fenetre.run()

            if choix == gtk.RESPONSE_APPLY:
                # Lance l'installation/mise à jour/suppression des paquets sélectionnés
                fenetre.destroy()
                #~ Event.lancerInstallationPaquets(self)
                self.erasePackage()
            else:
                fenetre.destroy()
        else:
            self.barreStatus.push(0, _("No change"))


    def updateWindow (self, *args):
        """
        Prévient qu'il y a des mises à jour et propose de les installer
        """

        self.fenetre.set_sensitive(False)

        listeTmp = []

        if len(self.listeMiseAJourPacman) > 0:
            # Affiche les paquets dont une mise à jour est disponible
            for element in self.listeMiseAJourPacman:
                if not element in self.listeInstallationPacman:
                    # On ne récupère que ceux qui ne font pas partie de la
                    # liste des paquets à installer
                    listeTmp.append(element)

            if len(listeTmp) > 0:
                # Si la liste n'est pas vide
                miseajour = gtk.Dialog(_("Update system"), None, gtk.DIALOG_MODAL, (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT, gtk.STOCK_OK, gtk.RESPONSE_OK))

                texteInfo = gtk.Label(_("Update available"))
                listeInfo = gtk.TreeStore(str)
                colonnesInfo = gtk.TreeView()
                colonneInfoNom = gtk.TreeViewColumn()
                celluleInfo = gtk.CellRendererText()
                defilementInfo = gtk.ScrolledWindow()
                grille = gtk.Table(2,2)

                #~ miseajour.set_has_separator(True)
                miseajour.set_default_response(gtk.RESPONSE_ACCEPT)
                miseajour.set_size_request(400, 400)

                colonnesInfo.set_headers_visible(False)
                colonnesInfo.set_hover_selection(True)
                colonnesInfo.expand_all()

                colonneInfoNom.pack_start(celluleInfo, True)
                colonneInfoNom.add_attribute(celluleInfo, "text", 0)

                colonnesInfo.append_column(colonneInfoNom)
                colonnesInfo.set_model(listeInfo)

                grille.set_border_width(4)

                defilementInfo.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                defilementInfo.add(colonnesInfo)
                defilementInfo.set_border_width(4)

                miseajour.vbox.pack_start(grille)

                grille.attach(texteInfo, 0, 1, 0, 1, yoptions=gtk.FILL)
                grille.attach(defilementInfo, 0, 1, 1, 2)

                for element in listeTmp:
                    listeInfo.append(None, [element])

                miseajour.show_all()
                choix = miseajour.run()

                if choix == gtk.RESPONSE_ACCEPT:
                    for element in self.listeMiseAJourPacman:
                        if not element in self.listeInstallationPacman:
                            self.listeInstallationPacman.append(str(element))
                    miseajour.destroy()
                else:
                    miseajour.destroy()
            else:
                # Dans le cas où la liste est vide
                self.barreStatus.push(0, _("No update available"))
        else:
            # Dans le cas où la liste est vide
            self.barreStatus.push(0, _("No update available"))

        self.fenetre.set_sensitive(True)

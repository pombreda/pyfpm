#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions permettant de créer l'interface
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys, pango, codecs, urllib, gettext, re
from threading import Thread

# Récupération de la traduction
gettext.bindtextdomain('pyfpm', 'lang')
gettext.textdomain('pyfpm')
_ = gettext.gettext

try:
    import pygtk, gtk
except ImportError:
    sys.exit(_("pygtk was not found"))

from . import preferences, pacman
from Functions import package, config, files, utils

# Initialisation des modules
Preferences = preferences.Preferences()
Package = package.Package()
File = files.File()
Config = config.Config()


class Interface (object):
    """
    Fonction concernant l'interface principale
    """

    #---------------------------------------------------------------------------
    #       Interface
    #---------------------------------------------------------------------------

    def __init__(self, devMode = False):
        """
        Initialisation de la fenêtre principale
        """

        # Il est nécessaire de reconstruire la base de données de pacman-g2 à
        # chaque redémarrage de pyFPM pour afficher les bonnes informations
        Package.resetPacman()

        # TODO
        # Trouver un moyen plus élégant pour cacher les sous-groupes
        self.listeGroupesProhibes = ['-extensions','adesklets-desklets','amsn-plugins','avidemux-plugin-cli','avidemux-plugin-gtk','avidemux-plugin-qt','chroot-core','core','cinnamon-desktop','devel-core','directfb-drivers','e17-apps','e17-misc','fatrat-plugins','firefox-extensions','geda-suite','gift-plugins','gnome-minimal','hk_classes-drivers','jdictionary-plugins','kde-apps','kde-build','kde-core','kde-doc','kde-docs','kde-minimal','kde-runtime','lxde-desktop','lxde-extra','pantheon-desktop','misc-fonts','phonon-backend','pidgin-plugins','qt4-libs','sawfish-scripts','seamonkey-addons','thunderbird-extensions','tuxcmd-plugins','wmaker-dockapps','xfce4-core','xfce4-goodies','xorg-apps','xorg-core','xorg-data','xorg-doc','xorg-drivers','xorg-fonts','xorg-libs','xorg-proto','xorg-util']

        self.paquetSelectionne = ""
        self.versionSelectionne = ""

        self.listeInstallationPacman = []
        self.listeSuppressionPacman = []
        self.listeMiseAJourPacman = []

        self.recherche_mode = False
        self.recherche_nom = ""
        self.developementMode = devMode

        # ------------------------------------------------------------------
        #       Fenetre
        # ------------------------------------------------------------------

        self.fenetre = gtk.Window()
        self.grille = gtk.Table(1,4)
        self.grilleSelectionDepots = gtk.Table(1,2)
        self.grilleDepotGroupes = gtk.Table(1,2)
        self.grilleColonnePaquets = gtk.Table(2,1)
        self.grillePaquetsInformations = gtk.VPaned()
        self.grilleInformationsOutils = gtk.Table(2,1)
        self.grilleInformations = gtk.Table(1,3)

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

        self.labelInformations = gtk.Label(_("General informations"))
        self.labelInformationsNom = gtk.Label()
        self.labelInformationsDescription = gtk.Label()
        self.labelInformationsLien = gtk.Label()

        self.iconePaquet = gtk.Image()
        self.iconeAllignement = gtk.Alignment(0, 0, 0, 0)

        self.outilsPaquet = gtk.HButtonBox()
        self.outilsPaquetFichier = gtk.Button(_("See files"))
        self.outilsPaquetJournal = gtk.Button(_("See Changelog"))
        self.outilsPaquetFrugalBuild = gtk.Button(_("See FrugalBuild"))

        self.labelPaquet = gtk.Label(_("Package informations"))
        self.listePaquet = gtk.TreeView()
        self.colonneLabelPaquet = gtk.TreeViewColumn()
        self.celluleLabelPaquet = gtk.CellRendererText()
        self.colonneValeurPaquet = gtk.TreeViewColumn()
        self.celluleValeurPaquet = gtk.CellRendererText()
        self.contenuPaquet = gtk.TreeStore(str,str)
        self.defilementPaquet = gtk.ScrolledWindow()


    def mainWindow (self):
        """
        Fenêtre principale
        """

        # ------------------------------------------------------------------
        #       Fenetre
        # ------------------------------------------------------------------

        self.fenetre.set_title(_("Install and Remove packages"))
        self.fenetre.set_default_size(int(Config.readConfig("screen", "width")), int(Config.readConfig("screen", "height")))
        self.fenetre.set_resizable(True)
        self.fenetre.set_position(gtk.WIN_POS_CENTER)

        self.fenetre.connect("destroy", gtk.main_quit)
        self.fenetre.connect("check-resize", self.resize)

        # ------------------------------------------------------------------
        #       Menu
        # ------------------------------------------------------------------

        # Lancement de la transaction (Installation/Suppression)
        self.menu_action_install.set_image(gtk.image_new_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU))
        self.menu_action_install.connect("activate", self.installWindow, self)
        # Nettoyage du cache
        self.menu_action_clean.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
        self.menu_action_clean.connect("activate", self.cleanCacheWindow, self)
        # Lancement de la mise à jour des bases de données pacman-g2
        self.menu_action_update.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU))
        self.menu_action_update.connect("activate", self.runAction, "update")
        # Affichage des mises à jour disponible
        self.menu_action_check.set_image(gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU))
        self.menu_action_check.connect("activate", self.updateWindow, self)
        # Fermeture de pyFPM
        self.menu_action_quit.set_image(gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU))
        self.menu_action_quit.connect("activate", self.closeWindow)

        self.menu.add(self.menu_action)
        self.menu_action_list.add(self.menu_action_install)
        self.menu_action_list.add(self.menu_action_clean)
        self.menu_action_list.add(self.menu_action_update)
        self.menu_action_list.add(self.menu_action_check)
        self.menu_action_list.add(self.menu_action_quit)
        self.menu_action.set_submenu(self.menu_action_list)

        # Remise à zéro des choix de l'utilisateur
        self.menu_edit_clear_changes.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
        self.menu_edit_clear_changes.connect("activate", self.erasePackage)
        # Affichage des préférences
        self.menu_edit_preference.set_image(gtk.image_new_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU))
        self.menu_edit_preference.connect("activate", Preferences.runPreferences, self)

        self.menu.add(self.menu_edit)
        self.menu_edit_list.add(self.menu_edit_clear_changes)
        self.menu_edit_list.add(self.menu_edit_preference)
        self.menu_edit.set_submenu(self.menu_edit_list)

        # Affichage de la boite A propos
        self.menu_help_about.set_image(gtk.image_new_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU))
        self.menu_help_about.connect("activate", self.aboutWindow)

        self.menu.add(self.menu_help)
        self.menu_help_list.add(self.menu_help_about)
        self.menu_help.set_submenu(self.menu_help_list)

        # ------------------------------------------------------------------
        #       Barre d'outils
        # ------------------------------------------------------------------

        self.outils.set_orientation(gtk.ORIENTATION_HORIZONTAL)

        # Lancement de la transaction (Installation/Suppression)
        self.outils.insert_stock(gtk.STOCK_APPLY, _("Apply changes"), None, self.installWindow, self, 0)
        # Effacer la liste des choix de l'utilisateur
        self.outils.insert_stock(gtk.STOCK_CLEAR, _("Reset installation list"), None, self.erasePackage, self, 1)
        self.outils.insert_space(2)
        # Affichage des mises à jour disponible
        self.outils.insert_stock(gtk.STOCK_REFRESH, _("Update databases"), None, self.runAction, "update", 3)
        self.outils.insert_space(4)
        # Champs de recherche
        self.texteRecherche.set_icon_from_stock(1, gtk.STOCK_CLEAR)
        self.texteRecherche.connect("activate", self.search, gtk.RESPONSE_OK)
        self.texteRecherche.connect("icon-press", self.eraseSearch)
        self.texteRecherche.grab_focus()
        self.outils.insert_widget(self.texteRecherche, _("Write your search here"), None, 5)
        self.outils.insert_stock(gtk.STOCK_FIND, _("Search"), None, self.search, None, 6)
        self.outils.insert_space(7)
        # Affichage des préférences
        self.outils.insert_stock(gtk.STOCK_PREFERENCES, _("Preferences"), None, Preferences.runPreferences, self, 8)
        # Fermeture de pyFPM
        self.outils.insert_stock(gtk.STOCK_QUIT, _("Quit"), None, self.closeWindow, None, 9)

        # ------------------------------------------------------------------
        #       Liste des dépôts
        # ------------------------------------------------------------------

        self.labelSelectionDepots.set_alignment(0.05,0.5)
        self.listeSelectionDepots.connect('changed', self.changeRepo, self)
        self.grilleSelectionDepots.set_border_width(2)

        # ------------------------------------------------------------------
        #       Colonnes des groupes
        # ------------------------------------------------------------------

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

        # Affichage du nom et de la version
        self.labelInformationsNom.set_use_markup(True)
        self.labelInformationsNom.set_alignment(0,0.5)
        self.labelInformationsNom.set_use_underline(False)
        # Affichage de la description
        self.labelInformationsDescription.set_alignment(0,0.5)
        self.labelInformationsDescription.set_line_wrap(True)
        self.labelInformationsDescription.set_use_underline(False)
        # Affichage du lien
        self.labelInformationsLien.set_use_markup(True)
        self.labelInformationsLien.set_alignment(0,0.5)
        self.labelInformationsLien.set_use_underline(False)
        # Affichage de l'icone de l'application si disponible
        self.iconeAllignement.add(self.iconePaquet)

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

        #~ self.zoneInformations.set_tab_pos(gtk.POS_LEFT)

        self.zoneInformations.set_border_width(4)
        self.zoneInformations.set_resize_mode(gtk.RESIZE_PARENT)

        self.grilleInformations.set_row_spacings(10)

        self.grilleInformationsOutils.set_border_width(4)

        self.outilsPaquet.set_layout(gtk.BUTTONBOX_END)
        self.outilsPaquet.pack_start(self.outilsPaquetFichier)
        self.outilsPaquetFichier.set_sensitive(False)
        self.outilsPaquet.pack_start(self.outilsPaquetJournal)
        self.outilsPaquetJournal.set_sensitive(False)
        self.outilsPaquet.pack_start(self.outilsPaquetFrugalBuild)
        self.outilsPaquetFrugalBuild.set_sensitive(False)

        self.outilsPaquetFichier.connect("clicked", self.fileWindow)
        self.outilsPaquetJournal.connect("clicked", self.changelogWindow)

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
        self.grilleColonnePaquets.attach(self.grillePaquetsInformations, 1, 2, 0, 1, yoptions=gtk.FILL)

        # Informations des paquets
        #~ self.grillePaquetsInformations.add1(self.zonePaquets)
        self.grilleInformations.attach(self.labelInformationsNom, 0, 1, 0, 1, yoptions=gtk.FILL)
        self.grilleInformations.attach(self.labelInformationsDescription, 0, 1, 1, 2, yoptions=gtk.FILL)
        self.grilleInformations.attach(self.labelInformationsLien, 0, 1, 2, 3, yoptions=gtk.FILL)

        self.grilleInformationsOutils.attach(self.grilleInformations, 0, 1, 0, 1)
        self.grilleInformationsOutils.attach(self.iconeAllignement, 1, 2, 0, 1, xoptions=gtk.SHRINK)
        self.grilleInformationsOutils.attach(self.outilsPaquet, 0, 2, 1, 2, yoptions=gtk.SHRINK)

        self.grillePaquetsInformations.add1(self.defilementPaquets)
        self.grillePaquetsInformations.add2(self.zoneInformations)

        self.zoneInformations.append_page(self.grilleInformationsOutils, self.labelInformations)
        self.zoneInformations.append_page(self.defilementPaquet, self.labelPaquet)

        # Grille principale
        self.grille.attach(self.menu, 0, 1, 0, 1, yoptions=gtk.FILL)
        self.grille.attach(self.outils, 0, 1, 1, 2, yoptions=gtk.FILL)
        self.grille.attach(self.grilleColonnePaquets, 0, 1, 2, 3)
        self.grille.attach(self.barreStatus, 0, 1, 3, 4, yoptions=gtk.FILL)

        self.fenetre.add(self.grille)
        self.fenetre.show_all()
        self.refresh()

        # Affichage des mises à jour disponible
        self.getUpdateList()

        # Ajout des dépôts
        self.addRepos()

        gtk.main()


    #---------------------------------------------------------------------------
    #       Gestion de l'interface
    #---------------------------------------------------------------------------

    def closeWindow (self, interface):
        """
        Fermeture de pyFPM
        """

        # Supprime le fichier de capture d'écran
        if os.path.exists("/tmp/picture"):
            os.remove("/tmp/picture")

        utils.printDebug("INFO", _("Bye bye"))
        gtk.main_quit()


    def updateStatusbar (self, texte = ""):
        """
        Changer le texte inscrit dans la barre inférieur
        """

        self.barreStatus.push(0, str(texte))
        self.refresh()


    def eraseInterface (self):
        """
        Efface l'ensemble de l'interface
        """

        modele = self.listeSelectionDepots.get_model()
        modele.clear()
        self.listeSelectionDepots.set_model(modele)

        self.listeColonneGroupes.clear()
        self.listeColonnePaquets.clear()

        self.labelInformationsNom.set_text("")
        self.labelInformationsDescription.set_text("")
        self.labelInformationsLien.set_text("")

        self.outilsPaquetFichier.set_sensitive(False)
        self.outilsPaquetJournal.set_sensitive(False)

        self.contenuPaquet.clear()

        self.recherche_nom = ""

        self.updateStatusbar("")


    def resize (self, *args):
        """
        Redimensionne la largueur de celluleValeur afin que le texte s'adapte à la fenêtre
        """

        newSize = self.fenetre.get_size()[0] - 450
        # On impose une taille minimum de 500px
        if newSize < 500:
            newSize = 500

        self.labelInformationsDescription.set_size_request(newSize, -1)

        self.celluleValeurPaquet.set_property("wrap-width", newSize)
        self.colonnePaquetsNom.set_min_width(self.fenetre.get_size()[0]/2)
        self.colonnePaquets.set_size_request(0, self.fenetre.get_size()[1]/2)


    @staticmethod
    def refresh ():
        """
        Rafraichit l'interface quand des changements ont lieux
        """

        try :
            while gtk.events_pending():
                gtk.main_iteration()
        except:
            pass


    #---------------------------------------------------------------------------
    #       Lancement d'une action pacman-g2
    #---------------------------------------------------------------------------

    def runAction (self, widget, mode, *args):
        """
        Lance une action pacman-g2
        """

        if mode == "update":
            title = _("Update databases")

        self.fenetre.set_sensitive(False)
        self.updateStatusbar(title)

        pacmanUi = pacman.Pacman(title, mode)
        pacmanUi.mainWindow()

        self.eraseInterface()
        Package.resetPacman()
        self.addRepos()
        self.refresh()

        self.fenetre.set_sensitive(True)
        self.refresh()

        self.getUpdateList()


    #---------------------------------------------------------------------------
    #       Récupération des mises à jour
    #---------------------------------------------------------------------------

    def getUpdateList (self):
        """
        Récupérer la liste des mises à jour
        """

        utils.printDebug("INFO", _("Get the update packages list"))

        if len(self.listeMiseAJourPacman) > 0:
            self.listeMiseAJourPacman = []

        listePaquetsMiseAJour = Package.getUpdateList()

        if listePaquetsMiseAJour > 0:
            for element in listePaquetsMiseAJour:
                self.listeMiseAJourPacman.append(element)
            utils.printDebug("INFO", _("%s update have been found") % str(len(self.listeMiseAJourPacman)))
        else:
            utils.printDebug("INFO", _("No update available"))

        if Config.readConfig("pyfpm", "startupdate") == "true":
            self.updateWindow()


    #---------------------------------------------------------------------------
    #       Gestion des dépôts
    #---------------------------------------------------------------------------

    def addRepos (self):
        """
        Ajout des dépots disponible sur le système dans l'interface
        """

        # On remet à jour les informations de pacman-g2
        #~ Package.resetPacman()

        # On récupère la liste des dépôts
        listeDepot = Package.getRepoList()
        utils.printDebug("DEBUG", _("%s repos have been found") % str(len(listeDepot)))

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


    #---------------------------------------------------------------------------
    #       Récupération des groupes
    #---------------------------------------------------------------------------

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

        utils.printDebug("DEBUG", _("%(nbr)s group(s) append for %(repo)s") % {'nbr':str(len(self.listeColonneGroupes)), 'repo':"\033[0;32m" + str(self.listeSelectionDepots.get_active_text())})


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


    #---------------------------------------------------------------------------
    #       Récupération des paquets
    #---------------------------------------------------------------------------

    def getPackages (self, nomGroupe):
        """
        Obtenir les paquets correspondant au groupe sélectionné
        """

        paquets = Package.getPackagesList(self.listeSelectionDepots.get_active(), nomGroupe)
        self.addPackages(paquets, nomGroupe)

        utils.printDebug("DEBUG", _("%(nbr)s package(s) append for %(grp)s") % {'nbr':str(len(paquets)), 'grp':"\033[0;32m" + str(nomGroupe)})


    def addPackages (self, paquets, value, recherche = False):
        """
        Ajoute les paquets dans l'interface
        """

        self.refresh()

        objetTrouve = 0
        n = 0
        self.listeColonnePaquets.clear()

        listePaquetsInstalles = Package.getInstalledList()

        # Supprime le mode de tri des colonnes pour accélérer l'affichage
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
                    # Le paquet est dans la liste des mises à jour
                    image = gtk.STOCK_REFRESH
                    objetTrouve = 0
                elif str(nomPaquet) in listePaquetsInstalles:
                    # Le paquet est dans une version supérieur à celle du paquet disponible
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
                n = 0

        self.colonnePaquets.set_model(modeleColonnePaquets)
        self.colonnePaquets.thaw_child_notify()
        self.refresh()

        if len(self.listeColonnePaquets) > 1:
            self.updateStatusbar(_("%(nbr)s packages were found for %(value)s") % {'nbr': str(len(self.listeColonnePaquets)), 'value': value})
        else:
            self.updateStatusbar(_("%(nbr)s package was found for %(value)s") % {'nbr': str(len(self.listeColonnePaquets)), 'value': value})


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
            nomPaquet, versionPaquet, versionDisponible = modele.get(tableau, 2, 3, 4)
            self.getPackageInfo(nomPaquet, versionPaquet, versionDisponible)
        except :
            return True

        return True


    def getPackageInfo (self, nomPaquet, versionPaquet, versionDisponible):
        """
        Obtient les détails du paquet
        """

        #~ t = Thread(target=self.downloadScreenshot, args=(nomPaquet,))
        #~ t.start()

        # On efface tout et on recommence :D
        self.labelInformationsNom.set_markup("")
        self.labelInformationsDescription.set_markup("")
        self.labelInformationsLien.set_markup("")

        self.iconePaquet.clear()

        self.outilsPaquetFichier.set_sensitive(False)
        self.outilsPaquetJournal.set_sensitive(False)

        objetTrouve = 0
        depotRecherche = ""
        modeRecherche = False

        if nomPaquet.find("]") != -1:
            # Dans le cas d'une recherche, il est nécessaire d'enlever le préfixe [<nom_dépôt>]
            split = utils.splitRepo(nomPaquet)
            depotRecherche = split[0]
            nomPaquet = split[1]
            modeRecherche = True

        self.updateStatusbar(_("Get informations about %s") % nomPaquet)

        texte = ""
        estInstalle = False

        self.contenuPaquet.clear()

        # Récupère les informations depuis local si le paquet est installé
        if Package.checkPackageInstalled(nomPaquet, versionPaquet):
            if len(versionDisponible) == 1:
                # Le paquet est installé
                depot = 0

                # On garde en mémoire que le paquet est installé
                estInstalle = True
            else:
                # Une mise à jour est disponible
                if not modeRecherche:
                    # Ce n'est pas une recherche donc on se base sur le
                    # dépôt local
                    depot = 0

                    # On garde en mémoire que le paquet est installé
                    estInstalle = True
                else:
                    # On récupère le dépôt du paquet
                    depot = Package.getRepoList().index(depotRecherche)
                    if depot == Package.getIndexFromRepo():
                        # Le dépot est celui de Frugalware donc on prend
                        # le local
                        depot = 0

                        # On garde en mémoire que le paquet est installé
                        estInstalle = True
        else:
            # Le paquet n'est pas installé
            if not modeRecherche:
                # Il ne s'agit pas d'une recherche
                depot = int(self.listeSelectionDepots.get_active())
            else:
                # Il s'agit d'une recherche donc on prend le dépot entre []
                depot = Package.getRepoList().index(depotRecherche)

        # Récupération des informations
        pointerPaquet = Package.getPackagePointer(nomPaquet, depot)
        infoPaquet = Package.getPackageInfo(pointerPaquet)

        # Nom et version du paquet
        self.labelInformationsNom.set_markup("<span font='18'><b>" + infoPaquet.get("name") + " - " + infoPaquet.get("version") + "</b></span>")

        # Description du paquet
        # [TODO] - Améliorer l'affichage
        self.labelInformationsDescription.set_markup(infoPaquet.get("description").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").encode('ascii', 'replace'))

        # Liste des groupes
        groupes = infoPaquet.get("groups")
        if len(groupes) > 0:
            self.contenuPaquet.append(None, [_("Groups"), ', '.join(groupes)])

        # Affichage du SHA1SUMS du paquet
        if infoPaquet.get("name") in self.listeMiseAJourPacman:
            # Le SHA1SUMS n'est pas dispo puisqu'une version plus récente est diponible
            # Cas possible que lors de l'utilisation de frugalware-current
            self.contenuPaquet.append(None, [_("SHA1SUMS"), _("An update is available (%s)") % str(versionDisponible)])
        else:
            if self.listeSelectionDepots.get_active() != 0:
                # On récupère le dépôt actif
                depot = self.listeSelectionDepots.get_active()
            else:
                # Sinon par défaut c'est le dépôt officiel (stable/current)
                listeDepot = Package.getIndexFromRepo()

            self.contenuPaquet.append(None, [_("SHA1SUMS"), str(Package.getSha1sums(infoPaquet.get("name"), int(depot)))])

        # Affiche des informations supplémentaires si le paquet est installé
        if estInstalle:
            # Lien vers le site du projet
            self.labelInformationsLien.set_markup("<a href='" + str(infoPaquet.get("url")) + "' title='" + str(infoPaquet.get("url")) + "'>" + _("Visit website") + "</a>")

            # Date d'installation
            self.contenuPaquet.append(None, [_("Install date"), str(infoPaquet.get("install_date"))])
            # Taille du paquet sur le disque
            self.contenuPaquet.append(None, [_("Size"), str(format(float(long(infoPaquet.get("size"))/1024)/1024, '.2f')) + " MB"])
            # Empaqueteur du paquet
            self.contenuPaquet.append(None, [_("Packager"), str(infoPaquet.get("packager").encode('ascii', 'replace'))])

            # On passe les boutons en actif puisque ces informations sont accessibles
            self.outilsPaquetFichier.set_sensitive(True)
            self.outilsPaquetJournal.set_sensitive(True)

            self.paquetSelectionne = infoPaquet.get("name")
            self.versionSelectionne = infoPaquet.get("version")
        else:
            # Taille compressé du paquet
            self.contenuPaquet.append(None, [_("Compress size"), str(format(float(long(infoPaquet.get("compress_size"))/1024)/1024, '.2f')) + " MB"])
            # Taille décompressé du paquet
            self.contenuPaquet.append(None, [_("Uncompress size"), str(format(float(long(infoPaquet.get("uncompress_size"))/1024)/1024, '.2f')) + " MB"])

        # Liste des dépendances
        depends = infoPaquet.get("depends")
        if len(depends) > 0:
            self.contenuPaquet.append(None, [_("Depends"), ', '.join(depends)])

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

        # Récupération de la capture d'écran
        if self.downloadScreenshot(infoPaquet.get("name")):
            self.iconePaquet.set_from_file("/tmp/picture")
        else:
            self.iconePaquet.clear()


    def downloadScreenshot (self, nomPaquet):
        """
        Récupère une screenshot depuis le site http://screenshots.ubuntu.com/
        """

        url = "http://screenshots.ubuntu.com/thumbnail/" + str(nomPaquet)

        if File.checkUrlError(url) == 1:
            # Le site est accessible
            webFile = urllib.urlopen(url)
            localFile = open("/tmp/picture", 'w')
            localFile.write(webFile.read())
            utils.printDebug("DEBUG", str(nomPaquet) + " screenshot is saved")
            webFile.close()
            localFile.close()
            return True
        else:
            return False


    #---------------------------------------------------------------------------
    #       Choix de l'utilisateur
    #---------------------------------------------------------------------------

    def checkPackage (self, cell_renderer, colonne, liste):
        """
        Permet de gérer les paquets à installer/desinstaller via deux
        tableau qui se mettent à jour en fonction du cochage.
        """

        # On met la checkbox à la valeur contraire (1 -> 0, 0 -> 1)
        modele = liste.get_model()
        modele[colonne][0] = not modele[colonne][0]

        nomPaquet = modele[colonne][2]

        # Dans le cas d'une recherche, il est nécessaire d'enlever le préfixe [<nom_dépôt>]
        if nomPaquet.find("]") != -1:
            nomPaquet = utils.splitRepo(nomPaquet)[1]

        # On vérifie si le paquet en question est dans la liste des paquets à enlever
        # ou à installer
        elementAjouter = utils.checkData(self.listeInstallationPacman, nomPaquet)
        elementEnlever = utils.checkData(self.listeSuppressionPacman, nomPaquet)

        # On récupère la liste des paquets installés
        listePaquetsInstalles = Package.getInstalledList()

        # Le paquet en question à été décoché
        if modele[colonne][0] == 0:

            # Le paquet n'a pas de mise à jour
            if len(modele[colonne][4]) == 1:
                # Le paquet en question est installé
                if Package.checkPackageInstalled(nomPaquet, modele[colonne][3]):
                    # Le paquet est mis dans la liste des paquets à supprimer
                    if elementEnlever == 0:
                        self.listeSuppressionPacman.append(nomPaquet)
                        modele[colonne][1] = gtk.STOCK_REMOVE

                else:
                    # Le paquet est enlevé de la liste des paquets à installer
                    if elementAjouter != 0:
                        self.listeInstallationPacman.remove(elementAjouter)
                        modele[colonne][1] = " "

            # Le paquet à une mise à jour
            else:
                # Le paquet est enlevé de la liste des paquets à installer
                if elementAjouter != 0:
                    self.listeInstallationPacman.remove(elementAjouter)
                    # Le paquet est dans la liste des paquets à installer
                    if str(nomPaquet) in self.listeInstallationPacman:
                        modele[colonne][1] = gtk.STOCK_ADD
                    # Le paquet est dans la liste des mises à jour
                    elif str(nomPaquet) in self.listeMiseAJourPacman:
                        modele[colonne][1] = gtk.STOCK_REFRESH
                    # Le paquet est dans une version supérieur à celle du paquet disponible
                    elif str(nomPaquet) in listePaquetsInstalles:
                        modele[colonne][1] = gtk.STOCK_REDO
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


    #---------------------------------------------------------------------------
    #       Gestion de la recherche
    #---------------------------------------------------------------------------

    def search (self, *args):
        """
        Affiche l'ensemble des paquets correspondant à la recherche
        """

        # La recherche n'est possible que si la chaine est non nulle et différente de celle précédement utilisée
        if len(self.texteRecherche.get_text()) > 0 and self.texteRecherche.get_text() != self.recherche_nom:
            self.listeColonnePaquets.clear()
            objetRechercher = self.texteRecherche.get_text()

            paquets = Package.searchPackage(objetRechercher)

            if len(paquets) > 1:
                self.updateStatusbar(_("%(nbr)s packages were found for %(value)s") % {'nbr': str(len(paquets)), 'value': objetRechercher})
            elif len(paquets) == 1:
                self.updateStatusbar(_("%(nbr)s package was found for %(value)s") % {'nbr': str(len(paquets)), 'value': objetRechercher})
            else:
                self.updateStatusbar(_("No package was found for %s") % objetRechercher)

            self.recherche_mode = True
            self.recherche_nom = objetRechercher

            if len(paquets) > 0:
                # Si la liste contient des paquets on lance l'ajout dans l'interface
                self.addPackages(paquets, objetRechercher, recherche = True)

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


# ------------------------------------------------------------------------------------------------------------
#
#                Fenêtres supplémentaires
#
# ------------------------------------------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #       Fenêtre à propos
    #---------------------------------------------------------------------------

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
        about.set_translator_credits("fr_FR - Anthony Jorion (Pingax)")
        about.set_license("This program is free software; you can redistribute it and/or " \
            "modify it under the terms of the GNU General Public Licence as " \
            "published by the Free Software Foundation; either version 2 of the " \
            "Licence, or (at your option) any later version.\n" \
            "\n" \
            "This program is distributed in the hope that it will be useful, " \
            "but WITHOUT ANY WARRANTY; without even the implied warranty of " \
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU " \
            "General Public Licence for more details.\n" \
            "\n" \
            "You should have received a copy of the GNU General Public Licence " \
            "along with this program; if not, write to the Free Software " \
            "Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, " \
            "MA  02110-1301  USA")
        about.set_wrap_license(True)
        about.set_website("http://www.frugalware.org")
        about.set_logo(logo)

        about.run()

        about.destroy()


    #---------------------------------------------------------------------------
    #       Popup d'information
    #---------------------------------------------------------------------------

    def informationWindow (self, titre, texte):
        """
        Affiche une fenêtre d'information
        """

        information = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, texte)

        information.set_title(titre)
        information.set_default_response(gtk.RESPONSE_OK)

        information.run()

        information.destroy()


    #---------------------------------------------------------------------------
    #       Affichage d'une fenêtre pour les fichiers et le changelog
    #---------------------------------------------------------------------------

    #~ def showTooltip(self, selection, modele, tooltip):
        #~ tooltip.set_text("test")


    def fileWindow (self, widget):
        """
        Affiche les fichiers d'un paquet
        """

        fenetre = gtk.Dialog(_("Files"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        fenetre.set_size_request(600, 600)

        tableau = Package.getFileFromPackage(self.paquetSelectionne)
        #~ tooltip = gtk.Tooltip()

        listeColonne = gtk.TreeStore(str)
        colonne = gtk.TreeView(listeColonne)
        colonne.set_has_tooltip(True)
        colonneFichier = gtk.TreeViewColumn(_("Files"))
        celluleFichier = gtk.CellRendererText()

        colonne.set_headers_visible(False)
        colonne.set_size_request(180,0)
        colonne.set_search_column(0)

        colonneFichier.set_sort_column_id(0)
        colonneFichier.pack_start(celluleFichier, True)
        colonneFichier.add_attribute(celluleFichier, 'text', 0)
        colonne.append_column(colonneFichier)
        defilement = gtk.ScrolledWindow()

        defilement.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        defilement.add(colonne)
        defilement.set_border_width(4)

        #~ selection = colonne.get_selection()
        #~ selection.connect("changed", self.showTooltip, listeColonne, tooltip)
        #~ tooltips.set_tip(colonne, 'TOOLTIP TEXT')

        # Affichage des fichiers sous forme d'arbre
        path = []
        # On défini la racine
        racine = listeColonne.append(None, ['/'])

        for element in tableau:
            # On va analyser la chaine en la divisant
            chaine = element.split('/')
            if len(chaine[-1]) == 0:
                # Cas d'un dossier
                if len(chaine) == 2:
                    # Dossier de niveau 1
                    path.append([str(element), listeColonne.append(racine, [str(element)])])
                else:
                    # Autre dossier
                    found = racine
                    for index in path:
                        if str(element[0:len(element) - len(chaine[-2]) - 1]) == index[0]:
                            # Le dossier parent existe
                            found = index[1]
                            break

                    path.append([str(element), listeColonne.append(found, [str(chaine[-2]) + '/'])])
            else:
                # Cas d'un fichier
                found = racine
                for index in path:
                    if element[0:len(element) - len(chaine[-1])] == index[0]:
                        # Le dossier parent existe
                        found = index[1]

                listeColonne.append(found, [str(chaine[-1])])

        colonne.expand_all()

        fenetre.vbox.pack_start(defilement)

        fenetre.show_all()
        fenetre.run()

        fenetre.destroy()


    def changelogWindow (self, widget):
        """
        Affiche le changelog d'un paquet
        """

        fenetre = gtk.Dialog(_("Changelog"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        fenetre.set_size_request(600, 600)

        liste = gtk.TextView()
        defilement = gtk.ScrolledWindow()

        defilement.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        defilement.add(liste)
        defilement.set_border_width(4)

        texte = ""
        texteBuffer = liste.get_buffer()

        listeDepot = Package.getRepoList()
        journal = "/var/lib/pacman-g2/" + listeDepot[0] + "/" + self.paquetSelectionne + "-" + self.versionSelectionne + "/changelog"
        if os.path.exists(journal):
            file = codecs.open(journal, "r", "iso-8859-15")
            self.listeChangelog = file
            for element in file:
                if element != "":
                    texte += "\t" + element
            file.close()
        else:
            texte = "\n\t" + _("No file found. This package must have been installed from a file.")

        texteBuffer.set_text(texte)

        fenetre.vbox.pack_start(defilement)

        fenetre.show_all()
        fenetre.run()

        fenetre.destroy()


    #---------------------------------------------------------------------------
    #       Fenêtre affichant les transactions à effectuer :
    #       installation/suppression
    #---------------------------------------------------------------------------

    def installWindow (self, widget, *event):
        """
        Affiche les modifications à effectuer sur les paquets
        """

        # On récupère la liste des dépôts
        listeDepot = Package.getRepoList()

        # On récupère l'index du dépôt initial
        index = Package.getIndexFromRepo()

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
            grilleFenetre = gtk.VBox()
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
            separateurInstallation = gtk.HSeparator()

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
            separateurSuppression = gtk.HSeparator()

            fenetre.set_default_response(gtk.RESPONSE_OK)
            fenetre.set_size_request(600, 600)

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
            grilleInstallation.attach(self.verifierDependancesInstallation, 0, 1, 1, 2, yoptions=gtk.SHRINK)
            grilleInstallation.attach(self.seulementTelecharger, 0, 1, 2, 3, yoptions=gtk.FILL)
            grilleInstallation.attach(separateurInstallation, 0, 1, 3, 4, yoptions=gtk.FILL)
            grilleInstallation.attach(tailleInstallation, 0, 1, 4, 5, yoptions=gtk.FILL, xoptions=gtk.FILL)
            grilleInstallation.set_border_width(4)
            grilleInstallation.set_row_spacings(5)

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
            grilleSuppression.attach(self.verifierDependancesSuppression, 0, 1, 1, 2, yoptions=gtk.FILL)
            grilleSuppression.attach(separateurSuppression, 0, 1, 2, 3, yoptions=gtk.FILL)
            grilleSuppression.attach(tailleSuppression, 0, 1, 3, 4, yoptions=gtk.FILL, xoptions=gtk.FILL)
            grilleSuppression.set_border_width(4)
            grilleSuppression.set_row_spacings(5)

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
                grilleFenetre.pack_start(zoneInstallation)

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
                grilleFenetre.pack_start(zoneSuppression)

            fenetre.vbox.pack_start(grilleFenetre)

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


    #---------------------------------------------------------------------------
    #       Fenêtre affichant les mises à jour disponible
    #---------------------------------------------------------------------------

    def updateWindow (self, *event):
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
                miseajour = gtk.Dialog(_("Update system"), None, gtk.DIALOG_MODAL, (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

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


    #---------------------------------------------------------------------------
    #       Fenêtre demandant la méthode de nettoyage du cache de
    #       pacman-g2
    #---------------------------------------------------------------------------

    def cleanCacheWindow (self, widget, *event):
        """
        Fenêtre demandant la confirmation d'utiliser le nettoyage
        des vieux paquets fpm
        """

        self.fenetre.set_sensitive(False)

        nettoyage = gtk.Dialog(_("Clear package cache"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_APPLY, gtk.RESPONSE_ACCEPT))
        nettoyage.set_resizable(False)

        texte = gtk.Label(_("What did you want to do with pacman-g2 cache ?"))

        radioGrille = gtk.VBox()
        radioOld = gtk.RadioButton(None, _("Remove only old packages from cache"), None)
        radioAll = gtk.RadioButton(radioOld, _("Remove all packages from cache"), None)

        nettoyage.set_border_width(4)
        nettoyage.vbox.set_spacing(8)
        nettoyage.vbox.pack_start(texte)
        radioGrille.pack_start(radioOld)
        radioGrille.pack_start(radioAll)
        nettoyage.vbox.pack_start(radioGrille)

        nettoyage.show_all()

        choix = nettoyage.run()

        if choix == gtk.RESPONSE_ACCEPT:
            if radioOld.get_active():
                mode = 0
            elif radioAll.get_active():
                mode = 1

            self.updateStatusbar(_("Clean cache"))
            Package.emitSignal(["run", "clean", str(mode)])
            self.updateStatusbar(_("Clean cache complete"))

            nettoyage.destroy()
            self.informationWindow(_("Cache cleared"), _("Finished clearing the cache"))
        else:
            self.updateStatusbar()
            nettoyage.destroy()

        self.fenetre.set_sensitive(True)

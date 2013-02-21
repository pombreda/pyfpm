#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions permettant de créer l'interface
#
# ----------------------------------------------------------------------

import sys, pango

try:
    import pygtk, gtk
except ImportError:
    sys.exit(fctLang.traduire("pygtk_not_found"))


from . import preferences
fctPrefs = preferences.fonctionsPreferences()

from Pacman.libpacman import *
from Pacman import package
fctPaquets = package.fonctionsPaquets()

from Misc import action, lang, config
fctLang = lang.fonctionsLang()
fctEvent = action.fonctionsEvenement()
fctConfig = config.fonctionsConfiguration()


class fonctionsInterface (object):
    def __init__(self):

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
            self.groupes = gtk.Table(1,2)
            self.zoneColonnePaquets = gtk.Table(2,1)
            self.zonePaquetsInformations = gtk.VPaned()

            self.barreStatus = gtk.Statusbar()

            # ------------------------------------------------------------------
            #       Menu
            # ------------------------------------------------------------------

            self.menu = gtk.MenuBar()
            self.menu_action = gtk.MenuItem(label=fctLang.traduire("action"))
            self.menu_action_list = gtk.Menu()
            self.menu_action_install = gtk.ImageMenuItem(fctLang.traduire("apply_pkg"))
            self.menu_action_clean = gtk.ImageMenuItem(fctLang.traduire("clean_cache"))
            self.menu_action_update = gtk.ImageMenuItem(fctLang.traduire("update_database"))
            self.menu_action_check = gtk.ImageMenuItem(fctLang.traduire("check_update"))
            self.menu_action_quit = gtk.ImageMenuItem(fctLang.traduire("quit"))
            self.menu_edit = gtk.MenuItem(label=fctLang.traduire("edit"))
            self.menu_edit_list = gtk.Menu()
            self.menu_edit_clear_changes = gtk.ImageMenuItem(fctLang.traduire("clear_changes"))
            self.menu_edit_preference = gtk.ImageMenuItem(fctLang.traduire("preferences"))
            self.menu_help = gtk.MenuItem(label=fctLang.traduire("help"))
            self.menu_help_list = gtk.Menu()
            self.menu_help_about = gtk.ImageMenuItem(fctLang.traduire("about"))

            # ------------------------------------------------------------------
            #       Barre d'outils
            # ------------------------------------------------------------------

            self.outils = gtk.Toolbar()
            self.texteRecherche = gtk.Entry()

            # ------------------------------------------------------------------
            #       Liste des groupes
            # ------------------------------------------------------------------

            self.zoneSelectionGroupe = gtk.Frame(fctLang.traduire("select_group"))
            self.listeSelectionGroupe = gtk.combo_box_new_text()

            # ------------------------------------------------------------------
            #       Colonnes des groupes
            # ------------------------------------------------------------------

            self.zoneGroupes = gtk.Frame(fctLang.traduire("list_groups"))
            self.listeColonneGroupes = gtk.ListStore(str)
            self.colonneGroupes = gtk.TreeView(self.listeColonneGroupes)
            self.colonneGroupesNom = gtk.TreeViewColumn(fctLang.traduire("groups"))
            self.celluleGroupesNom = gtk.CellRendererText()
            self.defilementGroupes = gtk.ScrolledWindow()

            # ------------------------------------------------------------------
            #       Colonnes des paquets
            # ------------------------------------------------------------------

            self.zonePaquets = gtk.Frame(fctLang.traduire("packages_list"))
            self.listeColonnePaquets = gtk.ListStore(int, str, str, str, str)
            self.colonnePaquets = gtk.TreeView(self.listeColonnePaquets)
            self.colonnePaquetsCheckbox = gtk.TreeViewColumn(" ")
            self.cellulePaquetsCheckbox = gtk.CellRendererToggle()
            self.colonnePaquetsImage = gtk.TreeViewColumn(" ")
            self.cellulePaquetsImage = gtk.CellRendererPixbuf()
            self.colonnePaquetsNom = gtk.TreeViewColumn(fctLang.traduire("name"))
            self.cellulePaquetsNom = gtk.CellRendererText()
            self.colonnePaquetsVersionActuelle = gtk.TreeViewColumn(fctLang.traduire("actual_version"))
            self.cellulePaquetsVersionActuelle = gtk.CellRendererText()
            self.colonnePaquetsVersionDisponible = gtk.TreeViewColumn(fctLang.traduire("current_version"))
            self.cellulePaquetsVersionDisponible = gtk.CellRendererText()
            self.defilementPaquets = gtk.ScrolledWindow()

            # ------------------------------------------------------------------
            #       Informations sur le paquet
            # ------------------------------------------------------------------

            self.zoneInformations = gtk.Notebook()
            self.labelInformations = gtk.Label(fctLang.traduire("informations"))
            self.listeInformations = gtk.TreeView()
            self.colonneLabelInformations = gtk.TreeViewColumn()
            self.celluleLabelInformations = gtk.CellRendererText()
            self.colonneValeurInformations = gtk.TreeViewColumn()
            self.celluleValeurInformations = gtk.CellRendererText()
            self.contenuInformations = gtk.TreeStore(str,str)
            self.defilementInformations = gtk.ScrolledWindow()
            self.labelPaquet = gtk.Label(fctLang.traduire("package"))
            self.listePaquet = gtk.TreeView()
            self.colonneLabelPaquet = gtk.TreeViewColumn()
            self.celluleLabelPaquet = gtk.CellRendererText()
            self.colonneValeurPaquet = gtk.TreeViewColumn()
            self.celluleValeurPaquet = gtk.CellRendererText()
            self.contenuPaquet = gtk.TreeStore(str,str)
            self.defilementPaquet = gtk.ScrolledWindow()
            self.labelFichiers = gtk.Label(fctLang.traduire("files"))
            self.listeFichiers = gtk.TextView()
            self.defilementFichiers = gtk.ScrolledWindow()
            self.labelJournal = gtk.Label(fctLang.traduire("changelog"))
            self.listeJournal = gtk.TextView()
            self.defilementJournal = gtk.ScrolledWindow()
            self.labelFrugalbuild = gtk.Label(fctLang.traduire("frugalbuild"))
            self.listeFrugalbuild = gtk.TextView()
            self.defilementFrugalbuild = gtk.ScrolledWindow()


    def fenetrePrincipale (self):

        #~ self.initialiserFenetre()
        longueur = fctConfig.lireConfig("screen", "width")
        hauteur = fctConfig.lireConfig("screen", "height")

        if int(longueur) >= 800 and int(hauteur) >= 600:

            # ------------------------------------------------------------------
            #       Fenetre
            # ------------------------------------------------------------------

            self.fenetre.set_title(fctLang.traduire("title"))
            self.fenetre.set_size_request(int(longueur), int(hauteur))
            self.fenetre.set_resizable(True)
            self.fenetre.set_position(gtk.WIN_POS_CENTER)

            # ------------------------------------------------------------------
            #       Menu
            # ------------------------------------------------------------------

            self.fenetre.connect("destroy", gtk.main_quit)
            self.fenetre.connect("check-resize", self.redimensionnement)

            self.menu_action_install.set_image(gtk.image_new_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU))
            self.menu_action_install.connect("activate", self.fenetreInstallation, self)

            self.menu_action_clean.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
            self.menu_action_clean.connect("activate", fctEvent.lancerNettoyerCache, self)

            self.menu_action_update.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU))
            self.menu_action_update.connect("activate", fctEvent.lancerMiseajourBaseDonnees, self)

            self.menu_action_check.set_image(gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU))
            self.menu_action_check.connect("activate", self.fenetreMiseAJour)

            self.menu_action_quit.set_image(gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU))
            self.menu_action_quit.connect("activate", fctEvent.detruire)

            self.menu.add(self.menu_action)

            self.menu_action_list.add(self.menu_action_install)
            self.menu_action_list.add(self.menu_action_clean)
            self.menu_action_list.add(self.menu_action_update)
            self.menu_action_list.add(self.menu_action_check)
            self.menu_action_list.add(self.menu_action_quit)

            self.menu_action.set_submenu(self.menu_action_list)

            self.menu_edit_clear_changes.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
            self.menu_edit_clear_changes.connect("activate", self.effacerListesPaquets)

            self.menu_edit_preference.set_image(gtk.image_new_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU))
            self.menu_edit_preference.connect("activate", fctPrefs.fenetrePreferences, self)

            self.menu.add(self.menu_edit)

            self.menu_edit_list.add(self.menu_edit_clear_changes)
            self.menu_edit_list.add(self.menu_edit_preference)

            self.menu_edit.set_submenu(self.menu_edit_list)
            self.menu_help_about.set_image(gtk.image_new_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU))
            self.menu_help_about.connect("activate", self.fenetreAPropos)

            self.menu.add(self.menu_help)

            self.menu_help_list.add(self.menu_help_about)

            self.menu_help.set_submenu(self.menu_help_list)

            # ------------------------------------------------------------------
            #       Barre d'outils
            # ------------------------------------------------------------------

            self.outils.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            self.outils.set_style(gtk.TOOLBAR_ICONS)

            self.outils.insert_stock(gtk.STOCK_APPLY, fctLang.traduire("apply_pkg"), None, self.fenetreInstallation, self, 0)
            self.outils.insert_stock(gtk.STOCK_REFRESH, fctLang.traduire("update_database"), None, fctEvent.lancerMiseajourBaseDonnees, self, 2)
            self.outils.insert_space(3)
            self.texteRecherche.set_icon_from_stock(1, gtk.STOCK_CLEAR)
            self.texteRecherche.connect("activate", self.effectuerRecherche, gtk.RESPONSE_OK)
            self.texteRecherche.connect("icon-press", self.effacerRecherche)
            self.texteRecherche.grab_focus()
            self.outils.insert_widget(self.texteRecherche, fctLang.traduire("write_search"), None, 4)
            self.outils.insert_stock(gtk.STOCK_FIND, fctLang.traduire("search"), None, self.effectuerRecherche, None, 5)
            self.outils.insert_space(6)
            self.outils.insert_stock(gtk.STOCK_PREFERENCES, fctLang.traduire("preferences"), None, fctPrefs.fenetrePreferences, self, 7)
            self.outils.insert_stock(gtk.STOCK_QUIT, fctLang.traduire("quit"), None, fctEvent.detruire, None, 8)

            # ------------------------------------------------------------------
            #       Liste des groupes
            # ------------------------------------------------------------------

            self.zoneSelectionGroupe.add(self.listeSelectionGroupe)
            self.zoneSelectionGroupe.set_border_width(4)
            self.listeSelectionGroupe.connect('changed', self.changementDepot, self)

            fctEvent.ajouterDepots(self)

            # ------------------------------------------------------------------
            #       Colonnes des groupes
            # ------------------------------------------------------------------

            self.listeColonneGroupes.clear()

            self.colonneGroupes.set_headers_visible(False)
            self.colonneGroupes.set_size_request(180,0)
            self.colonneGroupes.set_search_column(0)

            self.colonneGroupesNom.set_sort_column_id(0)
            self.colonneGroupesNom.pack_start(self.celluleGroupesNom, True)
            self.colonneGroupesNom.add_attribute(self.celluleGroupesNom, 'text', 0)
            self.colonneGroupes.append_column(self.colonneGroupesNom)

            fctEvent.ajouterGroupes(self)

            self.defilementGroupes.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.defilementGroupes.add(self.colonneGroupes)
            self.defilementGroupes.set_border_width(4)

            self.selectionGroupe = self.colonneGroupes.get_selection()
            self.selectionGroupe.connect('changed', self.selectionnerGroupe, self.listeColonneGroupes)

            self.zoneGroupes.add(self.defilementGroupes)
            self.zoneGroupes.set_border_width(4)
            self.zoneGroupes.set_resize_mode(gtk.RESIZE_PARENT)

            self.groupes.attach(self.zoneSelectionGroupe, 0, 1, 0, 1, yoptions=gtk.FILL)
            self.groupes.attach(self.zoneGroupes, 0, 1, 1, 2)

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
            self.cellulePaquetsCheckbox.connect('toggled', self.cocherPaquet, self.colonnePaquets)

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
            self.selectionPaquet.connect('changed', self.selectionnerPaquet, self.listeColonnePaquets)

            self.zonePaquets.add(self.defilementPaquets)
            self.zonePaquets.set_border_width(4)

            self.zoneColonnePaquets.attach(self.groupes, 0, 1, 0, 1, xoptions=gtk.FILL)
            self.zoneColonnePaquets.attach(self.zonePaquetsInformations, 1, 2, 0, 1)

            # ------------------------------------------------------------------
            #       Informations sur le paquet
            # ------------------------------------------------------------------

            self.listeInformations.set_headers_visible(False)
            self.listeInformations.set_hover_selection(False)

            self.celluleLabelInformations.set_property('weight', pango.WEIGHT_BOLD)

            self.colonneLabelInformations.pack_start(self.celluleLabelInformations, True)
            self.colonneLabelInformations.add_attribute(self.celluleLabelInformations, "text", 0)
            self.colonneValeurInformations.pack_start(self.celluleValeurInformations, True)
            self.colonneValeurInformations.add_attribute(self.celluleValeurInformations, "markup", 1)

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
            self.colonneValeurPaquet.add_attribute(self.celluleValeurPaquet, "markup", 1)

            self.celluleValeurPaquet.set_property('wrap-mode', pango.WRAP_WORD)
            self.celluleValeurPaquet.set_property('editable', True)

            self.listePaquet.append_column(self.colonneLabelPaquet)
            self.listePaquet.append_column(self.colonneValeurPaquet)
            self.listePaquet.set_model(self.contenuPaquet)

            self.defilementPaquet.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.defilementPaquet.add(self.listePaquet)
            self.defilementPaquet.set_border_width(4)

            self.listeFichiers.set_editable(False)
            self.listeFichiers.set_cursor_visible(False)

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
            if fctConfig.lireConfig("pyfpm", "developmentmode") == "true":
                self.zoneInformations.append_page(self.defilementFrugalbuild, self.labelFrugalbuild)
            self.zoneInformations.set_border_width(4)
            self.zoneInformations.set_resize_mode(gtk.RESIZE_PARENT)

            # ------------------------------------------------------------------
            #       Intégration des widgets
            # ------------------------------------------------------------------

            self.zonePaquetsInformations.add1(self.zonePaquets)
            self.zonePaquetsInformations.add2(self.zoneInformations)

            self.grille.attach(self.menu, 0, 1, 0, 1, yoptions=gtk.FILL)
            self.grille.attach(self.outils, 0, 1, 1, 2, yoptions=gtk.FILL)
            self.grille.attach(self.zoneColonnePaquets, 0, 1, 2, 3)
            self.grille.attach(self.barreStatus, 0, 1, 3, 4, yoptions=gtk.FILL)

            self.fenetre.add(self.grille)

            self.fenetre.show_all()

            if fctConfig.lireConfig("pyfpm", "startupdate") == "true":
                self.fenetreMiseAJour()
            else:
                fctPaquets.obtenirMiseAJour(self.listeMiseAJourPacman)

        else:
            try:
                self.fenetreInformation(fctLang.traduire("error"), fctLang.traduire("limit_size"))
            except:
                pass

            sys.exit("[ERROR] - " + fctLang.traduire("limit_size"))


    def selectionnerGroupe (self, selection, modele):
        """
        Récupère les informations concernant le groupe actuellement
        sélectionné.
        """

        try:
            choix = selection.get_selected()
            treeiter = choix[1]

            modele = self.colonneGroupes.get_model()

            selectionGroupe = modele.get_value(treeiter, 0)

            self.recherche_mode = False
            self.recherche_nom = ""

            fctEvent.obtenirGroupe(self, selectionGroupe)
        except:
            return True


    def selectionnerPaquet (self, selection, modele):
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
            fctEvent.obtenirPaquet(self, nomPaquet, versionPaquet)
        except :
            return True

        return True


    def ouvrirNavigateur (self, cell_renderer, colonne, liste):
        """
        Ouvre le navigateur internet lorsque l'on clique sur le lien
        """

        try:
            modele = liste.get_model()

            if modele[colonne][0] == fctLang.traduire("url"):
                print ("test")
        except:
            pass


    def cocherPaquet (self, cell_renderer, colonne, liste):
        """
        Permet de gérer les paquets à installer/desinstaller via deux
        tableau qui se mettent à jour en fonction du cochage.
        """

        modele = liste.get_model()
        modele[colonne][0] = not modele[colonne][0]

        nomPaquet = modele[colonne][2]

        if nomPaquet.find("]") != -1:
            nomPaquet = nomPaquet[nomPaquet.find("]") + 1:].strip()

        elementAjouter = fctEvent.verifierDonnee(self.listeInstallationPacman, nomPaquet)
        elementEnlever = fctEvent.verifierDonnee(self.listeSuppressionPacman, nomPaquet)

        if modele[colonne][0] == 0:
            # Le paquet en question à été décoché
            if pacman_package_intalled(nomPaquet, modele[colonne][3]) == 1:
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
            if pacman_package_intalled(nomPaquet, modele[colonne][3]) == 1:
                # Le paquet en question est installé
                if elementEnlever != 0:
                    # Le paquet est enlevé de la liste des paquets à supprimer
                    self.listeSuppressionPacman.remove(elementEnlever)
                    if modele[colonne][2] in self.listeMiseAJourPacman:
                        modele[colonne][1] = gtk.STOCK_REFRESH
                    else:
                        modele[colonne][1] = " "
            else:
                if elementAjouter == 0:
                    # Le paquet est mis dans la liste des paquets à installer
                    self.listeInstallationPacman.append(nomPaquet)
                    modele[colonne][1] = gtk.STOCK_ADD


    def effectuerRecherche (self, *args):
        """
        Affiche l'ensemble des paquets correspondant à la recherche
        """

        if self.texteRecherche.get_text != '':
            self.listeColonnePaquets.clear()
            objetRechercher = self.texteRecherche.get_text()

            #~ paquets = fctPaquets.chercherPaquet(db_list[self.listeSelectionGroupe.get_active()], objetRechercher)
            paquets = fctPaquets.chercherPaquet(objetRechercher)

            #~ if not self.recherche_mode:
            fctPaquets.printDebug("DEBUG", str(len(paquets)) + " " + fctLang.traduire("search_package") + " " + objetRechercher)
            self.changerTexteBarreStatus(str(len(paquets)) + " " + fctLang.traduire("search_package") + " " + objetRechercher)

            self.recherche_mode = True
            self.recherche_nom = objetRechercher

            if len(paquets) > 0:
                pacman_trans_release()
                fctEvent.remplirPaquets(self, paquets, recherche = True)

            self.effacerRecherche()


    def effacerRecherche (self, *args):
        """
        Efface la zone de recherche
        """

        self.texteRecherche.set_text("")


    def effacerInterface (self):
        """
        Efface l'ensemble de l'interface
        """

        modele = self.listeSelectionGroupe.get_model()
        modele.clear()
        self.listeSelectionGroupe.set_model(modele)

        self.listeColonneGroupes.clear()
        self.listeColonnePaquets.clear()

        self.contenuInformations.clear()
        self.contenuPaquet.clear()

        self.changerTexteBarreStatus("")


    def effacerListesPaquets (self, *args):
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

        self.changerTexteBarreStatus(fctLang.traduire("clear_changes_done"))


    def changementDepot (self, *args):
        """
        Permet de changer de dépôt
        """

        self.listeColonnePaquets.clear()
        self.listeColonneGroupes.clear()
        fctEvent.ajouterGroupes(self)

        self.changerTexteBarreStatus(fctLang.traduire("change_repo") + " " + str(self.listeSelectionGroupe.get_active_text()))


    def redimensionnement (self, *args):
        """
        Redimensionne la largueur de celluleValeur afin que le texte
        s'adapte à la fenêtre
        """

        self.celluleValeurInformations.set_property("wrap-width", self.fenetre.get_size()[0]/2)
        self.celluleValeurPaquet.set_property("wrap-width", self.fenetre.get_size()[0]/2)
        self.colonnePaquetsNom.set_min_width(self.fenetre.get_size()[0]/2)
        self.colonnePaquets.set_size_request(0, self.fenetre.get_size()[1]/2)


    @staticmethod
    def rafraichirFenetre ():
        """
        Rafraichit l'interface quand des changements ont lieux
        """

        try :
            while gtk.events_pending():
                gtk.main_iteration_do(False)

        except:
            pass


    def changerTexteBarreStatus (self, texte):
        """
        Changer le texte inscrit dans la barre inférieur
        """

        self.barreStatus.push(0, str(texte))


# ------------------------------------------------------------------------------------------------------------
#
#                Fenêtres supplémentaires
#
# ------------------------------------------------------------------------------------------------------------

    def fenetreAPropos (self, widget, *event):
        """
        Affiche la fenêtre A propos commune à toutes les applications :p
        """

        about = gtk.AboutDialog()
        logo = gtk.gdk.pixbuf_new_from_file("./data/logo.png")

        about.set_program_name("pyFPM")
        about.set_version("0001")
        about.set_comments(fctLang.traduire("about_desc"))
        about.set_copyright("(C) 2012-2013 Frugalware Developer Team (GPL)")
        about.set_authors(["Gaetan Gourdin (bouleetbil) - Module python pour pacman-g2", "Aurélien Lubert (PacMiam) - Interface"])
        about.set_license("Ce programme est un logiciel libre, vous pouvez le redistribuer\net/ou le modifier conformément aux dispositions de la Licence Publique\nGénérale GNU, telle que publiée par la Free Software Foundation.")
        about.set_logo(logo)

        about.run()

        about.destroy()


    def fenetreInformation (self, titre, texte):
        """
        Affiche une fenêtre d'information
        """

        information = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, texte)

        information.set_title(titre)
        information.set_default_response(gtk.RESPONSE_OK)

        information.run()

        information.destroy()


    def fenetreInstallation (self, widget, *event):
        """
        Affiche les modifications à effectuer sur les paquets
        """

        if "frugalware" in repo_list:
            index = repo_list.index("frugalware")
        elif "frugalware-current" in repo_list:
            index = repo_list.index("frugalware-current")

        if self.recherche_mode == False:
            self.selectionGroupe = self.colonneGroupes.get_selection()
            self.selectionnerGroupe(self.selectionGroupe, self.listeColonneGroupes)
        else:
            self.texteRecherche.set_text(self.recherche_nom)
            self.effectuerRecherche()

        if len(self.listeInstallationPacman) != 0 or len(self.listeSuppressionPacman):
            self.listeInstallationPacman.sort()
            self.listeSuppressionPacman.sort()

            fenetre = gtk.Dialog(fctLang.traduire("apply_pkg"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_APPLY, gtk.RESPONSE_APPLY))
            texteFenetre = gtk.Label(fctLang.traduire("change_todo"))

            grilleInstallation = gtk.Table(1,3)
            zoneInstallation = gtk.Frame(fctLang.traduire("install_pkg"))
            listeInstallation = gtk.TreeStore(str, str)
            colonnesInstallation = gtk.TreeView()
            colonneInstallationNom = gtk.TreeViewColumn()
            colonneInstallationTaille = gtk.TreeViewColumn()
            celluleInstallationNom = gtk.CellRendererText()
            celluleInstallationTaille = gtk.CellRendererText()
            defilementInstallation = gtk.ScrolledWindow()
            tailleInstallation = gtk.Label("")
            self.verifierDependancesInstallation = gtk.CheckButton(fctLang.traduire("skip_check_deps"))
            self.seulementTelecharger = gtk.CheckButton(fctLang.traduire("download_only"))

            grilleSuppression = gtk.Table(1,3)
            zoneSuppression = gtk.Frame(fctLang.traduire("remove_pkg"))
            listeSuppression = gtk.TreeStore(str, str)
            colonnesSuppression = gtk.TreeView()
            colonneSuppressionNom = gtk.TreeViewColumn()
            celluleSuppressionNom = gtk.CellRendererText()
            colonneSuppressionTaille = gtk.TreeViewColumn()
            celluleSuppressionTaille = gtk.CellRendererText()
            defilementSuppression = gtk.ScrolledWindow()
            tailleSuppression = gtk.Label("")
            self.verifierDependancesSuppression = gtk.CheckButton(fctLang.traduire("skip_check_deps"))

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
                valeurInstallation = 0
                for element in self.listeInstallationPacman:
                    if element.find("]") != -1:
                        element = element[element.find("]") + 1:].strip()
                    paquet = pacman_db_readpkg(db_list[index], element)
                    listeInstallation.append(None, [element, str(format(float(long(pacman_pkg_getinfo(paquet, PM_PKG_SIZE))/1024)/1024, '.2f')) + " MB"])

                    valeurInstallation += float(long(pacman_pkg_getinfo(paquet, PM_PKG_SIZE))/1024)/1024

                tailleInstallation.set_text(fctLang.traduire("total_size") + " : " + str(format(valeurInstallation, '.2f')) + " MB")
                fenetre.vbox.pack_start(zoneInstallation)

            if len(self.listeSuppressionPacman) != 0:
                valeurSuppression = 0
                for element in self.listeSuppressionPacman:
                    if element.find("]") != -1:
                        element = element[element.find("]") + 1:].strip()
                    paquet = pacman_db_readpkg(db_list[index], element)
                    listeSuppression.append(None, [element, str(format(float(long(pacman_pkg_getinfo(paquet, PM_PKG_SIZE))/1024)/1024, '.2f')) + " MB"])

                    valeurSuppression += float(long(pacman_pkg_getinfo(paquet, PM_PKG_SIZE))/1024)/1024

                tailleSuppression.set_text(fctLang.traduire("total_size") + " : " + str(format(valeurSuppression, '.2f')) + " MB")
                fenetre.vbox.pack_start(zoneSuppression)

            fenetre.show_all()
            choix = fenetre.run()

            if choix == gtk.RESPONSE_APPLY:
                fenetre.destroy()
                fctEvent.lancerInstallationPaquets(self)
                self.effacerListesPaquets()
            else:
                fenetre.destroy()
        else:
            self.fenetreInformation(fctLang.traduire("apply_pkg"), fctLang.traduire("no_change"))


    def fenetreMiseAJour (self, *args):
        """
        Prévient qu'il y a des mises à jour et propose de les installer
        """

        self.fenetre.set_sensitive(False)

        fctPaquets.obtenirMiseAJour(self.listeMiseAJourPacman)
        listeTmp = []

        if len(self.listeMiseAJourPacman) > 0:
            for element in self.listeMiseAJourPacman:
                if not element in self.listeInstallationPacman:
                    listeTmp.append(element)

            if len(listeTmp) > 0:
                miseajour = gtk.Dialog(fctLang.traduire("update_system"), None, gtk.DIALOG_MODAL, (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT, gtk.STOCK_OK, gtk.RESPONSE_OK))

                texteInfo = gtk.Label(fctLang.traduire("update_available"))
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
                self.barreStatus.push(0, fctLang.traduire("no_update_available"))

        self.fenetre.set_sensitive(True)


    def fenetreConfirmation (self, nomPaquet, listePaquet):
        """
        Fenêtre de confirmation pour la fonction fctPaquets.lancerPacman
        """

        fenetre = gtk.Dialog(fctLang.traduire("apply_pkg"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))

        texteConfirmation = gtk.Label(fctLang.traduire(nomPaquet))
        listeConfirmation = gtk.TreeStore(str)
        colonnesConfirmation = gtk.TreeView()
        colonneConfirmationNom = gtk.TreeViewColumn()
        celluleConfirmation = gtk.CellRendererText()
        defilementConfirmation = gtk.ScrolledWindow()
        grille = gtk.Table(2,2)

        #~ confirmation.set_has_separator(True)
        confirmation.set_default_response(gtk.RESPONSE_ACCEPT)
        confirmation.set_size_request(400, 400)

        colonnesConfirmation.set_headers_visible(False)
        colonnesConfirmation.set_hover_selection(True)
        colonnesConfirmation.expand_all()

        colonneConfirmationNom.pack_start(celluleConfirmation, True)
        colonneConfirmationNom.add_attribute(celluleConfirmation, "text", 0)

        colonnesConfirmation.append_column(colonneConfirmationNom)
        colonnesConfirmation.set_model(listeConfirmation)

        grille.set_border_width(4)

        defilementConfirmation.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        defilementConfirmation.add(colonnesConfirmation)
        defilementConfirmation.set_border_width(4)

        confirmation.vbox.pack_start(grille)

        grille.attach(texteConfirmation, 0, 1, 0, 1, yoptions=gtk.FILL)
        grille.attach(defilementConfirmation, 0, 1, 1, 2)

        for element in listePaquet:
            listeConfirmation.append(None, [element])

        confirmation.show_all()
        choix = confirmation.run()

        if choix == gtk.RESPONSE_ACCEPT:
            confirmation.destroy()
            return 1
        else:
            confirmation.destroy()
            return 0

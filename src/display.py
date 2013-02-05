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
    sys.exit("pyGTK introuvable")

from package import *
from action import *
from preferences import *
from config import *
from lang import *

fctPaquets = fonctionsPaquets()
fctEvent = fonctionsEvenement()
fctPrefs = fonctionsPreferences()
fctConfig = fonctionsConfiguration()
fctLang = fonctionsLang()


class fonctionsInterface:
    def __init__(interface):

            interface.paquetSelectionne = ""

            interface.listeInstallationPacman = []
            interface.listeSuppressionPacman = []
            interface.listeMiseAJourPacman = []

            interface.recherche_mode = False
            interface.recherche_nom = ""

            # ------------------------------------------------------------------
            #       Fenetre
            # ------------------------------------------------------------------

            interface.fenetre = gtk.Window()
            interface.grille = gtk.Table(1,4)
            interface.groupes = gtk.Table(1,2)
            interface.zoneColonnePaquets = gtk.Table(2,1)
            interface.zonePaquetsInformations = gtk.VPaned()

            interface.barreStatus = gtk.Statusbar()

            # ------------------------------------------------------------------
            #       Menu
            # ------------------------------------------------------------------

            interface.menu = gtk.MenuBar()
            interface.menu_action = gtk.MenuItem(label=fctLang.traduire("action"))
            interface.menu_action_list = gtk.Menu()
            interface.menu_action_install = gtk.ImageMenuItem(fctLang.traduire("apply_pkg"))
            interface.menu_action_clean = gtk.ImageMenuItem(fctLang.traduire("clean_cache"))
            interface.menu_action_update = gtk.ImageMenuItem(fctLang.traduire("update_database"))
            interface.menu_action_check = gtk.ImageMenuItem(fctLang.traduire("check_update"))
            interface.menu_action_quit = gtk.ImageMenuItem(fctLang.traduire("quit"))
            interface.menu_edit = gtk.MenuItem(label=fctLang.traduire("edit"))
            interface.menu_edit_list = gtk.Menu()
            interface.menu_edit_clear_changes = gtk.ImageMenuItem(fctLang.traduire("clear_changes"))
            interface.menu_edit_preference = gtk.ImageMenuItem(fctLang.traduire("preferences"))
            interface.menu_help = gtk.MenuItem(label=fctLang.traduire("help"))
            interface.menu_help_list = gtk.Menu()
            interface.menu_help_about = gtk.ImageMenuItem(fctLang.traduire("about"))

            # ------------------------------------------------------------------
            #       Barre d'outils
            # ------------------------------------------------------------------

            interface.outils = gtk.Toolbar()
            interface.texteRecherche = gtk.Entry()

            # ------------------------------------------------------------------
            #       Liste des groupes
            # ------------------------------------------------------------------

            interface.zoneSelectionGroupe = gtk.Frame(fctLang.traduire("select_group"))
            interface.listeSelectionGroupe = gtk.combo_box_new_text()

            # ------------------------------------------------------------------
            #       Colonnes des groupes
            # ------------------------------------------------------------------

            interface.zoneGroupes = gtk.Frame(fctLang.traduire("list_groups"))
            interface.listeColonneGroupes = gtk.ListStore(str)
            interface.colonneGroupes = gtk.TreeView(interface.listeColonneGroupes)
            interface.colonneGroupesNom = gtk.TreeViewColumn(fctLang.traduire("groups"))
            interface.celluleGroupesNom = gtk.CellRendererText()
            interface.defilementGroupes = gtk.ScrolledWindow()

            # ------------------------------------------------------------------
            #       Colonnes des paquets
            # ------------------------------------------------------------------

            interface.zonePaquets = gtk.Frame(fctLang.traduire("packages_list"))
            interface.listeColonnePaquets = gtk.ListStore(int, str, str, str, str)
            interface.colonnePaquets = gtk.TreeView(interface.listeColonnePaquets)
            interface.colonnePaquetsCheckbox = gtk.TreeViewColumn(" ")
            interface.cellulePaquetsCheckbox = gtk.CellRendererToggle()
            interface.colonnePaquetsImage = gtk.TreeViewColumn(" ")
            interface.cellulePaquetsImage = gtk.CellRendererPixbuf()
            interface.colonnePaquetsNom = gtk.TreeViewColumn(fctLang.traduire("name"))
            interface.cellulePaquetsNom = gtk.CellRendererText()
            interface.colonnePaquetsVersionActuelle = gtk.TreeViewColumn(fctLang.traduire("actual_version"))
            interface.cellulePaquetsVersionActuelle = gtk.CellRendererText()
            interface.colonnePaquetsVersionDisponible = gtk.TreeViewColumn(fctLang.traduire("current_version"))
            interface.cellulePaquetsVersionDisponible = gtk.CellRendererText()
            interface.defilementPaquets = gtk.ScrolledWindow()

            # ------------------------------------------------------------------
            #       Informations sur le paquet
            # ------------------------------------------------------------------

            interface.zoneInformations = gtk.Notebook()
            interface.labelInformations = gtk.Label(fctLang.traduire("informations"))
            interface.labelPaquet = gtk.Label(fctLang.traduire("package"))
            interface.labelFichiers = gtk.Label(fctLang.traduire("files"))
            interface.labelJournal = gtk.Label(fctLang.traduire("changelog"))
            interface.listeInformations = gtk.TreeView()
            interface.colonneLabelInformations = gtk.TreeViewColumn()
            interface.celluleLabelInformations = gtk.CellRendererText()
            interface.colonneValeurInformations = gtk.TreeViewColumn()
            interface.celluleValeurInformations = gtk.CellRendererText()
            interface.contenuInformations = gtk.TreeStore(str,str)
            interface.defilementInformations = gtk.ScrolledWindow()
            interface.listePaquet = gtk.TreeView()
            interface.colonneLabelPaquet = gtk.TreeViewColumn()
            interface.celluleLabelPaquet = gtk.CellRendererText()
            interface.colonneValeurPaquet = gtk.TreeViewColumn()
            interface.celluleValeurPaquet = gtk.CellRendererText()
            interface.contenuPaquet = gtk.TreeStore(str,str)
            interface.defilementPaquet = gtk.ScrolledWindow()
            interface.listeFichiers = gtk.TextView()
            interface.defilementFichiers = gtk.ScrolledWindow()
            interface.listeJournal = gtk.TextView()
            interface.defilementJournal = gtk.ScrolledWindow()


    def fenetrePrincipale (interface):

        longueur = fctConfig.lireConfig("screen", "width")
        hauteur = fctConfig.lireConfig("screen", "height")

        if int(longueur) >= 800 and int(hauteur) >= 600:

            # ------------------------------------------------------------------
            #       Fenetre
            # ------------------------------------------------------------------

            interface.fenetre.set_title(fctLang.traduire("title"))
            interface.fenetre.set_size_request(int(longueur), int(hauteur))
            interface.fenetre.set_resizable(True)
            interface.fenetre.set_position(gtk.WIN_POS_CENTER)

            # ------------------------------------------------------------------
            #       Menu
            # ------------------------------------------------------------------

            interface.fenetre.connect("destroy", gtk.main_quit)
            interface.fenetre.connect("check-resize", interface.redimensionnement)

            interface.menu_action_install.set_image(gtk.image_new_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU))
            interface.menu_action_install.connect("activate", interface.fenetreInstallation, interface)

            interface.menu_action_clean.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
            interface.menu_action_clean.connect("activate", fctEvent.lancerNettoyerCache, interface)

            interface.menu_action_update.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU))
            interface.menu_action_update.connect("activate", fctEvent.lancerMiseajourBaseDonnees, interface)

            interface.menu_action_check.set_image(gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU))
            interface.menu_action_check.connect("activate", interface.fenetreMiseAJour)

            interface.menu_action_quit.set_image(gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU))
            interface.menu_action_quit.connect("activate", fctEvent.detruire)

            interface.menu.add(interface.menu_action)

            interface.menu_action_list.add(interface.menu_action_install)
            interface.menu_action_list.add(interface.menu_action_clean)
            interface.menu_action_list.add(interface.menu_action_update)
            interface.menu_action_list.add(interface.menu_action_check)
            interface.menu_action_list.add(interface.menu_action_quit)

            interface.menu_action.set_submenu(interface.menu_action_list)

            interface.menu_edit_clear_changes.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
            interface.menu_edit_clear_changes.connect("activate", interface.effacerListesPaquets)

            interface.menu_edit_preference.set_image(gtk.image_new_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU))
            interface.menu_edit_preference.connect("activate", fctPrefs.fenetrePreferences, interface)

            interface.menu.add(interface.menu_edit)

            interface.menu_edit_list.add(interface.menu_edit_clear_changes)
            interface.menu_edit_list.add(interface.menu_edit_preference)

            interface.menu_edit.set_submenu(interface.menu_edit_list)
            interface.menu_help_about.set_image(gtk.image_new_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU))
            interface.menu_help_about.connect("activate", interface.fenetreAPropos)

            interface.menu.add(interface.menu_help)

            interface.menu_help_list.add(interface.menu_help_about)

            interface.menu_help.set_submenu(interface.menu_help_list)

            # ------------------------------------------------------------------
            #       Barre d'outils
            # ------------------------------------------------------------------

            interface.outils.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            interface.outils.set_style(gtk.TOOLBAR_ICONS)

            interface.outils.insert_stock(gtk.STOCK_APPLY, fctLang.traduire("apply_pkg"), None, interface.fenetreInstallation, interface, 0)
            interface.outils.insert_stock(gtk.STOCK_REFRESH, fctLang.traduire("update_database"), None, fctEvent.lancerMiseajourBaseDonnees, interface, 2)
            interface.outils.insert_space(3)
            interface.texteRecherche.set_icon_from_stock(1, gtk.STOCK_CLEAR)
            interface.texteRecherche.connect("activate", interface.effectuerRecherche, gtk.RESPONSE_OK)
            interface.texteRecherche.connect("icon-press", interface.effacerRecherche)
            interface.texteRecherche.grab_focus()
            interface.outils.insert_widget(interface.texteRecherche, fctLang.traduire("write_search"), None, 4)
            interface.outils.insert_stock(gtk.STOCK_FIND, fctLang.traduire("search"), None, interface.effectuerRecherche, None, 5)
            interface.outils.insert_space(6)
            interface.outils.insert_stock(gtk.STOCK_PREFERENCES, fctLang.traduire("preferences"), None, fctPrefs.fenetrePreferences, interface, 7)
            interface.outils.insert_stock(gtk.STOCK_QUIT, fctLang.traduire("quit"), None, fctEvent.detruire, None, 8)

            # ------------------------------------------------------------------
            #       Liste des groupes
            # ------------------------------------------------------------------

            interface.zoneSelectionGroupe.add(interface.listeSelectionGroupe)
            interface.zoneSelectionGroupe.set_border_width(4)
            interface.listeSelectionGroupe.connect('changed', interface.changementDepot, interface)

            fctEvent.ajouterDepots(interface)

            # ------------------------------------------------------------------
            #       Colonnes des groupes
            # ------------------------------------------------------------------

            interface.listeColonneGroupes.clear()

            interface.colonneGroupes.set_headers_visible(False)
            interface.colonneGroupes.set_size_request(180,0)
            interface.colonneGroupes.set_search_column(0)

            interface.colonneGroupesNom.set_sort_column_id(0)
            interface.colonneGroupesNom.pack_start(interface.celluleGroupesNom, True)
            interface.colonneGroupesNom.add_attribute(interface.celluleGroupesNom, 'text', 0)
            interface.colonneGroupes.append_column(interface.colonneGroupesNom)

            fctEvent.ajouterGroupes(interface)

            interface.defilementGroupes.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            interface.defilementGroupes.add(interface.colonneGroupes)
            interface.defilementGroupes.set_border_width(4)

            interface.selectionGroupe = interface.colonneGroupes.get_selection()
            interface.selectionGroupe.connect('changed', interface.selectionnerGroupe, interface.listeColonneGroupes)

            interface.zoneGroupes.add(interface.defilementGroupes)
            interface.zoneGroupes.set_border_width(4)
            interface.zoneGroupes.set_resize_mode(gtk.RESIZE_PARENT)

            interface.groupes.attach(interface.zoneSelectionGroupe, 0, 1, 0, 1, yoptions=gtk.FILL)
            interface.groupes.attach(interface.zoneGroupes, 0, 1, 1, 2)

            # ------------------------------------------------------------------
            #       Colonnes des paquets
            # ------------------------------------------------------------------

            interface.listeColonnePaquets.clear()
            interface.listeColonnePaquets.set_sort_column_id(2, gtk.SORT_ASCENDING)

            interface.colonnePaquets.set_headers_visible(True)
            interface.colonnePaquets.set_search_column(2)

            interface.colonnePaquetsCheckbox.set_sort_column_id(0)
            interface.colonnePaquetsImage.set_sort_column_id(1)
            interface.colonnePaquetsNom.set_min_width(300)
            interface.colonnePaquetsNom.set_sort_column_id(2)
            interface.colonnePaquetsVersionActuelle.set_sort_column_id(3)
            interface.colonnePaquetsVersionDisponible.set_sort_column_id(4)

            interface.cellulePaquetsCheckbox.set_property('active', 1)
            interface.cellulePaquetsCheckbox.set_property('activatable', True)
            interface.cellulePaquetsCheckbox.connect('toggled', interface.cocherPaquet, interface.colonnePaquets)

            interface.colonnePaquetsCheckbox.pack_start(interface.cellulePaquetsCheckbox, True)
            interface.colonnePaquetsCheckbox.add_attribute(interface.cellulePaquetsCheckbox, 'active', 0)
            interface.colonnePaquetsImage.pack_start(interface.cellulePaquetsImage, False)
            interface.colonnePaquetsImage.add_attribute(interface.cellulePaquetsImage, 'stock_id', 1)
            interface.colonnePaquetsNom.pack_start(interface.cellulePaquetsNom, True)
            interface.colonnePaquetsNom.add_attribute(interface.cellulePaquetsNom, 'text', 2)
            interface.colonnePaquetsVersionActuelle.pack_start(interface.cellulePaquetsVersionActuelle, True)
            interface.colonnePaquetsVersionActuelle.add_attribute(interface.cellulePaquetsVersionActuelle, 'text', 3)
            interface.colonnePaquetsVersionDisponible.pack_start(interface.cellulePaquetsVersionDisponible, True)
            interface.colonnePaquetsVersionDisponible.add_attribute(interface.cellulePaquetsVersionDisponible, 'text', 4)

            interface.colonnePaquets.append_column(interface.colonnePaquetsCheckbox)
            interface.colonnePaquets.append_column(interface.colonnePaquetsImage)
            interface.colonnePaquets.append_column(interface.colonnePaquetsNom)
            interface.colonnePaquets.append_column(interface.colonnePaquetsVersionActuelle)
            interface.colonnePaquets.append_column(interface.colonnePaquetsVersionDisponible)

            interface.defilementPaquets.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            interface.defilementPaquets.add(interface.colonnePaquets)
            interface.defilementPaquets.set_border_width(4)

            interface.selectionPaquet = interface.colonnePaquets.get_selection()
            interface.selectionPaquet.connect('changed', interface.selectionnerPaquet, interface.listeColonnePaquets)

            interface.zonePaquets.add(interface.defilementPaquets)
            interface.zonePaquets.set_border_width(4)

            interface.zoneColonnePaquets.attach(interface.groupes, 0, 1, 0, 1, xoptions=gtk.FILL)
            interface.zoneColonnePaquets.attach(interface.zonePaquetsInformations, 1, 2, 0, 1)

            # ------------------------------------------------------------------
            #       Informations sur le paquet
            # ------------------------------------------------------------------

            interface.listeInformations.set_headers_visible(False)
            interface.listeInformations.set_hover_selection(False)

            interface.celluleLabelInformations.set_property('weight', pango.WEIGHT_BOLD)

            interface.colonneLabelInformations.pack_start(interface.celluleLabelInformations, True)
            interface.colonneLabelInformations.add_attribute(interface.celluleLabelInformations, "text", 0)
            interface.colonneValeurInformations.pack_start(interface.celluleValeurInformations, True)
            interface.colonneValeurInformations.add_attribute(interface.celluleValeurInformations, "markup", 1)

            interface.celluleValeurInformations.set_property('wrap-mode', pango.WRAP_WORD)
            interface.celluleValeurInformations.set_property('editable', True)

            interface.listeInformations.append_column(interface.colonneLabelInformations)
            interface.listeInformations.append_column(interface.colonneValeurInformations)
            interface.listeInformations.set_model(interface.contenuInformations)

            interface.defilementInformations.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            interface.defilementInformations.add(interface.listeInformations)
            interface.defilementInformations.set_border_width(4)

            interface.listePaquet.set_headers_visible(False)
            interface.listePaquet.set_hover_selection(False)

            interface.celluleLabelPaquet.set_property('weight', pango.WEIGHT_BOLD)

            interface.colonneLabelPaquet.pack_start(interface.celluleLabelPaquet, True)
            interface.colonneLabelPaquet.add_attribute(interface.celluleLabelPaquet, "text", 0)
            interface.colonneValeurPaquet.pack_start(interface.celluleValeurPaquet, True)
            interface.colonneValeurPaquet.add_attribute(interface.celluleValeurPaquet, "markup", 1)

            interface.celluleValeurPaquet.set_property('wrap-mode', pango.WRAP_WORD)
            interface.celluleValeurPaquet.set_property('editable', True)

            interface.listePaquet.append_column(interface.colonneLabelPaquet)
            interface.listePaquet.append_column(interface.colonneValeurPaquet)
            interface.listePaquet.set_model(interface.contenuPaquet)

            interface.defilementPaquet.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            interface.defilementPaquet.add(interface.listePaquet)
            interface.defilementPaquet.set_border_width(4)

            interface.listeFichiers.set_editable(False)
            interface.listeFichiers.set_cursor_visible(False)

            interface.defilementFichiers.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            interface.defilementFichiers.add(interface.listeFichiers)
            interface.defilementFichiers.set_border_width(4)

            interface.listeJournal.set_editable(False)
            interface.listeJournal.set_cursor_visible(False)

            interface.defilementJournal.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            interface.defilementJournal.add(interface.listeJournal)
            interface.defilementJournal.set_border_width(4)

            interface.zoneInformations.set_tab_pos(gtk.POS_LEFT)
            interface.zoneInformations.append_page(interface.defilementInformations, interface.labelInformations)
            interface.zoneInformations.append_page(interface.defilementPaquet, interface.labelPaquet)
            interface.zoneInformations.append_page(interface.defilementFichiers, interface.labelFichiers)
            interface.zoneInformations.append_page(interface.defilementJournal, interface.labelJournal)
            interface.zoneInformations.set_border_width(4)
            interface.zoneInformations.set_resize_mode(gtk.RESIZE_PARENT)

            # ------------------------------------------------------------------
            #       Intégration des widgets
            # ------------------------------------------------------------------

            interface.zonePaquetsInformations.add1(interface.zonePaquets)
            interface.zonePaquetsInformations.add2(interface.zoneInformations)

            interface.grille.attach(interface.menu, 0, 1, 0, 1, yoptions=gtk.FILL)
            interface.grille.attach(interface.outils, 0, 1, 1, 2, yoptions=gtk.FILL)
            interface.grille.attach(interface.zoneColonnePaquets, 0, 1, 2, 3)
            interface.grille.attach(interface.barreStatus, 0, 1, 3, 4, yoptions=gtk.FILL)

            interface.fenetre.add(interface.grille)

            interface.fenetre.show_all()

            if fctConfig.lireConfig("pyfpm", "startupdate") == "true":
                interface.fenetreMiseAJour()
            else:
                fctPaquets.obtenirMiseAJour(interface.listeMiseAJourPacman)

        else:
            try:
                interface.fenetreInformation(fctLang.traduire("error"), fctLang.traduire("limit_size"))
            except:
                pass

            sys.exit("[ERROR] - La fenêtre ne peut avoir une taille inférieur à 800x600")


    def selectionnerGroupe (interface, selection, modele):
        """
        Récupère les informations concernant le groupe actuellement
        sélectionné.
        """

        try:
            choix = selection.get_selected()
            treeiter = choix[1]

            modele = interface.colonneGroupes.get_model()

            selectionGroupe = modele.get_value(treeiter, 0)

            interface.recherche_mode = False
            interface.recherche_nom = ""

            fctEvent.obtenirGroupe(interface, selectionGroupe)
        except:
            return True


    def selectionnerPaquet (interface, selection, modele):
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
            fctEvent.obtenirPaquet(interface, nomPaquet, versionPaquet)
        except :
            return True

        return True


    def ouvrirNavigateur (interface, cell_renderer, colonne, liste):
        """
        Ouvre le navigateur internet lorsque l'on clique sur le lien
        """

        try:
            modele = liste.get_model()

            if modele[colonne][0] == fctLang.traduire("url"):
                print ("test")
        except:
            pass


    def cocherPaquet (interface, cell_renderer, colonne, liste):
        """
        Permet de gérer les paquets à installer/desinstaller via deux
        tableau qui se mettent à jour en fonction du cochage.
        """

        modele = liste.get_model()
        modele[colonne][0] = not modele[colonne][0]
        
        nomPaquet = modele[colonne][2]
        
        if nomPaquet.find("]") != -1:
            nomPaquet = nomPaquet[nomPaquet.find("]") + 1:].strip()

        elementAjouter = fctEvent.verifierDonnee(interface.listeInstallationPacman, nomPaquet)
        elementEnlever = fctEvent.verifierDonnee(interface.listeSuppressionPacman, nomPaquet)

        if modele[colonne][0] == 0:
            # Le paquet en question à été décoché
            if pacman_package_intalled(nomPaquet, modele[colonne][3]) == 1:
                # Le paquet en question est installé
                if elementEnlever == 0:
                    # Le paquet est mis dans la liste des paquets à supprimer
                    interface.listeSuppressionPacman.append(nomPaquet)
                    modele[colonne][1] = gtk.STOCK_REMOVE
            else:
                if elementAjouter != 0:
                    # Le paquet est enlevé de la liste des paquets à installer
                    interface.listeInstallationPacman.remove(elementAjouter)
                    modele[colonne][1] = " "

        else:
            # Le paquet en question à été coché
            if pacman_package_intalled(nomPaquet, modele[colonne][3]) == 1:
                # Le paquet en question est installé
                if elementEnlever != 0:
                    # Le paquet est enlevé de la liste des paquets à supprimer
                    interface.listeSuppressionPacman.remove(elementEnlever)
                    if modele[colonne][2] in interface.listeMiseAJourPacman:
                        modele[colonne][1] = gtk.STOCK_REFRESH
                    else:
                        modele[colonne][1] = " "
            else:
                if elementAjouter == 0:
                    # Le paquet est mis dans la liste des paquets à installer
                    interface.listeInstallationPacman.append(nomPaquet)
                    modele[colonne][1] = gtk.STOCK_ADD


    def effectuerRecherche (interface, *args):
        """
        Affiche l'ensemble des paquets correspondant à la recherche
        """

        if interface.texteRecherche.get_text != '':
            interface.listeColonnePaquets.clear()
            objetRechercher = interface.texteRecherche.get_text()

            #~ paquets = fctPaquets.chercherPaquet(db_list[interface.listeSelectionGroupe.get_active()], objetRechercher)
            paquets = fctPaquets.chercherPaquet(objetRechercher)

            #~ if not interface.recherche_mode:
            fctPaquets.printDebug("DEBUG", str(len(paquets)) + " " + fctLang.traduire("search_package") + " " + objetRechercher)
            interface.changerTexteBarreStatus(str(len(paquets)) + " " + fctLang.traduire("search_package") + " " + objetRechercher)

            interface.recherche_mode = True
            interface.recherche_nom = objetRechercher

            if len(paquets) > 0:
                pacman_trans_release()
                fctEvent.remplirPaquets(interface, paquets, recherche = True)

            interface.effacerRecherche()


    def effacerRecherche (interface, *args):
        """
        Efface la zone de recherche
        """

        interface.texteRecherche.set_text("")


    def effacerInterface (interface):
        """
        Efface l'ensemble de l'interface
        """

        modele = interface.listeSelectionGroupe.get_model()
        modele.clear()
        interface.listeSelectionGroupe.set_model(modele)

        interface.listeColonneGroupes.clear()
        interface.listeColonnePaquets.clear()

        interface.contenuInformations.clear()
        interface.contenuPaquet.clear()

        interface.changerTexteBarreStatus("")


    def effacerListesPaquets (interface, *args):
        """
        Remet à zéro la liste des paquets à installer et désinstaller
        """

        interface.listeInstallationPacman = []
        interface.listeSuppressionPacman  = []

        try:
            interface.selectionGroupe = interface.colonneGroupes.get_selection()
            interface.selectionnerGroupe(interface.selectionGroupe, interface.listeColonneGroupes)
        except:
            pass

        interface.changerTexteBarreStatus(fctLang.traduire("clear_changes_done"))


    def changementDepot (interface, *args):
        """
        Permet de changer de dépôt
        """

        interface.listeColonnePaquets.clear()
        interface.listeColonneGroupes.clear()
        fctEvent.ajouterGroupes(interface)

        interface.changerTexteBarreStatus(fctLang.traduire("change_repo") + " " + str(interface.listeSelectionGroupe.get_active_text()))


    def redimensionnement (interface, *args):
        """
        Redimensionne la largueur de celluleValeur afin que le texte
        s'adapte à la fenêtre
        """

        interface.celluleValeurInformations.set_property("wrap-width", interface.fenetre.get_size()[0]/2)
        interface.celluleValeurPaquet.set_property("wrap-width", interface.fenetre.get_size()[0]/2)
        interface.colonnePaquetsNom.set_min_width(interface.fenetre.get_size()[0]/2)
        interface.colonnePaquets.set_size_request(0, interface.fenetre.get_size()[1]/2)


    def rafraichirFenetre (interface):
        """
        Rafraichit l'interface quand des changements ont lieux
        """

        try :
            while gtk.events_pending():
                gtk.main_iteration_do(False)

        except:
            pass


    def changerTexteBarreStatus (interface, texte):
        """
        Changer le texte inscrit dans la barre inférieur
        """

        interface.barreStatus.push(0, str(texte))


# ------------------------------------------------------------------------------------------------------------
#
#                Fenêtres supplémentaires
#
# ------------------------------------------------------------------------------------------------------------

    def fenetreAPropos (objet, widget, *event):
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


    def fenetreInformation (objet, titre, texte):
        """
        Affiche une fenêtre d'information
        """

        information = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, texte)

        information.set_title(titre)
        information.set_default_response(gtk.RESPONSE_OK)

        information.run()

        information.destroy()


    def fenetreInstallation (objet, widget, interface, *event):
        """
        Affiche les modifications à effectuer sur les paquets
        """

        if "frugalware" in repo_list:
            index = repo_list.index("frugalware")
        elif "frugalware-current" in repo_list:
            index = repo_list.index("frugalware-current")

        if interface.recherche_mode == False:
            interface.selectionGroupe = interface.colonneGroupes.get_selection()
            interface.selectionnerGroupe(interface.selectionGroupe, interface.listeColonneGroupes)
        else:
            interface.texteRecherche.set_text(interface.recherche_nom)
            interface.effectuerRecherche()

        if len(interface.listeInstallationPacman) != 0 or len(interface.listeSuppressionPacman):
            interface.listeInstallationPacman.sort()
            interface.listeSuppressionPacman.sort()

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
            verifierDependancesInstallation = gtk.CheckButton(fctLang.traduire("skip_check_deps"))
            seulementTelecharger = gtk.CheckButton(fctLang.traduire("download_only"))

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
            verifierDependancesSuppression = gtk.CheckButton(fctLang.traduire("skip_check_deps"))

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
            grilleInstallation.attach(verifierDependancesInstallation, 0, 1, 2, 3, yoptions=gtk.FILL)
            grilleInstallation.attach(seulementTelecharger, 0, 1, 3, 4, yoptions=gtk.FILL)
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
            grilleSuppression.attach(verifierDependancesSuppression, 0, 1, 2, 3, yoptions=gtk.FILL)
            grilleSuppression.set_border_width(4)

            zoneSuppression.add(grilleSuppression)
            zoneSuppression.set_border_width(4)

            fenetre.vbox.pack_start(texteFenetre, expand=False)
            if len(interface.listeInstallationPacman) != 0:
                valeurInstallation = 0
                for element in interface.listeInstallationPacman:
                    if element.find("]") != -1:
                        element = element[element.find("]") + 1:].strip()
                    paquet = pacman_db_readpkg(db_list[index], element)
                    listeInstallation.append(None, [element, str(format(float(long(pacman_pkg_getinfo(paquet, PM_PKG_SIZE))/1024)/1024, '.2f')) + " MB"])
                    
                    valeurInstallation += float(long(pacman_pkg_getinfo(paquet, PM_PKG_SIZE))/1024)/1024
                    
                tailleInstallation.set_text(fctLang.traduire("total_size") + " : " + str(format(valeurInstallation, '.2f')) + " MB")
                fenetre.vbox.pack_start(zoneInstallation)

            if len(interface.listeSuppressionPacman) != 0:
                valeurSuppression = 0
                for element in interface.listeSuppressionPacman:
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
                fctEvent.lancerInstallationPaquets(interface)
                interface.effacerListesPaquets()
            else:
                fenetre.destroy()
        else:
            interface.fenetreInformation(fctLang.traduire("apply_pkg"), fctLang.traduire("no_change"))


    def fenetreMiseAJour (interface, *args):
        """
        Prévient qu'il y a des mises à jour et propose de les installer
        """

        interface.fenetre.set_sensitive(False)

        fctPaquets.obtenirMiseAJour(interface.listeMiseAJourPacman)
        listeTmp = []

        if len(interface.listeMiseAJourPacman) > 0:
            for element in interface.listeMiseAJourPacman:
                if not element in interface.listeInstallationPacman:
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
                    for element in interface.listeMiseAJourPacman:
                        if not element in interface.listeInstallationPacman:
                            interface.listeInstallationPacman.append(str(element))
                    miseajour.destroy()
                else:
                    miseajour.destroy()
            else:
                interface.barreStatus.push(0, fctLang.traduire("no_update_available"))

        interface.fenetre.set_sensitive(True)


    def fenetreConfirmation (interface, nomPaquet, listePaquet):
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

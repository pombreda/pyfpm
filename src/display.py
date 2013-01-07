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

from config import *
fctConfig = fonctionsConfiguration()

from lang import *
fctLang = fonctionsLang()

from action import *
fctEvent = fonctionsEvenement()

# ----------------------------------------------------------------------
#   fonctionsInterface
#       cocherPaquet (interface, cell_renderer, colonne, liste)
#       effacerRecherche (interface, *args)
#       effectuerRecherche (interface, *args)
#       fenetreAPropos (objet, widget, *event)
#       fenetrePrincipale (objet)
#       selectionnerGroupe (interface, selection, modele)
#       selectionnerPaquet (interface, selection, modele)
# ----------------------------------------------------------------------

class fonctionsInterface:
    def __init__(interface):

            interface.listePaquetsInstalles = []
            interface.listeInstallation = []
            interface.listeSuppression = []
            interface.paquetSelectionne = ""

            interface.fenetre = gtk.Window()
            interface.grille = gtk.Table(1,4)

            interface.menu = gtk.MenuBar()
            interface.menu_action = gtk.MenuItem(label=fctLang.traduire("action"))
            interface.menu_action_list = gtk.Menu()
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

            interface.outils = gtk.Toolbar()
            interface.texteRecherche = gtk.Entry()

            interface.zoneGroupes = gtk.Frame(fctLang.traduire("groups"))
            interface.listeColonneGroupes = gtk.ListStore(str)
            interface.colonneGroupes = gtk.TreeView(interface.listeColonneGroupes)
            interface.colonneGroupesNom = gtk.TreeViewColumn(fctLang.traduire("groups"))
            interface.celluleGroupesNom = gtk.CellRendererText()
            interface.defilementGroupes = gtk.ScrolledWindow()

            interface.zonePaquets = gtk.Frame(fctLang.traduire("packages_list"))
            interface.listeColonnePaquets = gtk.ListStore(int, str, str)
            interface.colonnePaquets = gtk.TreeView(interface.listeColonnePaquets)
            interface.colonnePaquetsCheckbox = gtk.TreeViewColumn(" ")
            interface.colonnePaquetsNom = gtk.TreeViewColumn(fctLang.traduire("name"))
            interface.colonnePaquetsVersion = gtk.TreeViewColumn(fctLang.traduire("version"))
            interface.cellulePaquetsCheckbox = gtk.CellRendererToggle()
            interface.cellulePaquetsNom = gtk.CellRendererText()
            interface.cellulePaquetsVersion = gtk.CellRendererText()
            interface.defilementPaquets = gtk.ScrolledWindow()
            
            interface.zoneInformations = gtk.Frame(fctLang.traduire("informations"))
            interface.listeInformations = gtk.TreeView()
            interface.colonneLabel = gtk.TreeViewColumn()
            interface.celluleLabel = gtk.CellRendererText()
            interface.colonneValeur = gtk.TreeViewColumn()
            interface.celluleValeur = gtk.CellRendererText()
            interface.contenuInformations = gtk.TreeStore(str,str)
            interface.defilementInformations = gtk.ScrolledWindow()

            interface.barreStatus = gtk.Statusbar()
            interface.barreProgres = gtk.ProgressBar()

            interface.zoneBarreStatus = gtk.HBox()

            interface.zoneColonnePaquets = gtk.HPaned()
            interface.zonePaquetsInformations = gtk.VPaned()


    def fenetrePrincipale (interface):

        longueur = fctConfig.lireConfig("screen", "width")
        hauteur = fctConfig.lireConfig("screen", "height")

        if int(longueur) >= 800 and int(hauteur) >= 600:

            # ------------------------------------------------------------------
            #       Menu
            # ------------------------------------------------------------------

            interface.menu_action_clean.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
            interface.menu_action_clean.connect("activate", fctEvent.lancerNettoyerCache)

            interface.menu_action_update.set_image(gtk.image_new_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU))
            interface.menu_action_update.connect("activate", fctEvent.lancerMiseajourBaseDonnees)

            interface.menu_action_check.set_image(gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU))
            #~ interface.menu_action_update.connect("activate", fctPaquets.verifierMiseajour)

            interface.menu_action_quit.set_image(gtk.image_new_from_stock(gtk.STOCK_QUIT, gtk.ICON_SIZE_MENU))
            interface.menu_action_quit.connect("activate", fctEvent.detruire)

            interface.menu.add(interface.menu_action)

            interface.menu_action_list.add(interface.menu_action_clean)
            interface.menu_action_list.add(interface.menu_action_update)
            interface.menu_action_list.add(interface.menu_action_check)
            interface.menu_action_list.add(interface.menu_action_quit)

            interface.menu_action.set_submenu(interface.menu_action_list)

            interface.menu_edit_clear_changes.set_image(gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU))
            #~ menu_edit_clear_changes.connect("activate", resetSelect)

            interface.menu_edit_preference.set_image(gtk.image_new_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU))
            #~ menu_edit_preference.connect("activate", preferences)

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

            interface.outils.insert_stock(gtk.STOCK_APPLY, fctLang.traduire("apply_pkg"), None, None, None, 0)
            interface.outils.insert_stock(gtk.STOCK_REFRESH, fctLang.traduire("refresh_pkg"), None, fctEvent.lancerMiseajourBaseDonnees, None, 2)
            interface.outils.insert_space(3)
            interface.texteRecherche.set_icon_from_stock(1, gtk.STOCK_CLEAR)
            interface.texteRecherche.connect("activate", interface.effectuerRecherche, gtk.RESPONSE_OK)
            interface.texteRecherche.connect("icon-press", interface.effacerRecherche)
            interface.texteRecherche.grab_focus()
            interface.outils.insert_widget(interface.texteRecherche, fctLang.traduire("write_search"), None, 4)
            interface.outils.insert_stock(gtk.STOCK_FIND, fctLang.traduire("search"), None, interface.effectuerRecherche, None, 5)
            interface.outils.insert_space(6)
            interface.outils.insert_stock(gtk.STOCK_QUIT, fctLang.traduire("quit"), None, fctEvent.detruire, None, 7)


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


            # ------------------------------------------------------------------
            #       Colonnes des paquets
            # ------------------------------------------------------------------

            interface.listeColonnePaquets.clear()
            interface.listeColonnePaquets.set_sort_column_id(1, gtk.SORT_ASCENDING)

            interface.colonnePaquets.set_headers_visible(True)
            interface.colonnePaquets.set_size_request(0,300)
            interface.colonnePaquets.set_search_column(1)

            interface.colonnePaquetsCheckbox.set_sort_column_id(0)
            interface.colonnePaquetsNom.set_min_width(300)
            interface.colonnePaquetsNom.set_sort_column_id(1)
            interface.colonnePaquetsVersion.set_sort_column_id(2)

            interface.cellulePaquetsCheckbox.set_property('active', 1)
            interface.cellulePaquetsCheckbox.set_property('activatable', True)
            interface.cellulePaquetsCheckbox.connect('toggled', interface.cocherPaquet, interface.colonnePaquets)

            interface.colonnePaquetsCheckbox.pack_start(interface.cellulePaquetsCheckbox, True)
            interface.colonnePaquetsCheckbox.add_attribute(interface.cellulePaquetsCheckbox, 'active', 0)
            interface.colonnePaquetsNom.pack_start(interface.cellulePaquetsNom, True)
            interface.colonnePaquetsNom.add_attribute(interface.cellulePaquetsNom, 'text', 1)
            interface.colonnePaquetsVersion.pack_start(interface.cellulePaquetsVersion, True)
            interface.colonnePaquetsVersion.add_attribute(interface.cellulePaquetsVersion, 'text', 2)

            interface.colonnePaquets.append_column(interface.colonnePaquetsCheckbox)
            interface.colonnePaquets.append_column(interface.colonnePaquetsNom)
            interface.colonnePaquets.append_column(interface.colonnePaquetsVersion)

            interface.defilementPaquets.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            interface.defilementPaquets.add(interface.colonnePaquets)
            interface.defilementPaquets.set_border_width(4)
            
            interface.selectionPaquet = interface.colonnePaquets.get_selection()
            interface.selectionPaquet.connect('changed', interface.selectionnerPaquet, interface.listeColonnePaquets)

            interface.zonePaquets.add(interface.defilementPaquets)
            interface.zonePaquets.set_border_width(4)
            

            # ------------------------------------------------------------------
            #       Informations sur le paquet
            # ------------------------------------------------------------------
            
            interface.listeInformations.set_headers_visible(False)
            interface.listeInformations.set_hover_selection(True)
            
            interface.celluleLabel.set_property('weight', pango.WEIGHT_BOLD)
            
            interface.colonneLabel.pack_start(interface.celluleLabel, True)
            interface.colonneLabel.add_attribute(interface.celluleLabel, "text", 0)
            interface.colonneValeur.pack_start(interface.celluleValeur, True)
            interface.colonneValeur.add_attribute(interface.celluleValeur, "text", 1)
            
            interface.listeInformations.append_column(interface.colonneLabel)
            interface.listeInformations.append_column(interface.colonneValeur)
            interface.listeInformations.set_model(interface.contenuInformations)
            
            interface.defilementInformations.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            interface.defilementInformations.add(interface.listeInformations)
            interface.defilementInformations.set_border_width(4)

            interface.zoneInformations.add(interface.defilementInformations)
            interface.zoneInformations.set_border_width(4)
            interface.zoneInformations.set_resize_mode(gtk.RESIZE_PARENT)
            

            # ------------------------------------------------------------------
            #       Barre de status
            # ------------------------------------------------------------------

            interface.zoneBarreStatus.pack_start(interface.barreProgres, expand=False)
            interface.zoneBarreStatus.pack_start(interface.barreStatus)


            # ------------------------------------------------------------------
            #       Intégration des widgets
            # ------------------------------------------------------------------

            interface.zonePaquetsInformations.add1(interface.zonePaquets)
            interface.zonePaquetsInformations.add2(interface.zoneInformations)

            interface.zoneColonnePaquets.add1(interface.zoneGroupes)
            interface.zoneColonnePaquets.add2(interface.zonePaquetsInformations)

            interface.fenetre.set_title(fctLang.traduire("title"))
            interface.fenetre.set_size_request(int(longueur), int(hauteur))
            interface.fenetre.set_resizable(True)
            interface.fenetre.set_position(gtk.WIN_POS_CENTER)

            interface.grille.attach(interface.menu, 0, 1, 0, 1, yoptions=gtk.FILL)
            interface.grille.attach(interface.outils, 0, 1, 1, 2, yoptions=gtk.FILL)
            interface.grille.attach(interface.zoneColonnePaquets, 0, 1, 2, 3)
            interface.grille.attach(interface.zoneBarreStatus, 0, 1, 3, 4, yoptions=gtk.FILL)

            interface.fenetre.add(interface.grille)

            interface.fenetre.show_all()
            interface.barreProgres.hide()

        else:
            sys.exit("[ERROR] - La fenêtre ne peut avoir une taille inférieur à 800x600")


    def selectionnerGroupe (interface, selection, modele):

        choix = selection.get_selected()
        treeiter = choix[1]

        modele = interface.colonneGroupes.get_model()

        selectionGroupe = modele.get_value(treeiter, 0)

        fctEvent.obtenirGroupe(interface, selectionGroupe)

        return True

    
    def selectionnerPaquet (interface, selection, modele):
        
        choix = selection.get_selected()
        
        if choix == ():
            return

        tableau = choix[1]
        
        try :
            nomPaquet, versionPaquet = modele.get(tableau, 1, 2)
            fctEvent.obtenirPaquet(interface, nomPaquet, versionPaquet)
        except :
            return True
            
        return True
        

    def cocherPaquet (interface, cell_renderer, colonne, liste):

        modele = liste.get_model()
        modele[colonne][0] = not modele[colonne][0]
        
        elementEnlever = fctEvent.dansListe(interface.listeInstallation, modele[colonne][1])
        elementAjouter = fctEvent.dansListe(interface.listeSuppression, modele[colonne][1])

        if modele[colonne][0] == 0:
            if pacman_package_intalled(modele[colonne][1], modele[colonne][2]) == 1:
                if elementEnlever == 0:
                    interface.listeSuppression.append(modele[colonne][1])
            else:
                if elementAjouter != 0:
                    interface.listeInstallation.remove(elementAjouter)

        else:
            if pacman_package_intalled(modele[colonne][1], modele[colonne][2]) == 1:
                if elementEnlever != 0:
                    interface.listeSuppression.remove(elementEnlever)
            else:
                if elementAjouter == 0:
                    interface.listeInstallation.append(modele[colonne][1])


    def effectuerRecherche (interface, *args):
    
        if interface.texteRecherche.get_text != '':
            interface.listeColonnePaquets.clear()
            objetRechercher = interface.texteRecherche.get_text()
            
            interface.barreStatus.push(0, (fctLang.traduire("search_package") + " " + objetRechercher))
            paquets = pacman_search_pkg(objetRechercher)
            
            if len(paquets) == 0:
                return
            
            pacman_trans_release()
            fctEvent.ajouterPaquets(interface, paquets)
            
            
    def effacerRecherche (interface, *args):
        
        interface.texteRecherche.set_text("")
        
        
    def effacerInterface (interface):
        
        #~ interface.info_column.set_title("")
        interface.listeColonnePaquets.clear()
        

    def fenetreAPropos (objet, widget, *event):
    
        about = gtk.AboutDialog()
        
        about.set_program_name("pyFPM")
        about.set_version("0001")
        about.set_comments(fctLang.traduire("about_desc"))
        about.set_copyright("Copyright (c) 2012\nGaetan Gourdin\nAurélien Lubert")
        about.set_license("Ce programme est un logiciel libre, vous pouvez le redistribuer\net/ou le modifier conformément aux dispositions de la Licence Publique\nGénérale GNU, telle que publiée par la Free Software Foundation.")
        
        logo = gtk.gdk.pixbuf_new_from_file("./data/logo.png")
        about.set_logo(logo)
        
        about.run()
        
        about.destroy()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions concernant les préférences de pyFPM
#
# ----------------------------------------------------------------------

import sys, pango, os

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK introuvable")

from config import *
from lang import *
from action import *

fctConfig = fonctionsConfiguration()
fctLang = fonctionsLang()
fctEvent = fonctionsEvenement()

"""
    fonctionsPreferences
        fenetrePreferences (interface, widget)
"""

class fonctionsPreferences:
    def fenetrePreferences (interface, widget):

        fenetre = gtk.Dialog(fctLang.traduire("preferences_title"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_APPLY, gtk.RESPONSE_APPLY))

        onglets = gtk.Notebook()

        general = gtk.Label(fctLang.traduire("preferences_main"))
        grilleGeneral = gtk.Table(1,2)
        zoneGeneralLangue = gtk.Frame(fctLang.traduire("preferences_main"))
        generalLangue = gtk.Table(2,1)
        generalLangueLabel = gtk.Label(fctLang.traduire("language"))
        generalLangueChoix = gtk.combo_box_new_text()
        zoneGeneralDivers = gtk.Frame(fctLang.traduire("misc"))
        grilleGeneralCocher = gtk.Table(1,2)
        miseajourDemarrage = gtk.CheckButton(fctLang.traduire("start_update"))
        sauvegardeFenetre = gtk.CheckButton(fctLang.traduire("save_window"))

        commande = gtk.Label(fctLang.traduire("pacman"))
        grilleCommande = gtk.Table(1,1)
        zoneCommande = gtk.Frame(fctLang.traduire("preferences_command"))
        generalCommande = gtk.Table(2,1)
        generalCommandeLabel = gtk.Label(fctLang.traduire("choose_su"))
        generalCommandeChoix = gtk.combo_box_new_text()

        divers = gtk.Label(fctLang.traduire("preferences_misc"))
        zoneDivers = gtk.Table(1,1)

        fenetre.set_has_separator(False)
        fenetre.set_default_response(gtk.RESPONSE_OK)
        fenetre.set_resizable(True)
        fenetre.set_position(gtk.WIN_POS_CENTER)
        fenetre.set_size_request(400, 400)

        onglets.set_tab_pos(gtk.POS_LEFT)

        generalLangue.attach(generalLangueLabel, 0, 1, 0, 1, yoptions=gtk.FILL)
        generalLangue.attach(generalLangueChoix, 1, 2, 0, 1, yoptions=gtk.FILL)
        zoneGeneralLangue.add(generalLangue)
        zoneGeneralLangue.set_border_width(4)
        grilleGeneralCocher.attach(miseajourDemarrage, 0, 1, 0, 1)
        grilleGeneralCocher.attach(sauvegardeFenetre, 0, 1, 1, 2)
        zoneGeneralDivers.add(grilleGeneralCocher)
        zoneGeneralDivers.set_border_width(4)
        grilleGeneral.attach(zoneGeneralLangue, 0, 1, 0, 1)
        grilleGeneral.attach(zoneGeneralDivers, 0, 1, 1, 2, yoptions=gtk.FILL)
        onglets.append_page(grilleGeneral, general)
        
        interface.remplirLangue(generalLangueChoix)

        generalCommande.attach(generalCommandeLabel, 0, 1, 0, 1, yoptions=gtk.FILL)
        generalCommande.attach(generalCommandeChoix, 1, 2, 0, 1, yoptions=gtk.FILL)
        zoneCommande.add(generalCommande)
        zoneCommande.set_border_width(4)
        grilleCommande.attach(zoneCommande, 0, 1, 0, 1)
        onglets.append_page(grilleCommande, commande)

        interface.remplirOutils(generalCommandeChoix)

        onglets.append_page(zoneDivers, divers)

        fenetre.vbox.pack_start(onglets)

        fenetre.show_all()
        fenetre.run()

        fenetre.destroy()


    def remplirLangue (interface, liste):
        """
        Récupère les fichiers de langues disponible et en récupère le nom
        """

        listeLangues = ['fr', 'en']
        listeLangues.sort()
        
        for element in listeLangues:
            liste.append_text(fctLang.nomLangue(element))

        liste.set_active(listeLangues.index(fctLang.traduire(fctConfig.lireConfig("pyfpm", "lang"))))
        
        
    def remplirOutils (interface, liste):
        """
        Récupère les outils de connexion en mode administrateur
        """
        
        # Applications les plus connus
        listeOutils = ['gksu', 'kdsu']
        if not fctConfig.lireConfig("admin", "command") in listeOutils:
            listeOutils.append(fctConfig.lireConfig("admin", "command"))
        listeOutils.sort()

        for element in listeOutils:
            if os.path.exists("/usr/bin/" + element):
                liste.append_text(element)
                
        liste.set_active(listeOutils.index(fctConfig.lireConfig("admin", "command")))
        

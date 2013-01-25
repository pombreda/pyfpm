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


class fonctionsPreferences:
    def fenetrePreferences (objet, widget, interface):

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
        objet.miseajourDemarrage = gtk.CheckButton(fctLang.traduire("start_update"))
        objet.afficherGroupes = gtk.CheckButton(fctLang.traduire("use_prohibate_groups"))
        objet.horsLigne = gtk.CheckButton(fctLang.traduire("offline"))

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
        #~ fenetre.set_size_request(400, 400)

        onglets.set_tab_pos(gtk.POS_LEFT)

        generalLangue.attach(generalLangueLabel, 0, 1, 0, 1, yoptions=gtk.FILL)
        generalLangue.attach(generalLangueChoix, 1, 2, 0, 1, yoptions=gtk.FILL)
        generalLangue.set_border_width(4)
        zoneGeneralLangue.add(generalLangue)
        zoneGeneralLangue.set_border_width(4)
        grilleGeneralCocher.attach(objet.miseajourDemarrage, 0, 1, 0, 1)
        grilleGeneralCocher.attach(objet.afficherGroupes, 0, 1, 1, 2)
        grilleGeneralCocher.attach(objet.horsLigne, 0, 1,2, 3)
        grilleGeneralCocher.set_border_width(4)
        zoneGeneralDivers.add(grilleGeneralCocher)
        zoneGeneralDivers.set_border_width(4)
        grilleGeneral.attach(zoneGeneralLangue, 0, 1, 0, 1)
        grilleGeneral.attach(zoneGeneralDivers, 0, 1, 1, 2, yoptions=gtk.FILL)
        onglets.append_page(grilleGeneral, general)
        
        objet.remplirLangue(generalLangueChoix)
        objet.remplirCases()

        generalCommande.attach(generalCommandeLabel, 0, 1, 0, 1, yoptions=gtk.FILL)
        generalCommande.attach(generalCommandeChoix, 1, 2, 0, 1, yoptions=gtk.FILL)
        generalCommande.set_border_width(4)
        zoneCommande.add(generalCommande)
        zoneCommande.set_border_width(4)
        grilleCommande.attach(zoneCommande, 0, 1, 0, 1)
        onglets.append_page(grilleCommande, commande)

        objet.remplirOutils(generalCommandeChoix)
        
        #~ onglets.append_page(zoneDivers, divers)

        fenetre.vbox.pack_start(onglets)

        fenetre.show_all()
        reponse = fenetre.run()
        
        if reponse == gtk.RESPONSE_APPLY:
            dico = {"lang" : fctLang.fichierLangue(generalLangueChoix.get_active_text()), "offline" : fctConfig.booleenMinuscule(objet.horsLigne.get_active()), "startupdate" : fctConfig.booleenMinuscule(objet.miseajourDemarrage.get_active()), "useprohibategroups" : fctConfig.booleenMinuscule(objet.afficherGroupes.get_active()), "width" : "1024", "height" : "600", "command" : generalCommandeChoix.get_active_text()}
            
            modificationInterface = False
            if fctConfig.lireConfig("pyfpm", "useprohibategroups") != fctConfig.booleenMinuscule(objet.afficherGroupes.get_active()):
                modificationInterface = True
            
            fctConfig.ecrireConfig(dico)
            
            if modificationInterface:
                interface.effacerInterface()
                fctEvent.ajouterGroupes(interface)
                
            fctInstall.rafraichirFenetre()

        fenetre.destroy()


    def remplirLangue (objet, liste):
        """
        Récupère les fichiers de langues disponible et en récupère le nom
        """

        listeLangues = fctLang.recupererTraduction()
        listeLangues.sort()
        
        for element in listeLangues:
                liste.append_text(fctLang.nomLangue(element))

        liste.set_active(listeLangues.index(fctLang.traduire(fctConfig.lireConfig("pyfpm", "lang"))))
        
        
    def remplirOutils (objet, liste):
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
        
    
    def remplirCases (objet):
        """
        Met les cases à cocher aux bonnes valeurs
        """
    
        objet.miseajourDemarrage.set_active(fctConfig.booleenVersEntier(fctConfig.lireConfig("pyfpm", "startupdate")))
        objet.afficherGroupes.set_active(fctConfig.booleenVersEntier(fctConfig.lireConfig("pyfpm", "useprohibategroups")))
        objet.horsLigne.set_active(fctConfig.booleenVersEntier(fctConfig.lireConfig("pyfpm", "offline")))

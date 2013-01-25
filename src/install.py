#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Interface pour l'installation
#
# ----------------------------------------------------------------------

import sys, pango, os

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK introuvable")

from lang import *

fctLang = fonctionsLang()


class fonctionsInstallation:
    def __init__ (interface):
        
        interface.fenetre = gtk.Dialog(fctLang.traduire("pacman_title"), None, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
        
        interface.barreProgres = gtk.ProgressBar()
        
        
    def fenetreInstallation (interface):

        interface.fenetre.vbox.pack_start(interface.barreProgres)

        interface.fenetre.show_all()
        
    
    def fermerFenetre (interface):
        """
        Permet de fermer la fenetre d'installation
        """
        
        interface.fenetre.destroy()
    
    
    def changerLabel (interface, texte):
        """
        Changer le contenu du label
        """
        
        interface.barreProgres.set_text(texte)

    
    def changerBarreProgres (interface, valeur):
        """
        Mettre à jour la barre de progres
        """
        
        interface.barreProgres.set_fraction(valeur)

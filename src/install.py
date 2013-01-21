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

class fonctionsInstallation:
    def fenetreInstallation (interface):

        fenetre = gtk.Dialog(fctLang.traduire("pacman_title"), None, gtk.DIALOG_MODAL, (gtk.STOCK_OK, gtk.RESPONSE_OK))
        
        interface.barreProgres = gtk.ProgressBar()
        
        fenetre.vbox.pack_start(interface.barreProgres)

        fenetre.show_all()
        fenetre.run()
        
        fenetre.destroy()
        
        
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

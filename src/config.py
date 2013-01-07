#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions permettant de configurer pyFPM
#
# ----------------------------------------------------------------------

import os, sys

from string import strip
from ConfigParser import SafeConfigParser

from file import *
fctFichier = fonctionsFichier()


# ----------------------------------------------------------------------
# fonctionsConfiguration
#       lireConfig (objet, section, option)
# ----------------------------------------------------------------------

class fonctionsConfiguration:
    """
    Récupère la valeur correspondant dans le fichier de configuration
    suivant la section choisie
    """
    def lireConfig (objet, section, option):
        if fctFichier.fichier("./pyfpm.config") == True:
            try:
                configuration = SafeConfigParser()
                configuration.read("./pyfpm.config")
                
                return configuration.get(section, option)
            except:
                return False
        else:
            print("[ERROR] - Fichier inexistant")
            

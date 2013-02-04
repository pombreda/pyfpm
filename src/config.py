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


class fonctionsConfiguration:
    
    def lireConfig (objet, section, option):        
        """
        Récupère la valeur correspondant dans le fichier de configuration
        suivant la section choisie
        """
        if fctFichier.fichier("./pyfpm.config") == True:
            try:
                configuration = SafeConfigParser()
                configuration.read("./pyfpm.config")
                
                return configuration.get(section, option)
            except:
                return False
        else:
            print("[ERROR] - Fichier inexistant")
            
    
    def ecrireConfig (objet, dico):
        """
        Modifie la configuration
        """
    
        try:
            configuration = SafeConfigParser()
            
            configuration.add_section("pyfpm")
            configuration.add_section("screen")
            configuration.add_section("admin")
            
            configuration.set("pyfpm", "lang", dico.get("lang", "en"))
            configuration.set("pyfpm", "offline", dico.get("offline", "true"))
            configuration.set("pyfpm", "startupdate", dico.get("startupdate", "true"))
            configuration.set("pyfpm", "useprohibategroups", dico.get("useprohibategroups", "false"))
            
            configuration.set("screen", "width", objet.lireConfig("screen", "width"))
            configuration.set("screen", "height", objet.lireConfig("screen", "height"))
            
            configuration.set("admin", "command", dico.get("command", "gksu"))
            
            configuration.write(open("./pyfpm.config" , "w"))
            
        except:
            return False


    def booleenVersEntier (objet, valeur):
        """
        Tranforme un booleen en entier
        """
        
        if valeur == "true":
            return 1
        elif valeur == "false":
            return 0
        else:
            return -1


    def booleenMinuscule (objet, valeur):
        """
        Met le booléen en minuscule pour le fichier de configuration
        """
        
        if valeur == 1:
            return "true"
        elif valeur == 0:
            return "false"
        else:
            return -1

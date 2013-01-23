#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions de traduction de l'interface
#
# ----------------------------------------------------------------------

from config import *

fctConfig = fonctionsConfiguration()


"""
    fonctionsLang
        traduire (objet, mot)
"""

class fonctionsLang:
    def traduire (objet, mot):
        """
        Récupère la traduction du mot dans le fichier de langue
        correspondant
        """

        if mot != "":
            langue = fctConfig.lireConfig("pyfpm", "lang")
            try:
                traduction = SafeConfigParser()
                traduction.read("lang/" + langue + ".ini")

                motTrouve = traduction.get("traduction", mot)
                if motTrouve != "":
                    return motTrouve
                else:
                    return mot
            except:
                return mot
                
    
    def nomLangue (objet, fichier):
        """
        Récupère le nom de la langue
        """
        
        if fichier != "":
            try:
                traduction = SafeConfigParser()
                traduction.read("lang/" + fichier + ".ini")

                return traduction.get("information", "lang")
            except:
                return fichier
        
    
    def recupererNomLangue (objet):
        """
        Récupère la liste des fichier de language dans ./lang
        """
        
        os.system("ls ./lang/*.ini | awk 'BEGIN{FS=\".\"}{print $1}'")

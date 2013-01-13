#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions de traduction de l'interface
#
# ----------------------------------------------------------------------

from config import *

fctConfig = fonctionsConfiguration()


# ----------------------------------------------------------------------
#   fonctionsLang
#       traduire (objet, mot)
# ----------------------------------------------------------------------

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

                return traduction.get("traduction", mot)
            except:
                return mot

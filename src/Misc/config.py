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

from . import files
fctFichier = files.fonctionsFichier()


class fonctionsConfiguration (object):
    def lireConfig (self, section, option):
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


    def ecrireConfig (self, dico):
        """
        Modifie la configuration
        """

        try:
            configuration = SafeConfigParser()

            configuration.add_section("pyfpm")
            configuration.add_section("screen")
            configuration.add_section("admin")

            configuration.set("pyfpm", "lang", dico.get("lang", "en"))
            configuration.set("pyfpm", "developmentmode", dico.get("developmentmode", "true"))
            configuration.set("pyfpm", "startupdate", dico.get("startupdate", "true"))
            configuration.set("pyfpm", "useprohibategroups", dico.get("useprohibategroups", "false"))

            configuration.set("screen", "width", self.lireConfig("screen", "width"))
            configuration.set("screen", "height", self.lireConfig("screen", "height"))

            configuration.set("admin", "command", dico.get("command", "gksu"))

            configuration.write(open("./pyfpm.config" , "w"))

        except:
            return False


    def booleenVersEntier (self, valeur):
        """
        Tranforme un booleen en entier
        """

        if valeur == "true":
            return 1
        elif valeur == "false":
            return 0
        else:
            return -1


    def booleenMinuscule (self, valeur):
        """
        Met le booléen en minuscule pour le fichier de configuration
        """

        if valeur == 1:
            return "true"
        elif valeur == 0:
            return "false"
        else:
            return -1

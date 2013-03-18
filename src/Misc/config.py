#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions permettant de configurer pyFPM
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys

from string import strip
from ConfigParser import SafeConfigParser

from . import files

# Initialisation des modules
File = files.File()

# Variables globales
config_path = os.path.expanduser('~') + "/.config/pyfpm/"

class Config (object):
    """
    Ensemble de fonction permettant de gérer le fichier
    de configuration utilisateur
    """

    def checkConfig (self):
        """
        Créer le fichier de configuration si inexistant
        """

        if File.fichier(config_path) == False:
            # Le fichier de configuration doit être créé
            os.mkdir(config_path, 0744)

        if File.fichier(config_path + "pyfpm.config") == False:
            # Configuration par défaut
            dico = {"lang" : "en_US", "developmentmode" : "false", "startupdate" : "true", "useprohibategroups" : "false", "width" : "800", "height" : "600", "command" : "gksu"}
            self.writeConfig(dico)


    def readConfig (self, section, option):
        """
        Récupère la valeur correspondant dans le fichier de configuration
        suivant la section choisie
        """
        if File.fichier(config_path + "pyfpm.config") == True:
            try:
                configuration = SafeConfigParser()
                configuration.read(config_path + "pyfpm.config")

                return configuration.get(section, option)
            except:
                return False
        else:
            print("[ERROR] Fichier inexistant")


    def writeConfig (self, dico):
        """
        Modifie la configuration
        """

        try:
            configuration = SafeConfigParser()

            configuration.add_section("pyfpm")
            configuration.add_section("screen")
            configuration.add_section("admin")

            configuration.set("pyfpm", "lang", dico.get("lang", "en_US"))
            configuration.set("pyfpm", "developmentmode", dico.get("developmentmode", "true"))
            configuration.set("pyfpm", "startupdate", dico.get("startupdate", "true"))
            configuration.set("pyfpm", "useprohibategroups", dico.get("useprohibategroups", "false"))

            configuration.set("screen", "width", dico.get("width", "800"))
            configuration.set("screen", "height", dico.get("height", "600"))

            configuration.set("admin", "command", dico.get("command", "gksu"))

            configuration.write(open(config_path + "pyfpm.config" , "w"))

        except:
            return False


    def boolToInt (self, valeur):
        """
        Tranforme un booleen en entier
        """

        if valeur == "true":
            return 1
        elif valeur == "false":
            return 0
        else:
            return -1


    def boolMinus (self, valeur):
        """
        Met le booléen en minuscule pour le fichier de configuration
        """

        if valeur == 1:
            return "true"
        elif valeur == 0:
            return "false"
        else:
            return -1

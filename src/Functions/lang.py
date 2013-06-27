#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions de traduction de l'interface
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys, string, gettext
from ConfigParser import SafeConfigParser

from . import config, files

# Initialisation des modules
fctConfig = config.Config()

gettext.bindtextdomain('pyfpm', 'lang')
gettext.textdomain('pyfpm')
_ = gettext.gettext

class Lang (object):
    """
    Ensemble de fonctions pour translate pyfpm
    """

    def translate (self, mot):
        """
        Récupère la traduction du mot dans le fichier de langue
        correspondant
        """

        #~ if mot != "":
            #~ langue = fctConfig.readConfig("pyfpm", "lang")
            #~ try:
                #~ traduction = SafeConfigParser()
                #~ traduction.read("lang/" + langue + ".ini")

                #~ motTrouve = traduction.get("traduction", mot)
                #~ if motTrouve != "":
                    #~ return motTrouve
                #~ else:
                    #~ return mot
            #~ except:
                #~ return mot

        return _(mot)


    def nameLanguage (self, fichier):
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


    def getTranslation (self):
        """
        Récupère la liste des fichier de language dans ./lang
        """

        liste = os.listdir('./lang')
        liste2 = []

        for element in liste:
            nom = string.split(element, ".ini")
            liste2.append(nom[0])

        return liste2


    def fileLanguage (self, nom):

        liste = self.getTranslation()

        index = ""
        for element in liste:
            if self.nameLanguage(element) == nom:
                index = element

        return index


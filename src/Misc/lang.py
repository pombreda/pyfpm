#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions de traduction de l'interface
#
# ----------------------------------------------------------------------

import os, sys, string
from ConfigParser import SafeConfigParser

from . import config, files
fctConfig = config.fonctionsConfiguration()


class fonctionsLang (object):
    def traduire (self, mot):
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


    def nomLangue (self, fichier):
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


    def recupererTraduction (self):
        """
        Récupère la liste des fichier de language dans ./lang
        """

        liste = os.listdir('./lang')
        liste2 = []

        for element in liste:
            nom = string.split(element, ".ini")
            liste2.append(nom[0])

        return liste2


    def fichierLangue (self, nom):

        liste = self.recupererTraduction()

        index = ""
        for element in liste:
            if self.nomLangue(element) == nom:
                index = element

        return index


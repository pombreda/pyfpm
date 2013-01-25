#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions de traduction de l'interface
#
# ----------------------------------------------------------------------

import string

from config import *

fctConfig = fonctionsConfiguration()


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
        
    
    def recupererTraduction (objet):
        """
        Récupère la liste des fichier de language dans ./lang
        """
        
        liste = os.listdir('./lang')
        liste2 = []
        
        for element in liste:
            nom = string.split(element, ".ini")
            liste2.append(nom[0])
        
        return liste2


    def fichierLangue (objet, nom):
        
        liste = objet.recupererTraduction()
        
        index = ""
        for element in liste:
            if objet.nomLangue(element) == nom:
                index = element
                
        return index
                

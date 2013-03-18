#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions gérant les fichiers
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys, codecs
from urllib2 import Request, urlopen

class File (object):
    """
    Ensemble de fonction permettant de gérer les fichiers
    """
    
    def fichier (self, chemin):
        """
        Vérifie l'existance d'un fichier
        """
        
        return os.path.exists(chemin)


    def utf8 (self, chemin):
        """
        Vérifie l'encodage en utf-8 d'un fichier
        """
        
        if fichier(chemin) == True:
            try:
                chemin = unicode(chemin, 'UTF-8', 'strict')
                return True
            except UnicodeDecodeError:
                return False 


    def verifierErreurUrl (self, nomUrl):
        """
        Vérifie l'existence d'erreur 404
        """
        
        req = Request(nomUrl)
        try:
            response = urlopen(req)
            return 1
        except IOError, e:
            if hasattr(e, 'reason'):
                return e.reason
            elif hasattr(e, 'code'):
                return e.code


    def verifierFichierTelecharge (self, nom):
        """
        Permet d'éviter de récupérer à nouveau le fichier si celui-ci existe
        """
        
        trouve = False
        
        if self.fichier('/tmp/frugalbuild'):
            fichierLocal = open('/tmp/frugalbuild', 'w')
            
            print fichierLocal
            for element in fichierLocal.read():
                ligne = element.split('=')
                if ligne[0] == 'pkgname' and ligne[1] == nom:
                    trouve = True

            fichierLocal.close()
        
        return trouve
    

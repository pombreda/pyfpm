#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions gérant les fichiers
#
# ----------------------------------------------------------------------

import os, sys, codecs


# ----------------------------------------------------------------------
# fonctionsFichier
#       fichier (objet, chemin)
#       utf8 (objet, fichier)
# ----------------------------------------------------------------------

class fonctionsFichier:
    """
    Vérifie l'existance d'un fichier
    """
    def fichier (objet, chemin):
        return os.path.exists(chemin)

    """
    Vérifie l'encodage en utf-8 d'un fichier
    """
    def utf8 (objet, chemin):
        if fichier(chemin) == True:
            try:
                chemin = unicode(chemin, 'UTF-8', 'strict')
                return True
            except UnicodeDecodeError:
                return False 

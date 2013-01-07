#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions relatives au gestionnaire de paquet
#
# ----------------------------------------------------------------------

import sys

import pacmang2.libpacman
from pacmang2.libpacman import *

from lang import *
fctLang = fonctionsLang()

pacmang2.libpacman.printconsole=1
pacmang2.libpacman.debug=0

# ----------------------------------------------------------------------
#   fonctionsPaquets
#       initialiserGroupes (objet)
#       initialiserPacman (objet)
#       initialiserPaquets (objet, groupe)
#       miseajourBaseDonnees (objet)
#       nettoyerCache (objet)
#       terminerPacMan (objet)
#       verifierElements (objet, tableau, listeElements)
#       verifierInstallationPaquet (objet, interface, nom, version)
# ----------------------------------------------------------------------

class fonctionsPaquets:
    def initialiserPacman (objet):

        pacman_init()
        pacman_init_database()
        pacman_register_all_database()
        
    
    def nettoyerCache (objet):
        
        print "Nettoyage du cache"
        pacman_sync_cleancache()
        
        
    def miseajourBaseDonnees (objet):
        
        print "Mise à jour des bases de paquets"
        pacman_update_db(1)


    def terminerPacman (objet):

        pacman_finally()


    def verifierElements (objet, tableau, listeElements):

        objetTrouve = 0

        for element in tableau :
            if listeElements == element:
                objetTrouve = 1
                break

        return objetTrouve


    def initialiserGroupes (objet):

        baseDonnees = db_list[0]
        ensembleGroupes = []

        for baseDonnees in db_list:
            i = pacman_db_getgrpcache(baseDonnees)

            while i != 0:
                groupe = pacman_list_getdata(i)

                if objet.verifierElements (ensembleGroupes, pointer_to_string(groupe)) == 0:
                    ensembleGroupes.append(pointer_to_string(groupe))

                i = pacman_list_next(i)

        ensembleGroupes.sort()

        return ensembleGroupes


    def initialiserPaquets (objet, groupe):

        ensemblePaquets = []

        for baseDonnees in db_list:
            pm_group = pacman_db_readgrp (baseDonnees, groupe)
            i = pacman_grp_getinfo (pm_group, PM_GRP_PKGNAMES)

            while i != 0:
                paquet = pacman_db_readpkg (baseDonnees, pacman_list_getdata(i))

                if objet.verifierElements (ensemblePaquets, paquet) == 0:
                    ensemblePaquets.append(paquet)

                i = pacman_list_next(i)

        ensemblePaquets.sort()

        return ensemblePaquets


    def verifierInstallationPaquet (objet, interface, nom, version):

        objetTrouve = False

        for paquet in interface.listePaquetsInstalles:
            if paquet[0] == nom and paquet[1] == version:
                objetTrouve = True
                break

        return objetTrouve


def main (*args):
    fctPaquets = fonctionsPaquets()
    
    for arg in sys.argv:
        if arg=="cleancache":
            fctPaquets.nettoyerCache()
        elif arg=="updatedb":
            fctPaquets.miseajourBaseDonnees()

if __name__ == "__main__":
    sys.exit(main())

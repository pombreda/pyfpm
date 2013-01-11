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

pacmang2.libpacman.printconsole=0
pacmang2.libpacman.debug=0

# ----------------------------------------------------------------------
#   fonctionsPaquets
#       initialiserGroupes (objet)
#       initialiserPacman (objet)
#       initialiserPaquets (objet, groupe)
#       miseajourBaseDonnees (objet)
#       nettoyerCache (objet)
#       terminerPacman (objet)
#       verifierElements (objet, tableau, listeElements)
#       verifierInstallationPaquet (objet, interface, nom, version)
# ----------------------------------------------------------------------

class fonctionsPaquets:
    def initialiserPacman (objet):   
        """
        Initialise pacman-g2 pour permettre d'être utilisé
        """

        print "Initialisation de pacman"
        pacman_init()
        print "Initialisation de la base de données"
        pacman_init_database()
        print "Mise en place de la base de données"
        pacman_register_all_database()
        
    
    def nettoyerCache (objet):   
        """
        Nettoye le cache de pacman-g2
        """
        
        print "Nettoyage du cache"
        pacman_sync_cleancache()
        
        fonctionsInterface().fenetreInformation(fctLang.traduire("clean_cache"), fctLang.traduire("clean_cache_done"))
        
        
    def miseajourBaseDonnees (objet):   
        """
        Met à jour les dépôts de paquets
        """
        
        print "Mise à jour des bases de paquets"
        pacman_update_db(1)


    def terminerPacman (objet):   
        """
        Termine l'instance de pacman-g2
        """

        print "Fermeture de l'instance"
        pacman_finally()


    def initialiserGroupes (objet):   
        """
        Initialise la liste des groupes
        """

        baseDonnees = db_list[0]
        ensembleGroupes = []

        for baseDonnees in db_list:
            i = pacman_db_getgrpcache(baseDonnees)

            while i != 0:
                groupe = pacman_list_getdata(i)

                if not pointer_to_string(groupe) in ensembleGroupes:
                    ensembleGroupes.append(pointer_to_string(groupe))

                i = pacman_list_next(i)

        ensembleGroupes.sort()

        return ensembleGroupes


    def initialiserPaquets (objet, groupe):   
        """
        Initialise les paquets correspondant au groupe sélectionné
        """

        ensemblePaquets = []

        for baseDonnees in db_list:
            pm_group = pacman_db_readgrp (baseDonnees, groupe)
            i = pacman_grp_getinfo (pm_group, PM_GRP_PKGNAMES)

            while i != 0:
                paquet = pacman_db_readpkg (baseDonnees, pacman_list_getdata(i))

                if not paquet in ensemblePaquets:
                    ensemblePaquets.append(paquet)

                i = pacman_list_next(i)

        ensemblePaquets.sort()

        return ensemblePaquets


    def verifierInstallationPaquet (objet, interface, nom, version):   
        """
        Vérifie si un paquet particulier est installé sur le système
        """

        objetTrouve = False

        for paquet in interface.listePaquetsInstalles:
            if paquet[1] == nom and paquet[2] == version:
                objetTrouve = True
                break

        return objetTrouve
        
    
    def recupererDependances (objet, paquet):
        """
        Récupère les dépendances non installés d'un paquet
        """
        dependances = pacman_pkg_getinfo(paquet, PM_PKG_DEPENDS)
        listeDependances = []
        
        while dependances != 0:
            # Améliorer la séparation des caractères >, =, <
            nom = pointer_to_string(pacman_list_getdata(dependances)).split('=')
            nom = nom[0].split('<')
            nom = nom[0].split('>')
            
            paquetsDependance = pacman_search_pkg(nom[0])
            
            for element in paquetsDependance:
                if pacman_package_is_installed(pacman_pkg_get_info(element, PM_PKG_NAME)) == 0:
                    listeDependances.append(nom[0])
                    break
                
            dependances = pacman_list_next(dependances)
            
        print "Dependances : " + str(listeDependances)


    def obtenirMiseAJour (objet, liste):
        """
        Récupère les paquets dont une mise à jour est disponible
        """
        
        print "Obtention de la liste des paquets à mettre à jour"
        
        for element in pacman_check_update():
            liste.append(pointer_to_string(element))
        
        print liste

def main (*args):   
    """
    Partie nécessaire pour l'execution de certaines commandes avec les
    droits super-utilisateur
    """
    fctPaquets = fonctionsPaquets()
    
    for arg in sys.argv:
        if arg=="cleancache":
            fctPaquets.nettoyerCache()
        elif arg=="updatedb":
            fctPaquets.miseajourBaseDonnees()

if __name__ == "__main__":
    sys.exit(main())

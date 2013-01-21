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

"""
    fonctionsPaquets
        initialiserGroupes (objet)
        initialiserPacman (objet)
        initialiserPaquets (objet, groupe)
        miseajourBaseDonnees (objet)
        nettoyerCache (objet)
        terminerPacman (objet)
        verifierElements (objet, tableau, listeElements)
        verifierInstallationPaquet (objet, interface, nom, version)
"""

class fonctionsPaquets:
    def initialiserPacman (objet):
        """
        Initialise pacman-g2 pour permettre d'être utilisé
        """

        print ("Initialisation de pacman")
        pacman_init()
        print ("Initialisation de la base de données")
        pacman_init_database()
        print ("Mise en place de la base de données")
        pacman_register_all_database()


    def nettoyerCache (objet):
        """
        Nettoye le cache de pacman-g2
        """

        print ("Nettoyage du cache")
        pacman_sync_cleancache()


    def miseajourBaseDonnees (objet):
        """
        Met à jour les dépôts de paquets
        """

        print ("Mise à jour des bases de paquets")
        objet.terminerPacman()
        objet.initialiserPacman()

        pacman_update_db()


    def terminerPacman (objet):
        """
        Termine l'instance de pacman-g2
        """

        print ("Fermeture de l'instance")
        pacman_finally()


    def initialiserGroupes (objet, interface):
        """
        Initialise la liste des groupes
        """

        baseDonnees = db_list[interface.listeSelectionGroupe.get_active()]
        ensembleGroupes = []

        i = pacman_db_getgrpcache(baseDonnees)

        while i != 0:
            groupe = pacman_list_getdata(i)

            if not pointer_to_string(groupe) in ensembleGroupes:
                ensembleGroupes.append(pointer_to_string(groupe))

            i = pacman_list_next(i)

        ensembleGroupes.sort()

        return ensembleGroupes


    def initialiserPaquets (objet, interface, groupe):
        """
        Initialise les paquets correspondant au groupe sélectionné
        """

        ensemblePaquets = []

        pm_group = pacman_db_readgrp (db_list[interface.listeSelectionGroupe.get_active()], groupe)
        i = pacman_grp_getinfo (pm_group, PM_GRP_PKGNAMES)

        while i != 0:
            paquet = pacman_db_readpkg (db_list[interface.listeSelectionGroupe.get_active()], pacman_list_getdata(i))

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


    def recupererDependances (objet, nomPaquet):
        """
        Récupère les dépendances non installés d'un paquet
        """

        listeDependances = []

        if "frugalware" in repo_list:
            index = repo_list.index("frugalware")
        elif "frugalware-current" in repo_list:
            index = repo_list.index("frugalware-current")
            
        paquet = pacman_db_readpkg(db_list[index], nomPaquet)
        dependances = pacman_pkg_getinfo(paquet, PM_PKG_DEPENDS)

        while dependances != 0:
            nomDependance = pointer_to_string(pacman_list_getdata(dependances))

            nomDependance = nomDependance.split('=')
            nomDependance = nomDependance[0].split('<')
            nomDependance = nomDependance[0].split('>')
            nomDependance = nomDependance[0]
            
            information = pacman_db_readpkg(db_list[index], nomDependance)
            nomPaquetDependance = pacman_pkg_get_info(information, PM_PKG_NAME)
            versionPaquetDependance = pacman_pkg_get_info(information, PM_PKG_VERSION)
            
            if not pacman_package_intalled(nomPaquetDependance, versionPaquetDependance):
                listeDependances.append(nomPaquetDependance)

            dependances = pacman_list_next(dependances)

        return listeDependances


    def obtenirMiseAJour (objet, liste):
        """
        Récupère les paquets dont une mise à jour est disponible
        """

        print (fctLang.traduire("add_update_list"))

        if len(liste) > 0:
            liste = []

        listePaquetsMiseAJour = pacman_check_update()

        for element in listePaquetsMiseAJour:
            liste.append(pointer_to_string(element))


    def fpm_trans_conv(*args):
        print ("fpm_trans_conv")
        i = 1
        for arg in args:
            if i == 1:
                event = arg
                print_debug("event : " + str(event))
            elif i == 2:
                pkg=arg
            elif i == 5:
                INTP = ctypes.POINTER(ctypes.c_int)
                response = ctypes.cast(arg, INTP)
            else:
                print ("not yet implemented")

            i += 1

        if event == PM_TRANS_CONV_LOCAL_UPTODATE:
            if print_console_ask(pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME)) + " local version is up to date. Upgrade anyway? [Y/n]" ) == 1:
                response[0] = 1
        if event == PM_TRANS_CONV_LOCAL_NEWER:
            if print_console_ask(pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME)) + " local version is newer. Upgrade anyway? [Y/n]" ) == 1:
                response[0] = 1
        if event == PM_TRANS_CONV_CORRUPTED_PKG:
            if print_console_ask("Archive is corrupted. Do you want to delete it?") == 1:
                    response[0] = 1
            
            
    def print_console_ask(question):
        print_console(question)
        response = raw_input()
        if response == "y":
            return 1
        return -1
         
            
    def installerPaquets (objet, listePaquets):
        """
        Installer les paquets mis en paramêtre
        """
        
        for element in repo_list:
            pacman_set_option(PM_OPT_DLFNM, element)
            
        pm_trans = PM_TRANS_TYPE_SYNC
        flags = PM_TRANS_FLAG_NOCONFLICTS
            
        #~ try:
        pacman_trans_init(pm_trans, flags, None, pacman_trans_cb_conv(objet.fpm_trans_conv), None)

        for paquet in listePaquets:
            pacman_trans_addtarget(paquet)

        data = PM_LIST()
        pacman_trans_prepare(data)
        pacman_trans_commit(data)
                
        pacman_trans_release()
        #~ except:
            #~ print ("Erreurs lors de l'initialisation de l'installation")


def main (*args):
    """
    Partie nécessaire pour l'execution de certaines commandes avec les
    droits super-utilisateur
    """
    fctPaquets = fonctionsPaquets()

    if sys.argv[0] == "cleancache":
        fctPaquets.nettoyerCache()
    elif sys.argv[0] == "updatedb":
        fctPaquets.miseajourBaseDonnees()
    elif sys.argv[0] == "install":
        print sys.argv[1]
        fctPaquets.installerPaquets(sys.argv[1])

if __name__ == "__main__":
    sys.exit(main())

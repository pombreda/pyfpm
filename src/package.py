#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions relatives au gestionnaire de paquet
#
# ----------------------------------------------------------------------

import sys, string, time

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK introuvable")

import pacmang2.libpacman
from pacmang2.libpacman import *

from lang import *

fctLang = fonctionsLang()

pacmang2.libpacman.printconsole=0
pacmang2.libpacman.debug=0

modePacman = ""


class fonctionsPaquets:
    def initialiserPacman (objet):
        """
        Initialise pacman-g2 pour permettre d'être utilisé
        """

        print fctLang.traduire("init_pacman")
        pacman_init()
        print fctLang.traduire("init_db")
        pacman_init_database()
        print fctLang.traduire("register_db")
        pacman_register_all_database()


    def nettoyerCache (objet):
        """
        Nettoye le cache de pacman-g2
        """

        print fctLang.traduire("clean_cache")
        pacman_sync_cleancache()


    def miseajourBaseDonnees (objet):
        """
        Met à jour les dépôts de paquets
        """

        print fctLang.traduire("update_db")
        objet.terminerPacman()
        objet.initialiserPacman()
        pacman_update_db()
        

    def terminerPacman (objet):
        """
        Termine l'instance de pacman-g2
        """

        print fctLang.traduire("close_pacman")
        pacman_trans_release()
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
        
    
    def verifierConflits (objet, nomPaquet):
        """
        Vérifie si le paquet entre en conflit avec d'autres
        """
        
        if "frugalware" in repo_list:
            index = repo_list.index("frugalware")
        elif "frugalware-current" in repo_list:
            index = repo_list.index("frugalware-current")
            
        listePaquets = []
        
        information = pacman_db_readpkg (db_list[index], nomPaquet)
        paquets = pacman_pkg_getinfo(information, PM_PKG_CONFLICTS)

        while paquets != 0:
            if not pointer_to_string(pacman_list_getdata(paquets)) in interface.listeSuppression:
                listePaquets.append(pointer_to_string(pacman_list_getdata(paquets)))
            paquets = pacman_list_next(paquets)
            
        return listePaquets


    def preparerPacman (objet, listeInstallation, listeSuppression):
        """
        Permet de préparer les listes pour l'installation/suppression de paquets
        """
        
        if "frugalware" in repo_list:
            index = repo_list.index("frugalware")
        elif "frugalware-current" in repo_list:
            index = repo_list.index("frugalware-current")
        
        for element in listeInstallation:
            information = pacman_db_readpkg(db_list[index], element)
            
            # Vérification des dépendances
            listePaquets = pacman_pkg_getinfo(information, PM_PKG_DEPENDS)
            
            while listePaquets != 0:
                nomPaquet = pointer_to_string(pacman_list_getdata(listePaquets))
                nomPaquet = nomPaquet.split('=')
                nomPaquet = nomPaquet[0].split('<')
                nomPaquet = nomPaquet[0].split('>')
                
                if not nomPaquet[0] in listeInstallation and not nomPaquet[0] in objet.recupererPaquetsInstalles(nomPaquet[0]):
                    listeInstallation.append(nomPaquet[0])
                
                listePaquets = pacman_list_next(listePaquets)
            
            # Vérification des conflits
            listePaquets = pacman_pkg_getinfo(information, PM_PKG_CONFLICTS)
    
            while listePaquets != 0:
                nomPaquet = pointer_to_string(pacman_list_getdata(listePaquets))
                
                if not nomPaquet in listeSuppression and nomPaquet in objet.recupererPaquetsInstalles(nomPaquet):
                    listeSuppression.append(nomPaquet)
                
                listePaquets = pacman_list_next(listePaquets)
                
            # Vérification des remplacements
            listePaquets = pacman_pkg_getinfo(information, PM_PKG_REPLACES)
    
            while listePaquets != 0:
                nomPaquet = pointer_to_string(pacman_list_getdata(listePaquets))
                
                if not nomPaquet in listeSuppression and nomPaquet in objet.recupererPaquetsInstalles(nomPaquet):
                    listeSuppression.append(nomPaquet)
        
                listePaquets = pacman_list_next(listePaquets)
                
        for element in listeSuppression:
            information = pacman_db_readpkg(db_list[index], element)
            
            # Vérification des dépendances
            listePaquets = pacman_pkg_getinfo(information, PM_PKG_REQUIREDBY)
            
            while listePaquets != 0:
                nomPaquet = pointer_to_string(pacman_list_getdata(listePaquets))
                
                if nomPaquet in objet.recupererPaquetsInstalles(nomPaquet):
                    listeSuppression.remove(element)
                    break
        
                listePaquets = pacman_list_next(listePaquets)
                
            if element in listeInstallation:
                listeSuppression.remove(element)
                
        return listeInstallation, listeSuppression


    def recupererPaquetsInstalles (objet, nomPaquet):
        """
        Recupère la liste des paquets installés
        """
        
        liste = []
        
        pacman_set_option(PM_OPT_NEEDLES, nomPaquet)
        paquet = pacman_db_search(db_list[0])
        
        listePaquets = pacman_pkg_getinfo(paquet, PM_PKG_NAME)
        
        while listePaquets != 0:
            element = pointer_to_string(pacman_list_getdata(listePaquets))
            
            liste.append(element)
            
            listePaquets = pacman_list_next(listePaquets)

        return liste


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
            
            information = pacman_db_readpkg(db_list[index], nomDependance[0])
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

        if listePaquetsMiseAJour > 0:
            for element in listePaquetsMiseAJour:
                liste.append(pointer_to_string(element))


    def chercherPaquet (objet, depot, nomPaquet):
        """
        Chercher les paquets correspondant à la recherche dans le dépôt sélectionné
        """
        
        listePaquetsTrouves = []
        
        pacman_set_option(PM_OPT_NEEDLES, nomPaquet)
        listePaquets = pacman_db_search(depot)
        
        if listePaquets != None:
            i = pacman_list_first(listePaquets)
            
            while i != 0:
                paquet = pacman_db_readpkg(depot, pacman_list_getdata(i))
                
                listePaquetsTrouves.append(paquet)
                
                i = pacman_list_next(i)

        return listePaquetsTrouves
        

    def evenementPacman(*args):
        print ("fpm_trans_conv")
        i = 1
        for argument in args:
            if i == 1:
                evenement = argument
                print ("event : " + str(evenement))
            elif i == 2:
                paquet = argument
            elif i == 5:
                INTP = ctypes.POINTER(ctypes.c_int)
                reponse = ctypes.cast(argument, INTP)
            else:
                print ("not yet implemented")

            i += 1

        if evenement == PM_TRANS_CONV_LOCAL_UPTODATE:
            if terminalQuestion(pointer_to_string(pacman_pkg_getinfo(paquet, PM_PKG_NAME)) + " local version is up to date. Upgrade anyway? [Y/n]" ) == 1:
                reponse[0] = 1
        if evenement == PM_TRANS_CONV_LOCAL_NEWER:
            if terminalQuestion(pointer_to_string(pacman_pkg_getinfo(paquet, PM_PKG_NAME)) + " local version is newer. Upgrade anyway? [Y/n]" ) == 1:
                reponse[0] = 1
        if evenement == PM_TRANS_CONV_CORRUPTED_PKG:
            if terminalQuestion("Archive is corrupted. Do you want to delete it?") == 1:
                reponse[0] = 1
            
            
    def terminalQuestion (question):
        print (question)
        reponse = raw_input()
        if reponse == "y":
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
            
        pacman_trans_init(pm_trans, flags, None, pacman_trans_cb_conv(objet.evenementPacman), None)

        for paquet in listePaquets:
            pacman_trans_addtarget(paquet)

        data = PM_LIST()
        pacman_trans_prepare(data)
        pacman_trans_commit(data)
                
        pacman_trans_release()


    def changerDate (objet, date):
        """
        Adapte la date pour les pays francophone
        """
        
        # FORMAT : Jour Mois N° HH:MM:SS Année -> Jour N° Mois Année HH:MM:SS
        date = string.split(date, " ")
        
        if date[0] == "Mon":
            date[0] = "Lun"
        elif date[0] == "Tue":
            date[0] = "Mar"
        elif date[0] == "Wed":
            date[0] = "Mer"
        elif date[0] == "Thu":
            date[0] = "Jeu"
        elif date[0] == "Fri":
            date[0] = "Ven"
        elif date[0] == "Sat":
            date[0] = "Sam"
        elif date[0] == "Sun":
            date[0] = "Dim"
        
        nouvelleDate = date[0] + " " + date[2] + " " + date[1] + " " + date[4] + " " + date[3]
        return nouvelleDate
        

def main (*args):
    """
    Partie nécessaire pour l'execution de certaines commandes avec les
    droits super-utilisateur
    """
    
    fctPaquets = fonctionsPaquets()
    
    global modePacman
    for argument in sys.argv:
        if argument == "cleancache":
            modePacman = "cleancache"
            fctPaquets.nettoyerCache()
        elif argument == "updatedb":
            modePacman = "updatedb"
            fctPaquets.miseajourBaseDonnees()

if __name__ == "__main__":
    sys.exit(main())

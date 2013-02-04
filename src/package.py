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

from libpacman import *
from lang import *
from pypacman import *

fctLang = fonctionsLang()

modeDebug = 1


class fonctionsPaquets:
    def demarrerPacman (objet):
        """
        Vérifie qu'une instance de pacman-g2 n'est pas en cours
        """

        if os.path.exists(PM_LOCK):
            sys.exit(fctLang.traduire("pacman_already_run"))


    def initialiserPacman (objet):
        """
        Initialise pacman-g2 pour permettre d'être utilisé
        """

        objet.printDebug("DEBUG", fctLang.traduire("init_pacman"))
        pacman_init()
        objet.printDebug("DEBUG", fctLang.traduire("init_db"))
        pacman_init_database()
        objet.printDebug("DEBUG", fctLang.traduire("register_db"))
        pacman_register_all_database()


    def terminerPacman (objet):
        """
        Termine l'instance de pacman-g2
        """

        objet.printDebug("DEBUG", fctLang.traduire("close_pacman"))
        pacman_finally()



    def nettoyerCache (objet):
        """
        Nettoye le cache de pacman-g2
        """

        objet.printDebug("DEBUG", fctLang.traduire("clean_cache"))
        pacman_sync_cleancache()


    def miseajourBaseDonnees (objet):
        """
        Met à jour les dépôts de paquets
        """

        objet.printDebug("DEBUG", fctLang.traduire("update_db"))
        objet.terminerPacman()
        objet.initialiserPacman()
        pacman_update_db()


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


    def lancerPacman (objet, listeInstallationPacman, listeSuppressionPacman):
        """
        Installation et désinstallation de paquet

        Première étape : Désinstallation des paquets sélectionnés
        Deuxième étape : Installation des paquets sélectionnés
        """

        if listeSuppressionPacman != "None":
            listeSuppression = listeSuppressionPacman.split(",")
        else:
            listeSuppression = []

        if listeInstallationPacman != "None":
            listeInstallation = listeInstallationPacman.split(",")
        else:
            listeInstallation = []

        if len(listeSuppression) > 0:
            objet.terminerPacman()
            objet.initialiserPacman()
            objet.printDebug("DEBUG", "Suppression de paquets")
            objet.suppressionPaquet(listeSuppression)

        if len(listeInstallation) > 0:
            objet.terminerPacman()
            objet.initialiserPacman()
            objet.printDebug("DEBUG", "Installation de paquets")
            objet.installationPaquet(listeInstallation)


    def suppressionPaquet (objet, listePaquets, enleverDependances = 0):
        for element in listePaquets:
            if not element in objet.recupererPaquetsInstalles(element):
                # Dans le cas où le paquet ne serait pas installé
                objet.printDebug ("ERROR", "Paquet non installé")
                return -1

            pm_trans_flag = PM_TRANS_FLAG_NOCONFLICTS

            if enleverDependances == 1:
                objet.printDebug ("DEBUG", "Suppression des paquets en cascade")
                pm_trans_flag = PM_TRANS_FLAG_CASCADE

            if pacman_trans_init(PM_TRANS_TYPE_REMOVE, pm_trans_flag, pacman_trans_cb_event(fpm_progress_event), pacman_trans_cb_conv(fpm_trans_conv), pacman_trans_cb_progress(fpm_progress_install)) == -1:
                objet.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            objet.printDebug("DEBUG", "Initialisation de la transaction")

            if pacman_trans_addtarget(element) == -1:
                objet.printDebug ("ERROR", "Impossible de désinstaller " + element)
                objet.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            objet.printDebug("DEBUG", element + " ajouté")

            data = PM_LIST()
            objet.printDebug ("DEBUG", "Vérification des dépendances inverses")

            if pacman_trans_prepare(data) == -1:
                if pacman_get_pm_error() == pacman_c_long_to_int(PM_ERR_UNSATISFIED_DEPS):
                    liste = []
                    index = pacman_list_first(data)
                    while index != 0:
                        paquet = pacman_list_getdata(index)
                        nom = pointer_to_string(pacman_dep_getinfo(paquet, PM_DEP_NAME))
                        liste.append(nom)
                        index = pacman_list_next(index)

                    objet.printDebug ("DEBUG", element + " est requis par : " + str(liste))

                    #~ reponse = interface.fenetreConfirmation(nomPaquet, liste)
                    #~ if reponse == 0:
                        #~ return -1

                    pacman_trans_release()

                    # Redémarrer la transaction

                    return pacman_remove_pkg(element, 1)
                else:
                    objet.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                    return -1
            objet.printDebug ("DEBUG", "Transaction préparée avec succès")
             
            if pacman_trans_commit(data) == -1:
                objet.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            objet.printDebug ("DEBUG", "Suppression de " + element)

            pacman_trans_release()


    def installationPaquet (objet, listePaquets):
        for element in repo_list:
                pacman_set_option(PM_OPT_DLFNM, element)

        pm_trans = PM_TRANS_TYPE_SYNC
        flags = PM_TRANS_FLAG_NOCONFLICTS

        if pacman_trans_init(pm_trans, flags, pacman_trans_cb_event(fpm_progress_event), pacman_trans_cb_conv(fpm_trans_conv), pacman_trans_cb_progress(fpm_progress_install)) == -1:
            objet.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_init : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
            return -1
        else:
            objet.printDebug ("DEBUG", "Initialisation complète")

        for element in listePaquets:
            if pacman_trans_addtarget(element) == -1:
                objet.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_addtarget : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            else:
                objet.printDebug ("DEBUG", element + " ajouté")

        data = PM_LIST()
        objet.printDebug ("DEBUG", "Récupération des dépendances")

        if pacman_trans_prepare(data) == -1:
            objet.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_prepare : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
            return -1
        else:
            objet.printDebug ("DEBUG", "Téléchargement des paquets")

        if pacman_trans_commit(data) == -1:
            objet.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_commit : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
            return -1
        else:
            objet.printDebug ("DEBUG", "Installation des paquets")

        pacman_trans_release()
        return 1


    def progressionInstallation (*args):
        printDebug ("DEBUG", "Progression de l'installation")


    def progressionPaquet (*args):
        printDebug ("DEBUG", "Progression de la transaction")
        i = 1

        for arg in args:
            if i == 1:
                event = arg
                printDebug ("DEBUG", "Evenement : " + str(event))
            elif i == 2:
                pkg = arg
            elif i == 5:
                INTP = ctypes.POINTER(ctypes.c_int)
                reponse = ctypes.cast(arg, INTP)
            else:
                printDebug ("DEBUG", "Pas implanté :)")

            i += 1

        if event == PM_TRANS_CONV_LOCAL_UPTODATE:
            #~ if terminalQuestion (pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME))+" local version is up to date. Upgrade anyway? [Y/n]" ) == 1:
            reponse[0] = 1
        if event==PM_TRANS_CONV_LOCAL_NEWER:
            #~ if terminalQuestion (pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME))+" local version is newer. Upgrade anyway? [Y/n]" ) == 1:
            reponse[0] = 1
        if event==PM_TRANS_CONV_CORRUPTED_PKG:
            #~ if terminalQuestion ("Archive is corrupted. Do you want to delete it?") == 1:
            reponse[0] = 1


    def progressionEvenement(*args):
        printDebug ("DEBUG", "Evenement")


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


    def separerVersionNom (objet, paquet):
        """
        Permet de récupérer la version et le nom du paquet quand la chaîne est du format "kernel>=3.7"
        """

        liste = paquet.split('>')

        liste2 = []
        for element in liste:
            tmp =  element.split('=')
            liste2.extend(tmp)
        liste = liste2

        liste2 = []
        for element in liste:
            tmp =  element.split('<')
            liste2.extend(tmp)
        liste = liste2

        liste2 = []
        for element in liste:
            if element != "":
                liste2.append(element)

        if len(liste2) > 1:
            separateur = paquet[len(liste2[0]):len(paquet) - len(liste2[1])]
            liste2.append(separateur)

        return liste2


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
            if not pointer_to_string(pacman_list_getdata(paquets)) in interface.listeSuppressionPacman:
                listePaquets.append(pointer_to_string(pacman_list_getdata(paquets)))
            paquets = pacman_list_next(paquets)

        return listePaquets


    def verifierVersion (objet, paquet):
        """
        Permet de vérifier si il y a besoin de mettre à jour ou pas suivant la version
        -1 : Le paquet ne peut être modifié
        0 : Le paquet est installé et correspond
        1 : Le paquet peut être mis à jour
        """

        if "frugalware" in repo_list:
            index = repo_list.index("frugalware")
        elif "frugalware-current" in repo_list:
            index = repo_list.index("frugalware-current")

        if len(paquet) > 1:
            nom = paquet[0]
            version = paquet[1]
            symbole = paquet[2]

            informationDepot = pacman_db_readpkg(db_list[index], nom)
            versionPaquetDepot = pacman_pkg_get_info(informationDepot, PM_PKG_VERSION)

            informationLocal = pacman_db_readpkg(db_list[0], nom)
            versionPaquetLocal = pacman_pkg_get_info(informationLocal, PM_PKG_VERSION)

            if symbole == "=":
                if versionPaquetLocal == version:
                    return 0
                elif versionPaquetDepot >= version:
                    return 1
                else:
                    return -1
            elif symbole in [">=", "=>", ">"]:
                if versionPaquetDepot >= version:
                    return 1
            elif symbole in ["<=", "=<", "<"]:
                return -1
        else:
            return 0


    def obtenirMiseAJour (objet, liste):
        """
        Récupère les paquets dont une mise à jour est disponible
        """

        objet.printDebug("DEBUG", fctLang.traduire("add_update_list"))

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


    def terminalQuestion (question):
        print (question)
        reponse = raw_input()
        if reponse == "y":
            return 1
        return -1


    def printDebug (objet, typeErreur, erreur):
        """
        Affiche une sortie terminal
        """

        if modeDebug == 1:
            print ("[" + typeErreur + "] " + erreur)


def main (*args):
    """
    Partie nécessaire pour l'execution de certaines commandes avec les
    droits super-utilisateur
    """

    fctPaquets = fonctionsPaquets()

    for argument in sys.argv:
        if argument == "cleancache":
            fctPaquets.nettoyerCache()
        elif argument == "updatedb":
            fctPaquets.miseajourBaseDonnees()
        elif argument == "install":
            fctPaquets.lancerPacman(sys.argv[sys.argv.index(argument) + 1], sys.argv[sys.argv.index(argument) + 2])

if __name__ == "__main__":
    sys.exit(main())

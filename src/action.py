#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions utilisées par l'interface pour communiquer
#
# ----------------------------------------------------------------------

import os

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK introuvable")

from display import *
from package import *
from lang import *

fctPaquets = fonctionsPaquets()
fctLang = fonctionsLang()


"""
    fonctionsEvenement
        ajouterGroupes (objet, liste)
        remplirPaquets (objet, interface, paquets)
        verifierDonnee (objet, liste, nom)
        detruire (objet, fenetre)
        lancerMiseajourBaseDonnees (objet, interface)
        lancerNettoyerCache (objet, interface)
        obtenirGroupe (objet, interface, groupe)
"""

class fonctionsEvenement:
    def detruire (objet, fenetre):
        """
        Détruit l'interface et termine pyFPM
        """

        fctPaquets.terminerPacman()
        gtk.main_quit()


    def ajouterDepots (objet, interface):
        """
        Récupère les dépots disponible sur le système
        """

        # Met le dépôt du système en choix principal
        index = 0
        if "frugalware" in repo_list:
            index = repo_list.index("frugalware")
        elif "frugalware-current" in repo_list:
            index = repo_list.index("frugalware-current")

        # Intègre les dépôts dans la liste
        for element in repo_list:
            if element == "local":
                element = fctLang.traduire("installed_packages")

            interface.listeSelectionGroupe.append_text(element)

        # Met le dépôt du système en actif
        interface.listeSelectionGroupe.set_active(index)


    def ajouterGroupes (objet, interface):
        """
        Ajouter les groupes dans l'interface
        """

        interface.listeColonnePaquets.clear()
        ensembleGroupes = fctPaquets.initialiserGroupes(interface)

        for nom in ensembleGroupes:
            interface.listeColonneGroupes.append([nom])


    def obtenirGroupe (objet, interface, groupe):
        """
        Obtenir les paquets correspondant au groupe sélectionné
        """

        paquets = fctPaquets.initialiserPaquets(interface, groupe)
        objet.remplirPaquets(interface, paquets)


    def remplirPaquets (objet, interface, paquets):
        """
        Ajoute les paquets dans l'interface
        """

        objetTrouve = 0
        interface.listeColonnePaquets.clear()

        for element in paquets:
            nomPaquet = pacman_pkg_get_info(element, PM_PKG_NAME)
            versionPaquet = pacman_pkg_get_info(element, PM_PKG_VERSION)

            if pacman_package_intalled(nomPaquet, versionPaquet):
                # Le paquet est installé
                objetTrouve = 1
                image = " "
                nouvelleVersion = " "
            elif nomPaquet in interface.listeMiseAJour:
                # Le paquet à une mise à jour
                objetTrouve = 1
                image = gtk.STOCK_REFRESH
                information = pacman_db_readpkg(db_list[0], nomPaquet)
                nouvelleVersion = versionPaquet
                versionPaquet = pacman_pkg_get_info(information, PM_PKG_VERSION)
            else:
                # Le paquet n'est pas installé
                objetTrouve = 0
                image = " "
                nouvelleVersion = " "

            if nomPaquet in interface.listeInstallation:
                objetTrouve = 1
                image = gtk.STOCK_YES
            elif nomPaquet in interface.listeSuppression:
                objetTrouve = 0
                image = gtk.STOCK_NO

            interface.listeColonnePaquets.append([objetTrouve, image, nomPaquet, versionPaquet, nouvelleVersion])

        interface.barreStatus.push(0, str(len(interface.listeColonnePaquets)) + " " + fctLang.traduire("read_packages_done"))


    def obtenirPaquet (objet, interface, nomPaquet, versionPaquet):
        """
        FIXME : Fusioner avec obtenirDetailsPaquet
        """

        interface.barreStatus.push(0, (fctLang.traduire("read_pkg") + " " + nomPaquet))
        objetTrouve = 0

        try:
            listePaquets = pacman_search_pkg(nomPaquet)
            interface.paquetSelectionne = nomPaquet

            for paquet in listePaquets:
                if pacman_pkg_get_info(paquet, PM_PKG_NAME) == nomPaquet and pacman_pkg_get_info(paquet, PM_PKG_VERSION) == versionPaquet:
                    objetTrouve = 1
                    objet.obtenirDetailsPaquet(interface, nomPaquet, versionPaquet, paquet)
                    break

        except:
            pass

        if objetTrouve == 0:
            paquet = pacman_db_readpkg(db_list[0], nomPaquet)
            objet.obtenirDetailsPaquet(interface, nomPaquet, versionPaquet, paquet)


    def obtenirDetailsPaquet (objet, interface, nomPaquet, versionPaquet, paquet):
        """
        Récupérer les informations correspondant au paquet délectionné :
            - nom
            - version
            - description
            - dépendances
            Si installé :
            - site du projet
            - SHA1SUMS
        """

        texte = ""
        paquetInstalle = None

        interface.contenuInformations.clear()

        if pacman_package_intalled(nomPaquet, versionPaquet) == 1:
            paquetInstalle = pacman_db_readpkg (db_list[0], nomPaquet)

        interface.contenuInformations.append(None, [fctLang.traduire("name"), nomPaquet])
        interface.contenuInformations.append(None, [fctLang.traduire("version"), versionPaquet])

        interface.contenuInformations.append(None, [fctLang.traduire("description"), pacman_pkg_get_info(paquet, PM_PKG_DESC)])
        #~ interface.contenuInformations.append(None, [fctLang.traduire("groups"), str(pointer_to_string(pacman_pkg_get_info(paquetInstalle, PM_PKG_GROUPS)))])

        if paquetInstalle <> None:
            interface.contenuInformations.append(None, [fctLang.traduire("url"), "<span foreground='blue'><u>" + pointer_to_string(pacman_pkg_get_info(paquetInstalle, PM_PKG_URL)) + "</u></span>"])
            if nomPaquet in interface.listeMiseAJour:
                interface.contenuInformations.append(None, ["SHA1SUMS", fctLang.traduire("package_update_available")])
            else:
                interface.contenuInformations.append(None, ["SHA1SUMS", pacman_pkg_get_info(paquet, PM_PKG_SHA1SUM)])

        dependances = pacman_pkg_getinfo(paquet, PM_PKG_DEPENDS)

        while dependances != 0:
            nomDependance = pointer_to_string(pacman_list_getdata(dependances))

            nomDependance = nomDependance.split('=')
            nomDependance = nomDependance[0].split('<')
            nomDependance = nomDependance[0].split('>')

            texte += nomDependance[0]

            dependances = pacman_list_next(dependances)
            if dependances != 0:
                texte += ", "

        interface.contenuInformations.append(None, [fctLang.traduire("depends"), texte])


    def verifierDonnee (objet, liste, donnee):
        """
        Vérifie si nom est dans liste
        """

        objetTrouve = 0

        for element in liste:
            if donnee == element:
                objetTrouve = element
                break

        return objetTrouve


    def verifierUtilisateur (objet):
        """
        Verifie quel utilisateur est en train d'utiliser pyFPM
        """

        if not os.geteuid() == 0:
            return 0

        return 1


    def lancerNettoyerCache (objet, image, interface):
        """
        Lancer la commande de nettoyage du cache
        """

        if objet.verifierUtilisateur() == 0:
            os.system(fctConfig.lireConfig("admin", "command") + " python ./src/package.py cleancache")
        else:
            os.system("python ./src/package.py cleancache")

        interface.effacerInterface()
        interface.barreStatus.push(0, fctLang.traduire("clean_cache_done"))


    def lancerMiseajourBaseDonnees (objet, image, interface):
        """
        Lancer la commande de mise à jour des dépôts de paquets
        """

        if objet.verifierUtilisateur() == 0:
            os.system(fctConfig.lireConfig("admin", "command") + " python ./src/package.py updatedb")
        else:
            os.system("python ./src/package.py updatedb")

        interface.effacerInterface()
        interface.barreStatus.push(0, fctLang.traduire("update_db_done"))

        fctPaquets.initialiserGroupes(interface)
        fctPaquets.obtenirMiseAJour(interface.listeMiseAJour)

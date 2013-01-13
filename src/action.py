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


# ----------------------------------------------------------------------
#   fonctionsEvenement
#       ajouterGroupes (objet, liste)
#       remplirPaquets (objet, interface, paquets)
#       verifierDonnee (objet, liste, nom)
#       detruire (objet, fenetre)
#       lancerMiseajourBaseDonnees (objet, interface)
#       lancerNettoyerCache (objet, interface)
#       obtenirGroupe (objet, interface, groupe)
# ----------------------------------------------------------------------

class fonctionsEvenement:
    def detruire (objet, fenetre):
        """
        Détruit l'interface et termine pyFPM
        """

        fctPaquets.terminerPacman()
        gtk.main_quit()


    def ajouterGroupes (objet, interface):
        """
        Ajouter les groupes dans l'interface
        """

        interface.listeColonnePaquets.clear()
        ensembleGroupes = fctPaquets.initialiserGroupes()

        for nom in ensembleGroupes:
            interface.listeColonneGroupes.append([nom])


    def obtenirGroupe (objet, interface, groupe):
        """
        Obtenir les paquets correspondant au groupe sélectionné
        """

        interface.barreStatus.push(0, (" " + fctLang.traduire("read_grp") + " " + groupe))

        paquets = fctPaquets.initialiserPaquets(groupe)
        objet.remplirPaquets(interface, paquets)


    def remplirPaquets (objet, interface, paquets):
        """
        Ajoute les paquets dans l'interface
        """

        objetTrouve = 0
        listeMiseAJour = []

        interface.listePaquetsInstalles = []
        interface.listeColonnePaquets.clear()

        for element in paquets:
            if pacman_package_intalled(pacman_pkg_get_info(element, PM_PKG_NAME), pacman_pkg_get_info(element, PM_PKG_VERSION)):
                # Le paquet est installé
               if not fctPaquets.verifierInstallationPaquet (interface, pacman_pkg_get_info(element, PM_PKG_NAME), pacman_pkg_get_info(element, PM_PKG_VERSION)):
                   interface.listePaquetsInstalles.append([1, pacman_pkg_get_info(element, PM_PKG_NAME), pacman_pkg_get_info(element, PM_PKG_VERSION), ""])
            else:
                # Le paquet n'est pas installé
                if not pacman_pkg_get_info(element, PM_PKG_NAME) in interface.listeMiseAJour:
                    # Le paquet n'est pas une mise à jour
                    interface.listePaquetsInstalles.append([0, pacman_pkg_get_info(element, PM_PKG_NAME), pacman_pkg_get_info(element, PM_PKG_VERSION), ""])
                else:
                    interface.listeMiseAJour.append([pacman_pkg_get_info(element, PM_PKG_NAME), pacman_pkg_get_info(element, PM_PKG_VERSION)])

        indexInstall = 0
        while indexInstall < len(interface.listePaquetsInstalles):
            indexMiseAJour = 0
            image = ""
            while indexMiseAJour < len(interface.listeMiseAJour):
                if interface.listePaquetsInstalles[indexInstall][1] == interface.listeMiseAJour[indexMiseAJour][0]:
                    interface.listePaquetsInstalles[indexInstall][3] = interface.listeMiseAJour[indexMiseAJour][1]
                    image = gtk.STOCK_REFRESH

                indexMiseAJour += 1

            modificationPaquet = interface.listePaquetsInstalles[indexInstall][0]
            if interface.listePaquetsInstalles[indexInstall][1] in interface.listeSuppression or interface.listePaquetsInstalles[indexInstall][1] in interface.listeInstallation:
                modificationPaquet = not modificationPaquet

                if interface.listePaquetsInstalles[indexInstall][1] in interface.listeInstallation:
                    image = gtk.STOCK_YES
                elif interface.listePaquetsInstalles[indexInstall][1] in interface.listeSuppression:
                    image = gtk.STOCK_NO

            interface.listeColonnePaquets.append([modificationPaquet, image, interface.listePaquetsInstalles[indexInstall][1], interface.listePaquetsInstalles[indexInstall][2], interface.listePaquetsInstalles[indexInstall][3]])
            indexInstall += 1


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
        #~ interface.contenuInformations.append(None, [fctLang.traduire("groups"), pointer_to_string(pacman_pkg_get_info(paquetInstalle, PM_PKG_GROUPS))])

        if paquetInstalle <> None:
            interface.contenuInformations.append(None, [fctLang.traduire("url"), pointer_to_string(pacman_pkg_get_info(paquetInstalle, PM_PKG_URL))])
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

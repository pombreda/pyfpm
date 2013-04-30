#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions utilisées par l'interface pour communiquer
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys, urllib, codecs

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK introuvable")

from Pacman.libpacman import *
from Pacman import package
from . import files, lang, config

# Initialisation des modules
Package = package.Package()
Lang = lang.Lang()
File = files.File()
Config = config.Config()


class Events (object):
    """
    Ensemble de fonctions permettant à pyFPM d'obtenir des
    informations
    """

    def initGroups (self, interface):
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


    def initPackages (self, interface, nomGroupe):
        """
        Initialise les paquets correspondant au groupe sélectionné
        """

        ensemblePaquets = []

        pm_group = pacman_db_readgrp (db_list[interface.listeSelectionGroupe.get_active()], nomGroupe)
        i = pacman_grp_getinfo (pm_group, PM_GRP_PKGNAMES)

        while i != 0:
            paquet = pacman_db_readpkg (db_list[interface.listeSelectionGroupe.get_active()], pacman_list_getdata(i))

            if not paquet in ensemblePaquets:
                ensemblePaquets.append(paquet)

            i = pacman_list_next(i)

        ensemblePaquets.sort()

        return ensemblePaquets


    def getUpdate (self, liste):
        """
        Récupère les paquets dont une mise à jour est disponible
        """

        Package.printDebug("DEBUG", Lang.translate("add_update_list"))

        if len(liste) > 0:
            liste = []

        listePaquetsMiseAJour = pacman_check_update()

        if listePaquetsMiseAJour > 0:
            for element in listePaquetsMiseAJour:
                liste.append(pointer_to_string(element))


    def getPackageInfo (self, interface, nomPaquet, versionPaquet):
        """
        Obtient les détails du paquet
        """

        objetTrouve = 0

        if nomPaquet.find("]") != -1:
            nomPaquet = nomPaquet[nomPaquet.find("]") + 1:].strip()

        interface.updateStatusbar(Lang.translate("read_pkg") + " " + nomPaquet)

        try:
            listePaquets = pacman_search_pkg(nomPaquet)
            interface.paquetSelectionne = nomPaquet

            for paquet in listePaquets:
                if pacman_pkg_get_info(paquet, PM_PKG_NAME) == nomPaquet and pacman_pkg_get_info(paquet, PM_PKG_VERSION) == versionPaquet:
                    objetTrouve = 1
                    self.obtenirDetailsPaquet(interface, nomPaquet, versionPaquet, paquet)
                    break

        except:
            pass

        if objetTrouve == 0:
            paquet = pacman_db_readpkg(db_list[0], nomPaquet)

        texte = ""
        paquetInstalle = None

        interface.contenuInformations.clear()
        interface.contenuPaquet.clear()

        # Récupère les informations depuis local si le paquet est installé
        if pacman_package_intalled(nomPaquet, versionPaquet) == 1:
            paquetInstalle = pacman_db_readpkg (db_list[0], nomPaquet)

        interface.contenuInformations.append(None, [Lang.translate("name"), nomPaquet])
        interface.contenuInformations.append(None, [Lang.translate("version"), versionPaquet])

        interface.contenuInformations.append(None, [Lang.translate("description"), pacman_pkg_get_info(paquet, PM_PKG_DESC).replace("&","&amp;")])

        # Liste des groupes
        texte = ""
        groupes = pacman_pkg_getinfo(paquet, PM_PKG_GROUPS)

        while groupes != 0:
            nomGroupe = pointer_to_string(pacman_list_getdata(groupes))

            texte += nomGroupe

            groupes = pacman_list_next(groupes)
            if groupes != 0:
                texte += ", "

        if texte != "":
            interface.contenuInformations.append(None, [Lang.translate("groups"), texte])

        # Affiche des informations supplémentaires si le paquet est installé
        if paquetInstalle != None:
            interface.contenuInformations.append(None, [Lang.translate("url"), pacman_pkg_get_info(paquetInstalle, PM_PKG_URL)])

            if nomPaquet in interface.listeMiseAJourPacman:
                interface.contenuPaquet.append(None, ["SHA1SUMS", Lang.translate("package_update_available")])
            else:
                interface.contenuPaquet.append(None, ["SHA1SUMS", pacman_pkg_get_info(paquet, PM_PKG_SHA1SUM)])

            interface.contenuPaquet.append(None, [Lang.translate("install_date"), pacman_pkg_get_info(paquetInstalle, PM_PKG_INSTALLDATE)])
            interface.contenuPaquet.append(None, [Lang.translate("size"), str(format(float(long(pacman_pkg_getinfo(paquetInstalle, PM_PKG_SIZE))/1024)/1024, '.2f')) + " MB"])
            interface.contenuPaquet.append(None, [Lang.translate("packager"), pacman_pkg_get_info(paquetInstalle, PM_PKG_PACKAGER)])
        else:
            interface.contenuPaquet.append(None, ["SHA1SUMS", pacman_pkg_get_info(paquet, PM_PKG_SHA1SUM)])
            interface.contenuPaquet.append(None, [Lang.translate("compress_size"), str(format(float(long(pacman_pkg_getinfo(paquet, PM_PKG_SIZE))/1024)/1024, '.2f')) + " MB"])
            interface.contenuPaquet.append(None, [Lang.translate("uncompress_size"), str(format(float(long(pacman_pkg_getinfo(paquet, PM_PKG_USIZE))/1024)/1024, '.2f')) + " MB"])

        # Liste des dépendances
        texte = ""
        paquets = pacman_pkg_getinfo(paquet, PM_PKG_DEPENDS)

        while paquets != 0:
            element = pointer_to_string(pacman_list_getdata(paquets))

            nom = Package.splitVersionName(element)
            texte += nom[0]

            paquets = pacman_list_next(paquets)
            if paquets != 0:
                texte += ", "

        if texte != "":
            interface.contenuInformations.append(None, [Lang.translate("depends"), texte])

        # Liste des paquets ajoutés
        texte = ""
        paquets = pacman_pkg_getinfo(paquet, PM_PKG_PROVIDES)

        while paquets != 0:
            element = pointer_to_string(pacman_list_getdata(paquets))

            texte += element

            paquets = pacman_list_next(paquets)
            if paquets != 0:
                texte += ", "

        if texte != "":
            interface.contenuPaquet.append(None, [Lang.translate("provides"), texte])

        # Liste des paquets remplacés
        texte = ""
        paquets = pacman_pkg_getinfo(paquet, PM_PKG_REPLACES)

        while paquets != 0:
            element = pointer_to_string(pacman_list_getdata(paquets))

            texte += element

            paquets = pacman_list_next(paquets)
            if paquets != 0:
                texte += ", "

        if texte != "":
            interface.contenuPaquet.append(None, [Lang.translate("replaces"), texte])

        # Liste des dépendances inverses
        texte = ""
        paquets = pacman_pkg_getinfo(paquet, PM_PKG_REQUIREDBY)

        while paquets != 0:
            element = pointer_to_string(pacman_list_getdata(paquets))

            texte += element

            paquets = pacman_list_next(paquets)
            if paquets != 0:
                texte += ", "

        if texte != "":
            interface.contenuInformations.append(None, [Lang.translate("required_by"), texte])

        # Liste des paquets en conflit
        texte = ""
        paquets = pacman_pkg_getinfo(paquet, PM_PKG_CONFLICTS)

        while paquets != 0:
            element = pointer_to_string(pacman_list_getdata(paquets))

            texte += element

            paquets = pacman_list_next(paquets)
            if paquets != 0:
                texte += ", "

        if texte != "":
            interface.contenuPaquet.append(None, [Lang.translate("conflits"), texte])

        # Liste des fichiers inclus dans le paquet
        texte = ""
        texteBuffer = interface.listeFichiers.get_buffer()

        if pacman_package_intalled(nomPaquet, versionPaquet) == 1:
            fichiers = pacman_pkg_getinfo(paquetInstalle, PM_PKG_FILES)
            while fichiers != 0:
                texte += "  /" + pointer_to_string(pacman_list_getdata(fichiers)) + "\n"
                fichiers = pacman_list_next(fichiers)
        else:
            texte = " " + Lang.translate("no_info")

        texteBuffer.set_text(texte)

        # Changelog du paquet
        texte = ""
        texteBuffer = interface.listeJournal.get_buffer()

        if pacman_package_intalled(nomPaquet, versionPaquet) == 1:
            try:
                journal = PM_ROOT + PM_DBPATH + "/" + repo_list[0] + "/" + nomPaquet + "-" + versionPaquet + "/changelog"
                if os.path.exists(journal) == True:
                    file = codecs.open(journal, "r", "iso-8859-15")
                    for element in file:
                        if element != "":
                            texte += " " + element
                    file.close()
                else:
                    texte = " " + Lang.translate("no_file_found")
            except:
                texte = " " + Lang.translate("error")
        else:
            texte = " " + Lang.translate("no_info")

        texteBuffer.set_text(texte)

        if Config.readConfig("pyfpm", "developmentmode") == "true":
            # Fichier de création du paquet
            texte = ""
            texteBuffer = interface.listeFrugalbuild.get_buffer()

            try:
                if self.getFrugalBuild(paquet):
                    if os.path.exists("/tmp/frugalbuild") == True:
                        file = codecs.open("/tmp/frugalbuild", "r", "utf-8")
                        for element in file:
                            if element != "":
                                texte += " " + element
                        file.close()
            except:
                texte = " " + Lang.translate("no_file_found")

            texteBuffer.set_text(texte)


    def getFrugalBuild (self, paquet):
        """
        Récupère le FrugalBuild via le git de Frugalware
        """

        if "frugalware" in repo_list:
            index = "frugalware"
        elif "frugalware-current" in repo_list:
            index = "frugalware-current"

        listeGroupesProhibes = ['-extensions','adesklets-desklets','amsn-plugins','avidemux-plugin-cli','avidemux-plugin-gtk','avidemux-plugin-qt','chroot-core','core','cinnamon-desktop','devel-core','directfb-drivers','e17-apps','e17-misc','fatrat-plugins','firefox-extensions','geda-suite','gift-plugins','gnome-minimal','hk_classes-drivers','jdictionary-plugins','kde-apps','kde-build','kde-core','kde-doc','kde-docs','kde-minimal','kde-runtime','lxde-desktop','lxde-extra','pantheon-desktop','misc-fonts','phonon-backend','pidgin-plugins','qt4-libs','sawfish-scripts','seamonkey-addons','thunderbird-extensions','tuxcmd-plugins','wmaker-dockapps','xfce4-core','xfce4-goodies','xorg-apps','xorg-core','xorg-data','xorg-doc','xorg-drivers','xorg-fonts','xorg-libs','xorg-proto','xorg-util']
        listeGroupes = []

        # Liste des groupes
        texte = ""

        nomPaquet = pacman_pkg_get_info(paquet, PM_PKG_NAME)
        groupes = pacman_pkg_getinfo(paquet, PM_PKG_GROUPS)

        while groupes != 0:
            nomGroupe = pointer_to_string(pacman_list_getdata(groupes))

            listeGroupes.append(nomGroupe)

            groupes = pacman_list_next(groupes)

        for element in listeGroupes:
            if not element in listeGroupesProhibes:
                nomGroupe = element
                break

        url = "http://www7.frugalware.org/pub/frugalware/" + index + "/source/" + nomGroupe + "/" + nomPaquet + "/FrugalBuild"

        try:
            if File.verifierErreurUrl(url) == 1:
                fichierFB = urllib.urlopen(url)
                fichierLocal = open("/tmp/frugalbuild", 'w')
                fichierLocal.write(fichierFB.read())
                fichierFB.close()
                fichierLocal.close()
                Package.printDebug("DEBUG", Lang.translate("download_complete") + " " + url)
                resultat = True
            else:
                Package.printDebug("ERROR", Lang.translate("download_failed_404") + " " + url)
        except:
            Package.printDebug("ERROR", Lang.translate("download_failed") + " " + url)
            resultat = False
            pass

        return resultat


    def checkData (self, liste, donnee):
        """
        Vérifie si nom est dans liste
        """

        objetTrouve = 0

        for element in liste:
            if donnee == element:
                objetTrouve = element
                break

        return objetTrouve


    def checkUser (self):
        """
        Verifie quel utilisateur est en train d'utiliser pyFPM
        """

        if not os.geteuid() == 0:
            return 0

        return 1


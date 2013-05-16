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

from Pacman import package
from . import files, lang, config

# Initialisation des modules
Package = package.Package()
Lang = lang.Lang()
File = files.File()
Config = config.Config()

modeDebug = True

class Events (object):
    """
    Ensemble de fonctions permettant à pyFPM d'obtenir des
    informations
    """


    def getUpdate (self, liste):
        """
        Récupère les paquets dont une mise à jour est disponible
        """

        Event.printDebug("DEBUG", Lang.translate("add_update_list"))

        if len(liste) > 0:
            liste = []

        listePaquetsMiseAJour = Package.getUpdateList()

        if listePaquetsMiseAJour > 0:
            for element in listePaquetsMiseAJour:
                liste.append(element)


    def getPackageInfo (self, interface, nomPaquet, versionPaquet):
        """
        Obtient les détails du paquet
        """

        objetTrouve = 0

        if nomPaquet.find("]") != -1:
            # Dans le cas d'une recherche, il est nécessaire d'enlever le préfixe [<nom_dépôt>]
            nomPaquet = nomPaquet[nomPaquet.find("]") + 1:].strip()

        interface.updateStatusbar(Lang.translate("read_pkg") + " " + nomPaquet)

        texte = ""

        interface.contenuInformations.clear()
        interface.contenuPaquet.clear()

        # Récupère les informations depuis local si le paquet est installé
        if Package.checkPackageInstalled(nomPaquet, versionPaquet):
            depot = 0
        else:
            depot = int(interface.listeSelectionGroupe.get_active())

        pointerPaquet = Package.getPackagePointer(nomPaquet, depot)
        infoPaquet = Package.getPackageInfo(pointerPaquet)

        interface.contenuInformations.append(None, [Lang.translate("name"), infoPaquet.get("name")])
        interface.contenuInformations.append(None, [Lang.translate("version"), infoPaquet.get("version")])

        interface.contenuInformations.append(None, [Lang.translate("description"), infoPaquet.get("description").replace("&","&amp;").encode('ascii', 'replace')])

        # Liste des groupes
        texte = infoPaquet.get("groups")

        if texte != "":
            interface.contenuInformations.append(None, [Lang.translate("groups"), texte])

        if infoPaquet.get("name") in interface.listeMiseAJourPacman:
            interface.contenuPaquet.append(None, ["SHA1SUMS", Lang.translate("package_update_available")])
        else:
            interface.contenuPaquet.append(None, ["SHA1SUMS", infoPaquet.get("sha1sums")])

        # Affiche des informations supplémentaires si le paquet est installé
        if Package.checkPackageInstalled(nomPaquet, versionPaquet):
            interface.contenuInformations.append(None, [Lang.translate("url"), infoPaquet.get("url")])

            interface.contenuPaquet.append(None, [Lang.translate("install_date"), infoPaquet.get("install_date")])
            interface.contenuPaquet.append(None, [Lang.translate("size"), str(format(float(long(infoPaquet.get("size"))/1024)/1024, '.2f')) + " MB"])
            interface.contenuPaquet.append(None, [Lang.translate("packager"), infoPaquet.get("packager")])
        else:
            interface.contenuPaquet.append(None, [Lang.translate("compress_size"), str(format(float(long(infoPaquet.get("compress_size"))/1024)/1024, '.2f')) + " MB"])
            interface.contenuPaquet.append(None, [Lang.translate("uncompress_size"), str(format(float(long(infoPaquet.get("uncompress_size"))/1024)/1024, '.2f')) + " MB"])

        # Liste des dépendances
        texte = infoPaquet.get("depends")
        if texte != "":
            interface.contenuInformations.append(None, [Lang.translate("depends"), texte])

        # Liste des paquets ajoutés
        texte = infoPaquet.get("provides")
        if texte != "":
            interface.contenuPaquet.append(None, [Lang.translate("provides"), texte])

        # Liste des paquets remplacés
        texte = infoPaquet.get("replaces")
        if texte != "":
            interface.contenuPaquet.append(None, [Lang.translate("replaces"), texte])

        # Liste des dépendances inverses
        texte = infoPaquet.get("required_by")
        if texte != "":
            interface.contenuPaquet.append(None, [Lang.translate("required_by"), texte])

        # Liste des paquets en conflit
        texte = infoPaquet.get("conflits")
        if texte != "":
            interface.contenuPaquet.append(None, [Lang.translate("conflits"), texte])

        # Liste des fichiers inclus dans le paquet
        texte = ""
        texteBuffer = interface.listeFichiers.get_buffer()

        if Package.checkPackageInstalled(nomPaquet, versionPaquet):
            texte = Package.getFileFromPackage(nomPaquet)
        else:
            texte = " " + Lang.translate("no_info")

        texteBuffer.set_text(texte)

        # Changelog du paquet
        texte = ""
        texteBuffer = interface.listeJournal.get_buffer()

        if Package.checkPackageInstalled(nomPaquet, versionPaquet):
            try:
                listeDepot = Package.getRepoList()
                journal = "/var/lib/pacman-g2/" + listeDepot[0] + "/" + nomPaquet + "-" + versionPaquet + "/changelog"
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
            index = "frugalware-stable"
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
                Event.printDebug("DEBUG", Lang.translate("download_complete") + " " + url)
                resultat = True
            else:
                Event.printDebug("ERROR", Lang.translate("download_failed_404") + " " + url)
        except:
            Event.printDebug("ERROR", Lang.translate("download_failed") + " " + url)
            resultat = False
            pass

        return resultat


    def checkData (self, liste, donnee):
        """
        Vérifie si donnee est dans liste
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


    def printDebug (self, typeErreur, erreur):
        """
        Affiche une sortie terminal
        """

        if typeErreur == "DEBUG":
            color = "\033[0;32m"
        elif typeErreur == "ERROR":
            color = "\033[0;34m"
        elif typeErreur == "INFO":
            color = "\033[0;36m"
        else:
            color = "\033[0m"

        if modeDebug or typeErreur != "INFO":
            print (str(color) + "[" + typeErreur + "]\t\033[0m" + str(erreur))


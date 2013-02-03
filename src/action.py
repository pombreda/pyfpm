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


class fonctionsEvenement:
    def detruire (objet, fenetre):
        """
        Détruit l'interface et termine pyFPM
        """

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

        listeGroupesProhibes = ['-extensions','adesklets-desklets','amsn-plugins','avidemux-plugin-cli','avidemux-plugin-gtk','avidemux-plugin-qt','chroot-core','core','cinnamon-desktop','devel-core','directfb-drivers','e17-apps','e17-misc','fatrat-plugins','firefox-extensions','geda-suite','gift-plugins','gnome-minimal','hk_classes-drivers','jdictionary-plugins','kde-apps','kde-build','kde-core','kde-doc','kde-docs','kde-minimal','kde-runtime','lxde-desktop','lxde-extra','pantheon-desktop','misc-fonts','phonon-backend','pidgin-plugins','qt4-libs','sawfish-scripts','seamonkey-addons','thunderbird-extensions','tuxcmd-plugins','wmaker-dockapps','xfce4-core','xfce4-goodies','xorg-apps','xorg-core','xorg-data','xorg-doc','xorg-drivers','xorg-fonts','xorg-libs','xorg-proto','xorg-util']

        interface.listeColonnePaquets.clear()
        ensembleGroupes = fctPaquets.initialiserGroupes(interface)

        for nom in ensembleGroupes:
            if fctConfig.lireConfig("pyfpm", "useprohibategroups") == "false":
                if not nom in listeGroupesProhibes:
                    interface.listeColonneGroupes.append([nom])
            else:
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
            elif nomPaquet in interface.listeMiseAJourPacman:
                # Le paquet à une mise à jour
                objetTrouve = 1
                if not nomPaquet in interface.listeInstallationPacman:
                    image = gtk.STOCK_REFRESH
                else:
                    image = gtk.STOCK_ADD
                information = pacman_db_readpkg(db_list[0], nomPaquet)
                nouvelleVersion = versionPaquet
                versionPaquet = pacman_pkg_get_info(information, PM_PKG_VERSION)
            else:
                # Le paquet n'est pas installé
                objetTrouve = 0
                image = " "
                nouvelleVersion = " "

            if nomPaquet in interface.listeInstallationPacman:
                objetTrouve = 1
                if not nomPaquet in interface.listeMiseAJourPacman:
                    image = gtk.STOCK_ADD
            elif nomPaquet in interface.listeSuppressionPacman:
                objetTrouve = 0
                image = gtk.STOCK_REMOVE

            interface.listeColonnePaquets.append([objetTrouve, image, nomPaquet, versionPaquet, nouvelleVersion])

        interface.rafraichirFenetre()
        interface.changerTexteBarreStatus(str(len(interface.listeColonnePaquets)) + " " + fctLang.traduire("read_packages_done"))


    def obtenirPaquet (objet, interface, nomPaquet, versionPaquet):
        """
        FIXME : Fusioner avec obtenirDetailsPaquet
        """

        interface.changerTexteBarreStatus(fctLang.traduire("read_pkg") + " " + nomPaquet)
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
            - groupes
            Si installé :
            - site du projet
            - SHA1SUMS
        """

        texte = ""
        paquetInstalle = None

        interface.contenuInformations.clear()
        interface.contenuPaquet.clear()

        # Récupère les informations depuis local si le paquet est installé
        if pacman_package_intalled(nomPaquet, versionPaquet) == 1:
            paquetInstalle = pacman_db_readpkg (db_list[0], nomPaquet)

        interface.contenuInformations.append(None, [fctLang.traduire("name"), nomPaquet])
        interface.contenuInformations.append(None, [fctLang.traduire("version"), versionPaquet])

        interface.contenuInformations.append(None, [fctLang.traduire("description"), str(pacman_pkg_get_info(paquet, PM_PKG_DESC))])

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
            interface.contenuInformations.append(None, [fctLang.traduire("groups"), texte])

        # Affiche des informations supplémentaires si le paquet est installé
        if paquetInstalle != None:
            interface.contenuInformations.append(None, [fctLang.traduire("url"), "<span foreground='blue'><u>" + pacman_pkg_get_info(paquetInstalle, PM_PKG_URL) + "</u></span>"])

            if nomPaquet in interface.listeMiseAJourPacman:
                interface.contenuPaquet.append(None, ["SHA1SUMS", fctLang.traduire("package_update_available")])
            else:
                interface.contenuPaquet.append(None, ["SHA1SUMS", pacman_pkg_get_info(paquet, PM_PKG_SHA1SUM)])

            interface.contenuPaquet.append(None, [fctLang.traduire("install_date"), fctPaquets.changerDate(pacman_pkg_get_info(paquetInstalle, PM_PKG_INSTALLDATE))])
            interface.contenuPaquet.append(None, [fctLang.traduire("size"), str(format(float(long(pacman_pkg_getinfo(paquetInstalle, PM_PKG_SIZE))/1024)/1024, '.2f')) + " MB"])
            interface.contenuPaquet.append(None, [fctLang.traduire("packager"), pacman_pkg_get_info(paquetInstalle, PM_PKG_PACKAGER)])
        else:
            interface.contenuPaquet.append(None, ["SHA1SUMS", pacman_pkg_get_info(paquet, PM_PKG_SHA1SUM)])
            interface.contenuPaquet.append(None, [fctLang.traduire("compress_size"), str(format(float(long(pacman_pkg_getinfo(paquet, PM_PKG_SIZE))/1024)/1024, '.2f')) + " MB"])
            interface.contenuPaquet.append(None, [fctLang.traduire("uncompress_size"), str(format(float(long(pacman_pkg_getinfo(paquet, PM_PKG_USIZE))/1024)/1024, '.2f')) + " MB"])

        # Liste des dépendances
        texte = ""
        paquets = pacman_pkg_getinfo(paquet, PM_PKG_DEPENDS)

        while paquets != 0:
            element = pointer_to_string(pacman_list_getdata(paquets))

            nom = fctPaquets.separerVersionNom(element)
            texte += nom[0]

            paquets = pacman_list_next(paquets)
            if paquets != 0:
                texte += ", "

        if texte != "":
            interface.contenuInformations.append(None, [fctLang.traduire("depends"), texte])

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
            interface.contenuPaquet.append(None, [fctLang.traduire("provides"), texte])

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
            interface.contenuPaquet.append(None, [fctLang.traduire("replaces"), texte])

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
            interface.contenuInformations.append(None, [fctLang.traduire("required_by"), texte])

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
            interface.contenuPaquet.append(None, [fctLang.traduire("conflits"), texte])

        # Liste des fichiers inclus dans le paquet
        texte = ""
        texteBuffer = interface.listeFichiers.get_buffer()

        if pacman_package_intalled(nomPaquet, versionPaquet) == 1:
            fichiers = pacman_pkg_getinfo(paquetInstalle, PM_PKG_FILES)
            while fichiers != 0:
                texte += "  /" + pointer_to_string(pacman_list_getdata(fichiers)) + "\n"
                fichiers = pacman_list_next(fichiers)
        else:
            texte = " " + fctLang.traduire("no_info")

        texteBuffer.set_text(texte)

        # Liste des fichiers inclus dans le paquet
        texte = ""
        texteBuffer = interface.listeJournal.get_buffer()

        if pacman_package_intalled(nomPaquet, versionPaquet) == 1:
            journal = PM_ROOT + PM_DBPATH + "/" + repo_list[0] + "/" + nomPaquet + "-" + versionPaquet + "/changelog"
            if os.path.exists(journal) == True:
                file = codecs.open(journal, "r", "utf-8")
                for element in file:
                    if element != "":
                        texte += " " + element
                file.close()
            else:
                texte = " " + fctLang.traduire("no_file_found")
        else:
            texte = " " + fctLang.traduire("no_info")

        texteBuffer.set_text(texte)

        chemin = "/usr/share/icons/Frugalware/apps/16/" + nomPaquet + ".png"
        if os.path.exists(chemin) == True:
            image = gtk.gdk.pixbuf_new_from_file(chemin)
        else:
            image = None
        interface.iconeInformations.set_from_pixbuf(image)


    def lancerNettoyerCache (objet, image, interface):
        """
        Lancer la commande de nettoyage du cache
        """

        interface.fenetre.set_sensitive(False)
        interface.changerTexteBarreStatus(fctLang.traduire("clean_cache"))
        interface.rafraichirFenetre()

        if objet.verifierUtilisateur() == 0:
            os.system(fctConfig.lireConfig("admin", "command") + " python ./src/package.py cleancache")
        else:
            fctPaquets.nettoyerCache()

        interface.effacerInterface()
        objet.ajouterDepots(interface)
        objet.ajouterGroupes(interface)
        interface.changerTexteBarreStatus(fctLang.traduire("clean_cache_done"))

        interface.fenetre.set_sensitive(True)


    def lancerMiseajourBaseDonnees (objet, image, interface):
        """
        Lancer la commande de mise à jour des dépôts de paquets
        """

        interface.fenetre.set_sensitive(False)
        interface.changerTexteBarreStatus(fctLang.traduire("update_db"))
        interface.rafraichirFenetre()

        if objet.verifierUtilisateur() == 0:
            os.system(fctConfig.lireConfig("admin", "command") + " python ./src/package.py updatedb")
        else:
            os.system("python ./src/package.py updatedb")

        interface.effacerInterface()
        objet.ajouterDepots(interface)
        objet.ajouterGroupes(interface)
        interface.changerTexteBarreStatus(fctLang.traduire("update_db_done"))

        fctPaquets.initialiserGroupes(interface)
        fctPaquets.obtenirMiseAJour(interface.listeMiseAJourPacman)

        if len(interface.listeMiseAJourPacman) > 0:
            interface.fenetreMiseAJour()

        interface.fenetre.set_sensitive(True)


    def lancerInstallationPaquets (objet, interface):
        """
        Lancer la commande d'installation de paquets
        """

        interface.fenetre.set_sensitive(False)
        interface.rafraichirFenetre()

        argumentInstallation = ""
        argumentSuppression = ""

        if len(interface.listeInstallationPacman) > 0:
            for element in interface.listeInstallationPacman:
                argumentInstallation += element
                if interface.listeInstallationPacman.index(element) + 1 < len(interface.listeInstallationPacman):
                    argumentInstallation += ","
        else:
            argumentInstallation = None

        if len(interface.listeSuppressionPacman) > 0:
            for element in interface.listeSuppressionPacman:
                argumentSuppression += element
                if interface.listeSuppressionPacman.index(element) + 1 < len(interface.listeSuppressionPacman):
                    argumentSuppression += ","
        else:
            argumentSuppression = None

        if objet.verifierUtilisateur() == 0:
            os.system(fctConfig.lireConfig("admin", "command") + " python ./src/package.py install " + str(argumentInstallation) + " " + str(argumentSuppression))
        else:
            os.system("python ./src/package.py install " + str(argumentInstallation) + " " + str(argumentSuppression))

        interface.effacerInterface()
        objet.ajouterDepots(interface)
        objet.ajouterGroupes(interface)

        fctPaquets.initialiserGroupes(interface)
        fctPaquets.obtenirMiseAJour(interface.listeMiseAJourPacman)

        if len(interface.listeMiseAJourPacman) > 0:
            interface.fenetreMiseAJour()

        interface.fenetre.set_sensitive(True)


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


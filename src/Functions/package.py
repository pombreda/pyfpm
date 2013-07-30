#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions relatives au gestionnaire de paquet
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys, string, time, gettext, dbus

# Récupération de la traduction
gettext.bindtextdomain('pyfpm', 'lang')
gettext.textdomain('pyfpm')
_ = gettext.gettext

# Noms dbus
BUSNAME = 'org.frugalware.fpmd.Instance'
OBJPATH = '/org/frugalware/fpmd/Instance/object'


class Package (object):
    """
    Fonctions concernant la gestion de pacman-g2
    """

    def __init__ (self):
        """
        Récupération des fonctions de FPMd
        """

        # Récupération des fonctions de FPMd
        packageBus = dbus.SystemBus()

        try:
            proxy = packageBus.get_object(BUSNAME, OBJPATH, introspect=False)
        except dbus.DBusException:
            sys.exit(_("DBus interface is not available"))

        # Fonction interne a Fpmd
        self.fpmd_resetPacman = proxy.get_dbus_method('resetPacman', BUSNAME)
        self.fpmd_emitSignal = proxy.get_dbus_method('emitSignal', BUSNAME)

        # Fonciton de pacman-g2
        self.fpmd_getRepoList = proxy.get_dbus_method('getRepoList', BUSNAME)
        self.fpmd_searchRepoPackage = proxy.get_dbus_method('searchRepoPackage', BUSNAME)
        self.fpmd_getGroupsList = proxy.get_dbus_method('getGroupsList', BUSNAME)
        self.fpmd_searchInstalledPackage = proxy.get_dbus_method('searchInstalledPackage', BUSNAME)
        self.fpmd_getPackagesList = proxy.get_dbus_method('getPackagesList', BUSNAME)
        self.fpmd_getPackageInfo = proxy.get_dbus_method('getPackageInfo', BUSNAME)
        self.fpmd_getSha1sums = proxy.get_dbus_method('getSha1sums', BUSNAME)
        self.fpmd_getPackagePointer = proxy.get_dbus_method('getPackagePointer', BUSNAME)
        self.fpmd_getUpdateList = proxy.get_dbus_method('getUpdateList', BUSNAME)
        self.fpmd_checkPackageInstalled = proxy.get_dbus_method('checkPackageInstalled', BUSNAME)
        self.fpmd_getFileFromPackage = proxy.get_dbus_method('getFileFromPackage', BUSNAME)
        self.fpmd_getInstalledList = proxy.get_dbus_method('getInstalledList', BUSNAME)


    def resetPacman (self):
        """
        Remet à zéro les informations de pacman-g2
        """

        self.fpmd_resetPacman()


    #~ def runPacman (self, interface, listeInstallationPacman, listeSuppressionPacman):
        #~ """
        #~ Installation et désinstallation de paquet

        #~ Première étape : Désinstallation des paquets sélectionnés
        #~ Deuxième étape : Installation des paquets sélectionnés
        #~ """

        #~ self.printDebug ("DEBUG", "runPacman")

        #~ if listeSuppressionPacman != "None":
            #~ listeSuppression = listeSuppressionPacman.split(",")
        #~ else:
            #~ listeSuppression = []

        #~ if listeInstallationPacman != "None":
            #~ listeInstallation = listeInstallationPacman.split(",")
        #~ else:
            #~ listeInstallation = []


        #~ if len(listeSuppression) > 0:
            #~ self.closePacman()
            #~ self.initPacman()
            #~ self.printDebug("DEBUG", "Suppression de paquets")
            #~ self.removePackage(listeSuppression)

        #~ if len(listeInstallation) > 0:
            #~ self.closePacman()
            #~ self.initPacman()
            #~ self.printDebug("DEBUG", "Installation de paquets")
            #~ self.installPackage(interface, listeInstallation)


    def getInstalledPackage (self, nomPaquet):
        """
        Recupère la liste des paquets installés et regarde si
        nomPaquet est dedans
        """

        return self.fpmd_searchInstalledPackage(nomPaquet)


    def getRepoList (self):
        """
        Recupère la liste des dépôts
        """

        return self.fpmd_getRepoList()


    def getIndexFromRepo (self):
        """
        Récupère l'index du dépôt principal (frugalware ou
        frugalware-current)
        """

        repoList = self.getRepoList()

        if "frugalware" in repoList:
            index = repoList.index("frugalware")
        elif "frugalware-current" in repoList:
            index = repoList.index("frugalware-current")
        else:
            index = 0

        return int(index)


    def getGroupsList (self, depot):
        """
        Récupère la liste des groupes de paquets
        """

        return self.fpmd_getGroupsList(depot)


    def getPackagesList (self, depot, nomGroupe):
        """
        Récupère la liste des paquets pour un groupe
        """

        return self.fpmd_getPackagesList(depot, nomGroupe)


    def getFileFromPackage (self, nomPaquet):
        """
        Récupère la liste des fichiers inclus dans un paquet installé
        """

        return self.fpmd_getFileFromPackage(nomPaquet)


    def searchPackage (self, nomPaquet):
        """
        Chercher les paquets correspondant à la recherche dans le dépôt sélectionné
        """

        return self.fpmd_searchRepoPackage(nomPaquet)


    def getUpdateList (self):
        """
        """

        return self.fpmd_getUpdateList()


    def getInstalledList (self):
        """
        Recupère la liste des paquets installés
        """

        return self.fpmd_getInstalledList()


    def getPackageInfo (self, paquet):
        """
        Obtient les informations d'un paquet
        """

        return self.fpmd_getPackageInfo (paquet)


    def getPackagePointer (self, nomPaquet, repo = 0):
        """
        Obtient le pointer d'un paquet à partir de son nom
        """

        return self.fpmd_getPackagePointer (nomPaquet, repo)


    def checkPackageInstalled (self, nomPaquet, versionPaquet):
        """
        Vérifie si un paquet est installé
        """

        return self.fpmd_checkPackageInstalled (nomPaquet, versionPaquet)


    def getSha1sums (self, nomPaquet, repo = 1):
        """
        Obtient le pointer d'un paquet à partir de son nom
        """

        return self.fpmd_getSha1sums (nomPaquet, repo)


    def emitSignal (self, texte):
        """
        Envoie un signal
        """

        return self.fpmd_emitSignal(texte)

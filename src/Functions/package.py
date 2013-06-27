#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions relatives au gestionnaire de paquet
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys, string, time, gettext
import dbus
#~ import dbus.service, dbus.mainloop.glib, gobject

gettext.bindtextdomain('pyfpm', 'lang')
gettext.textdomain('pyfpm')
_ = gettext.gettext

from . import lang

# Initialisation des modules
Lang = lang.Lang()

# Récupération des fonctions de FPMd
bus = dbus.SystemBus()
proxy = bus.get_object('org.frugalware.fpmd.deamon','/org/frugalware/fpmd/deamon/object', introspect=False)

fpmd_closeDeamon = proxy.get_dbus_method('closeDeamon', 'org.frugalware.fpmd.deamon')
fpmd_updateDatabase = proxy.get_dbus_method('updateDatabase', 'org.frugalware.fpmd.deamon')
fpmd_cleanCache = proxy.get_dbus_method('cleanCache', 'org.frugalware.fpmd.deamon')
fpmd_getRepoList = proxy.get_dbus_method('getRepoList', 'org.frugalware.fpmd.deamon')
fpmd_searchRepoPackage = proxy.get_dbus_method('searchRepoPackage', 'org.frugalware.fpmd.deamon')
fpmd_getGroupsList = proxy.get_dbus_method('getGroupsList', 'org.frugalware.fpmd.deamon')
fpmd_searchInstalledPackage = proxy.get_dbus_method('searchInstalledPackage', 'org.frugalware.fpmd.deamon')
fpmd_getPackagesList = proxy.get_dbus_method('getPackagesList', 'org.frugalware.fpmd.deamon')
fpmd_getPackageInfo = proxy.get_dbus_method('getPackageInfo', 'org.frugalware.fpmd.deamon')
fpmd_getSha1sums = proxy.get_dbus_method('getSha1sums', 'org.frugalware.fpmd.deamon')
fpmd_getPackagePointer = proxy.get_dbus_method('getPackagePointer', 'org.frugalware.fpmd.deamon')
fpmd_getUpdateList = proxy.get_dbus_method('getUpdateList', 'org.frugalware.fpmd.deamon')
fpmd_checkPackageInstalled = proxy.get_dbus_method('checkPackageInstalled', 'org.frugalware.fpmd.deamon')
fpmd_getFileFromPackage = proxy.get_dbus_method('getFileFromPackage', 'org.frugalware.fpmd.deamon')
fpmd_getInstalledList = proxy.get_dbus_method('getInstalledList', 'org.frugalware.fpmd.deamon')


class Package (object):


    def cleanCache (self, widget, interface):
        """
        Nettoye le cache de pacman-g2
        """

        interface.updateStatusbar(_("Clean cache"))
        interface.fenetre.set_sensitive(False)
        interface.refresh()

        fpmd_cleanCache()

        interface.updateStatusbar(_("Clean cache complete"))
        interface.fenetre.set_sensitive(True)
        interface.refresh()


    def updateDatabase (self, widget, interface):
        """
        Met à jour les dépôts de paquets
        """

        interface.updateStatusbar(_("Update databases"))
        interface.fenetre.set_sensitive(False)
        interface.refresh()

        fpmd_updateDatabase()

        interface.eraseInterface()
        interface.addRepos()
        #~ interface.addGroups()

        interface.fenetre.set_sensitive(True)
        interface.refresh()

        interface.getUpdateList()


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

        return fpmd_searchInstalledPackage(nomPaquet)


    def getRepoList (self):
        """
        Recupère la liste des dépôts
        """

        return fpmd_getRepoList()


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

        return fpmd_getGroupsList(depot)


    def getPackagesList (self, depot, nomGroupe):
        """
        Récupère la liste des paquets pour un groupe
        """

        return fpmd_getPackagesList(depot, nomGroupe)


    def getFileFromPackage (self, nomPaquet):
        """
        Récupère la liste des fichiers inclus dans un paquet installé
        """

        return fpmd_getFileFromPackage(nomPaquet)


    def searchPackage (self, nomPaquet):
        """
        Chercher les paquets correspondant à la recherche dans le dépôt sélectionné
        """

        return fpmd_searchRepoPackage(nomPaquet)


    def getUpdateList (self):
        """
        """

        return fpmd_getUpdateList()


    def getInstalledList (self):
        """
        Recupère la liste des paquets installés
        """

        return fpmd_getInstalledList()


    def getPackageInfo (self, paquet):
        """
        Obtient les informations d'un paquet
        """

        return fpmd_getPackageInfo (paquet)


    def getPackagePointer (self, nomPaquet, repo=0):
        """
        Obtient le pointer d'un paquet à partir de son nom
        """

        return fpmd_getPackagePointer (nomPaquet, repo)


    def checkPackageInstalled (self, nomPaquet, versionPaquet):
        """
        Vérifie si un paquet est installé
        """

        return fpmd_checkPackageInstalled (nomPaquet, versionPaquet)


    def getSha1sums (self, nomPaquet, repo=1):
        """
        Obtient le pointer d'un paquet à partir de son nom
        """

        return fpmd_getSha1sums (nomPaquet, repo)


    def splitVersionName (self, paquet):
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




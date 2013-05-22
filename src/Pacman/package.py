#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions relatives au gestionnaire de paquet
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys, string, time
import dbus
#~ import dbus.service, dbus.mainloop.glib, gobject

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pygtk_not_found")

from Misc import lang

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


class Package (object):

    def cleanCache (self, widget, interface):
        """
        Nettoye le cache de pacman-g2
        """

        interface.updateStatusbar(Lang.translate("clean_cache"))
        interface.fenetre.set_sensitive(False)
        interface.refresh()

        fpmd_cleanCache()

        interface.updateStatusbar(Lang.translate("clean_cache_done"))
        interface.fenetre.set_sensitive(True)
        interface.refresh()


    def updateDatabase (self, widget, interface):
        """
        Met à jour les dépôts de paquets
        """

        interface.updateStatusbar(Lang.translate("update_db"))
        interface.fenetre.set_sensitive(False)
        interface.refresh()

        fpmd_updateDatabase()

        interface.eraseInterface()
        interface.addRepos()
        interface.addGroups()

        interface.fenetre.set_sensitive(True)
        interface.refresh()


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


    #~ def removePackage (self, listePaquets, enleverDependances = 0):
        #~ """
        #~ Fonction pour supprimer des paquets
        #~ """

        #~ self.printDebug ("DEBUG", "removePackage")

        #~ for element in listePaquets:
            #~ if not element in self.getInstalledPackage(element):
                #~ # Dans le cas où le paquet ne serait pas installé
                #~ self.printDebug ("ERROR", "Paquet non installé")
                #~ return -1

            #~ pm_trans_flag = PM_TRANS_FLAG_NOCONFLICTS

            #~ if enleverDependances == 1:
                #~ self.printDebug ("DEBUG", "Suppression des paquets en cascade")
                #~ pm_trans_flag = PM_TRANS_FLAG_CASCADE

            #~ if pacman_trans_init(PM_TRANS_TYPE_REMOVE, pm_trans_flag, pacman_trans_cb_event(fpm_progress_event), pacman_trans_cb_conv(fpm_trans_conv), pacman_trans_cb_progress(fpm_progress_install)) == -1:
                #~ self.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                #~ return -1
            #~ self.printDebug("DEBUG", "Initialisation de la transaction")

            #~ if pacman_trans_addtarget(element) == -1:
                #~ self.printDebug ("ERROR", "Impossible de désinstaller " + element)
                #~ self.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                #~ return -1
            #~ self.printDebug("DEBUG", element + " ajouté")

            #~ data = PM_LIST()
            #~ self.printDebug ("DEBUG", "Vérification des dépendances inverses")

            #~ if pacman_trans_prepare(data) == -1:
                #~ if pacman_get_pm_error() == pacman_c_long_to_int(PM_ERR_UNSATISFIED_DEPS):
                    #~ liste = []
                    #~ index = pacman_list_first(data)
                    #~ while index != 0:
                        #~ paquet = pacman_list_getdata(index)
                        #~ nom = pointer_to_string(pacman_dep_getinfo(paquet, PM_DEP_NAME))
                        #~ liste.append(nom)
                        #~ index = pacman_list_next(index)

                    #~ self.printDebug ("DEBUG", element + " est requis par : " + str(liste))

                    #~ reponse = self.fenetreQuestion("DEBUG", element + " est requis par : " + str(liste) + "\nSouhaitez-vous continuer ?")
                    #~ if reponse == False:
                        #~ pacman_trans_release()
                        #~ return -1

                    #~ pacman_trans_release()

                    #~ # Redémarrer la transaction

                    #~ return pacman_remove_pkg(element, 1)
                #~ else:
                    #~ self.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                    #~ return -1
            #~ self.printDebug ("DEBUG", "Transaction préparée avec succès")

            #~ if pacman_trans_commit(data) == -1:
                #~ self.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                #~ return -1
            #~ self.printDebug ("DEBUG", "Suppression de " + element)

            #~ pacman_trans_release()


    #~ def installPackage (self, interface, listePaquets):
        #~ """
        #~ Fonction pour installer des paquets
        #~ """

        #~ self.printDebug ("DEBUG", "installPackage")

        #~ interface.changeLabel(Lang.translate("install_pkg"))
        #~ interface.refresh()

        #~ for element in repo_list:
                #~ pacman_set_option(PM_OPT_DLFNM, element)

        #~ pm_trans = PM_TRANS_TYPE_SYNC

        #~ flags = PM_TRANS_FLAG_NOCONFLICTS
        #~ flags = PM_TRANS_FLAG_DOWNLOADONLY

        #~ progres = 1.0

        #~ if pacman_trans_init(pm_trans, flags, pacman_trans_cb_event(self.progressEvent), pacman_trans_cb_conv(self.progressPackage), pacman_trans_cb_progress(self.progressInstall)) == -1:
            #~ self.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_init : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
            #~ return -1
        #~ else:
            #~ self.printDebug ("DEBUG", "Initialisation complète")
            #~ interface.changeProgressbar("Initialisation complète", progres)

        #~ for element in listePaquets:
            #~ if pacman_trans_addtarget(element) == -1:
                #~ self.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_addtarget : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                #~ return -1
            #~ else:
                #~ self.printDebug ("DEBUG", element + " ajouté")
                #~ interface.changeProgressbar(element + " ajouté", progres)

        #~ self.printDebug ("DEBUG", "Récupération des dépendances")
        #~ interface.changeProgressbar("Récupération des dépendances", progres)

        #~ data = PM_LIST()
        #~ try:
            #~ if pacman_trans_prepare(data) == -1:
                #~ self.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_prepare : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                #~ return -1
            #~ else:
                #~ self.printDebug ("DEBUG", "Téléchargement des paquets")
                #~ interface.changeProgressbar("Téléchargement des paquets", progres)

            #~ if pacman_trans_commit(data) == -1:
                #~ self.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_commit : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                #~ return -1
            #~ else:
                #~ self.printDebug ("DEBUG", "Installation des paquets")
                #~ interface.changeProgressbar("Installation des paquets", progres)
        #~ except:
            #~ self.printDebug ("ERROR", "pacman_trans_prepare")

        #~ pacman_trans_release()
        #~ return 1


    #~ def progressInstall (self, *args):
        #~ """
        #~ """

        #~ printDebug ("DEBUG", "Progression de l'installation")

        #~ from Pacman import package
        #~ interface = package.fenetreInstallation()

        #~ index = 1
        #~ pourcent = 0
        #~ event = 0
        #~ compte = 0

        #~ texte = ""
        #~ progres = 0

        #~ for arg in args:
            #~ if index == 1 and arg != None:
                #~ event = arg
            #~ elif index == 3 and arg != None:
                #~ pourcent = arg
            #~ elif index == 4 and arg != None:
                #~ compte = arg
            #~ else:
                #~ pass

            #~ index += 1

        #~ try :
            #~ progres = float(float(pourcent)/100)
            #~ printDebug ("DEBUG", progres)
        #~ except :
            #~ pass

        #~ if event == PM_TRANS_PROGRESS_ADD_START:
            #~ if compte > 1:
                #~ texte = "Installing packages..."
            #~ else:
                #~ texte = "Installing package..."
        #~ elif event == PM_TRANS_PROGRESS_UPGRADE_START:
            #~ if compte > 1:
                #~ texte = "Upgrading packages..."
            #~ else:
                #~ texte = "Upgrading package..."
        #~ elif event == PM_TRANS_PROGRESS_REMOVE_START:
            #~ if compte > 1:
                #~ texte = "Removing packages..."
            #~ else:
                #~ texte = "Removing package..."
        #~ elif event == PM_TRANS_PROGRESS_CONFLICTS_START:
            #~ if compte > 1:
                #~ texte = "Checking packages for file conflicts..."
            #~ else:
                #~ texte = "Checking package for file conflicts..."
        #~ else:
            #~ pass

        #~ if texte != "":
            #~ printDebug ("DEBUG", texte)

        #~ self.printDebug ("DEBUG", "fpm_progress_install finish")

        #~ interface.changeProgressbar(texte, progres)


    #~ def progressPackage (self, *args):
        #~ printDebug ("DEBUG", "Progression de la transaction")
        #~ index = 1

        #~ for arg in args:
            #~ if index == 1:
                #~ event = arg
                #~ self.printDebug ("DEBUG", "Evenement : " + str(event))
            #~ elif index == 2:
                #~ pkg = arg
            #~ elif index == 5:
                #~ INTP = ctypes.POINTER(ctypes.c_int)
                #~ reponse = ctypes.cast(arg, INTP)
            #~ else:
                #~ self.printDebug ("DEBUG", "Pas implanté :)")

            #~ index += 1

        #~ if event == PM_TRANS_CONV_LOCAL_UPTODATE:
            #~ if terminalQuestion (pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME))+" local version is up to date. Upgrade anyway? [Y/n]" ) == 1:
            #~ reponse[0] = 1
        #~ if event==PM_TRANS_CONV_LOCAL_NEWER:
            #~ if terminalQuestion (pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME))+" local version is newer. Upgrade anyway? [Y/n]" ) == 1:
            #~ reponse[0] = 1
        #~ if event==PM_TRANS_CONV_CORRUPTED_PKG:
            #~ if terminalQuestion ("Archive is corrupted. Do you want to delete it?") == 1:
            #~ reponse[0] = 1


    #~ def progressEvent(self, *args):
        #~ """
        #~ Affiche l'evenement en cours
        #~ """

        #~ self.printDebug ("DEBUG", "Evenement")

        #~ from Pacman import package
        #~ interface = package.fenetreInstallation()

        #~ try:
            #~ index = 1

            #~ event = None
            #~ data1 = None
            #~ data2 = None

            #~ for arg in args:
                #~ if index == 1 and arg != None:
                    #~ event = arg
                #~ elif index == 2 and arg != None:
                    #~ data1 = arg
                #~ elif index == 3 and arg != None:
                    #~ data2=arg
                #~ else:
                    #~ pass

                #~ index += 1

            #~ self.printDebug ("DEBUG", event)
            #~ self.printDebug ("DEBUG", data1)
            #~ self.printDebug ("DEBUG", data2)
        #~ except :
            #~ pass


        #~ if event != PM_TRANS_EVT_RETRIEVE_START and event != PM_TRANS_EVT_RESOLVEDEPS_START and event != PM_TRANS_EVT_RESOLVEDEPS_DONE:
            #~ telechargement = False

        #~ texte = ""
        #~ progres = 0.0

        #~ if event == PM_TRANS_EVT_CHECKDEPS_START:
            #~ texte = Lang.translate("checking_dependencies")
            #~ progres = 1.0
        #~ elif event == PM_TRANS_EVT_FILECONFLICTS_START:
            #~ texte = Lang.translate("checking_file_conflicts")
            #~ progres = 1.0
        #~ elif event == PM_TRANS_EVT_RESOLVEDEPS_START:
            #~ texte = Lang.translate("resolving_dependencies")
        #~ elif event == PM_TRANS_EVT_INTERCONFLICTS_START:
            #~ texte = Lang.translate("looking_interconflicts")
            #~ progres = 1.0
        #~ elif event == PM_TRANS_EVT_INTERCONFLICTS_DONE:
            #~ texte = Lang.translate("looking_interconflicts_done")
        #~ elif event == PM_TRANS_EVT_ADD_START:
            #~ texte = Lang.translate("installing")
            #~ progres = 1.0
        #~ elif event == PM_TRANS_EVT_ADD_DONE:
            #~ texte = Lang.translate("installing_done")
        #~ elif event == PM_TRANS_EVT_UPGRADE_START:
            #~ texte = Lang.translate("upgrading")
            #~ progres = 1.0
        #~ elif event == PM_TRANS_EVT_UPGRADE_DONE:
            #~ texte = Lang.translate("upgrading_done")
        #~ elif event == PM_TRANS_EVT_REMOVE_START:
            #~ texte = Lang.translate("removing")
        #~ elif event == PM_TRANS_EVT_REMOVE_DONE:
            #~ texte = Lang.translate("removing_done")
        #~ elif event == PM_TRANS_EVT_INTEGRITY_START:
            #~ texte = Lang.translate("checking_integrity")
        #~ elif event == PM_TRANS_EVT_INTEGRITY_DONE:
            #~ texte = Lang.translate("checking_integrity_done")
        #~ elif event == PM_TRANS_EVT_SCRIPTLET_INFO:
            #~ texte = pointer_to_string(data1)
        #~ elif event == PM_TRANS_EVT_SCRIPTLET_START:
            #~ texte = str_data1
        #~ elif event == PM_TRANS_EVT_SCRIPTLET_DONE:
            #~ texte = Lang.translate("scriptlet_done")
        #~ elif event == PM_TRANS_EVT_RETRIEVE_START:
            #~ texte = Lang.translate("retrieving_packages")
            #~ progres = 1.0
            #~ telechargement = True
        #~ else :
            #~ pass

        #~ self.printDebug ("DEBUG", texte)
        #~ self.printDebug ("DEBUG", "fpm_progress_event finish")

        #~ interface.changeProgressbar(texte, progres)


    def getInstalledPackage (self, nomPaquet):
        """
        Recupère la liste des paquets installés
        """

        return fpmd_searchInstalledPackage(nomPaquet)


    def getRepoList (self):
        """
        Recupère la liste des dépôts
        """

        return fpmd_getRepoList()


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




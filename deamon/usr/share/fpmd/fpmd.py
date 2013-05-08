#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#                        FPMd - Clide
#
#   Auteur :
#       - Lubert Aurélien (PacMiam)
#
#   But du programme :
#       Il s'agit d'un démon permettant d'utiliser pacman-g2
#       depuis pyFPM ou pyFUN.
#
# ----------------------------------------------------------------------

# Importation des modules
import dbus, dbus.service, dbus.mainloop.glib, gobject, time

from libpacman import *

BUSNAME = 'org.frugalware.fpmd.deamon'
OBJPATH = '/org/frugalware/fpmd/deamon/object'

class FPMd (dbus.service.Object):
    def __init__ (self):
        self.startPacman()
        
        # Connexion au bus system
        connection = dbus.service.BusName(BUSNAME, bus=dbus.SystemBus())
        # Initalisation de l'objet
        dbus.service.Object.__init__(self, connection, OBJPATH)
        

    def startPacman (self):
        """
        Start pacman-g2 instance
        """

        pacman_started()
            
        self.printDebug("INFO", "init_pacman")
        pacman_init()
        self.printDebug("INFO", "init_db")
        pacman_init_database()
        self.printDebug("INFO", "register_db")
        pacman_register_all_database()
        

    def closePacman (self):
        """
        End pacman-g2 instance
        """

        self.printDebug("INFO", "close_pacman")
        pacman_finally()

        
    def printDebug (self, typeErreur, erreur):
        """
        Affiche une sortie terminal
        """

        print ("[" + typeErreur + "] " + str(erreur))
        

    @dbus.service.method (BUSNAME, in_signature='su', out_signature='u')
    def getPackagePointer (self, pkgName, repo):
        """
        Get the package pointer
        """

        pkg = pacman_db_readpkg(db_list[int(repo)], str(pkgName))
        
        return pkg
        

    @dbus.service.method (BUSNAME, in_signature='u', out_signature='a{ss}')
    def getPackageInfo (self, pkg):
        """
        Get some informations about the package
        """

        pkgName = pacman_pkg_get_info(pkg, PM_PKG_NAME)
        pkgVersion = pacman_pkg_get_info(pkg, PM_PKG_VERSION)

        pkgDict = {"name" : str(pkgName), \
                            "version" : str(pkgVersion), \
                            "description" : str(pacman_pkg_get_info(pkg, PM_PKG_DESC)), \
                            "sha1sums" : str(pacman_pkg_get_info(pkg, PM_PKG_SHA1SUM)), \
                            "groups" : str(self.getInfoFromPackage(pkg, PM_PKG_GROUPS)), \
                            "depends" : str(self.getInfoFromPackage(pkg, PM_PKG_DEPENDS)), \
                            "provides" : str(self.getInfoFromPackage(pkg, PM_PKG_PROVIDES)), \
                            "replaces" : str(self.getInfoFromPackage(pkg, PM_PKG_REPLACES)), \
                            "required_by" : str(self.getInfoFromPackage(pkg, PM_PKG_REQUIREDBY)), \
                            "conflits" : str(self.getInfoFromPackage(pkg, PM_PKG_CONFLICTS)) }

        if self.checkPackageInstalled(str(pkgName), str(pkgVersion)):
            pkgDict2 = {"url" : str(pacman_pkg_get_info(pkg, PM_PKG_URL)), \
                                    "install_date" : str(pacman_pkg_get_info(pkg, PM_PKG_INSTALLDATE)), \
                                    "size" : str(pacman_pkg_getinfo(pkg, PM_PKG_SIZE)), \
                                    "packager" : str(pacman_pkg_get_info(pkg, PM_PKG_PACKAGER)) }
        else:
            pkgDict2 = {"compress_size" : str(pacman_pkg_getinfo(pkg, PM_PKG_SIZE)), \
                                    "uncompress_size" : str(pacman_pkg_getinfo(pkg, PM_PKG_USIZE)) }

        pkgDict.update(pkgDict2)
        
        return pkgDict


    @dbus.service.method (BUSNAME, in_signature='s', out_signature='s')
    def getFileFromPackage (self, pkgName):
        """
        """

        text = ""

        pkg = pacman_db_readpkg(db_list[0], str(pkgName))
        
        files = pacman_pkg_getinfo(pkg, PM_PKG_FILES)
        while files != 0:
            text += "  /" + pointer_to_string(pacman_list_getdata(files)) + "\n"
            files = pacman_list_next(files)

        return text


    def getInfoFromPackage (self, pkg, typeInfo):
        """
        """

        text = ""
        listInfo = pacman_pkg_getinfo(pkg, typeInfo)

        while listInfo != 0:
            infoName = pointer_to_string(pacman_list_getdata(listInfo))

            text += infoName

            listInfo = pacman_list_next(listInfo)
            if listInfo != 0:
                text += ", "

        return text
        

    @dbus.service.method (BUSNAME, in_signature='ss', out_signature='b')
    def checkPackageInstalled (self, pkgName, pkgVersion):
        """
        """

        return pacman_package_intalled(str(pkgName), str(pkgVersion))


    @dbus.service.method (BUSNAME)
    def getRepoList (self):
        """
        """
        
        return repo_list
        

    @dbus.service.method (BUSNAME, in_signature='u', out_signature='as')
    def getGroupsList (self, repo):

        groupsList = []

        i = pacman_db_getgrpcache(db_list[repo])

        while i != 0:
            group = pacman_list_getdata(i)

            if not pointer_to_string(group) in groupsList:
                groupsList.append(pointer_to_string(group))

            i = pacman_list_next(i)

        return groupsList


    @dbus.service.method (BUSNAME, in_signature='us', out_signature='au')
    def getPackagesList (self, repo, groupName):

        packagesList = []

        pm_group = pacman_db_readgrp (db_list[repo], str(groupName))
        i = pacman_grp_getinfo (pm_group, PM_GRP_PKGNAMES)

        while i != 0:
            pkg = pacman_db_readpkg (db_list[repo], pacman_list_getdata(i))

            if not pkg in packagesList:
                packagesList.append(pkg)

            i = pacman_list_next(i)

        return packagesList

        
    @dbus.service.method (BUSNAME, in_signature='s', out_signature='a(si)')
    def searchRepoPackage (self, pkgName):
        """
        Chercher les paquets correspondant à la recherche dans le dépôt sélectionné
        """

        foundPkgList = []

        for element in repo_list:
            if repo_list.index(element) > 0:
                pacman_set_option(PM_OPT_NEEDLES, pkgName)
                pkgList = pacman_db_search(db_list[repo_list.index(element)])

                if pkgList != None:
                    i = pacman_list_first(pkgList)

                    while i != 0:
                        pkg = pacman_db_readpkg(db_list[repo_list.index(element)], pacman_list_getdata(i))
                        foundPkgList.append([element, pkg])
                        i = pacman_list_next(i)

        return foundPkgList

        
    @dbus.service.method (BUSNAME, in_signature='s')
    def searchInstalledPackage (self, pkgName):
        """
        Recupère la liste des paquets installés
        """

        foundPkgList = []

        pacman_set_option(PM_OPT_NEEDLES, pkgName)
        paquet = pacman_db_search(db_list[0])

        pkgList = pacman_pkg_getinfo(paquet, PM_PKG_NAME)

        while pkgList != 0:
            element = pointer_to_string(pacman_list_getdata(pkgList))

            foundPkgList.append(element)

            pkgList = pacman_list_next(pkgList)

        return foundPkgList


    @dbus.service.method (BUSNAME, out_signature="as")
    def getUpdateList (self):
        """
        """

        stringList = []

        updateList = pacman_check_update()

        for element in updateList:
            stringList.append(pointer_to_string(element))

        return stringList
        

    @dbus.service.method (BUSNAME)
    def updateDatabase (self):
        """
        Met à jour les dépôts de paquets
        """

        for element in db_list:
            if repo_list[db_list.index(element)] != "local":
                #~ self.printDebug("DEBUG", "update_db_name " + str(db_list.index(element)) + ":" + repo_list[db_list.index(element)])

                #~ pourcentage = float(index - 1) / float(len(repo_list) - 1)
                #~ interface.changeProgressbar("update_db_name " + repo_list[index], float(pourcentage))

                if pacman_db_update (1, element) == -1:
                    #~ self.printDebug("ERROR", "Can't update pacman-g2")
                    pacman_print_error()
                
            #~ time.sleep(0.2)
                

    @dbus.service.method (BUSNAME)
    def cleanCache (self):
        """
        Nettoye le cache de pacman-g2
        """

        self.printDebug("INFO", "clean_cache")
        pacman_sync_cleancache()
        

    @dbus.service.method (BUSNAME)
    def closeDeamon (self):
        self.closePacman()
        loop.quit()
        
        
if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    gobject.threads_init()
    dbus.mainloop.glib.threads_init()
    _fpmd = FPMd()
    loop = gobject.MainLoop()
    loop.run()

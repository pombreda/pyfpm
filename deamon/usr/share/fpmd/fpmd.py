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
        # Connexion au bus system
        connection = dbus.service.BusName(BUSNAME, bus=dbus.SystemBus())
        # Initalisation de l'objet
        dbus.service.Object.__init__(self, connection, OBJPATH)

        self.startPacman()


    def startPacman (self):
        """
        Start pacman-g2 instance
        """

        pacman_started()

        self.sendSignal("init_pacman")
        pacman_init()
        self.sendSignal("init_db")
        pacman_init_database()
        self.sendSignal("register_db")
        pacman_register_all_database()


    def closePacman (self):
        """
        End pacman-g2 instance
        """

        self.sendSignal("close_pacman")
        pacman_finally()


    @dbus.service.signal(BUSNAME, signature='s')
    def sendSignal (self, string):
        """
        Send a string
        """

        pass


    @dbus.service.method (BUSNAME, in_signature='su', out_signature='u')
    def getPackagePointer (self, pkgName, repo):
        """
        Get the package pointer
        """

        pkg = pacman_db_readpkg(db_list[int(repo)], str(pkgName))

        return pkg


    @dbus.service.method (BUSNAME, in_signature='u', out_signature='a{sv}')
    def getPackageInfo (self, pkg):
        """
        Get some informations about the package
        """

        pkgName = pacman_pkg_get_info(pkg, PM_PKG_NAME)
        pkgVersion = pacman_pkg_get_info(pkg, PM_PKG_VERSION)

        pkgDict = {"name" : str(pkgName), \
                    "version" : str(pkgVersion), \
                    "description" : unicode(str(pacman_pkg_get_info(pkg, PM_PKG_DESC)), errors='replace'), \
                    "groups" : self.getInfoFromPackage(pkg, PM_PKG_GROUPS), \
                    "depends" : self.getInfoFromPackage(pkg, PM_PKG_DEPENDS), \
                    "provides" : self.getInfoFromPackage(pkg, PM_PKG_PROVIDES), \
                    "replaces" : self.getInfoFromPackage(pkg, PM_PKG_REPLACES), \
                    "required_by" : self.getInfoFromPackage(pkg, PM_PKG_REQUIREDBY), \
                    "conflits" : self.getInfoFromPackage(pkg, PM_PKG_CONFLICTS) }

        if self.checkPackageInstalled(str(pkgName), str(pkgVersion)):
            pkgDict2 = {"url" : str(pacman_pkg_get_info(pkg, PM_PKG_URL)), \
                        "install_date" : str(pacman_pkg_get_info(pkg, PM_PKG_INSTALLDATE)), \
                        "size" : str(pacman_pkg_getinfo(pkg, PM_PKG_SIZE)), \
                        "packager" : unicode(str(pacman_pkg_get_info(pkg, PM_PKG_PACKAGER)), errors='replace') }
        else:
            pkgDict2 = {"compress_size" : str(pacman_pkg_getinfo(pkg, PM_PKG_SIZE)), \
                        "uncompress_size" : str(pacman_pkg_getinfo(pkg, PM_PKG_USIZE)) }

        pkgDict.update(pkgDict2)

        return pkgDict


    @dbus.service.method (BUSNAME, in_signature='su', out_signature='s')
    def getSha1sums (self, pkgName, repo):
        """
        Get the correct SHA1SUMS from frugalware/repos
        """

        pkg = pacman_db_readpkg(db_list[int(repo)], str(pkgName))

        sha1sums = str(pacman_pkg_get_info(pkg, PM_PKG_SHA1SUM))

        return sha1sums


    @dbus.service.method (BUSNAME, in_signature='s', out_signature='s')
    def getFileFromPackage (self, pkgName):
        """
        Get the files list of the package
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
        Get informations about a package and put them into a string
        """

        content = []
        listInfo = pacman_pkg_getinfo(pkg, typeInfo)

        while listInfo != 0:
            infoName = pointer_to_string(pacman_list_getdata(listInfo))

            content.append(str(infoName))

            listInfo = pacman_list_next(listInfo)

        if len(content) > 0:
            return content
        else:
            return ""


    @dbus.service.method (BUSNAME, in_signature='ss', out_signature='b')
    def checkPackageInstalled (self, pkgName, pkgVersion):
        """
        Check if a package is installed or not
        """

        return pacman_package_intalled(str(pkgName), str(pkgVersion))


    @dbus.service.method (BUSNAME)
    def getRepoList (self):
        """
        Get the repository list
        """

        return repo_list


    @dbus.service.method (BUSNAME, in_signature='u', out_signature='as')
    def getGroupsList (self, repo):
        """
        Get the groups list from a repository
        """

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
        """
        Get the packages list from a group and a repository
        """

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
        Search the pkgName into the repository
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


    @dbus.service.method (BUSNAME, out_signature="as")
    def getInstalledList (self):
        """
        """

        return pacman_package_installed()


    @dbus.service.method (BUSNAME)
    def updateDatabase (self):
        """
        Met à jour les dépôts de paquets
        """

        for element in db_list:
            if repo_list[db_list.index(element)] != "local":
                self.sendSignal("update_db_name " + str(db_list.index(element)) + ":" + repo_list[db_list.index(element)])

                #~ pourcentage = float(index - 1) / float(len(repo_list) - 1)

                if pacman_db_update (1, element) == -1:
                    self.sendSignal("cant_update_pacmang2")
                    #~ pacman_print_error()

        return True


    @dbus.service.method (BUSNAME)
    def cleanCache (self):
        """
        Nettoye le cache de pacman-g2
        """

        self.sendSignal("clean_cache")
        pacman_sync_cleancache()
        self.sendSignal("done")


    @dbus.service.method (BUSNAME, in_signature="su", out_signature="b")
    def removePackage (self, pkgName, removeDeps = 0):
        """
        Remove a package
        """

        self.sendSignal("remove_package")
        if not pkgName in self.searchInstalledPackage(pkgName):
            # This package is already installed
            return False

        pm_trans_flag = PM_TRANS_FLAG_NOCONFLICTS
        if removeDeps == 1:
            pm_trans_flag = PM_TRANS_FLAG_CASCADE

        self.sendSignal("pacman_trans_init")
        if pacman_trans_init(PM_TRANS_TYPE_REMOVE, pm_trans_flag, pacman_trans_cb_event(self.progressEvent), pacman_trans_cb_conv(self.transConv), pacman_trans_cb_progress(self.progressInstall)) == -1:
            return False

        self.sendSignal("add_target")
        if pacman_trans_addtarget(pkgName) == -1:
            return False

        data = PM_LIST()

        self.sendSignal("pacman_trans_prepare")
        if pacman_trans_prepare(data) == -1:
            if pacman_get_pm_error() == pacman_c_long_to_int(PM_ERR_UNSATISFIED_DEPS):
                liste = []
                index = pacman_list_first(data)
                while index != 0:
                    paquet = pacman_list_getdata(index)
                    nom = pointer_to_string(pacman_dep_getinfo(paquet, PM_DEP_NAME))
                    liste.append(nom)
                    index = pacman_list_next(index)

                #~ reponse = self.fenetreQuestion("DEBUG", element + " est requis par : " + str(liste) + "\nSouhaitez-vous continuer ?")
                #~ if reponse == False:
                    #~ pacman_trans_release()
                    #~ return False

                self.sendSignal("pacman_trans_release")
                pacman_trans_release()

                self.sendSignal("pacman_remove_pkg")
                pacman_remove_pkg(pkgName, 1)
                return True
            else:
                return False

        self.sendSignal("pacman_trans_commit")
        if pacman_trans_commit(data) == -1:
            return False

        pacman_trans_release()
        self.sendSignal("done")

        return True


    @dbus.service.method (BUSNAME)
    def closeDeamon (self):
        self.closePacman()
        loop.quit()


    def progressInstall (self, *args):
        """
        """

        index = 1
        pourcent = 0
        event = 0
        compte = 0

        texte = ""

        for arg in args:
            if index == 1 and arg != None:
                event = arg
            elif index == 3 and arg != None:
                pourcent = arg
            elif index == 4 and arg != None:
                compte = arg
            else:
                pass

            index += 1

        if event == PM_TRANS_PROGRESS_ADD_START:
            if compte > 1:
                self.sendSignal("Installing packages...")
            else:
                self.sendSignal("Installing package...")
        elif event == PM_TRANS_PROGRESS_UPGRADE_START:
            if compte > 1:
                self.sendSignal("Upgrading packages...")
            else:
                self.sendSignal("Upgrading package...")
        elif event == PM_TRANS_PROGRESS_REMOVE_START:
            if compte > 1:
                self.sendSignal("Removing packages...")
            else:
                self.sendSignal("Removing package...")
        elif event == PM_TRANS_PROGRESS_CONFLICTS_START:
            if compte > 1:
                self.sendSignal("Checking packages for file conflicts...")
            else:
                self.sendSignal("Checking package for file conflicts...")
        else:
            pass


    def transConv (self, *args):
        """
        """

        index = 1

        for arg in args:
            if index == 1:
                event = arg
                self.sendSignal("Evenement : " + str(event))
            elif index == 2:
                pkg = arg
            elif index == 5:
                INTP = ctypes.POINTER(ctypes.c_int)
                reponse = ctypes.cast(arg, INTP)
            else:
                self.sendSignal("We must work on it -_-")

            index += 1

        #~ if event == PM_TRANS_CONV_LOCAL_UPTODATE:
            #~ if terminalQuestion (pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME))+" local version is up to date. Upgrade anyway? [Y/n]" ) == 1:
            #~ reponse[0] = 1
        #~ if event==PM_TRANS_CONV_LOCAL_NEWER:
            #~ if terminalQuestion (pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME))+" local version is newer. Upgrade anyway? [Y/n]" ) == 1:
            #~ reponse[0] = 1
        #~ if event==PM_TRANS_CONV_CORRUPTED_PKG:
            #~ if terminalQuestion ("Archive is corrupted. Do you want to delete it?") == 1:
            #~ reponse[0] = 1


    def progressEvent(self, *args):
        """
        Affiche l'evenement en cours
        """

        try:
            index = 1

            event = None
            data1 = None
            data2 = None

            for arg in args:
                if index == 1 and arg != None:
                    event = arg
                elif index == 2 and arg != None:
                    data1 = arg
                elif index == 3 and arg != None:
                    data2=arg
                else:
                    pass

                index += 1
        except :
            pass

        if event != PM_TRANS_EVT_RETRIEVE_START and event != PM_TRANS_EVT_RESOLVEDEPS_START and event != PM_TRANS_EVT_RESOLVEDEPS_DONE:
            telechargement = False

        texte = ""
        progres = 0.0

        if event == PM_TRANS_EVT_CHECKDEPS_START:
            self.sendSignal("checking_dependencies")
            progres = 1.0
        elif event == PM_TRANS_EVT_FILECONFLICTS_START:
            self.sendSignal("checking_file_conflicts")
            progres = 1.0
        elif event == PM_TRANS_EVT_RESOLVEDEPS_START:
            self.sendSignal("resolving_dependencies")
        elif event == PM_TRANS_EVT_INTERCONFLICTS_START:
            self.sendSignal("looking_interconflicts")
            progres = 1.0
        elif event == PM_TRANS_EVT_INTERCONFLICTS_DONE:
            self.sendSignal("looking_interconflicts_done")
        elif event == PM_TRANS_EVT_ADD_START:
            self.sendSignal("installing")
            progres = 1.0
        elif event == PM_TRANS_EVT_ADD_DONE:
            self.sendSignal("installing_done")
        elif event == PM_TRANS_EVT_UPGRADE_START:
            self.sendSignal("upgrading")
            progres = 1.0
        elif event == PM_TRANS_EVT_UPGRADE_DONE:
            self.sendSignal("upgrading_done")
        elif event == PM_TRANS_EVT_REMOVE_START:
            self.sendSignal("removing")
        elif event == PM_TRANS_EVT_REMOVE_DONE:
            self.sendSignal("removing_done")
        elif event == PM_TRANS_EVT_INTEGRITY_START:
            self.sendSignal("checking_integrity")
        elif event == PM_TRANS_EVT_INTEGRITY_DONE:
            self.sendSignal("checking_integrity_done")
        elif event == PM_TRANS_EVT_SCRIPTLET_INFO:
            self.sendSignal(pointer_to_string(data1))
        elif event == PM_TRANS_EVT_SCRIPTLET_START:
            self.sendSignal(str_data1)
        elif event == PM_TRANS_EVT_SCRIPTLET_DONE:
            self.sendSignal("scriptlet_done")
        elif event == PM_TRANS_EVT_RETRIEVE_START:
            self.sendSignal("retrieving_packages")
            progres = 1.0
            telechargement = True
        else :
            pass


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    gobject.threads_init()
    dbus.mainloop.glib.threads_init()
    _fpmd = FPMd()
    loop = gobject.MainLoop()
    loop.run()

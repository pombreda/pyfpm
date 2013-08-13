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

# Modules importation
import os, sys, dbus, dbus.service, dbus.mainloop.glib, gobject, time, datetime, ctypes

from libpacman import *

BUSNAME = 'org.frugalware.fpmd.Instance'
OBJPATH = '/org/frugalware/fpmd/Instance/object'
# Only simple pacman-g2 actions (search, getInfo, ...)
BUSNAME_INSTANCE = 'org.frugalware.fpmd.Instance'
# Actions like update, install or remove packages
BUSNAME_ACTIONS = 'org.frugalware.fpmd.Actions'

# Log file
LOGPATH = '/var/log/fpmd.log'
# Configuration file
CFG_FILE = "/etc/pacman-g2.conf"
# Pacman-g2 path
PM_ROOT = "/"
PM_DBPATH = "/var/lib/pacman-g2"
PM_CACHEDIR = "/var/cache/pacman-g2/pkg"
PM_HOOKSDIR = "/etc/pacman-g2/hooks"
PM_LOCK = "/tmp/pacman-g2.lck"
# Name of local repo
FW_LOCAL = "local"

# Dbus loop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
gobject.threads_init()
dbus.mainloop.glib.threads_init()

loop = gobject.MainLoop()


class FPMd (dbus.service.Object):
    """
    FPMd is a daemon for pacman-g2
    """

    def __init__ (self):
        """
        FPMd initialization
        """

        connection = dbus.service.BusName(BUSNAME, bus=dbus.SystemBus())
        dbus.service.Object.__init__(self, connection, OBJPATH)

        pacmanBus = dbus.SystemBus()

        try:
            proxy = pacmanBus.get_object(BUSNAME, OBJPATH, introspect=False)
        except dbus.DBusException:
            self.writeLog("DBus interface is not available")
            sys.exit("DBus interface is not available")

        pacmanBus.add_signal_receiver(self.listenSignal, dbus_interface=BUSNAME_INSTANCE, signal_name='sendSignal')

        self.startPacman()


    def startPacman (self):
        """
        Start pacman-g2 instance
        """

        try:
            if os.path.exists(PM_LOCK):
                sys.exit("An instance of pacman-g2 is already running.")

            if pacman_initialize(PM_ROOT) == -1:
                self.writeLog("Failed to initialize libpacman - " + str(pacman_print_error()))
                sys.exit()

            # Set some important pacman-g2 options
            if pacman_set_option (PM_OPT_LOGMASK, str(-1)) == -1:
                self.writeLog("Can't set option PM_OPT_LOGMASK - " + str(pacman_print_error()))
                sys.exit()

            # Get repos
            repo_list.append(FW_LOCAL)
            pacman_parse_config()

            for repo in repo_list:
                db = pacman_db_register(repo)
                db_list.append(db)

            self.writeLog("Fpmd have been run succesfully")
        except:
            self.writeLog("Failed to initialize libpacman")
            self.closeDaemon()


    def closePacman (self):
        """
        End pacman-g2 instance
        """

        pacman_finally()
        self.writeLog("Fpmd have been closed succesfully")


    @dbus.service.method (BUSNAME_INSTANCE)
    def closeDaemon (self):
        """
        Close FPMd
        """

        self.closePacman()
        loop.quit()


    def resetList (self):
        """
        Reset repos and database lists
        """

        repo_searchlist = []
        repo_list = []
        db_list = []


    @dbus.service.method (BUSNAME_INSTANCE)
    def resetPacman (self):
        """
        Reset pacman-g2 instance to update informations
        """

        #~ pacman_finally()

        repo_searchlist = []
        repo_list = []

        pacman_initialize(PM_ROOT)
        pacman_parse_config()

        db_list = []
        for repo in repo_list:
            db = pacman_db_register(repo)
            db_list.append(db)

        self.writeLog("Fpmd have been reset succesfully")


    @dbus.service.signal (BUSNAME_INSTANCE, signature='as')
    def sendSignal (self, value):
        """
        Send a value
        """
        pass


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='as')
    def emitSignal (self, text):
        """
        Emit a signal, very usefull when you doesn't want to
        use signal in your function
        """

        self.sendSignal(text)


    def listenSignal (self, texte):
        """
        Listen and apply
        """

        if texte[0] == "run":
            if texte[1] == "update":
                # User want to update repository database
                self.updateDatabase()
            if texte[1] == "clean":
                if len(texte[2]) > 0:
                    # We have specify a clean method
                    # 0 -> old package
                    # 1 -> all package
                    self.cleanCache(int(texte[2]))
                else:
                    # By default, we erase only old package
                    self.cleanCache(0)
            else:
                pass
        else:
            pass


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='su', out_signature='u')
    def getPackagePointer (self, pkgName, repo):
        """
        Get the package pointer
        """

        return pacman_db_readpkg(db_list[int(repo)], str(pkgName))


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='u', out_signature='a{sv}')
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

        # Add pkgDict2 into pkgDict
        pkgDict.update(pkgDict2)

        return pkgDict


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='su', out_signature='s')
    def getSha1sums (self, pkgName, repo):
        """
        Get the correct SHA1SUMS from frugalware/repos
        """

        pkg = pacman_db_readpkg(db_list[int(repo)], str(pkgName))

        return str(pacman_pkg_get_info(pkg, PM_PKG_SHA1SUM))


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='s', out_signature='as')
    def getFileFromPackage (self, pkgName):
        """
        Get the files list of the package
        """

        filesList = []

        pkg = pacman_db_readpkg(db_list[0], str(pkgName))

        files = pacman_pkg_getinfo(pkg, PM_PKG_FILES)
        while files != 0:
            filesList.append(pointer_to_string(pacman_list_getdata(files)))
            files = pacman_list_next(files)

        return filesList


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


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='ss', out_signature='b')
    def checkPackageInstalled (self, pkgName, pkgVersion):
        """
        Check if a package is installed or not
        """

        return pacman_package_intalled(str(pkgName), str(pkgVersion))


    @dbus.service.method (BUSNAME_INSTANCE)
    def getRepoList (self):
        """
        Get the repository list
        """

        return repo_list


    @dbus.service.method (BUSNAME_INSTANCE)
    def getDBList (self):
        """
        Get the repository list
        """

        return db_list


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='u', out_signature='as')
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


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='us', out_signature='au')
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


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='s', out_signature='a(si)')
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


    @dbus.service.method (BUSNAME_INSTANCE, in_signature='s')
    def searchInstalledPackage (self, pkgName):
        """
        Get the list of installed packages for a specific
        package name
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


    @dbus.service.method (BUSNAME_INSTANCE, out_signature="as")
    def getUpdateList (self):
        """
        Get the list of packages to update
        """

        stringList = []

        updateList = pacman_check_update()

        for element in updateList:
            stringList.append(pointer_to_string(element))

        return stringList


    @dbus.service.method (BUSNAME_INSTANCE, out_signature="as")
    def getInstalledList (self):
        """
        Get the list of installed packages
        """

        return pacman_package_installed()


    @dbus.service.method (BUSNAME_ACTIONS)
    def updateDatabase (self):
        """
        Update pacman-g2 database
        """

        self.emitSignal({"action", "start"})

        for element in db_list:
            # We don't use local repo for update
            if repo_list[db_list.index(element)] != FW_LOCAL:
                # Send the name of the repo
                self.emitSignal({"repo", str(repo_list[db_list.index(element)])})

                # Run update of this repo
                ret = pacman_db_update (1, element)
                if ret == -1:
                    # There is an error
                    self.emitSignal({"repo", str(repo_list[db_list.index(element)]) , "failed"})
                    self.writeLog("failed to update " + str(repo_list[db_list.index(element)]))
                elif ret == 1:
                    # Up-to-date
                    self.emitSignal({"repo", str(repo_list[db_list.index(element)]) , "uptodate"})
                else:
                    pass

        self.writeLog("Synchronizing package lists")

        self.emitSignal({"action", "end"})

        self.resetPacman()


    @dbus.service.method (BUSNAME_ACTIONS, in_signature="u")
    def cleanCache (self, mode):
        """
        Clean pacman-g2 cache
        """

        if pacman_sync_cleancache(mode) == -1:
            self.writeLog("Failed to clean the cache with mode " + str(mode))
        else:
            self.writeLog("Clean cache with mode " + str(mode))


    @dbus.service.method (BUSNAME_ACTIONS, in_signature="us")
    def installPackage(self, downloadOnly, pkgList):
        """
        Install a packages list or download them only
        """

        self.emitSignal({"action","start"})

        #FIXME
        #pacman_set_option (PM_OPT_DLCB, globals()["fpm_progress_update"]())

        for repo in repo_list:
            pacman_set_option(PM_OPT_DLFNM, repo)

        if downloadOnly == 1:
            flags = PM_TRANS_FLAG_DOWNLOADONLY
        else:
            flags = PM_TRANS_FLAG_NOCONFLICTS

        if pacman_trans_init(PM_TRANS_TYPE_SYNC, flags, pacman_trans_cb_event(self.progressEvent), pacman_trans_cb_conv(self.transConv), pacman_trans_cb_progress(self.progressInstall)) == -1:
            self.writeLog("Pacman_trans_init failed - " + str(pacman_get_error()))
            if pacman_trans_release() == -1:
                self.writeLog("Can't release transaction - " + str(pacman_get_error()))

            self.emitSignal({"action", "end"})
            return

        #~ for pkg in pkgList:
            #~ if pacman_trans_addtarget(pkg) == -1:
                #~ self.writeLog("Can't add " + str(pkg) + " - " + str(pacman_get_error()))
                #~ if pacman_trans_release() == -1:
                    #~ self.writeLog("Can't release transaction - " + str(pacman_get_error()))
                #~ return
        if pacman_trans_addtarget(str(pkgList)) == -1:
            self.writeLog("Can't add " + str(pkgList) + " - " + str(pacman_get_error()))
            if pacman_trans_release() == -1:
                self.writeLog("Can't release transaction - " + str(pacman_get_error()))

            self.emitSignal({"action", "end"})
            return

        data = PM_LIST()

        if pacman_trans_prepare(data) == -1:
            self.writeLog("Pacman_trans_prepare failed - " + str(pacman_get_error()))
            if pacman_trans_release() == -1:
                self.writeLog("Can't release transaction - " + str(pacman_get_error()))

            self.emitSignal({"action", "end"})
            return

        if pacman_trans_commit(data) == -1:
            if pacman_get_pm_error() == pacman_c_long_to_int(PM_ERR_FILE_CONFLICTS):
                text = "Conflicting Files\n"

                index = pacman_list_first(data)
                while index != 0:
                    cnf = pacman_list_getdata(index)
                    reason = pacman_conflict_getinfo(cnf,PM_CONFLICT_TYPE)

                    if reason == PM_CONFLICT_TYPE_FILE:
                        text = text + "Package : " + pointer_to_string(pacman_conflict_getinfo(cnf, PM_CONFLICT_TARGET)) + " already provide :\n"
                        text = text + pointer_to_string(pacman_conflict_getinfo(cnf, PM_CONFLICT_FILE)) + "\n"
                    index = pacman_list_next(index)

                self.emitSignal({"install", text})

            elif pacman_get_pm_error() == pacman_c_long_to_int(PM_ERR_PKG_CORRUPTED):
                """
                # TODO : find package corrupted
                i=pacman_list_first(data)
                while i != 0:
                    packages=pacman_list_getdata(i)
                    i=pacman_list_next(i)
                """
                self.emitSignal({"install", "Corrupted package(s)"})

            elif pacman_get_pm_error() == pacman_c_long_to_int(PM_ERR_RETRIEVE):
                self.emitSignal({"install", "Couldn't download package"})

            else:
                self.writeLog("Pacman_trans_commit failed - " + str(pacman_get_error()))

            if pacman_trans_release() == -1:
                self.writeLog("Can't release transaction - " + str(pacman_get_error()))

            self.emitSignal({"action", "end"})
            return

        if pacman_trans_release() == -1:
            self.writeLog("Can't release transaction - " + str(pacman_get_error()))

        if downloadOnly == 0:
            self.writeLog(str(pkgList) + " have been installed successfully.")

        self.emitSignal({"action", "end"})

        self.resetPacman()


    @dbus.service.method (BUSNAME_ACTIONS, in_signature="su", out_signature="b")
    def removePackage (self, pkgName, removeDeps = 0):
        """
        Remove a package
        """

        data = PM_LIST()

        # Check if package is installed
        self.sendSignal("remove_package")
        if not pkgName in self.searchInstalledPackage(pkgName):
            # This package is already installed
            return False

        # Use a specific flag
        pm_trans_flag = PM_TRANS_FLAG_NOCONFLICTS
        if removeDeps == 1:
            pm_trans_flag = PM_TRANS_FLAG_CASCADE

        # Step 1 : Create a new transaction
        self.sendSignal("pacman_trans_init")
        if pacman_trans_init(PM_TRANS_TYPE_REMOVE, pm_trans_flag, pacman_trans_cb_event(self.progressEvent), pacman_trans_cb_conv(self.transConv), pacman_trans_cb_progress(self.progressInstall)) == -1:
            return False

        # Add target to it
        self.sendSignal("add_target")
        if pacman_trans_addtarget(pkgName) == -1:
            pacman_trans_release()
            return False

        # Step 2 : Prepare the transaction based on its type, targets and flags
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
                pacman_trans_release()
                return False

        # Step 3 : Actually perform the removal
        self.sendSignal("pacman_trans_commit")
        if pacman_trans_commit(data) == -1:
            pacman_trans_release()
            return False

        # Step 4 : Release transaction resources
        pacman_trans_release()
        self.sendSignal("done")

        return True


    @staticmethod
    def progressInstall (event, package, percent, count, remaining):
        """
        Progress of package transaction
        """

        if package == None:
            return
        if percent < 0 or percent > 100:
            return

        if event == PM_TRANS_PROGRESS_ADD_START:
            if count > 1:
                emitSignal({"progress", "Installing packages..."})
            else:
                emitSignal({"progress", "Installing package..."})
        elif event == PM_TRANS_PROGRESS_UPGRADE_START:
            if count > 1:
                emitSignal({"progress", "Upgrading packages..."})
            else:
                emitSignal({"progress", "Upgrading package..."})
        elif event == PM_TRANS_PROGRESS_REMOVE_START:
            if count > 1:
                emitSignal({"progress", "Removing packages..."})
            else:
                emitSignal({"progress", "Removing package..."})
        elif event == PM_TRANS_PROGRESS_CONFLICTS_START:
            if count > 1:
                emitSignal({"progress", "Checking packages for file conflicts..."})
            else:
                emitSignal({"progress", "Checking package for file conflicts..."})
        else:
            pass

        self.emitSignal({"percent",str(percent)})


    @staticmethod
    def transConv (event, data1, data2, data3, response):
        """
        Requests from pacman-g2
        """

        # TODO:
        # Faire en sorte d'envoyer un signal et d'attendre la réponse
        # de l'utilisateur
        if event == PM_TRANS_CONV_LOCAL_UPTODATE:
            writeLog(str(pacman_pkg_getinfo(data1, PM_PKG_NAME)) + " local version is up to date.")
            response[0] = 0
        if event==PM_TRANS_CONV_LOCAL_NEWER:
            writeLog(str(pacman_pkg_getinfo(data1, PM_PKG_NAME)) + " local version is newer.")
            response[0] = 0
        if event==PM_TRANS_CONV_CORRUPTED_PKG:
            writeLog("Archive is corrupted")
            response[0] = 1

        return


    @staticmethod
    def progressEvent(event, data1, data2):
        """
        Get actual event
        """

        if data1 == None:
            return

        if event == PM_TRANS_EVT_CHECKDEPS_START:
            emitSignal({"event", "Checking dependencies"})
        elif event == PM_TRANS_EVT_FILECONFLICTS_START:
            emitSignal({"event", "Checking for file conflicts"})
        elif event == PM_TRANS_EVT_RESOLVEDEPS_START:
            emitSignal({"event", "Resolving dependencies"})
        elif event == PM_TRANS_EVT_INTERCONFLICTS_START:
            emitSignal({"event", "looking for inter-conflicts"})
        elif event == PM_TRANS_EVT_INTERCONFLICTS_DONE:
            emitSignal({"event", "Looking for inter-conflicts done"})
        elif event == PM_TRANS_EVT_ADD_START:
            emitSignal({"event", "Installing"})
        elif event == PM_TRANS_EVT_ADD_DONE:
            emitSignal({"event", "Installing done"})
        elif event == PM_TRANS_EVT_UPGRADE_START:
            emitSignal({"event", "Upgrading"})
        elif event == PM_TRANS_EVT_UPGRADE_DONE:
            emitSignal({"event", "Upgrading done"})
        elif event == PM_TRANS_EVT_REMOVE_START:
            emitSignal({"event", "Removing"})
        elif event == PM_TRANS_EVT_REMOVE_DONE:
            emitSignal({"event", "Removing done"})
        elif event == PM_TRANS_EVT_INTEGRITY_START:
            emitSignal({"event", "Checking integrity"})
        elif event == PM_TRANS_EVT_INTEGRITY_DONE:
            emitSignal({"event", "Checking integrity done"})
        elif event == PM_TRANS_EVT_SCRIPTLET_INFO:
            emitSignal({"event", pointer_to_string(data1)})
        elif event == PM_TRANS_EVT_SCRIPTLET_START:
            emitSignal({"event", pointer_to_string(data1)})
        elif event == PM_TRANS_EVT_SCRIPTLET_DONE:
            emitSignal({"event", "Scriptlet done"})
        elif event == PM_TRANS_EVT_RETRIEVE_START:
            emitSignal({"event", "Retrieving packages"})
        else:
            return


    def writeLog (self, text):
        """
        Write an entry into log
        """

        date = datetime.datetime.today().strftime("[%D %H:%M] ")

        if os.path.exists(LOGPATH):
            file = open(LOGPATH, "a")
            file.write("\n" + str(date) + str(text))
            file.close()
        else:
            file = open(LOGPATH, "w")
            file.write(str(date) + "First run of fpmd\n")
            file.close()
            self.writeLog(text)


if __name__ == '__main__':

    _fpmd = FPMd()

    loop.run()

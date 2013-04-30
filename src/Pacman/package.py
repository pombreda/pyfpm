#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions relatives au gestionnaire de paquet
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys, string, time

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pygtk_not_found")

from libpacman import *
from Misc import lang

# Initialisation des modules
fctLang = lang.Lang()

modeDebug = True


class Package (object):
    def startPacman (self):
        """
        Vérifie qu'une instance de pacman-g2 n'est pas en cours
        """

        if os.path.exists(PM_LOCK):
            sys.exit(fctLang.translate("pacman_already_run"))


    def initPacman (self):
        """
        Initialise pacman-g2 pour permettre d'être utilisé
        """

        self.printDebug("INFO", fctLang.translate("init_pacman"))
        pacman_init()
        self.printDebug("INFO", fctLang.translate("init_db"))
        pacman_init_database()
        self.printDebug("INFO", fctLang.translate("register_db"))
        pacman_register_all_database()


    def closePacman (self):
        """
        Termine l'instance de pacman-g2
        """

        self.printDebug("INFO", fctLang.translate("close_pacman"))
        pacman_finally()


    def cleanCache (self):
        """
        Nettoye le cache de pacman-g2
        """

        self.printDebug("INFO", fctLang.translate("clean_cache"))
        pacman_sync_cleancache()


    def updateDatabase (self, interface):
        """
        Met à jour les dépôts de paquets
        """

        self.printDebug("INFO", fctLang.translate("update_db"))
        self.closePacman()
        self.initPacman()

        interface.changeLabel(fctLang.translate("update_db"))
        interface.refreshWindow()

        index = 0
        for element in db_list:
            if index != 0:
                self.printDebug("DEBUG", fctLang.translate("update_db_name") + " " + str(index) + ":" + repo_list[index])

                pourcentage = float(index - 1) / float(len(repo_list) - 1)
                interface.changeProgressbar(fctLang.translate("update_db_name") + " " + repo_list[index], float(pourcentage))
                valeur = pacman_db_update (1, element)
                if valeur == -1:
                    self.printDebug("ERROR", "Can't update pacman-g2")
                    pacman_print_error()
            index += 1
            time.sleep(0.2)

        interface.changeProgressbar(fctLang.translate("update_db_done"), 1)
        interface.refreshWindow()


    def runPacman (self, interface, listeInstallationPacman, listeSuppressionPacman):
        """
        Installation et désinstallation de paquet

        Première étape : Désinstallation des paquets sélectionnés
        Deuxième étape : Installation des paquets sélectionnés
        """

        self.printDebug ("DEBUG", "runPacman")

        if listeSuppressionPacman != "None":
            listeSuppression = listeSuppressionPacman.split(",")
        else:
            listeSuppression = []

        if listeInstallationPacman != "None":
            listeInstallation = listeInstallationPacman.split(",")
        else:
            listeInstallation = []


        if len(listeSuppression) > 0:
            self.closePacman()
            self.initPacman()
            self.printDebug("DEBUG", "Suppression de paquets")
            self.removePackage(listeSuppression)

        if len(listeInstallation) > 0:
            self.closePacman()
            self.initPacman()
            self.printDebug("DEBUG", "Installation de paquets")
            self.installPackage(interface, listeInstallation)


    def removePackage (self, listePaquets, enleverDependances = 0):
        """
        Fonction pour supprimer des paquets
        """

        self.printDebug ("DEBUG", "removePackage")

        for element in listePaquets:
            if not element in self.getInstalledPackage(element):
                # Dans le cas où le paquet ne serait pas installé
                self.printDebug ("ERROR", "Paquet non installé")
                return -1

            pm_trans_flag = PM_TRANS_FLAG_NOCONFLICTS

            if enleverDependances == 1:
                self.printDebug ("DEBUG", "Suppression des paquets en cascade")
                pm_trans_flag = PM_TRANS_FLAG_CASCADE

            if pacman_trans_init(PM_TRANS_TYPE_REMOVE, pm_trans_flag, pacman_trans_cb_event(fpm_progress_event), pacman_trans_cb_conv(fpm_trans_conv), pacman_trans_cb_progress(fpm_progress_install)) == -1:
                self.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            self.printDebug("DEBUG", "Initialisation de la transaction")

            if pacman_trans_addtarget(element) == -1:
                self.printDebug ("ERROR", "Impossible de désinstaller " + element)
                self.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            self.printDebug("DEBUG", element + " ajouté")

            data = PM_LIST()
            self.printDebug ("DEBUG", "Vérification des dépendances inverses")

            if pacman_trans_prepare(data) == -1:
                if pacman_get_pm_error() == pacman_c_long_to_int(PM_ERR_UNSATISFIED_DEPS):
                    liste = []
                    index = pacman_list_first(data)
                    while index != 0:
                        paquet = pacman_list_getdata(index)
                        nom = pointer_to_string(pacman_dep_getinfo(paquet, PM_DEP_NAME))
                        liste.append(nom)
                        index = pacman_list_next(index)

                    self.printDebug ("DEBUG", element + " est requis par : " + str(liste))

                    reponse = self.fenetreQuestion("DEBUG", element + " est requis par : " + str(liste) + "\nSouhaitez-vous continuer ?")
                    if reponse == False:
                        pacman_trans_release()
                        return -1

                    pacman_trans_release()

                    # Redémarrer la transaction

                    return pacman_remove_pkg(element, 1)
                else:
                    self.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                    return -1
            self.printDebug ("DEBUG", "Transaction préparée avec succès")

            if pacman_trans_commit(data) == -1:
                self.printDebug ("ERROR " + str(pacman.pacman_geterror()), pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            self.printDebug ("DEBUG", "Suppression de " + element)

            pacman_trans_release()


    def installPackage (self, interface, listePaquets):
        """
        Fonction pour installer des paquets
        """

        self.printDebug ("DEBUG", "installPackage")

        interface.changeLabel(fctLang.translate("install_pkg"))
        interface.refresh()

        for element in repo_list:
                pacman_set_option(PM_OPT_DLFNM, element)

        pm_trans = PM_TRANS_TYPE_SYNC

        #~ flags = PM_TRANS_FLAG_NOCONFLICTS
        flags = PM_TRANS_FLAG_DOWNLOADONLY

        progres = 1.0

        if pacman_trans_init(pm_trans, flags, pacman_trans_cb_event(self.progressEvent), pacman_trans_cb_conv(self.progressPackage), pacman_trans_cb_progress(self.progressInstall)) == -1:
            self.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_init : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
            return -1
        else:
            self.printDebug ("DEBUG", "Initialisation complète")
            interface.changeProgressbar("Initialisation complète", progres)

        for element in listePaquets:
            if pacman_trans_addtarget(element) == -1:
                self.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_addtarget : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            else:
                self.printDebug ("DEBUG", element + " ajouté")
                interface.changeProgressbar(element + " ajouté", progres)

        self.printDebug ("DEBUG", "Récupération des dépendances")
        interface.changeProgressbar("Récupération des dépendances", progres)

        data = PM_LIST()
        try:
            if pacman_trans_prepare(data) == -1:
                self.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_prepare : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            else:
                self.printDebug ("DEBUG", "Téléchargement des paquets")
                interface.changeProgressbar("Téléchargement des paquets", progres)

            if pacman_trans_commit(data) == -1:
                self.printDebug ("ERROR " + str(pacman.pacman_geterror()), "trans_commit : " + pointer_to_string(pacman.pacman_strerror(pacman.pacman_geterror())))
                return -1
            else:
                self.printDebug ("DEBUG", "Installation des paquets")
                interface.changeProgressbar("Installation des paquets", progres)
        except:
            self.printDebug ("ERROR", "pacman_trans_prepare")

        pacman_trans_release()
        return 1


    def progressInstall (self, *args):
        """
        """

        printDebug ("DEBUG", "Progression de l'installation")

        from Pacman import package
        interface = package.fenetreInstallation()

        index = 1
        pourcent = 0
        event = 0
        compte = 0

        texte = ""
        progres = 0

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

        try :
            progres = float(float(pourcent)/100)
            printDebug ("DEBUG", progres)
        except :
            pass

        if event == PM_TRANS_PROGRESS_ADD_START:
            if compte > 1:
                texte = "Installing packages..."
            else:
                texte = "Installing package..."
        elif event == PM_TRANS_PROGRESS_UPGRADE_START:
            if compte > 1:
                texte = "Upgrading packages..."
            else:
                texte = "Upgrading package..."
        elif event == PM_TRANS_PROGRESS_REMOVE_START:
            if compte > 1:
                texte = "Removing packages..."
            else:
                texte = "Removing package..."
        elif event == PM_TRANS_PROGRESS_CONFLICTS_START:
            if compte > 1:
                texte = "Checking packages for file conflicts..."
            else:
                texte = "Checking package for file conflicts..."
        else:
            pass

        if texte != "":
            printDebug ("DEBUG", texte)

        self.printDebug ("DEBUG", "fpm_progress_install finish")

        interface.changeProgressbar(texte, progres)


    def progressPackage (self, *args):
        printDebug ("DEBUG", "Progression de la transaction")
        index = 1

        for arg in args:
            if index == 1:
                event = arg
                self.printDebug ("DEBUG", "Evenement : " + str(event))
            elif index == 2:
                pkg = arg
            elif index == 5:
                INTP = ctypes.POINTER(ctypes.c_int)
                reponse = ctypes.cast(arg, INTP)
            else:
                self.printDebug ("DEBUG", "Pas implanté :)")

            index += 1

        if event == PM_TRANS_CONV_LOCAL_UPTODATE:
            #~ if terminalQuestion (pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME))+" local version is up to date. Upgrade anyway? [Y/n]" ) == 1:
            reponse[0] = 1
        if event==PM_TRANS_CONV_LOCAL_NEWER:
            #~ if terminalQuestion (pointer_to_string(pacman_pkg_getinfo(pkg, PM_PKG_NAME))+" local version is newer. Upgrade anyway? [Y/n]" ) == 1:
            reponse[0] = 1
        if event==PM_TRANS_CONV_CORRUPTED_PKG:
            #~ if terminalQuestion ("Archive is corrupted. Do you want to delete it?") == 1:
            reponse[0] = 1


    def progressEvent(self, *args):
        """
        Affiche l'evenement en cours
        """

        self.printDebug ("DEBUG", "Evenement")

        from Pacman import package
        interface = package.fenetreInstallation()

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

            self.printDebug ("DEBUG", event)
            self.printDebug ("DEBUG", data1)
            self.printDebug ("DEBUG", data2)
        except :
            pass


        if event != PM_TRANS_EVT_RETRIEVE_START and event != PM_TRANS_EVT_RESOLVEDEPS_START and event != PM_TRANS_EVT_RESOLVEDEPS_DONE:
            telechargement = False

        texte = ""
        progres = 0.0

        if event == PM_TRANS_EVT_CHECKDEPS_START:
            texte = fctLang.translate("checking_dependencies")
            progres = 1.0
        elif event == PM_TRANS_EVT_FILECONFLICTS_START:
            texte = fctLang.translate("checking_file_conflicts")
            progres = 1.0
        elif event == PM_TRANS_EVT_RESOLVEDEPS_START:
            texte = fctLang.translate("resolving_dependencies")
        elif event == PM_TRANS_EVT_INTERCONFLICTS_START:
            texte = fctLang.translate("looking_interconflicts")
            progres = 1.0
        elif event == PM_TRANS_EVT_INTERCONFLICTS_DONE:
            texte = fctLang.translate("looking_interconflicts_done")
        elif event == PM_TRANS_EVT_ADD_START:
            texte = fctLang.translate("installing")
            progres = 1.0
        elif event == PM_TRANS_EVT_ADD_DONE:
            texte = fctLang.translate("installing_done")
        elif event == PM_TRANS_EVT_UPGRADE_START:
            texte = fctLang.translate("upgrading")
            progres = 1.0
        elif event == PM_TRANS_EVT_UPGRADE_DONE:
            texte = fctLang.translate("upgrading_done")
        elif event == PM_TRANS_EVT_REMOVE_START:
            texte = fctLang.translate("removing")
        elif event == PM_TRANS_EVT_REMOVE_DONE:
            texte = fctLang.translate("removing_done")
        elif event == PM_TRANS_EVT_INTEGRITY_START:
            texte = fctLang.translate("checking_integrity")
        elif event == PM_TRANS_EVT_INTEGRITY_DONE:
            texte = fctLang.translate("checking_integrity_done")
        elif event == PM_TRANS_EVT_SCRIPTLET_INFO:
            texte = pointer_to_string(data1)
        elif event == PM_TRANS_EVT_SCRIPTLET_START:
            texte = str_data1
        elif event == PM_TRANS_EVT_SCRIPTLET_DONE:
            texte = fctLang.translate("scriptlet_done")
        elif event == PM_TRANS_EVT_RETRIEVE_START:
            texte = fctLang.translate("retrieving_packages")
            progres = 1.0
            telechargement = True
        else :
            pass

        self.printDebug ("DEBUG", texte)
        self.printDebug ("DEBUG", "fpm_progress_event finish")

        interface.changeProgressbar(texte, progres)


    def getInstalledPackage (self, nomPaquet):
        """
        Recupère la liste des paquets installés
        """

        liste = []

        pacman_set_option(PM_OPT_NEEDLES, nomPaquet)
        paquet = pacman_db_search(db_list[0])

        listePaquets = pacman_pkg_getinfo(paquet, PM_PKG_NAME)

        while listePaquets != 0:
            element = pointer_to_string(pacman_list_getdata(listePaquets))

            liste.append(element)

            listePaquets = pacman_list_next(listePaquets)

        return liste


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


    def searchPackage (self, nomPaquet):
        """
        Chercher les paquets correspondant à la recherche dans le dépôt sélectionné
        """

        listePaquetsTrouves = []

        for element in repo_list:
            if repo_list.index(element) > 0:
                pacman_set_option(PM_OPT_NEEDLES, nomPaquet)
                listePaquets = pacman_db_search(db_list[repo_list.index(element)])

                if listePaquets != None:
                    i = pacman_list_first(listePaquets)

                    while i != 0:
                        paquet = pacman_db_readpkg(db_list[repo_list.index(element)], pacman_list_getdata(i))

                        listePaquetsTrouves.append([element, paquet])

                        i = pacman_list_next(i)

        return listePaquetsTrouves


    def terminalQuestion (question):
        print (question)
        reponse = raw_input()
        if reponse == "y":
            return 1
        return -1


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


    def fenetreQuestion (self, titre, texte):
        """
        Affiche une fenêtre d'information
        """

        fenetre = gtk.Dialog(titre, None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
        texteConfirmation = gtk.Label(texte)

        fenetre.set_default_response(gtk.RESPONSE_OK)

        fenetre.vbox.pack_start(texteConfirmation)

        fenetre.show_all()
        choix = fenetre.run()
        reponse = False
        if choix == gtk.RESPONSE_OK:
            reponse = True

        fenetre.destroy()

        return reponse


class InstallWindow (object):
    """
    Fenêtre d'installation
    """

    def __init__ (self):
        """
        Initialisation de la fenêtre
        """

        self.fenetre = gtk.Window()
        self.grille = gtk.Table(1,2)

        self.informations = gtk.Label("")
        self.barreProgres = gtk.ProgressBar()

        self.fenetre.set_title(fctLang.translate("pacman_title"))
        self.fenetre.set_size_request(300,50)
        self.fenetre.set_resizable(True)
        self.fenetre.set_position(gtk.WIN_POS_CENTER)
        self.fenetre.set_decorated(False)
        self.fenetre.set_skip_taskbar_hint(True)

        self.grille.attach(self.informations, 0, 1, 0, 1, yoptions=gtk.FILL)
        self.grille.attach(self.barreProgres, 0, 1, 1, 2, yoptions=gtk.FILL)
        self.grille.set_border_width(4)

        self.fenetre.add(self.grille)

        self.fenetre.show_all()
        self.refreshWindow()


    def runWindow (self, mode, arguments=None):

        Pkg = Package()

        if mode == "updatedb":
            Pkg.updateDatabase(self)
        elif mode == "cleancache":
            Pkg.cleanCache()
        elif mode == "install":
            Pkg.runPacman(self, arguments[0], arguments[1])

        self.closeWindow()


    def closeWindow (self):
        """
        Permet de fermer la fenetre d'installation
        """

        self.fenetre.destroy()


    def changeLabel (self, texte):
        """
        Changer le contenu du label
        """

        self.informations.set_text(texte)
        self.refreshWindow()


    def changeProgressbar (self, texte, valeur):
        """
        Mettre à jour la barre de progres
        """

        self.barreProgres.set_text(texte)

        self.barreProgres.set_fraction(valeur)
        self.refreshWindow()


    def refreshWindow (self):
        """
        Rafraichit l'self quand des changements ont lieux
        """

        try :
            while gtk.events_pending():
                gtk.main_iteration_do(False)
        except:
            pass


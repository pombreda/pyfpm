#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Interface affichant la progression en cours des actions
#       de pacman-g2
#
# ----------------------------------------------------------------------

# Importation des modules
import sys, gettext, dbus, time, gobject

# Gestion de la boucle dbus - Merci wicd
if getattr(dbus, "version", (0, 0, 0)) < (0, 80, 0):
    import dbus.glib
else:
    from dbus.mainloop.glib import DBusGMainLoop
    DBusGMainLoop(set_as_default=True)

# Récupération de la traduction
gettext.bindtextdomain('pyfpm', 'lang')
gettext.textdomain('pyfpm')
_ = gettext.gettext

try:
    import pygtk, gtk
except ImportError:
    sys.exit(_("pygtk was not found"))

from Functions import package, utils

# Initialisation des modules
Package = package.Package()

# Noms dbus
BUSNAME = 'org.frugalware.fpmd.Instance'
OBJPATH = '/org/frugalware/fpmd/Instance/object'


class Pacman (object):

    def __init__ (self, titre, mode):
        """
        Initialisation de la fenêtre de progression
        """

        utils.printDebug("DEBUG", "Lancement de dbus")
        pacmanBus = dbus.SystemBus()

        try:
            proxy = pacmanBus.get_object(BUSNAME, OBJPATH, introspect=False)
        except dbus.DBusException:
            sys.exit(_("DBus interface is not available"))

        # Fonction interne a Fpmd
        self.fpmd_emitSignal = proxy.get_dbus_method('emitSignal', 'org.frugalware.fpmd.deamon')

        # ------------------------------------------------------------------
        #       Fenetre
        # ------------------------------------------------------------------

        self.fenetre = gtk.Window()
        self.grille = gtk.Table(2,3)

        # ------------------------------------------------------------------
        #       Informations
        # ------------------------------------------------------------------

        self.image = gtk.Image()
        self.labelAction = gtk.Label("")
        self.progressionInfo = gtk.ProgressBar()
        self.labelInfo = gtk.Label("")
        self.boutons = gtk.HButtonBox()
        self.boutonClose = gtk.Button(stock=gtk.STOCK_CLOSE)

        self.titre = titre
        self.mode = mode
        self.info = {"action": "", "state": False, "data": "", "event": ""}
        self.end = False


    def mainWindow (self):
        """
        Fenêtre principale
        """

        # ------------------------------------------------------------------
        #       Fenetre
        # ------------------------------------------------------------------

        self.fenetre.set_title(self.titre)
        self.fenetre.set_position(gtk.WIN_POS_CENTER)
        self.fenetre.set_skip_taskbar_hint(True)
        self.fenetre.set_decorated(False)


        # ------------------------------------------------------------------
        #       Informations
        # ------------------------------------------------------------------

        # Titre
        self.labelAction.set_use_markup(True)
        self.labelAction.set_markup_with_mnemonic("<big><b>" + self.titre + "</b></big>")
        self.labelAction.set_alignment(0.025,0)

        # Image
        logo = gtk.gdk.pixbuf_new_from_file("data/icons/48x48/aptdaemon-update-cache.png")
        self.image.set_from_pixbuf(logo)

        # Barre de progression générale
        self.progressionInfo.set_size_request(500, 26)
        self.progressionInfo.set_fraction(0.0)

        # Info
        self.labelInfo.set_use_markup(True)
        self.labelInfo.set_alignment(0,0)

        # Boutons
        self.boutons.set_layout(gtk.BUTTONBOX_END)
        #~ self.boutons.add(self.boutonTmp)
        self.boutons.add(self.boutonClose)
        self.boutonClose.set_sensitive(False)

        #~ self.boutonTmp.connect('clicked', self.runFunction)
        self.boutonClose.connect('clicked', self.quitWindow)

        self.grille.attach(self.image, 0, 1, 0, 3, yoptions=gtk.FILL)
        self.grille.attach(self.labelAction, 1, 2, 0, 1, yoptions=gtk.FILL)
        self.grille.attach(self.progressionInfo, 1, 2, 1, 2, xoptions=gtk.FILL, yoptions=gtk.FILL)
        self.grille.attach(self.labelInfo, 1, 2, 2, 3, xoptions=gtk.FILL, yoptions=gtk.FILL)
        self.grille.attach(self.boutons, 0, 2, 3, 4, xoptions=gtk.FILL, yoptions=gtk.FILL)
        self.grille.set_border_width(10)
        self.grille.set_col_spacings(10)
        self.grille.set_row_spacings(10)

        #~ self.fenetre.vbox.pack_start(self.grille, expand=False)
        self.fenetre.add(self.grille)
        self.fenetre.show_all()
        self.refresh()

        # Envoie un signal à FPMd demandant l'execution de self.mode
        utils.printDebug("DEBUG", "Envoie du signal " + str(self.mode))
        Package.emitSignal(["run", self.mode])
        self.refresh()

        utils.printDebug("DEBUG", "Lancement de l'interface")

        # On récupère les informations
        self.info = Package.getActionInformations()

        task = self.getInformationsFromAction()
        gobject.idle_add(task.next)

        self.getCloseButton()


    def quitWindow (self, *args):
        """
        Termine l'instance
        """

        self.fenetre.destroy()


    def refresh (self):
        """
        Met à jour la fenêtre
        """

        while gtk.events_pending():
            gtk.main_iteration()


    def getInformationsFromAction (self):
        """
        Récupération des informations concernant l'action
        """

        # On reste dans la boucle tant que l'action n'est pas terminée
        while not self.end:
            print str(self.mode)

            if self.mode == "update":
            # Lancement de la mise à jour des dépôts
                if len(self.info.get("event")) > 0:
                    if self.info.get("event") == "failed":
                        # Erreur de connexion
                        self.writeEntry(_("Cannot connect to %s") % str(self.info.get("data")))
                    elif self.info.get("event") == "uptodate":
                        # Le dépôt est déjà à jour
                        self.writeEntry(_("%s is up-to-date") % str(self.info.get("data")))
                else:
                    # Synchronisation du dépôt
                    self.writeEntry(_("Synchronizing package databases..."), str(self.info.get("data")) + "...")

            # Dés que l'action est terminé on peut quitter la boucle
            if not self.info.get("state"):
                self.writeEntry("Complete")
                self.end = True
            else:
                self.info = Package.getActionInformations()
                self.refresh()
                yield True

        yield False


    def getCloseButton (self):
        """
        Termine la boucle et donne accès au bouton Fermer
        """

        self.boutonClose.set_sensitive(True)


    def writeEntry (self, titre, texte=""):
        """
        Ecris une entrée dans la zone d'informations
        """

        self.labelInfo.set_markup_with_mnemonic("<big><b>" + titre + "</b></big>\n" + texte + "")
        self.refresh()


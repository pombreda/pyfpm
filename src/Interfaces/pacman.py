#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Interface affichant la progression en cours des actions
#       de pacman-g2
#
# ----------------------------------------------------------------------

# Importation des modules
import sys, gettext, dbus, time

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

# Noms dbus
BUSNAME = 'org.frugalware.fpmd.deamon'
OBJPATH = '/org/frugalware/fpmd/deamon/object'


class Pacman (object):

    def __init__ (self, titre, mode):
        """
        Initialisation de la fenêtre de progression
        """

        self.printDebug("DEBUG", "Lancement de dbus")
        pacmanBus = dbus.SystemBus()

        try:
            proxy = pacmanBus.get_object('org.frugalware.fpmd.deamon','/org/frugalware/fpmd/deamon/object', introspect=False)
        except dbus.DBusException:
            sys.exit(_("DBus interface is not available"))

        # Fonction interne a Fpmd
        self.fpmd_emitSignal = proxy.get_dbus_method('emitSignal', 'org.frugalware.fpmd.deamon')

        # Assignation des signaux
        self.printDebug("DEBUG", "Récupération des signaux")
        pacmanBus.add_signal_receiver(self.signal, dbus_interface=BUSNAME, signal_name='sendSignal')

        # ------------------------------------------------------------------
        #       Fenetre
        # ------------------------------------------------------------------

        self.fenetre = gtk.Dialog("", None, gtk.DIALOG_MODAL)
        self.grille = gtk.Table(2,3)

        # ------------------------------------------------------------------
        #       Informations
        # ------------------------------------------------------------------

        self.image = gtk.Image()
        self.labelAction = gtk.Label("")
        self.progressionInfo = gtk.ProgressBar()
        self.labelInfo = gtk.Label("")
        self.boutons = gtk.HButtonBox()
        #~ self.boutonTmp = gtk.Button(stock=gtk.STOCK_NEW)
        self.boutonClose = gtk.Button(stock=gtk.STOCK_CLOSE)

        self.titre = titre
        self.mode = mode


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
        logo = gtk.gdk.pixbuf_new_from_file("/usr/share/icons/Frugalware/status/48/aptdaemon-update-cache.png")
        self.image.set_from_pixbuf(logo)

        # Barre de progression générale
        self.progressionInfo.set_size_request(500, 26)
        self.progressionInfo.set_fraction(0.4)

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

        self.fenetre.vbox.pack_start(self.grille, expand=False)
        self.fenetre.show_all()

        self.fpmd_emitSignal(["run", self.mode])

        self.printDebug("DEBUG", "Lancement de l'interface")
        self.fenetre.run()


    def quitWindow (self, *args):
        """
        Termine l'instance
        """

        self.fenetre.destroy()


    def signal (self, chaine):
        """
        Récupère le signal émis
        """

        print str(chaine)

        if self.mode == "update":
            # Lancement de la mise à jour des dépôts
            if chaine[0] == "repo":
                if chaine[1] == "-1":
                    # Erreur de connexion
                    self.writeEntry(_("Cannot connect to %s") % str(chaine[1]))
                    self.getCloseButton()
                else:
                    # Synchronisation du dépôt
                    self.writeEntry(_("Synchronizing package databases..."), str(chaine[1]))
            elif chaine[0] == "action" and chaine[1] == "end":
                # L'action est terminée
                self.writeEntry(_("Synchronizing package databases..."), _("Done"))
                self.getCloseButton()


    def getCloseButton (self):
        """
        Termine la boucle et donne accès au bouton Fermer
        """

        self.boutonClose.set_sensitive(True)


    def writeEntry (self, titre, texte):
        """
        Ecris une entrée dans la zone d'informations
        """

        self.labelInfo.set_markup_with_mnemonic("<big><b>" + titre + "</b></big>\n" + texte + "")


    def printDebug (self, typeErreur, erreur):
        """
        Affiche une sortie terminal
        """

        modeDebug = True

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


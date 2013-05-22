#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Interface affichant la progression en cours des actions
#       de pacman-g2
#
# ----------------------------------------------------------------------

# Importation des modules
import dbus, dbus.mainloop.glib, gobject

try:
    import pygtk, gtk
except ImportError:
    sys.exit(fctLang.translate("pygtk_not_found"))

from Misc import lang

# Initialisation des modules
Lang = lang.Lang()


class Pacman (object):

    def __init__ (self):
        """
        Initialisation de la fenêtre de progression
        """

        bus = dbus.SystemBus()

        proxy = self.bus.get_object('org.frugalware.fpmd.deamon','/org/frugalware/fpmd/deamon/object', introspect=False)
        proxy.connect_to_signal('sendSignal', self.signal, dbus_interface='org.frugalware.fpmd.deamon')

        bus.add_signal_receiver(self.signal, dbus_interface='org.frugalware.fpmd.deamon', signal_name='sendSignal')

        # ------------------------------------------------------------------
        #       Fenetre
        # ------------------------------------------------------------------

        self.fenetre = gtk.Window()
        self.grille = gtk.Table(1,4)

        # ------------------------------------------------------------------
        #       Informations
        # ------------------------------------------------------------------

        self.labelInfo = gtk.Label("")
        self.progressionInfo = gtk.ProgressBar()

        self.logInfo = gtk.TextView()

        self.boutonFermer = gtk.Button(Lang.translate("close"))


    def mainWindow (self, titre):
        """
        Fenêtre principale
        """

        # ------------------------------------------------------------------
        #       Fenetre
        # ------------------------------------------------------------------

        self.fenetre.set_title(Lang.translate(titre))
        self.fenetre.set_resizable(False)
        self.fenetre.set_position(gtk.WIN_POS_CENTER)

        self.fenetre.connect("destroy", gtk.main_quit)


        # ------------------------------------------------------------------
        #       Informations
        # ------------------------------------------------------------------

        self.logInfo.set_editable(False)
        self.logInfo.set_cursor_visible(False)

        self.grille.attach(self.labelInfo, 0, 2, 0, 1, yoptions=gtk.FILL)
        self.grille.attach(self.progressionInfo, 0, 2, 1, 2, yoptions=gtk.FILL)
        self.grille.attach(self.logInfo, 0, 2, 2, 3, yoptions=gtk.EXPAND)
        self.grille.attach(self.boutonFermer, 1, 2, 3, 4, xoptions=gtk.FILL, yoptions=gtk.FILL)

        self.fenetre.add(self.grille)
        self.fenetre.show_all()



    def runWindow (self):
        """
        Affiche l'interface
        """

        #~ gtk.main()


    def signal (self, chaine):
        """
        """

        if not chaine == "done":
            print str(chaine)
        else:
            loop.quit()


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    gobject.threads_init()
    dbus.mainloop.glib.threads_init()
    _pacman = Pacman()
    loop = gobject.MainLoop()
    loop.run()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions concernant les préférences de pyFPM
#
# ----------------------------------------------------------------------

# Importation des modules
import sys, pango, os, gettext

# Récupération de la traduction
gettext.bindtextdomain('pyfpm', 'lang')
gettext.textdomain('pyfpm')
_ = gettext.gettext

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pygtk was not found")

from Functions import config, files

# Initialisation des modules
Config = config.Config()
File = files.File()


class Preferences (object):
    """
    Gestion du fichier de configuration via une fenêtre
    """

    def runPreferences (self, widget, interface):
        """
        Fenêtre de gestion des préférences
        """

        fenetre = gtk.Dialog(_("Preferences"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_APPLY, gtk.RESPONSE_APPLY))

        onglets = gtk.Notebook()

        general = gtk.Label(_("General"))
        grilleGeneral = gtk.Table(1,2)
        self.miseajourDemarrage = gtk.CheckButton(_("Show update list when pyfpm start"))
        self.afficherGroupes = gtk.CheckButton(_("Use 'prohibate' groups"))

        cache = gtk.Label(_("Cache"))
        grilleCache = gtk.Table(1,2)
        self.cachesize = gtk.Label(_("Currently, the cache size is %s MB") % str(format(File.getFolderSize(os.path.expanduser('~') + "/.local/share/pyfpm/"), '.2f')))
        self.resetCache = gtk.Button(stock=gtk.STOCK_CLOSE, label=_("Clean cache folder"))

        fenetre.set_has_separator(False)
        fenetre.set_default_response(gtk.RESPONSE_OK)
        fenetre.set_resizable(True)
        fenetre.set_position(gtk.WIN_POS_CENTER)

        onglets.set_tab_pos(gtk.POS_LEFT)

        grilleGeneral.attach(self.miseajourDemarrage, 0, 1, 0, 1)
        grilleGeneral.attach(self.afficherGroupes, 0, 1, 1, 2)
        grilleGeneral.set_border_width(4)
        onglets.append_page(grilleGeneral, general)
        grilleCache.attach(self.cachesize, 0, 1, 0, 1)
        grilleCache.attach(self.resetCache, 0, 1, 1, 2)
        grilleCache.set_border_width(4)
        onglets.append_page(grilleCache, cache)

        self.fillCheckbox()

        fenetre.vbox.pack_start(onglets)

        fenetre.show_all()
        reponse = fenetre.run()

        if reponse == gtk.RESPONSE_APPLY:
            dico = {"startupdate" : Config.boolMinus(self.miseajourDemarrage.get_active()), \
                "useprohibategroups" : Config.boolMinus(self.afficherGroupes.get_active()), \
                "width" : Config.readConfig("screen", "width"), \
                "height" : Config.readConfig("screen", "height")}

            modificationInterface = False
            if Config.readConfig("pyfpm", "useprohibategroups") != Config.boolMinus(self.afficherGroupes.get_active()):
                modificationInterface = True

            Config.writeConfig(dico)

            if modificationInterface:
                interface.eraseInterface()
                interface.addRepos()

            interface.refresh()

        fenetre.destroy()


    def fillCheckbox (self):
        """
        Met les cases à cocher aux bonnes valeurs
        """

        self.miseajourDemarrage.set_active(Config.boolToInt(Config.readConfig("pyfpm", "startupdate")))
        self.afficherGroupes.set_active(Config.boolToInt(Config.readConfig("pyfpm", "useprohibategroups")))
        #~ self.modeDeveloppement.set_active(Config.boolToInt(Config.readConfig("pyfpm", "developmentmode")))

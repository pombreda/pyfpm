#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions concernant les préférences de pyFPM
#
# ----------------------------------------------------------------------

# Importation des modules
import sys, pango, os

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK introuvable")

from Misc import config, lang, files, events

# Initialisation des modules
Lang = lang.Lang()
Config = config.Config()
Event = events.Events()


class Preferences (object):
    """
    Gestion du fichier de configuration via une fenêtre
    """

    def runPreferences (self, widget, interface):
        """
        Fenêtre de gestion des préférences
        """

        fenetre = gtk.Dialog(Lang.translate("preferences_title"), None, gtk.DIALOG_MODAL, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_APPLY, gtk.RESPONSE_APPLY))

        onglets = gtk.Notebook()

        general = gtk.Label(Lang.translate("preferences_main"))
        grilleGeneral = gtk.Table(1,2)
        zoneGeneralLangue = gtk.Frame(Lang.translate("preferences_main"))
        generalLangue = gtk.Table(2,1)
        generalLangueLabel = gtk.Label(Lang.translate("language") + "*")
        generalLangueChoix = gtk.combo_box_new_text()
        zoneGeneralDivers = gtk.Frame(Lang.translate("misc"))
        grilleGeneralCocher = gtk.Table(1,2)
        self.miseajourDemarrage = gtk.CheckButton(Lang.translate("start_update"))
        self.afficherGroupes = gtk.CheckButton(Lang.translate("use_prohibate_groups"))
        self.modeDeveloppement = gtk.CheckButton(Lang.translate("development_mode") + "*")
        generalLangueAsterix = gtk.Label(" *" + Lang.translate("need_reboot"))

        #~ commande = gtk.Label(Lang.translate("pacman"))
        #~ grilleCommande = gtk.Table(1,1)
        #~ zoneCommande = gtk.Frame(Lang.translate("preferences_command"))
        #~ generalCommande = gtk.Table(2,1)
        #~ generalCommandeLabel = gtk.Label(Lang.translate("choose_su"))
        #~ generalCommandeChoix = gtk.combo_box_new_text()

        #~ divers = gtk.Label(Lang.translate("preferences_misc"))
        #~ zoneDivers = gtk.Table(1,1)

        fenetre.set_has_separator(False)
        fenetre.set_default_response(gtk.RESPONSE_OK)
        fenetre.set_resizable(True)
        fenetre.set_position(gtk.WIN_POS_CENTER)

        onglets.set_tab_pos(gtk.POS_LEFT)

        generalLangueAsterix.set_alignment(0,0.5)

        generalLangue.attach(generalLangueLabel, 0, 1, 0, 1, yoptions=gtk.FILL)
        generalLangue.attach(generalLangueChoix, 1, 2, 0, 1, yoptions=gtk.FILL)
        generalLangue.set_border_width(4)
        zoneGeneralLangue.add(generalLangue)
        zoneGeneralLangue.set_border_width(4)
        grilleGeneralCocher.attach(self.miseajourDemarrage, 0, 1, 0, 1)
        grilleGeneralCocher.attach(self.afficherGroupes, 0, 1, 1, 2)
        grilleGeneralCocher.attach(self.modeDeveloppement, 0, 1,2, 3)
        grilleGeneralCocher.set_border_width(4)
        zoneGeneralDivers.add(grilleGeneralCocher)
        zoneGeneralDivers.set_border_width(4)
        grilleGeneral.attach(zoneGeneralLangue, 0, 1, 0, 1)
        grilleGeneral.attach(zoneGeneralDivers, 0, 1, 1, 2, yoptions=gtk.FILL)
        grilleGeneral.attach(generalLangueAsterix, 0, 1, 2, 3)
        onglets.append_page(grilleGeneral, general)

        self.getLanguages(generalLangueChoix)
        self.fillCheckbox()

        #~ generalCommande.attach(generalCommandeLabel, 0, 1, 0, 1, yoptions=gtk.FILL)
        #~ generalCommande.attach(generalCommandeChoix, 1, 2, 0, 1, yoptions=gtk.FILL)
        #~ generalCommande.set_border_width(4)
        #~ zoneCommande.add(generalCommande)
        #~ zoneCommande.set_border_width(4)
        #~ grilleCommande.attach(zoneCommande, 0, 1, 0, 1)
        #~ onglets.append_page(grilleCommande, commande)

        #~ self.getTools(generalCommandeChoix)

        #~ onglets.append_page(zoneDivers, divers)

        fenetre.vbox.pack_start(onglets)

        fenetre.show_all()
        reponse = fenetre.run()

        if reponse == gtk.RESPONSE_APPLY:
            dico = {"lang" : Lang.fileLanguage(generalLangueChoix.get_active_text()), "developmentmode" : Config.boolMinus(self.modeDeveloppement.get_active()), "startupdate" : Config.boolMinus(self.miseajourDemarrage.get_active()), "useprohibategroups" : Config.boolMinus(self.afficherGroupes.get_active()), "width" : Config.readConfig("screen", "width"), "height" : Config.readConfig("screen", "height")}

            modificationInterface = False
            if Config.readConfig("pyfpm", "useprohibategroups") != Config.boolMinus(self.afficherGroupes.get_active()):
                modificationInterface = True

            Config.writeConfig(dico)

            if modificationInterface:
                interface.eraseInterface()
                interface.addRepos()

            interface.refresh()

        fenetre.destroy()


    def getLanguages (self, liste):
        """
        Récupère les fichiers de langues disponible et en récupère le nom
        """

        listeLangues = Lang.getTranslation()
        listeLangues.sort()

        for element in listeLangues:
                liste.append_text(Lang.nameLanguage(element))

        liste.set_active(listeLangues.index(Lang.translate(Config.readConfig("pyfpm", "lang"))))


    def getTools (self, liste):
        """
        Récupère les outils de connexion en mode administrateur
        """

        # Applications les plus connus
        listeOutils = ['ktsuss', 'gksu', 'gksudo', 'gnomesu', 'kdesu', 'kdesudo', 'xdg-su']

        if not Config.readConfig("admin", "command") in listeOutils:
            listeOutils.append(Config.readConfig("admin", "command"))
        listeOutils.sort()

        for element in listeOutils:
            if os.path.exists("/usr/bin/" + element):
                liste.append_text(element)
            elif os.path.exists(element):
                liste.append_text(element)

        liste.set_active(listeOutils.index(Config.readConfig("admin", "command")))


    def fillCheckbox (self):
        """
        Met les cases à cocher aux bonnes valeurs
        """

        self.miseajourDemarrage.set_active(Config.boolToInt(Config.readConfig("pyfpm", "startupdate")))
        self.afficherGroupes.set_active(Config.boolToInt(Config.readConfig("pyfpm", "useprohibategroups")))
        self.modeDeveloppement.set_active(Config.boolToInt(Config.readConfig("pyfpm", "developmentmode")))

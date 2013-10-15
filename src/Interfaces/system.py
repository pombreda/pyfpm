#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Interface rassemblant toutes les informations système
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

from Functions import system


class Systeme (object):

    def runSysteme(self, widget, interface):

       fenetre = gtk.Dialog(_("System informations"), None, gtk.DIALOG_MODAL, 
           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
           
       onglets = gtk.Notebook()
       
       lblGeneral = gtk.Label(_("General"))
       lblGtk = gtk.Label(_("GTK+3"))
       
       grilleGeneral = gtk.Table(5, 1)
       
       self.lblUser = gtk.Label(system.sysinfos["user"])
       self.lblKernel = gtk.Label(_("Kernel : ") + system.sysinfos["kernel"])
       self.lblUptime = gtk.Label(_("Uptime : ") + system.sysinfos["uptime"])
       self.lblNbPaquets = gtk.Label(_("%s installed packages") % system.sysinfos["nb_pkgs"])
       self.lblProcessor = gtk.Label(_("Processor : ") + ' '.join(system.sysinfos["proc"].split()))
       
       grilleGTK3 = gtk.Table(3, 1)
       
       self.lblGtk3Theme = gtk.Label(_("GTK3 Theme") + system.sysinfos["gtk-theme-name"])
       
       fenetre.set_position(gtk.WIN_POS_CENTER)
       
       onglets.set_tab_pos(gtk.POS_LEFT)
       
       grilleGeneral.attach(self.lblUser, 0, 1, 0, 1)
       grilleGeneral.attach(self.lblKernel, 0, 1, 1, 2)
       grilleGeneral.attach(self.lblUptime, 0, 1, 2, 3)
       grilleGeneral.attach(self.lblNbPaquets, 0, 1, 3, 4)
       grilleGeneral.attach(self.lblProcessor, 0, 1, 4, 5)
       
       
       grilleGTK3.attach(self.lblGtk3Theme, 0, 1, 0, 1)
       
       onglets.append_page(grilleGeneral, lblGeneral)
       onglets.append_page(grilleGTK3, lblGtk)
       
       fenetre.vbox.pack_start(onglets)
       
       fenetre.show_all()
       reponse = fenetre.run()
       
       if reponse == gtk.RESPONSE_CANCEL:
		   fenetre.destroy()

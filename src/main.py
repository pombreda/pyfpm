#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#                        pyFPM - Inky
#
#   Auteurs :
#       - Gaetan Gourdin (bouleetbil)
#       - Aurélien Lubert (PacMiam)
#
#   But du programme :
#       Ce programme à pour but de fournir une interface graphique au
#       gestionnaire de paquet pacman-g2 de Frugalware.
#
# ----------------------------------------------------------------------

# Importation des modules
import os, sys

try:
    import pygtk, gtk
except ImportError:
    sys.exit(fctLang.translate("pygtk_not_found"))

from Display import display
from Pacman import package
from Misc import config

# Initialisation des modules
Config = config.Config()
Package = package.Package()

# ----------------------------------------------------------------------
#   Main
#
#       Utilisation : pyfpm <option>
#               -h      affiche l'aide
#               -v      affiche la version de pyfpm
#
# ----------------------------------------------------------------------


def main():
    """
    Lancement de pyfpm
    """

    if len(sys.argv) > 1:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print ("Utilisation : pyfpm <option>\n\t-h\taffiche l'aide\n\t-v\taffiche la version de pyfpm")
        elif sys.argv[1] == "-v" or sys.argv[1] == "--version":
            print ("pyFPM (Inky)")
    else:
        Config.checkConfig()

        Interface = display.Interface()

        Package.startPacman()
        Package.initPacman()

        Interface.mainWindow()
        Interface.runWindow()

        Package.closePacman()


if __name__ == "__main__":
    sys.exit(main())

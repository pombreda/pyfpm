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
import sys, argparse

try:
    import pygtk, gtk
except ImportError:
    sys.exit(fctLang.translate("pygtk_not_found"))

from Display import display, pacman
from Misc import config

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
        parser = argparse.ArgumentParser(description='pyFPM is a pacman-g2 front-end', epilog='(C) 2012-2013 Frugalware Developer Team (GPL)')

        parser.add_argument('-v', '--version', action='version', version="pyFPM Inky Licence GPL", help="show the current version")
        parser.add_argument('--fpm', action='store_true', help="install or update a package with fpm file [TODO]")

        args = parser.parse_args()
    else:
        Config = config.Config()
        Config.checkConfig()

        Interface = display.Interface()

        Interface.mainWindow()
        Interface.runWindow()


if __name__ == "__main__":
    sys.exit(main())

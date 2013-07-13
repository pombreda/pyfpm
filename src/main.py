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
import sys, argparse, gettext

# Récupération de la traduction
gettext.bindtextdomain('pyfpm', 'lang')
gettext.textdomain('pyfpm')
_ = gettext.gettext

try:
    import pygtk, gtk
except ImportError:
    sys.exit(_("pygtk was not found"))

from Interfaces import display
from Functions import config

# ----------------------------------------------------------------------
#   Main
# ----------------------------------------------------------------------

def main():
    """
    Lancement de pyfpm
    """

    parser = argparse.ArgumentParser(description='pyFPM is a pacman-g2 front-end', epilog='(C) 2012-2013 Frugalware Developer Team (GPL)')

    parser.add_argument('-v', '--version', action='version', version="pyFPM Inky Licence GPL", help="show the current version")

    parser.add_argument('--debug', action='store_true', help="use debug mode [TODO]")

    parserGrpPkg = parser.add_argument_group('package')
    parserGrpPkg.add_argument('--fpm', action='store', metavar='FILE', help="install or update a package with fpm file [TODO]")

    parserGrpDev = parser.add_argument_group('development')
    parserGrpDev.add_argument('--dev', action='store_true', help="use pyFPM with development mode [TODO]")

    args = parser.parse_args()

    if len(sys.argv) == 1 or args.dev or args.debug:
        Config = config.Config()
        Config.checkConfig()

        Interface = display.Interface()

        Interface.mainWindow(args.dev)
        Interface.runWindow()


if __name__ == "__main__":
    sys.exit(main())

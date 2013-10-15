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
import sys, argparse, dbus

from Interfaces import display
from Functions import config

# ----------------------------------------------------------------------
#   Main
# ----------------------------------------------------------------------

def main():
    """
    Lancement de pyfpm
    """

    if len(sys.argv) >= 1:

        # On lance le parser d'argument seulement dans le cas où on a des arguments
        parser = argparse.ArgumentParser(description='pyFPM is a pacman-g2 front-end', epilog='(C) 2012-2013 Frugalware Developer Team (GPL)')

        parser.add_argument('-v', '--version', action='version', version="pyFPM Inky Licence GPL", help="show the current version")
        parser.add_argument('--debug', action='store_true', help="use debug mode [TODO]")

        parserGrpPkg = parser.add_argument_group('package')
        parserGrpPkg.add_argument('--fpm', action='store', metavar='FILE', help="install or update a package with fpm file [TODO]")

        parserGrpDev = parser.add_argument_group('system')
        parserGrpDev.add_argument('--show-system', action='store_true', help="show system informations [TODO]")

        args = parser.parse_args()

    pacmanBus = dbus.SystemBus()

    try:
        proxy = pacmanBus.get_object(BUSNAME, OBJPATH, introspect=False)
    except dbus.DBusException:
        sys.exit(_("DBUS interface is not available."))

    if len(sys.argv) == 1 or args.debug:

        # On vérifie la configuration de pyFPM
        Config = config.Config()
        Config.checkConfig()

        # On lance l'interface
        Interface = display.Interface()
        Interface.mainWindow()


if __name__ == "__main__":
    sys.exit(main())

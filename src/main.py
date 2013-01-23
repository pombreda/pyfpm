#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#                        pyFPM version 0001
#
#   Auteurs :
#       - Gaetan Gourdin
#       - Aurélien Lubert
#
#   But du programme :
#       Ce programme à pour but de fournir une interface graphique au
#       gestionnaire de paquet pacman-g2 de Frugalware.
#
# ----------------------------------------------------------------------

import os, sys

from package import *
from display import *

fctPaquets = fonctionsPaquets()
fctInterface = fonctionsInterface()


# ----------------------------------------------------------------------
#   Main
#
#       Utilisation : pyfpm <option>
#               -h      affiche l'aide
#               -v      affiche la version de pyfpm
#
# ----------------------------------------------------------------------


def main():

    if sys.argv[0] == "-h" or sys.argv[0] == "--help":
        print ("Utilisation : pyfpm <option>\n\t-h\taffiche l'aide\n\t-v\taffiche la version de pyfpm")
    elif sys.argv[0] == "-v" or sys.argv[0] == "--version":
        print ("pyFPM v.0001")
    else:
        fctPaquets.initialiserPacman()
        #~ fctPaquets.test_infoPaquets("frugalware")
        fctInterface.fenetrePrincipale()
        gtk.main()
        fctPaquets.terminerPacman()

if __name__ == "__main__":
    sys.exit(main())

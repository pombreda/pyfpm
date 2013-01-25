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
from config import *

fctPaquets = fonctionsPaquets()
fctInterface = fonctionsInterface()
fctConfig = fonctionsConfiguration()

# ----------------------------------------------------------------------
#   Main
#
#       Utilisation : pyfpm <option>
#               -h      affiche l'aide
#               -v      affiche la version de pyfpm
#
# ----------------------------------------------------------------------


def main():

    if len(sys.argv) > 1:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print ("Utilisation : pyfpm <option>\n\t-h\taffiche l'aide\n\t-v\taffiche la version de pyfpm")
        elif sys.argv[1] == "-v" or sys.argv[1] == "--version":
            print ("pyFPM v.0001")
    else:
        fctPaquets.initialiserPacman()
        
        fctLang.recupererTraduction()
        fctInterface.fenetrePrincipale()
        gtk.main()
        fctPaquets.terminerPacman()

if __name__ == "__main__":
    sys.exit(main())

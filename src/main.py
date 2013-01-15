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

    fctPaquets.initialiserPacman()
    fctInterface.fenetrePrincipale()
    gtk.main()

if __name__ == "__main__":
    sys.exit(main())

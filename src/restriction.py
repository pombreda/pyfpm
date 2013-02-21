#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions lancés en mode superadministrateur
#
# ----------------------------------------------------------------------

import sys

from Pacman import package
fctPaquets = package.fonctionsPaquets()


def main (*args):
    """
    Partie nécessaire pour l'execution de certaines commandes avec les
    droits super-utilisateur
    """

    for argument in sys.argv:
        if argument == "cleancache":
            fctPaquets.nettoyerCache()
        elif argument == "updatedb":
            fctPaquets.miseajourBaseDonnees()
        elif argument == "install":
            fctPaquets.lancerPacman(sys.argv[sys.argv.index(argument) + 1], sys.argv[sys.argv.index(argument) + 2])

if __name__ == "__main__":
    sys.exit(main())

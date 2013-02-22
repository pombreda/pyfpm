#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions lancés en mode superadministrateur
#
# ----------------------------------------------------------------------

import sys

from Pacman import package


def main (*args):
    """
    Partie nécessaire pour l'execution de certaines commandes avec les
    droits super-utilisateur
    """

    argument = None

    if sys.argv[1] == "install":
        argument = sys.argv[sys.argv.index(sys.argv[1]) + 1], sys.argv[sys.argv.index(sys.argv[1]) + 2]

    fctInstallation = package.fenetreInstallation()
    fctInstallation.initialiserFenetre(sys.argv[1], argument)

if __name__ == "__main__":
    sys.exit(main())

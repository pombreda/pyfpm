#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Ensemble de fonctions utiles
#
# ----------------------------------------------------------------------

import os, re

def printDebug (typeErreur, erreur):
    """
    Affiche une sortie terminal
    """

    modeDebug = True

    if typeErreur == "DEBUG":
        color = "\033[0;32m"
    elif typeErreur == "ERROR":
        color = "\033[0;34m"
    elif typeErreur == "INFO":
        color = "\033[0;36m"
    elif typeErreur == "DBUS":
        color = "\033[0;35m"
    else:
        color = "\033[0m"

    if modeDebug or typeErreur != "INFO":
        print (str(color) + "[" + typeErreur + "]\t\033[0m" + str(erreur))


def splitRepo (chaine):
    """
    Sépare le dépot et le nom du paquet d'une chaine de type :
    [repo] name
    """

    pattern = '[\[a-z0-9]]'

    for element in re.findall(pattern, chaine):
        repo = str(chaine[1 : chaine.find(element) + 1].strip())
        name = str(chaine[chaine.find(element) + 2 :].strip())

    return [repo, name]


def checkData (liste, donnee):
    """
    Vérifie si donnee est dans liste
    """

    objetTrouve = 0

    for element in liste:
        if donnee == element:
            objetTrouve = element
            break

    return objetTrouve


def checkUser ():
    """
    Verifie quel utilisateur est en train d'utiliser pyFPM
    """

    if not os.geteuid() == 0:
        return 0

    return 1


def splitVersionName (paquet):
    """
    Permet de récupérer la version et le nom du paquet quand la chaîne est du format "kernel>=3.7"
    """

    # TODO
    # Utiliser les Regex

    liste = paquet.split('>')

    liste2 = []
    for element in liste:
        tmp =  element.split('=')
        liste2.extend(tmp)
    liste = liste2

    liste2 = []
    for element in liste:
        tmp =  element.split('<')
        liste2.extend(tmp)
    liste = liste2

    liste2 = []
    for element in liste:
        if element != "":
            liste2.append(element)

    if len(liste2) > 1:
        separateur = paquet[len(liste2[0]):len(paquet) - len(liste2[1])]
        liste2.append(separateur)

    return liste2

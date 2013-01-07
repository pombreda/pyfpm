#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions utilisées par l'interface pour communiquer
#
# ----------------------------------------------------------------------

import os

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK introuvable")

from display import *

from package import *
fctPaquets = fonctionsPaquets()

from lang import *
fctLang = fonctionsLang()


# ----------------------------------------------------------------------
#   fonctionsEvenement
#       ajouterGroupes (objet, liste)
#       ajouterPaquets (objet, interface, paquets)
#       dansListe (objet, liste, nom)
#       detruire (objet, fenetre)
#       lancerMiseajourBaseDonnees (objet, interface)
#       lancerNettoyerCache (objet, interface)
#       obtenirGroupe (objet, interface, groupe)
# ----------------------------------------------------------------------

class fonctionsEvenement:
    def detruire (objet, fenetre):

        fctPaquets.terminerPacman()
        gtk.main_quit()


    def ajouterGroupes (objet, interface):

        interface.listeColonnePaquets.clear()
        ensembleGroupes = fctPaquets.initialiserGroupes()

        for nom in ensembleGroupes:
            interface.listeColonneGroupes.append([nom])


    def obtenirGroupe (objet, interface, groupe):

        interface.barreStatus.push(0, (" " + fctLang.traduire("read_grp") + " " + groupe))

        paquets = fctPaquets.initialiserPaquets(groupe)
        objet.ajouterPaquets(interface, paquets)


    def ajouterPaquets (objet, interface, paquets):

        objetTrouve = 0

        interface.listePaquetsInstalles = []
        interface.listeColonnePaquets.clear()

        for paquet in paquets:
            if pacman_package_intalled(pacman_pkg_get_info(paquet, PM_PKG_NAME), pacman_pkg_get_info(paquet, PM_PKG_VERSION)) == 1:
                if objet.dansListe(interface.listeSuppression, pacman_pkg_get_info(paquet, PM_PKG_NAME)) == 0:
                    objetTrouve = 1
                else:
                    objetTrouve = 0
                if fctPaquets.verifierInstallationPaquet(interface, pacman_pkg_get_info(paquet, PM_PKG_NAME), pacman_pkg_get_info(paquet, PM_PKG_VERSION)) == False:
                    interface.listePaquetsInstalles.append([pacman_pkg_get_info(paquet, PM_PKG_NAME), pacman_pkg_get_info(paquet, PM_PKG_VERSION)])
                    interface.listeColonnePaquets.append([objetTrouve, pacman_pkg_get_info(paquet, PM_PKG_NAME), pacman_pkg_get_info(paquet, PM_PKG_VERSION)])
            else:
                if objet.dansListe(interface.listeInstallation, pacman_pkg_get_info(paquet, PM_PKG_NAME)) == 0:
                    objetTrouve = 0
                else:
                    objetTrouve = 1
                interface.listeColonnePaquets.append([objetTrouve, pacman_pkg_get_info(paquet, PM_PKG_NAME), pacman_pkg_get_info(paquet, PM_PKG_VERSION)])

        paquets.sort()

        #~ self.eraseData()


    def obtenirPaquet (objet, interface, nomPaquet, versionPaquet):
        
        interface.barreStatus.push(0, (fctLang.traduire("read_pkg") + " " + nomPaquet))
        objetTrouve = 0
        
        try:
            listePaquets = pacman_search_pkg(nomPaquet)
            interface.paquetSelectionne = nomPaquet
            
            for paquet in listePaquets:
                if pacman_pkg_get_info(paquet, PM_PKG_NAME) == nomPaquet and pacman_pkg_get_info(paquet, PM_PKG_VERSION) == versionPaquet:
                    objetTrouve = 1
                    objet.obtenirDetailsPaquet(interface, nomPaquet, versionPaquet, paquet)
                    break
                    
        except:
            pass
            
        if objetTrouve == 0:
            paquet = pacman_db_readpkg(db_list[0], nomPaquet)
            objet.obtenirDetailsPaquet(interface, nomPaquet, versionPaquet, paquet)
            
    
    def obtenirDetailsPaquet (objet, interface, nomPaquet, versionPaquet, paquet):

        texte = ""
        paquetInstalle = None

        interface.contenuInformations.clear()

        if pacman_package_intalled(nomPaquet, versionPaquet) == 1:
            paquetInstalle = pacman_db_readpkg (db_list[0], nomPaquet)

        interface.contenuInformations.append(None, [fctLang.traduire("name"), nomPaquet])
        interface.contenuInformations.append(None, [fctLang.traduire("version"), versionPaquet])
        
        interface.contenuInformations.append(None, [fctLang.traduire("description"), pacman_pkg_get_info(paquet, PM_PKG_DESC)])
        #~ interface.contenuInformations.append(None, [fctLang.traduire("groups"), pointer_to_string(pacman_pkg_get_info(paquet, PM_PKG_GROUPS))])
        
        try:
            if paquetInstalle <> None:
                interface.contenuInformations.append(None, [fctLang.traduire("url"), pointer_to_string(pacman_pkg_get_info(paquetInstalle, PM_PKG_URL))])
                #~ interface.contenuInformations.append(None, ["SHA1SUMS", pacman_pkg_get_info(paquet, PM_PKG_SHA1SUM)])

                dependances = pacman_pkg_getinfo(paquet, PM_PKG_DEPENDS)
                
                while dependances != 0:
                    texte += pointer_to_string(pacman_list_getdata(dependances))
                    dependances = pacman_list_next(dependances)
                    if dependances != 0:
                        texte += ", "
                        
                interface.contenuInformations.append(None, [fctLang.traduire("depends"), texte])
        except:
            pass


    def dansListe (objet, liste, nom):

        objetTrouve = 0

        for donnee in liste:
            if nom == donnee:
                objetTrouve = donnee
                break

        return objetTrouve
        
    
    def lancerNettoyerCache (objet, interface):
        
        os.system(fctConfig.lireConfig("admin", "command") + " python ./src/package.py cleancache")
        #~ fonctionsInterface.effacerInterface()

    
    def lancerMiseajourBaseDonnees (objet, interface):
        
        os.system(fctConfig.lireConfig("admin", "command") + " python ./src/package.py updatedb")
        #~ fonctionsInterface.effacerInterface()

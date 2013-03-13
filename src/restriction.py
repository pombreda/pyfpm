#!/usr/bin/python
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
#
#       Fonctions lancés en mode superadministrateur
#
# ----------------------------------------------------------------------

import sys
import dbus

from Pacman import package

def policykitTest(sender,connexion, action):
    bus = dbus.SystemBus()
    proxy_dbus = connexion.get_object('org.freedesktop.DBus','/org/freedesktop/DBus/Bus', False)
    dbus_info = dbus.Interface(proxy_dbus,'org.freedesktop.DBus')
    sender_pid = dbus_info.GetConnectionUnixProcessID(sender)
    proxy_policykit = bus.get_object('org.freedesktop.PolicyKit1','/org/freedesktop/PolicyKit1/Authority',False)
    policykit_authority = dbus.Interface(proxy_policykit,'org.freedesktop.PolicyKit1.Authority')

    Subject = ('unix-process', {'pid': dbus.UInt32(sender_pid, variant_level=1),
                    'start-time': dbus.UInt64(0, variant_level=1)})
    (is_authorized,is_challenge,details) = policykit_authority.CheckAuthorization(Subject, action, {'': ''}, dbus.UInt32(1), '')
    return is_authorized
    

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

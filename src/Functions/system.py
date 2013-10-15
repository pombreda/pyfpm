#!/usr/bin/python
# -*- coding: utf-8 *-*

# ----------------------------------------------------------------------
#
#       Permet de récupérer certaines informations système
#
# ----------------------------------------------------------------------

import platform, os, subprocess, re, package, ConfigParser
from datetime import timedelta
import files

Package = package.Package()
Config = ConfigParser.ConfigParser()
File = files.File()
gtk3_settings = os.path.expanduser('~') + "/.config/gtk-3.0/settings.ini"

sysinfos = {}

sysinfos["user"] = os.getlogin() + "@" + platform.node()

sysinfos["kernel"] = str("%s %s %s") % (platform.machine(), platform.uname()[0], platform.uname()[2])

with open('/proc/uptime', 'r') as f:
	uptime_seconds = float(f.readline().split()[0])
	uptime_string = str(timedelta(seconds = uptime_seconds))

sysinfos["uptime"] = uptime_string

''' Workaround as platform.processor() returns empty string '''
command = "cat /proc/cpuinfo"
all_info = subprocess.check_output(command, shell=True).strip()
for line in all_info.split("\n"):
	if "model name" in line:
		sysinfos["proc"] = re.sub(".*model name.*:", " ", line, 1)

sysinfos["nb_pkgs"] = len(Package.getInstalledList())

if File.fichier(gtk3_settings) == True:
    Config.read(gtk3_settings)
    sysinfos["gtk-theme-name"] = Config.get('Settings', 'gtk-theme-name')
    sysinfos["gtk-icon-theme"] = Config.get('Settings', 'gtk-icon-theme-name')
    sysinfos["gtk-font-name"] = Config.get('Settings', 'gtk-font-name')

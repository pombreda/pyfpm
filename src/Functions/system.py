#!/usr/bin/python
# -*- coding: utf-8 *-*


import platform, os
from datetime import timedelta
import psutil

print ("%s@%s") % (os.getlogin(), platform.node())

print ("Kernel : %s %s %s") % (platform.machine(), platform.uname()[0], platform.uname()[2])

with open('/proc/uptime', 'r') as f:
	uptime_seconds = float(f.readline().split()[0])
	uptime_string = str(timedelta(seconds = uptime_seconds))

print ("Uptime : %s" % uptime_string)

#!/usr/bin/python
# -*- coding: utf-8 -*-

########################################################################
#
#                   Outils - pacman.py
#
# Commencé le : 02 septembre 2012
#
########################################################################
#
# Copyright (C) gaetan gourdin 2011 <bouleetbil@frogdev.info>
# 
# pyfpm is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pyfpm is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

try:
    import pygtk, gtk
except ImportError:
    sys.exit("pyGTK not found.")
    
import os, sys

class INTERFACE():
    def __init__(self):
        gtk.Window()
        
class OUTILS():

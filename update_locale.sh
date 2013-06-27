#!/bin/bash

# Create a new translation :
# msginit -i lang/pyfpm.pot -o lang/fr/LC_MESSAGES/pyfpm.po

echo "Update locales"
xgettext -k_ -kN_ -o lang/pyfpm.pot src/main.py src/Functions/*.py src/Interfaces/*.py

msgmerge -U lang/en/LC_MESSAGES/pyfpm.po lang/pyfpm.pot
msgmerge -U lang/fr/LC_MESSAGES/pyfpm.po lang/pyfpm.pot

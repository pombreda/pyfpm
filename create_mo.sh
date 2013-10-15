#!/bin/bash

echo "Create mo translation"
msgfmt lang/en/LC_MESSAGES/pyfpm.po -o lang/en/LC_MESSAGES/pyfpm.mo
msgfmt lang/fr/LC_MESSAGES/pyfpm.po -o lang/fr/LC_MESSAGES/pyfpm.mo

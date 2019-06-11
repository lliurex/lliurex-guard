#!/bin/bash

xgettext --join-existing ./lliurex-guard/python3-lliurexguard/MainWindow.py -o ./translations/lliurex-guard.pot
xgettext --join-existing ./lliurex-guard/python3-lliurexguard/OptionsBox.py -o ./translations/lliurex-guard.pot
xgettext --join-existing ./lliurex-guard/python3-lliurexguard/LoginBox.py -o ./translations/lliurex-guard.pot
xgettext --join-existing ./lliurex-guard/python3-lliurexguard/EditBox.py -o ./translations/lliurex-guard.pot
xgettext --join-existing ./lliurex-guard/python3-lliurexguard/rsrc/lliurex-guard.ui -o ./translations/lliurex-guard.pot

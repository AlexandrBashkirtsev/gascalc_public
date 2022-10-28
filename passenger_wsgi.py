import sys

import os

import logging

INTERP = os.path.expanduser("/var/www/u1119424/data/gascalcenv/bin/python")
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from gascalc import app

application = app
handler = logging.FileHandler('/var/www/u1119424/data/www/gascalc.ru/app.log')  # errors logged to this file
handler.setLevel(logging.ERROR)  # only log errors and above
application.logger.addHandler(handler)  # attach the handler to the app's logger
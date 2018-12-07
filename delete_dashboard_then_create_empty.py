#!/usr/bin/env python3

version="0.1.0"

import os

def remove_if_exists(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        pass

os.system('TASKKILL /F /T /FI "WINDOWTITLE eq KPI Dashboard"')

remove_if_exists("kpi/db.sqlite3")
remove_if_exists("kpi/summary/migrations/0001_initial.py")

os.system('python kpi/manage.py makemigrations summary')
os.system('python kpi/manage.py migrate')

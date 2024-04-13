# see https://huey.readthedocs.io/en/latest/imports.html for evilness

# heury scheduler
from huey import SqliteHuey

# custom settings
JR_BypassHuey = True


# Globally instantiate the heuy task scheduler helper object (this will be referred to via commandline tool so needs to be module global)
# see https://huey.readthedocs.io/en/latest/guide.html
huey = SqliteHuey(filename='./hueyHl.db', immediate=JR_BypassHuey)

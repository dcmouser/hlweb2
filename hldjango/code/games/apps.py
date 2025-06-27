# django modules
from django.apps import AppConfig
from django.conf import settings
from django.db import migrations


# user modules
from lib.jr import jrfuncs
from lib.jr import jrdfuncs
from lib.casebook.casebookDefines import DefCbBuildString


class GamesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "games"


    def ready(self):
        # run at startup
        logDirPath = settings.JRBASELOGDIR + "jrlogs/casebook/"
        jrfuncs.setLogFileDir(str(logDirPath))
        # log startup
        # announce version and settings in use
        buildStr = ""
        buildStr += DefCbBuildString
        jrdfuncs.announceDjangoAndSettingsVersion(buildStr)



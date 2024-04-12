# django modules
from django.apps import AppConfig
from django.conf import settings

# user modules
from lib.jr import jrfuncs



class GamesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "games"


    def ready(self):
        # run at startup
        logDirPath = settings.BASE_DIR / "jrlogs/"
        jrfuncs.setLogFileDir(str(logDirPath))



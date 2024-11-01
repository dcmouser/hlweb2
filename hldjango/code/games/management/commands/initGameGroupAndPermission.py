from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.conf import settings

# helpers
from lib.jr import jrfuncs, jrdfuncs




class Command(BaseCommand):
    def handle(self, **options):
        runCommand()



# ---------------------------------------------------------------------------

def runCommand():
    from ...models import Game

    # details
    groupName = settings.JR_GROUPNAME_GAMEAUTHOR
    permissionCodename = settings.JR_PERMISSIONNAME_CANPUBLISHGAMES
    permissionLabel = "Can Publish Games"
    contentModel = Game
    
    jrdfuncs.createDjangoGroupAndPermission(permissionCodename, permissionLabel, groupName, contentModel)

# ---------------------------------------------------------------------------



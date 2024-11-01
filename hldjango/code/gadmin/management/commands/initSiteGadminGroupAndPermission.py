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
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.sites.models import Site

    # details
    groupName = settings.JR_GROUPNAME_SITEGADMIN
    permissionCodename = settings.JR_PERMISSIONNAME_CANGADMINSITE
    permissionLabel = "Can Administer (Gadmin) the Site"
    contentModel = Site
    
    jrdfuncs.createDjangoGroupAndPermission(permissionCodename, permissionLabel, groupName, contentModel)
# ---------------------------------------------------------------------------

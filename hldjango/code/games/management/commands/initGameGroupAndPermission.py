from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.conf import settings

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

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

    # add permission to add game to group
    content_type = ContentType.objects.get_for_model(Game)
    permission, created = Permission.objects.get_or_create(
        codename='add_game',  # 'add_' followed by the model's name in lowercase
        name='Can add game',  # Descriptive name for the permission
        content_type=content_type,
    )
    #
    group, created = Group.objects.get_or_create(name=groupName)
    group.permissions.add(permission)
    group.save()
# ---------------------------------------------------------------------------



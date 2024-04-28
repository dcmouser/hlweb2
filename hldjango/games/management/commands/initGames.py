# FUCKING EVIL

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        setupGameGroupsAndPermissions()




# ---------------------------------------------------------------------------

def setupGameGroupsAndPermissions():
    print("Running setupGameGroupsAndPermissions..")

    from django.contrib.auth.models import Group, User, Permission
    from django.contrib.contenttypes.models import ContentType
    from ...models import Game

    # create author group
    authorGameGroup, created = Group.objects.get_or_create(name="GameAuthor")

    # authoring permission for games
    content_type = ContentType.objects.get_for_model(Game)
    try:
        permissionAuthorGames = Permission.objects.create(
            codename="canPublishGames",
            name="Can Publish Games",
            content_type=content_type,
        )
    except:
        print("permissionAuthorGames seems to already exist.")
        permissionAuthorGames = Permission.objects.get(codename="canAuthorGames")

    # now give the author permission to the authorGroup
    authorGameGroup.permissions.add(permissionAuthorGames)

# ---------------------------------------------------------------------------

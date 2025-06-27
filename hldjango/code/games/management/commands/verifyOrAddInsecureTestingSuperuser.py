from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

# helpers
from lib.jr import jrfuncs, jrdfuncs





class Command(BaseCommand):
    def handle(self, **options):
        runCommand()




# ---------------------------------------------------------------------------
def runCommand():
    print("Running custom management command: verifyOrAddInsecureTestingSuperuser..")
    # see https://stackoverflow.com/questions/70309300/django-deployment-with-docker-create-superuser
    from django.db import IntegrityError
    from accounts.models import CustomUser

    optionReAddSuperuserToGroups = True

    # need to create super user
    username = settings.JR_DEFAULT_SUPERUSER_USERNAME
    password = settings.JR_DEFAULT_SUPERUSER_PASSWORD
    email = settings.JR_DEFAULT_SUPERUSER_EMAIL
    first_name = settings.JR_DEFAULT_SUPERUSER_FIRSTNAME
    last_name = settings.JR_DEFAULT_SUPERUSER_LASTNAME
    groupNameList = [settings.JR_GROUPNAME_GAMEAUTHOR, settings.JR_GROUPNAME_SITEGADMIN]

    try:
        superUsers = CustomUser.objects.filter(is_superuser=True)
        superUserCount = superUsers.count()
        if (superUserCount>0):
            #print("Confirmed existence of superuser in database; nothing more to do (initial username/password = {}/{}).".format(username, password))
            print("Confirmed existence of superuser in database; nothing more to do (initial username = {}; see verifyOrAddInsecureTestingSuperuser.py).".format(username))
            if (optionReAddSuperuserToGroups):
                for superuser in superUsers:
                    # readd superuser to groups
                    jrdfuncs.addUserToGroups(superuser, groupNameList)
            return
    except Exception as e:
        print(e)





    try:
        superuser = CustomUser.objects.create_superuser(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        superuser.save()
        print("Success: Created superuser with username '{}' and password '{}'.".format(username, password))
        # add new superuser to some groups
        jrdfuncs.addUserToGroups(superuser, groupNameList)
    except Exception as e:
        print(f"Super User with username {username} could not be created; Exception:")
        print(e)

    return
# ---------------------------------------------------------------------------



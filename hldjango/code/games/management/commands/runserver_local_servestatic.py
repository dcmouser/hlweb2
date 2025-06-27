# django funcs
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application

# ATTN: note we inherit from STATIC FILES runserver so that we can server up static files
# This is a bit of a kludge because django treats runserver management command specially in that it calls that static contrib version so we need to derive from that
#from django.core.management.commands.runserver import Command as RunserverCommand
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand



class Command(RunserverCommand):
    help = "Thin wrapper around built-in staticfiles local runserver command"

    def add_arguments(self, parser):
        # if we dont force this to true it refuses to server static files
        #settings.DEBUG = True
        super().add_arguments(parser)

    def handle(self, *args, **options):
        super().handle(*args, **options)

# django funcs
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application

# ATTN: note that this derived command will REFUSE to serve static files locally, even if normal runserver would
from django.core.management.commands.runserver import Command as RunserverCommand



class Command(RunserverCommand):
    help = "Thin wrapper around built-in staticfiles runserver command"

    def add_arguments(self, parser):
        super().add_arguments(parser)

    def handle(self, *args, **options):
        super().handle(*args, **options)

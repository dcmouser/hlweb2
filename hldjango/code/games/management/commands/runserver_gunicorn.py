# see https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/gunicorn/
# ATTN: THIS DOES NOT CURRENTLY WORK instead shell the command: gunicorn hldjango:application

# django funcs
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.wsgi import get_wsgi_application

# my funcs
from lib.jr.jrfuncs import jrprint

# helper logger
from paste.translogger import TransLogger

# web server
from gunicorn import serve


# Use paste translogger (see https://docs.pylonsproject.org/projects/waitress/en/stable/logging.html) to output all requests to stdout
optionUseTransLogger = False




class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('host', nargs='?', default=None)
        parser.add_argument('port', nargs='?', type=int, default=None)
        parser.add_argument('--unix', dest='unix', default=None)

    def handle(self, *args, **options):
        application = get_wsgi_application()

        if options['unix'] is not None:
            serve(application, unix_socket=options['unix'])
        else:
            host = options['host']
            if host is None:
                host = getattr(settings, 'DJANGO_HOST', 'localhost')
            port = options['port']
            if port is None:
                port = getattr(settings, 'DJANGO_PORT', 8000)
            
            # wrap around logger
            if (optionUseTransLogger):
                application = TransLogger(application, setup_console_handler=False)

            # serve it
            hostStr = "127.0.0.1" if (host=="0.0.0.0") else host
            jrprint("Starting gunicorn web server at {}:{}/ ...".format(hostStr, port))
            if (hostStr != host):
                jrprint(" (actual configured host ip is {})".format(host))
            #
            serve(application, host=host, port=port)


#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hldjango.settingsdir.jrlocal_win10")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # ATTN: this line was sometimes getting indented when debugger breaks on editing file in visual studio, so im adding an "if (True)" here to trigger syntax error if a line gets indented by mistake; otherwise if thinks execute_from_command is part of exectption
    if (True):
        execute_from_command_line(sys.argv)

    print("Finished executing manage.py from commandline.")

if __name__ == "__main__":
    main()

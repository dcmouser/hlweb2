"""
Django settings for hldjango project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""


# EARLY DEFAULT SETTINGS
from lib.jr.jrglobalenv import jrGlobalEnv
# set default value for some environment-supported options, which will be visible to settings_base
jrGlobalEnv.setDefault("JR_DJANGO_DEBUG", False)
#jrGlobalEnv.setDefault("JR_DJANGO_DEBUG", True)


# base settings
from .settings_base import *



ADMINS = [
 ('admin', 'jessereichler@gmail.com'),
]




# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db/hlDjangoDb.sqlite3",
    }
}




# HUEY DB SETUP
# see https://huey.readthedocs.io/en/latest/django.html
HUEY = {
    "huey_class": "huey.SqliteHuey",  # Huey implementation to use.
    "name": "HlHueyDb",
    "filename": BASE_DIR / "db/hlHueyDb.sqlite3",
    "results": True,  # Store return values of tasks.
    "store_none": False,  # If a task returns None, do not save to results.

    # ATTN: controls whether we use queued huey or run tasks immediately
    "immediate": False,

    "utc": True,  # Use UTC for all times internally.
    "connection": {},
    "consumer": {
        "workers": 1, # the server can handle 2, but makes it easier for us to track moving through the queue
        "worker_type": "process",
        "initial_delay": 0.1,  # Smallest polling interval, same as -d.
        "backoff": 1.15,  # Exponential backoff using this rate, -b.
        "max_delay": 10.0,  # Max possible polling interval, -m.
        "scheduler_interval": 1,  # Check schedule every second, -s.
        "periodic": True,  # Enable crontab feature.
        "check_worker_health": True,  # Enable worker health checks.
        "health_check_interval": 1,  # Check worker health every second.
    },
    # To run Huey in "immediate" mode with a live storage API, specify
    # immediate_use_memory=False.
    #'immediate_use_memory': False,
}





# HUEY DB SETUP
# see https://huey.readthedocs.io/en/latest/django.html
HUEY_OLD_PRE102624 = {
    "huey_class": "huey.SqliteHuey",  # Huey implementation to use.
    "name": "HlHueyDb",
    "filename": BASE_DIR / "db/hlHueyDb.sqlite3",
    "results": True,  # Store return values of tasks.
    "store_none": False,  # If a task returns None, do not save to results.

    # ATTN: controls whether we use queued huey or run tasks immediately
    "immediate": False,

    "utc": True,  # Use UTC for all times internally.
    "connection": {},
    "consumer": {
        "workers": 1,
        "worker_type": "thread",
        "initial_delay": 0.1,  # Smallest polling interval, same as -d.
        "backoff": 1.15,  # Exponential backoff using this rate, -b.
        "max_delay": 10.0,  # Max possible polling interval, -m.
        "scheduler_interval": 1,  # Check schedule every second, -s.
        "periodic": True,  # Enable crontab feature.
        "check_worker_health": True,  # Enable worker health checks.
        "health_check_interval": 1,  # Check worker health every second.
    },
    # To run Huey in "immediate" mode with a live storage API, specify
    # immediate_use_memory=False.
    #'immediate_use_memory': False,
}




# force secure ssl https only settings
JR_DJANGO_FORCE_SECURE = False
if (JR_DJANGO_FORCE_SECURE):
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    # this one shouldnt be needed if we force redirect in nginx config, which is more recommended?
    SECURE_SSL_REDIRECT = True


# 10/25/24 see https://stackoverflow.com/questions/12174040/forbidden-403-csrf-verification-failed-request-aborted
CSRF_TRUSTED_ORIGINS = ['https://nycnoir.org', 'https://www.nycnoir.org']



# now override with any secret settings
from .production_docker_secret import *
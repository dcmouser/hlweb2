# these are safe to share, they are mock values for emailing, and superuser


# initial site info (used in confirmation emails, etc.)
JR_SITE_DOMAIN = "localhost"
JR_SITE_NAME = "hlweb example"



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-8fl.nmsavsewg3ogfdighssgat.,mvlzdso_353"


# email sender
# smtp real or console fake
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"

# no need for email smtp settings since this doesn't use real email


# real default superuser with password (key secret)
JR_DEFAULT_SUPERUSER_USERNAME = "admin"
JR_DEFAULT_SUPERUSER_PASSWORD = "admin"
JR_DEFAULT_SUPERUSER_EMAIL = ""
JR_DEFAULT_SUPERUSER_FIRSTNAME = ""
JR_DEFAULT_SUPERUSER_LASTNAME = ""


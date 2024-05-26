# these should not be shared on github, etc.

# Email Settings
EMAIL_HOST = ""
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""














# can be configured in the admin/ area dynamically AND/OR here (though both for same provider is problematic)
# see https://docs.allauth.org/en/latest/socialaccount/provider_configuration.html
SOCIALACCOUNT_PROVIDERS = {
    "github": {
        # For each provider, you can choose whether or not the
        # email address(es) retrieved from the provider are to be
        # interpreted as verified.
        "AUTO_SIGNUP": False,
        "VERIFIED_EMAIL": False,
        "APPS": [
            {
                "client_id": "",
                "secret": "",
                "key": "",
            },
        ],
    },
    "google": {
        # google tutorial: https://medium.com/powered-by-django/add-social-authentication-django-allauth-google-oauth-example-d8d69a603356
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        "AUTO_SIGNUP": False,
        "VERIFIED_EMAIL": False,
        "APPS": [
            {
                "client_id": "",
                "secret": "",
                "key": "",
            },
        ],
    },
}

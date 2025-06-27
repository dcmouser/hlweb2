from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
#
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

import re


# custom user class

class CustomUser(AbstractUser):
    bggname = models.CharField(blank=True, max_length=32, help_text="Bgg Username", default="")
    webpage = models.CharField(blank=True, max_length=256, help_text="Web page", default="")

    def get_absolute_url(self):
        return reverse("accountProfile", kwargs={'pk':self.pk})

    def get_is_gadmin(self):
        # ATTN: needs improvement, check if they are part of a special group of custom gadmin
        if (not self.is_authenticated):
            return False
        # note this will return TRUE for all superusers even if they don't explicitly have the permission
        if (self.has_perm(settings.JR_PERMISSIONNAME_CANGADMINSITE)):
            return True
        # default
        return False

    def clean(self):
        super().clean()  # Call the base class clean() method first
        # prevent certain characters in username
        if '@' in self.username:
            raise ValidationError("The '@' character is not allowed in the username.")
        if ' ' in self.username:
            raise ValidationError("Username cannot contain spaces.")

    def calcBggUrl(self):
        if (self.bggname is None) or (self.bggname==""):
            return ""
        return "https://boardgamegeek.com/user/" + self.bggname





@deconstructible
# based on AsciiUsernameValidator but no @ sign
class JrUsernameValidator(validators.RegexValidator):
    regex = r"^[\w.+-]+\Z"
    message = _(
        "Enter a valid username. This value may contain only unaccented lowercase a-z "
        "and uppercase A-Z letters, numbers, and ./+/-/_ characters."
    )
    flags = re.ASCII

myCustomUserUsernameValidators = [JrUsernameValidator()]
#myCustomUserUsernameValidators = [UnicodeUsernameValidator()]
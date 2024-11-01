from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.conf import settings



# custom user class

class CustomUser(AbstractUser):
    bgglink = models.CharField(blank=True, max_length=255)

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

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse



# custom user class

class CustomUser(AbstractUser):
    bgglink = models.CharField(blank=True, max_length=255)

    def get_absolute_url(self):
        return reverse("accountProfile", kwargs={'pk':self.pk})


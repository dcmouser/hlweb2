from django.db import models
from django.contrib.auth.models import AbstractUser


# custom user class

class CustomUser(AbstractUser):
    bgglink = models.CharField(blank=True, max_length=255)


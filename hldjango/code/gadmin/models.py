# django modules
from django.db import models
from django.core.exceptions import ValidationError




class GlobalSettings(models.Model):
    # fields
    homePageHtml = models.TextField(verbose_name="Html to be display on the Home page", help_text="Just type raw html here", default="", blank=True)
    aboutPageHtml = models.TextField(verbose_name="Html to be display on the About page", help_text="Just type raw html here", default="", blank=True)
    downloadPageHtml = models.TextField(verbose_name="Html to be display on the Downloads page", help_text="Just type raw html here", default="", blank=True)

    def __str__(self):
        return "Global Settings"
    
    class Meta:
        verbose_name_plural = "Global Settings"

    def save(self, *args, **kwargs):
        if not self.pk and GlobalSettings.objects.exists():
            raise ValidationError('There can be only one GlobalSettings instance')
        return super(GlobalSettings, self).save(*args, **kwargs)

    def getSingleton():
        # class static accesor to singleton
        # note this will return None if it doesn't exist yet
        obj, created = GlobalSettings.objects.get_or_create(id=1)
        return obj

    def getHomePageHtml(self):
        return self.homePageHtml if (self.homePageHtml is not None) else ""
    def getAboutPageHtml(self):
        return self.aboutPageHtml if (self.aboutPageHtml is not None) else ""
    def getDownloadPageHtml(self):
        return self.downloadPageHtml if (self.downloadPageHtml is not None) else ""

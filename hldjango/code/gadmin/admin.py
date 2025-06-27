from django.contrib import admin

# Register your models here.

from .models import GlobalSettings

# Register your models here.

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    #list_display = ["homePageHtml", "aboutPageHtml", "downloadPageHtml"]
    pass


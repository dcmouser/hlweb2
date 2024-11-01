# ATTN:JR
# this manually created migration file is an attempt to override the default example.com site setting; pretty ugly stuff
# DO NOT DELETE THIS FILE(!)
# see https://aidenbell.me/django-sites-data-migration/

from django.conf import settings
from django.db import migrations


def updateOverideFeaultDjangoSiteInformation(apps, schema_change):
    SiteModel = apps.get_model('sites', 'Site')
    # we ASSUME because of when this is run that there is no existing site, otherwise this will create an extra one which is useless
    SiteModel.objects.get_or_create(domain=settings.JR_SITE_DOMAIN, name=settings.JR_SITE_NAME)


class Migration(migrations.Migration):
    dependencies = [
        # these ensure it runs before built in sites migration, and before our own core migration
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(updateOverideFeaultDjangoSiteInformation)
    ]

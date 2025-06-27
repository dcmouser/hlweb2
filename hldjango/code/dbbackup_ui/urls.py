#from django.conf.urls import url
from django.urls import re_path
from .views import BackupView

urlpatterns = [
    # ATTN: JR FIX
    re_path(r'^backup-database-and-media/$', BackupView.as_view(), name="backup_view"),
    #url(r'^backup-database-and-media/$', BackupView.as_view(), name="backup_view"),
]

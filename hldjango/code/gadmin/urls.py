from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from .views import gadminHomePageView, gadminStatusPageView, gadminSettingsPageView, gadminActionsPageView, gadminLogsPageView, gadminLogFilePageView



urlpatterns = [
    path("", gadminHomePageView, name="gadminHome"),
    path("status", gadminStatusPageView.as_view(), name="gadminStatus"),
    path("settings", gadminSettingsPageView.as_view(), name="gadminSettings"),
    path("actions", gadminActionsPageView.as_view(), name="gadminActions"),
    path("logs", gadminLogsPageView.as_view(), name="gadminLogs"),
    path("log/<str:logfile>/<str:action>", gadminLogFilePageView.as_view(), name="gadminLogFile"),
]


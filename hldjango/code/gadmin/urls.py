from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from .views import gadminHomePageView, gadminStatusPageView



urlpatterns = [
    path("", gadminHomePageView, name="gadminHome"),
    path("status", gadminStatusPageView, name="gadminStatus"),
]


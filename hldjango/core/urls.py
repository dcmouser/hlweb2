from django.urls import path

from .views import homePageView, aboutPageView



urlpatterns = [
    path("about", aboutPageView, name="coreAbout"),
    path("", homePageView, name="coreHome"),
]

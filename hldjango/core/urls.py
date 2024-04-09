from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from .views import homePageView, aboutPageView



urlpatterns = [
    path("about", aboutPageView, name="coreAbout"),
    path("", homePageView, name="coreHome"),
    #path("__debug__/", include("debug_toolbar.urls")),
]


# in debug mode we let the django development server serve static files
if (settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    #urlpatterns += path("__debug__/", include("debug_toolbar.urls"))
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]


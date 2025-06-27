from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from .views import homePageView, aboutPageView, downloadPageView



urlpatterns = [
    path("about", aboutPageView, name="coreAbout"),
    path("downloads", downloadPageView, name="coreDownloads"),
    path("", homePageView, name="coreHome"),

    # to avoid an error log when browsers ask for plain favicon.ico
    path("favicon.ico", RedirectView.as_view(url="/static/favicon/favicon.ico"))
]


# in debug mode we let the django development server serve static files
if (settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]

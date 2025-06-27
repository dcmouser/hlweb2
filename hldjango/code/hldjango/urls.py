"""
URL configuration for hldjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    # django-dbbackup-ui (6/9/25)
    path("admin/backups/", include("dbbackup_ui.urls")),

    # django admin
    path("admin/", admin.site.urls),

    # our custom admin areas
    path("gadmin/", include("gadmin.urls")),

    # django original account routes for login/logout
    # ATTN: This is the evil part that prevented allauth from getting login
    #path("accounts/", include("django.contrib.auth.urls")),
    #
    # allauth
    path("accounts/", include("allauth.urls")),

    # custom account app
    path("accounts/", include("accounts.urls")),

    # our app url paths
    path("games/", include("games.urls")),

    # our app url paths
    path("", include("core.urls")),
]

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings


def homePageView(request):
    return render(request, "core/home.html")


def aboutPageView(request):
    versionString = "v" + str(settings.JR_VERSION_NUMBER) + " (" + settings.JR_VERSION_DATE_STR + ")"
    vars = {"versionString": versionString}
    return render(request, "core/about.html", vars)




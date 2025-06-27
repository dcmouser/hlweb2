from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

from lib.casebook.casebookDefines import DefCbVersionString, DefCbVersionHistory
from gadmin.models import GlobalSettings



def homePageView(request):
    #
    globalSettings = GlobalSettings.getSingleton()
    pageHtml = globalSettings.getHomePageHtml()

    # Ensure version info is shown
    pageHtml = putVersionInfoIntoPageHtml(pageHtml)

    #
    vars = {
            "pageHtml": pageHtml,
            }
    #
    return render(request, "core/home.html", vars)


def aboutPageView(request):
    versionString = DefCbVersionString
    versionHistory = DefCbVersionHistory.strip()
    #
    globalSettings = GlobalSettings.getSingleton()
    pageHtml = globalSettings.getAboutPageHtml()

    # Ensure version info is shown
    pageHtml = putVersionInfoIntoPageHtml(pageHtml)

    #
    vars = {
            "versionHistory": versionHistory,
            "pageHtml": pageHtml,
            }
    return render(request, "core/about.html", vars)


def downloadPageView(request):
    globalSettings = GlobalSettings.getSingleton()
    pageHtml = globalSettings.getDownloadPageHtml()
    #
    vars = {
            "pageHtml": pageHtml,
            }
    return render(request, "core/downloads.html", vars)




def putVersionInfoIntoPageHtml(pageHtml):
    # Ensure version info is shown
    verstionStringTemplatePattern = "{{versionString}}"
    # replace version info
    versionString = DefCbVersionString
    if (verstionStringTemplatePattern in pageHtml):
        pageHtml = pageHtml.replace(verstionStringTemplatePattern, versionString)
    else:
        # add version info at top IF its not mentioned
        pageHtml = "<p>This is the New York Noir / Casebook Web Services Website {}.</p>".format(versionString) + "\n" + pageHtml
    return pageHtml
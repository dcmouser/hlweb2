from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.utils.safestring import mark_safe

# helpers
from lib.jr import jrfuncs, jrdfuncs




def gadminHomePageView(request):
    return render(request, "gadmin/gadminHome.html")



def gadminStatusPageView(request):
    vars = {}

    # huey stuff
    from huey.contrib.djhuey import HUEY as huey
    hueyStorage = huey.storage
    hueyEnqueuedItems = hueyStorage.enqueued_items()
    hueyAllResults = huey.all_results()

    # huey settings
    vars["huey"] = {
        "settingsHtml": mark_safe(jrfuncs.dictToHtmlPre(settings.HUEY)),
        "queueSize": hueyStorage.queue_size(),
        "enqueued_items": hueyEnqueuedItems,
        "enqueued_itemsHtml": mark_safe(jrfuncs.dictToHtmlPre(hueyEnqueuedItems)),
        "all_results": hueyAllResults,
        "all_resultsHtml": mark_safe(jrfuncs.dictToHtmlPre(hueyAllResults)),
    }


    return render(request, "gadmin/gadminStatus.html", vars)


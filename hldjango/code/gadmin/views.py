from django import forms
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.utils.safestring import mark_safe

from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.http import JsonResponse
from django.http import Http404, HttpResponseForbidden

from .models import GlobalSettings
from .forms import GlobalSettingsForm

from games.gametasks import get_running_task_count


# helpers
from lib.jr import jrfuncs, jrdfuncs

# modules
import time




def gadminHomePageView(request):
    return render(request, "gadmin/gadminHome.html")




class gadminStatusPageView(UserPassesTestMixin, TemplateView):
    template_name ="gadmin/gadminStatus.html"

    def test_func(self):
        return jrdfuncs.requestUserIsAuthenticatedAndGadmin(self.request)


    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)

         # huey stuff
        from huey.contrib.djhuey import HUEY as huey
        hueyStorage = huey.storage
        hueyEnqueuedItems = hueyStorage.enqueued_items()
        hueyAllResults = huey.all_results()
        hueyRunningTaskCount = get_running_task_count()


        # huey settings
        context["huey"] = {
            "settingsHtml": mark_safe(jrfuncs.dictToHtmlPre(settings.HUEY)),
            "queueSize": hueyStorage.queue_size(),
            "enqueued_items": hueyEnqueuedItems,
            "enqueued_itemsHtml": mark_safe(jrfuncs.dictToHtmlPre(hueyEnqueuedItems)),
            "all_results": hueyAllResults,
            "all_resultsHtml": mark_safe(jrfuncs.dictToHtmlPre(hueyAllResults)),
            "runningTaskCount": hueyRunningTaskCount,
        }

        # add some info
        info = {
            "timeZone": time.tzname,
            "currentDateString": jrfuncs.getNiceCurrentDateTime(),
        }
        context["info"] = info

        return context


    def post(self, request, *args, **kwargs):
        # Get data from POST request
        action = request.POST.get("action", "")
        result = self.performAction(action)
       
        # Pass the result to the template (uncomment if needed)
        context = self.get_context_data(result=result)
        return self.render_to_response(context)

    def performAction(self, action):
        if (action == "cleanHuey"):
            result = self.cleanHuey()
        else:
            result = "action not understood."
        #
        return result


    def cleanHuey(self):
        # return summary string
         # huey stuff
        from huey.contrib.djhuey import HUEY as huey
        hueyStorage = huey.storage
        hueyAllResultsPre = huey.all_results()
        hueyStorage.flush_results()
        hueyAllResultsPost = huey.all_results()
        result = "All huey results should have been flushed/deleted (from {} to {} results).".format(len(hueyAllResultsPre), len(hueyAllResultsPost))
        return result





class gadminSettingsPageView(UserPassesTestMixin, UpdateView):
    model = GlobalSettings
    form_class = GlobalSettingsForm
    template_name = 'gadmin/gadminSettings.html'
    #
    success_url = reverse_lazy("gadminHome")  # Redirect to home/index page after saving

    def test_func(self):
        return jrdfuncs.requestUserIsAuthenticatedAndGadmin(self.request)

    def get_object(self, queryset=None):
        # Ensures a single instance exists or creates it if not, and fetches it for editing
        obj, created = GlobalSettings.objects.get_or_create(id=1)
        return obj



class gadminActionsPageView(UserPassesTestMixin, TemplateView):
    template_name ="gadmin/gadminActions.html"

    def test_func(self):
        return jrdfuncs.requestUserIsAuthenticatedAndGadmin(self.request)

    def post(self, request, *args, **kwargs):
        # Get data from POST request
        action = request.POST.get("action", "")
        result = self.performAction(action)
       
        # Pass the result to the template (uncomment if needed)
        context = self.get_context_data(result=result)
        return self.render_to_response(context)

    def performAction(self, action):
        if (action == "exportDocs"):
            result = "Documentation exported to file."
            from lib.casebook.cbtools import CbTools
            cbt = CbTools()
            result = cbt.runCommandMakeDocs({})
        else:
            result = "action not understood."
        #
        return result







class gadminLogsPageView(UserPassesTestMixin, TemplateView):
    template_name ="gadmin/gadminLogs.html"

    def test_func(self):
        return jrdfuncs.requestUserIsAuthenticatedAndGadmin(self.request)

    def post(self, request, *args, **kwargs):
        # Get data from POST request
        action = request.POST.get("action", "")
        result = self.performAction(action)
       
        # Pass the result to the template (uncomment if needed)
        context = self.get_context_data(result=result)
        return self.render_to_response(context)

    def performAction(self, action):
        if (action == "removeLogs"):
            result = "Deleting log files."
            from lib.jr.jrfilecleaner import JrFileCleaner
            fileCleaner = JrFileCleaner(getLogDirs(), getLogExtensions(), True)
            fileCleaner.scanFiles()
            optionDryRun = False
            retv = fileCleaner.deleteAllFiles(optionDryRun, getFilesToNotDelete(), True)
            result = retv["summary"]
        else:
            result = "action not understood."
        #
        return result


    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)

        # get log file list
        from lib.jr.jrfilecleaner import JrFileCleaner
        fileCleaner = JrFileCleaner(getLogDirs(), getLogExtensions(), True)
        fileCleaner.scanFiles()
        logFiles = fileCleaner.getFileListForDisplay()
        #
        for l in logFiles:
            bfName = l["baseName"]
            # fix up requestd log filename of illegal chars
            bfName = bfName.replace("/","_fs_",)
            # create urls
            l["viewUrl"] = reverse("gadminLogFile", kwargs={"logfile": bfName, "action": "view"})
            l["downloadUrl"] = reverse("gadminLogFile", kwargs={"logfile": bfName, "action": "download"})
            l["deleteUrl"] = reverse("gadminLogFile", kwargs={"logfile": bfName, "action": "delete"})
        #
        context['logFiles'] = logFiles
        return context







class gadminLogFilePageView(UserPassesTestMixin, View):
    # stream the file to the user
    def test_func(self):
        return jrdfuncs.requestUserIsAuthenticatedAndGadmin(self.request)

    def get(self, request, *args, **kwargs):
        # get log file list
        from lib.jr.jrfilecleaner import JrFileCleaner
        fileCleaner = JrFileCleaner(getLogDirs(), getLogExtensions(), True)
        fileCleaner.scanFiles()
        logFiles = fileCleaner.getFileList()

        requestedFileBaseName = kwargs["logfile"]

        # fix up requestd log filename of illegal chars
        requestedFileBaseName = requestedFileBaseName.replace("_fs_","/")
        # find it in log files
        reqFile = jrfuncs.findListRowWithDictFieldValue(logFiles, "baseName", requestedFileBaseName)
        if (reqFile is None):
            # not found
            raise Http404
        path = reqFile["path"]

        action = kwargs["action"]
        if (action == "download"):
            response = jrdfuncs.streamFileRequest(path, "text/plain")
        elif (action == "view"):
            # tail view
            optionTailLines = 100
            response = jrdfuncs.streamFileTailRequest(path, optionTailLines)
        elif (action == "delete"):
            # delete the file
            # ATTN: TODO -- protect this under a post with csrf
            try:
                if (requestedFileBaseName in getFilesToNotDelete()):
                    jrfuncs.truncateFileIfExists(path)
                    result = "Truncated file "
                else:
                    jrfuncs.deleteFilePathIfExists(path)
                    result = "Delete file "
            except Exception as e:
                result = "Failed to delete/truncase file "
            # set flash messages
            jrdfuncs.addFlashMessage(request, result + path, False)
            # redirect to file list
            return redirect("gadminLogs")
        else:
            raise HttpResponseForbidden

        return response
        





# helpers
def getLogDirs():
    logDirPath = str(settings.JRBASELOGDIR +  "jrlogs/")
    mainLogDirDict = {"prefix":"", "path": logDirPath}
    return [mainLogDirDict]

def getLogExtensions():
    return [".txt",".log"]


def getFilesToNotDelete():
    # in the production server if we delete these files logging stops (i guess we need to truncate them instead)
    flist = settings.JRLOGVIEWER_DONTDELETE_LIST
    flist = [s.lower() for s in flist]
    return flist
from django.shortcuts import redirect
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.db.models import Q
from django.db.models import F, Func, Value
from django.db.models.functions import NullIf
from django.db.models.expressions import OrderBy
from django.db.models import Case, When, Value, CharField
#
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden
from django.core.exceptions import ValidationError
from django.http import FileResponse
#
from django.conf import settings

# python modules
import os
import uuid

# for downloading image files as zip
import zipfile
from io import BytesIO


# user modules
from .models import Game, GameFile
from .forms import GameFileMultipleUploadForm, GameFormForEdit, GameFormForCreate, GameFormForChangeDir
from . import gamefilemanager
from lib.jr import jrdfuncs, jrfuncs

from lib.casebook.casebookDefines import *





# shared view helpers
def viewAddGameFileListCountToContext(gameViewInstance, context):
    # get the game instance this view is working on
    game = gameViewInstance.get_object()
    # query list of files associated with this game
    querySet = GameFile.objects.filter(game=game.pk)
    # how many ?
    gameFileListCount = querySet.count()
    # add it to context
    context['gameFileListCount'] = gameFileListCount




# Games

class GameListView(ListView):
    model = Game
    template_name = "games/gameList.html"

    def get_queryset(self, *args, **kwargs): 
        sort = self.request.GET.get('sort', 'admin')
        onlyPublic = self.request.GET.get('onlyPublic', False)
        #
        # basic query
        qs = super(GameListView, self).get_queryset()
        # now filter
        requestUser = self.request.user
        if (onlyPublic) or (not requestUser.is_authenticated):
            qs = Game.objects.filter(Q(isPublic=True))
        else:
            isAdmin = jrdfuncs.userIsAuthenticatedAndGadmin(requestUser)
            if (isAdmin):
                # show them full list
                pass
            else:
                # show them THEIR games and PUBLIC games
                qs = Game.objects.filter(Q(owner=requestUser) | Q(isPublic=True))
        #
        # new sortable
        sort_map = {
            'owner': {'primary': 'owner'},
            'title': {'primary': 'title'},
            'created': {'primary': 'created', 'descending': True},
            'modified': {'primary': 'modified', 'descending': True},
            'default': {'primary': 'adminSortKey'},
            'campaign': {'primary': 'campaignName','secondary':'campaignPosition'}
        }
        sort_field = sort_map.get(sort, {'primary':'adminSortKey'})
        #
        primary = sort_field["primary"]
        secondary = sort_field["secondary"] if ("secondary" in sort_field) else None
        descending = sort_field["descending"] if ("descending" in sort_field) else False
        #
        # this code forces blank values for fields to sort at bottom (even in case of empty string); this is important when sorting by something like campaign or adminSortKey where blank values should be lower
        if (secondary is None):
            qs = qs.order_by(
                OrderBy(F(primary), descending=descending, nulls_last=True)
            )
        else:
            qs = qs.order_by(
                OrderBy(NullIf(F(primary), Value('')), descending=descending, nulls_last=True),
                OrderBy(NullIf(F(secondary), Value('')), nulls_last=True),
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_sort'] = self.request.GET.get('sort', 'admin')
        context['current_onlyPublic'] = self.request.GET.get('onlyPublic', False)
        requestUser = self.request.user
        return context






class GameDetailView(UserPassesTestMixin, DetailView):
    model = Game
    template_name = "games/gameDetail.html"

    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)
        # add context
        viewAddGameFileListCountToContext(self, context)
        return context

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        # true if the game is public OR we are the owner
        return (jrdfuncs.userOwnsObjectOrStrongerPermission(obj, self.request.user) or (obj.isPublic))






class GameCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Game
    form_class = GameFormForCreate
    permission_required = "games.add_game"
    template_name = "games/gameCreate.html"
    #fields = ["name", "preferredFormatPaperSize", "preferredFormatLayout", "isPublic", "text"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the URL to the context
        context['sampleStartingTemplateUrl'] = DefCbDefine_NewGameStartingSourceTemlateUrl
        context['simpleStartingTemplateUrl'] = DefCbDefine_NewGameSimpleSourceTemlateUrl
        return context

    def form_valid(self, form):
        # force owner field to logged in creating user
        form.instance.owner = self.request.user

        # set this so save() makes it unieue
        self.flagSlugChanged = True

        # save
        response = super().form_valid(form)
        # force random subdirname
        #obj = self.get_object()
        #self.object.subdirname = uuid.uuid4()
        return response

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        text = "// For a mostly blank starting game template see: " + DefCbDefine_NewGameStartingSourceTemlateUrl + "\n"
        text += "// For a short but fully working sample case see: " + DefCbDefine_NewGameSimpleSourceTemlateUrl + "\n"
        initial['text'] = text + "\n\n"
        return initial

    def handle_no_permission(self):
        # You can render a custom template or return any HttpResponse here
        if self.raise_exception or self.request.user.is_authenticated:
            #context = self.get_context_data()
            context = {}
            content = render_to_string("games/missingPermissionToCreateGame.html", context, self.request)
            return HttpResponseForbidden(content)
        return super().handle_no_permission()





class GameEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    form_class = GameFormForEdit
    template_name = "games/gameEdit.html"

    def get_form_kwargs(self):
        # we need a custom get_form_kwargs function so that we can add ownerId to it
        """Pass the owner_id to the form."""
        kwargs = super(GameEditView, self).get_form_kwargs()
        if self.object:  # Check if the object exists
            kwargs['ownerId'] = self.object.owner.id
        # request user
        kwargs['requestUser'] = self.request.user  # Pass user to the form
        return kwargs
    
    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)
        # add context
        viewAddGameFileListCountToContext(self, context)
        return context
    
    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (jrdfuncs.userOwnsObjectOrStrongerPermission(obj, self.request.user))

    def form_valid(self, form):
        game = self.object

        # force slug rebuild on name change
        if ("name" in form.changed_data) and (not "slug" in form.changed_data):
            # when they change the name, we reset the slug value, so it will get an updated value
            # force slug value blank so it will be reset to game.name during save (we COULD do it here also)
            game.slug = ""
            game.flagSlugChanged = True
        if ("slug" in form.changed_data):
            game.flagSlugChanged = True

        # save -- BUT we have a problem, if there is an error for a field that is dynamically set from contents options, it will LOOK bad to the validator even though we are going to replace it
        response = super(GameEditView, self).form_valid(form)

        # now check if there is an error in settings
        #
        # get_object fails if we change slug?
        #game = self.get_object()
        #game = self.object

        #
        if (not game.isErrorInSettings):
            # no error, just do as normal
            jrdfuncs.addFlashMessage(self.request, "Modifications to game have been saved.", False)
            # test
            flagRequestRebuild = ("saveBuildPreferred" in self.request.POST)
            if (flagRequestRebuild):
                jrdfuncs.addFlashMessage(self.request, "Requesting Preferred Rebuild..", False)
                # inject build request
                retv = game.buildGame(self.request, "buildPreferred")
                # redirect to generate page
                url =  reverse_lazy("gameGenerate", kwargs={'slug':game.slug})
                return HttpResponseRedirect(url)
            # redirect to detail view (use reverse lazy in case slug has changed)
            url =  reverse_lazy("gameDetail", kwargs={'slug':game.slug})
            return HttpResponseRedirect(url)
            #return response

        # error; report it
        jrdfuncs.addFlashMessage(self.request, "There was an error parsing the game text settings. Your changes have been saved but game will not built until these are fixed.  See 'last build log' for details: {}".format(game.lastBuildLog), True)
        # and redirect to edit page
        url =  reverse_lazy("gameEdit", kwargs={'slug':game.slug})
        return HttpResponseRedirect(url)








class GameChangeDirView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    form_class = GameFormForChangeDir
    template_name = "games/gameChangeDir.html"

    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)
        # add context
        viewAddGameFileListCountToContext(self, context)
        return context
    
    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (jrdfuncs.userOwnsObjectOrStrongerPermission(obj, self.request.user))


    def form_valid(self, form):
        if ("subdirname" not in form.changed_data):
            # nothing to do
            return super(GameChangeDirView, self).form_valid(form)

        # we will be changing subdirname

        # get old
        priorSubDirName = form.initial["subdirname"]
        # save
        response = super(GameChangeDirView, self).form_valid(form)
        # new
        game = self.object

        # now rename
        gameFileManager = gamefilemanager.GameFileManager(game)
        priorPath = gameFileManager.getBaseDirectoryPathForGameWithExplicitSubdir(priorSubDirName)
        game.renameDirectoryFrom(self.request, priorPath)
        game.reconcileFiles(self.request)

        # and redirect to edit page
        url =  reverse_lazy("gameEdit", kwargs={'slug':game.slug})
        return HttpResponseRedirect(url)




















class GameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Game
    template_name = "games/gameDelete.html"
    success_url = reverse_lazy("gameHome")

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (jrdfuncs.userOwnsObjectOrStrongerPermission(obj, self.request.user))

    def form_valid(self, form):
        # now delete folders
        game = self.object
        game.deleteUserGameDirectories(self.request)
        # normal delete of object
        response = super().form_valid(form)
        #
        return response



class GameVersionFileListView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Game
    template_name = "games/gameVersionFileList.html"

    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (jrdfuncs.userOwnsObjectOrStrongerPermission(obj, self.request.user))





class GameGenerateView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Game
    template_name = "games/gameGeneratedFileList.html"

    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (jrdfuncs.userOwnsObjectOrStrongerPermission(obj, self.request.user))

    def post(self, request, *args, **kwargs):
        # handle BUILD request
        game = self.get_object()

        # build the game
        retv = game.buildGame(request, None)

        url =  reverse("gameGenerate", kwargs={'slug':game.slug})
        return HttpResponseRedirect(url)

























# Game related to files


# helpers -- these could go into MODEL?

def getQueryArgGameId(gameFileViewInstance, keyname):
    gameSlug = gameFileViewInstance.request.resolver_match.kwargs[keyname]
    return gameSlug

def gameFileViewHelperGetQuaryArgGameObj(gameFileViewInstance, keyname):
    gameSlug = getQueryArgGameId(gameFileViewInstance, keyname)
    game = get_object_or_404(Game, slug=gameSlug)
    return game

def gameSetFileExtraGameContextAndCheckGameOwner(gameFileViewInstance):
    game = gameFileViewHelperGetQuaryArgGameObj(gameFileViewInstance, 'slug')
    gameFileViewInstance.extra_context={'game': game}
    return jrdfuncs.userOwnsObjectOrStrongerPermission(game, gameFileViewInstance.request.user)


class GameFilesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = GameFile
    template_name = "games/gameFileList.html"

    # utility functions used by the superclass ListView
    # override get_queryset to customize the list of files returned
    def get_queryset(self):
        # get the game owning the files we are looking at; we can use the result of test_func so we dont query twice
        game = self.extra_context['game']
        gameId = game.pk
        # return the filter so our listview shows all files attached to this game
        return GameFile.objects.filter(game=gameId)

    # is user allowed to look at the file list for this game?
    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        return gameSetFileExtraGameContextAndCheckGameOwner(self)





class GameFilesReconcileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    # helper view to reconcile all uploaded files for a game
    model = GameFile
    template_name = "games/gameFileReconcile.html"

    def post(self, request, *args, **kwargs):
        game = self.extra_context['game']
        # do reconciliation; function should set flash messages to tell user what is happening
        retv = game.reconcileFiles(request)
        # set flash messages
        jrdfuncs.addFlashMessage(request, retv, False)
        # redirect to file list
        return redirect("gameFileList", slug=game.slug)


    # is user allowed to look at the file list for this game?
    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        return gameSetFileExtraGameContextAndCheckGameOwner(self)





class GameFilesDownloadView(LoginRequiredMixin, UserPassesTestMixin, View):
    # helper view to download all uploaded files for a game in a zip
    model = GameFile

    # is user allowed to look at the file list for this game?
    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        return gameSetFileExtraGameContextAndCheckGameOwner(self)
    
    def post(self, request, *args, **kwargs):
        # ask the game to build a zip file of images in debug directory
        game = self.extra_context['game']
        retDict = game.zipImageFilesIntoDebugDirectory(request)

        filePath = jrfuncs.getDictValueOrDefault(retDict, "filePath", None)
        fileName = jrfuncs.getDictValueOrDefault(retDict, "fileName", None)
        if (filePath is None):
            # set flash messages
            errorMessage = jrfuncs.getDictValueOrDefault(retDict, "error", "error unknown")
            msg = "Error, failed to generate zip file ({}).".format(errorMessage)
            jrdfuncs.addFlashMessage(request, msg, False)
            # redirect to file list
            return redirect("gameFileList", slug=game.slug)
    
        # Open the temporary zip file for reading in binary mode.
        zip_file_handle = open(filePath, 'rb')

        # Create a FileResponse to stream the file to the client.
        response = FileResponse(
            zip_file_handle,
            as_attachment=True,
            filename=fileName,
            content_type='application/zip'
        )
        return response
    



# specialty form when adding new files to a game which allows multiple uploads
class GameCreateFileView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    model = GameFile
    template_name = "games/gameFileMultipleUpload.html"
    form_class = GameFileMultipleUploadForm

    def form_valid(self, form):
        # force owner field to logged in creating user
        #form.instance.owner = self.request.user

        # get game from extra_context found during tesxt
        game = self.extra_context['game']

        # handle (possibly multiple) file uploads
        # delete existing file model (and disk file) with this name
        if form.is_valid():
            files = form.cleaned_data["files"]
            for f in files:
                self.handleFileUpload(game, f, form)

        # we have handled the multiple uploads above, how do we avoid auto creating? simple, dont inherit from CreateView

        #
        # this call creates the new file and will give it a unique name if needed to avoid overwriting which we need to fix
        formValidRetv = super().form_valid(form)
        # return validity
        return formValidRetv


    # is user allowed to do this?
    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        return gameSetFileExtraGameContextAndCheckGameOwner(self)


    def handleFileUpload(self, game, fileup, form):
        # delete exisiting file with this same filename
        # this is called during uploading so that author can reupload a new version of an image and it will just overwrite existing

        # properties
        formFileName = fileup.name
        note = form.cleaned_data["note"]
        owner = self.request.user

        # delete existing file for this game if it already exists
        game.deleteExistingFileIfFound(formFileName, True, None)

        # create new GameFile instance and save it
        instance = GameFile(filefield=fileup, game=game, gameFileType=gamefilemanager.EnumGameFileTypeName_StoryUpload, owner=owner, note = note)
        instance.save()


    def get_success_url(self):
        # success after delete goes to file list of game
        game = self.extra_context['game']
        success_url = reverse_lazy("gameFileList", args = (game.slug,))
        return success_url

















# GameFile

def gameFileSetExtraGameContextAndCheckGameOwner(gameFileViewInstance):
    obj = gameFileViewInstance.get_object()
    game = obj.game
    gameFileViewInstance.extra_context={'game': game}
    return jrdfuncs.userOwnsObjectOrStrongerPermission(game, gameFileViewInstance.request.user)



class GameFileDetailView(UserPassesTestMixin, DetailView):
    model = GameFile
    template_name = "games/gameFileDetail.html"

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        return gameFileSetExtraGameContextAndCheckGameOwner(self)




class GameFileEditView(UserPassesTestMixin, UpdateView):
    model = GameFile
    template_name = "games/gameFileEdit.html"
    fields = ["note", "filefield"]

    def form_valid(self, form):
        game = self.extra_context['game']
        #
        formFileRelativePath = form.cleaned_data['filefield'].name
        initialFileRelativePath = form.initial['filefield'].name

        # delete existing file model (and disk file) with this name - PART 1
        if form.is_valid():
            if (formFileRelativePath != initialFileRelativePath):
                # they are changing the file
                formFileName = form.cleaned_data['filefield'].name
                # delete old file
                game.deleteExistingFileIfFound(formFileName, True, form.instance)

        # this call creates the new file and will give it a unique name if needed to avoid overwriting which we need to fix
        formValidRetv = super().form_valid(form)

        # delete existing file model (and disk file) with this name - PART 2
        if form.is_valid():
            if (formFileRelativePath != initialFileRelativePath):
                # they are changing the file
                # so delete previous image held by this gamefile
                # problem is django claims the file is in use
                form.instance.filefield.close()
                game.deleteExistingMediaPathedFileIfFound(initialFileRelativePath)

        # return validity
        return formValidRetv

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        return gameFileSetExtraGameContextAndCheckGameOwner(self)




class GameFileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = GameFile
    template_name = "games/gameFileDelete.html"

    def get_success_url(self):
        # success after delete goes to file list of game
        game = self.extra_context['game']
        success_url = reverse_lazy("gameFileList", args = (game.slug,))
        return success_url

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        return gameFileSetExtraGameContextAndCheckGameOwner(self)


















class GamePlayView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Game
    template_name = "games/gamePlay.html"


    def test_func(self):
        # ensure access to this view only if game is public
        obj = self.get_object()
        return (obj.isPublic == True)











class GameFileEffectView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = GameFile
    template_name = "games/gameFileDetail.html"

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        return gameFileSetExtraGameContextAndCheckGameOwner(self)


    def post(self, request, *args, **kwargs):
        action = request.POST.get("action", "")
        result = self.performAction(request, action)
        return result


    def performAction(self, request, action):
        # ok get the parent game, and the path of the image we are working with
        game = gameFile.game
        gameFile = self.get_object()
        relativePath = gameFile.getPath()

        retv = game.runEffectOnImageFileAddOrReplaceGameFile(action, relativePath, "suffixShort", True)
        success = retv["success"]
        message = retv["message"]
        # new game file if succeeded, or default back to current one on error
        gameFile = jrfuncs.getDictValueOrDefault(retv, "gameFile", gameFile)

        # show message
        jrdfuncs.addFlashMessage(self.request, message, not success)

        # redirect to image view
        url =  reverse_lazy("gameFileDetail", kwargs={'pk':gameFile.pk})
        return HttpResponseRedirect(url)

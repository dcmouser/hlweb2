from django.shortcuts import render, redirect
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect


# python modules
import os
import uuid

# user modules
from .models import Game, GameFile
from .forms import GameFileMultipleUploadForm, GameFormForEdit, GameFormForCreate, GameFormForChangeDir
from . import gamefilemanager
from lib.jr import jrdfuncs







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
        return (obj.owner == self.request.user) or (obj.isPublic)




class GameCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Game
    form_class = GameFormForCreate
    permission_required = "games.add_game"
    template_name = "games/gameCreate.html"
    #fields = ["name", "preferredFormatPaperSize", "preferredFormatLayout", "isPublic", "text"]

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





class GameEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    form_class = GameFormForEdit
    template_name = "games/gameEdit.html"

    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)
        # add context
        viewAddGameFileListCountToContext(self, context)
        return context
    
    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (obj.owner == self.request.user)


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

        # save
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
        jrdfuncs.addFlashMessage(self.request, "There was an error parsing the game text settings. Your changes have been saved but game will not build until these are fixed.  See 'last build log' for details.", True)
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
        return (obj.owner == self.request.user)


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
        return (obj.owner == self.request.user)

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
        return (obj.owner == self.request.user)





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
        return (obj.owner == self.request.user)

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
    return (game.owner == gameFileViewInstance.request.user)


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
    return (game.owner == gameFileViewInstance.request.user)



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


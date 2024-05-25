from django.shortcuts import render, redirect
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404


# python modules
import os

# user modules
from .models import Game, GameFile
from .forms import BuildGameForm, GameFileMultipleUploadForm
from . import gamefilemanager






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


class GameDetailView(DetailView):
    model = Game
    template_name = "games/gameDetail.html"

    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)
        # add context
        viewAddGameFileListCountToContext(self, context)
        return context


class GameCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Game
    permission_required = "games.add_game"
    template_name = "games/gameCreate.html"
    fields = ["name", "preferredFormatPaperSize", "preferredFormatLayout", "isPublic", "text", "gameName", "title", "subtitle", "authors", "version", "versionDate", "summary", "difficulty", "cautions", "duration", "extraInfo", "url", "textHash", "textHashChangeDate", "publishDate", "leadStats", "settingsStatus", "buildResultsJsonField", ]

    def form_valid(self, form):
        # force owner field to logged in creating user
        form.instance.owner = self.request.user
        return super().form_valid(form)


class GameEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    template_name = "games/gameEdit.html"
    fields = ["name", "preferredFormatPaperSize", "preferredFormatLayout", "isPublic", "text", "gameName", "title", "subtitle", "authors", "version", "versionDate", "summary", "difficulty", "cautions", "duration", "extraInfo", "url", "textHash", "textHashChangeDate", "publishDate", "leadStats", "settingsStatus", "buildResultsJsonField", ]

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


class GameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Game
    template_name = "games/gameDelete.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (obj.owner == self.request.user)



class GameAllFileListView(DetailView):
    model = Game
    template_name = "games/gameAllFileList.html"

    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)
        return context







# Game related to files


# helpers -- these could go into MODEL?

def getQueryArgGameId(gameFileViewInstance, keyname):
    gameId = gameFileViewInstance.request.resolver_match.kwargs[keyname]
    return gameId

def gameFileViewHelperGetQuaryArgGameObj(gameFileViewInstance, keyname):
    gameId = getQueryArgGameId(gameFileViewInstance, keyname)
    game = get_object_or_404(Game, pk=gameId)
    return game

def gameSetFileExtraGameContextAndCheckGameOwner(gameFileViewInstance):
    game = gameFileViewHelperGetQuaryArgGameObj(gameFileViewInstance, 'pk')
    gameFileViewInstance.extra_context={'game': game}
    return (game.owner == gameFileViewInstance.request.user)


class GameListFilesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
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
        gamePk = game.pk
        success_url = reverse_lazy("gameFileList", args = (gamePk,))
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
        gamePk = game.pk
        success_url = reverse_lazy("gameFileList", args = (gamePk,))
        return success_url

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        return gameFileSetExtraGameContextAndCheckGameOwner(self)














class GameBuildView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Game
    template_name = "games/gameBuild.html"

    def test_func(self):
        # ensure access to this view only if it is owner accessing it
        obj = self.get_object()
        return (obj.owner == self.request.user)

    def post(self, request, *args, **kwargs):
        # handle BUILD request
        obj = self.get_object()

        # get the game file directory
        retv = obj.buildGame(request)

        # redirect to detail view; the buildGame() function should set flash messages to tell user what is happening
        return redirect("gameDetail", pk=obj.pk)





class GamePublishView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, DetailView):
    model = Game
    permission_required = "games.canPublishGames"
    template_name = "games/gamePublish.html"

    def test_func(self):
        # ensure access to this view only if it is owner accessing it
        obj = self.get_object()
        return (obj.owner == self.request.user)

    def post(self, request, *args, **kwargs):
        # handle request
        obj = self.get_object()

        # get the game file directory
        retv = obj.publishGame(request)

        # redirect to detail view; the buildGame() function should set flash messages to tell user what is happening
        return redirect("gameDetail", pk=obj.pk)
    





class GamePlayView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Game
    template_name = "games/gamePlay.html"
    form_class = BuildGameForm


    def test_func(self):
        # ensure access to this view only if game is public
        obj = self.get_object()
        return (obj.isPublic == True)


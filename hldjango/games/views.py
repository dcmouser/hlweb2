from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404

from .models import Game, GameFile



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


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    template_name = "games/gameCreate.html"
    fields = ["name", "text"]

    def form_valid(self, form):
        # force author field to logged in creating user
        form.instance.author = self.request.user
        return super().form_valid(form)


class GameEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    template_name = "games/gameEdit.html"
    fields = ["name", "text"]

    def get_context_data(self, **kwargs):
        # override to add context
        context = super().get_context_data(**kwargs)
        # add context
        viewAddGameFileListCountToContext(self, context)
        return context
    
    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (obj.author == self.request.user)


class GameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Game
    template_name = "games/gameDelete.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (obj.author == self.request.user)

















# GameFiles


# helpers -- these could go into MODEL?

def getQueryArgGameId(gameFileViewInstance, keyname):
    gameId = gameFileViewInstance.request.resolver_match.kwargs[keyname]
    return gameId

def gameFileViewHelperGetQuaryArgGameObj(gameFileViewInstance, keyname):
    gameId = getQueryArgGameId(gameFileViewInstance, keyname)
    game = get_object_or_404(Game, pk=gameId)
    return game




class GameFileListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
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
        game = gameFileViewHelperGetQuaryArgGameObj(self, 'pk')
        # add it to context so template can see it, and also later funcs
        self.extra_context={'game': game}
        return (game.author == self.request.user)



class GameFileCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = GameFile
    template_name = "games/gameFileCreate.html"
    fields = ["label", "filefield"]

    def form_valid(self, form):
        # force author field to logged in creating user
        form.instance.owner = self.request.user
        # get game from extra_context found during tesxt
        game = self.extra_context['game']
        # force it
        form.instance.game = game
        # ok we approve, now to parent checks
        return super().form_valid(form)

    # is user allowed to do this?
    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        game = gameFileViewHelperGetQuaryArgGameObj(self, 'pk')
        # add it to context so template can see it, and also later funcs
        self.extra_context={'game': game}
        return (game.author == self.request.user)


class GameFileDetailView(UserPassesTestMixin, DetailView):
    model = GameFile
    template_name = "games/gameFileDetail.html"

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        game = obj.game
        self.extra_context={'game': game}
        return (game.author == self.request.user)


class GameFileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = GameFile
    template_name = "games/gameFileDelete.html"

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        game = obj.game
        self.extra_context={'game': game}
        return (game.author == self.request.user)

    def get_success_url(self):
        # success after delete goes to file list of game
        game = self.extra_context['game']
        gamePk = game.pk
        success_url = reverse_lazy("gameFileList", args = (gamePk,))
        return success_url
        #return success_url

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Game



class GameListView(ListView):
    model = Game
    template_name = "games/gameList.html"


class GameDetailView(DetailView):
    model = Game
    template_name = "games/gameDetail.html"


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    template_name = "games/gameCreate.html"
    fields = ["name", "text"]

    def form_valid(self, form):
        # overriding to force author field to logged in creating user
        form.instance.author = self.request.user
        return super().form_valid(form)


class GameEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    template_name = "games/gameEdit.html"
    fields = ["name", "text"]

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return obj.author == self.request.user


class GameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Game
    template_name = "games/gameDelete.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return obj.author == self.request.user
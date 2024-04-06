from django.urls import path

from .views import GameListView, GameDetailView, GameCreateView, GameEditView, GameDeleteView
from .views import GameFileListView, GameFileCreateView, GameFileDetailView, GameFileDeleteView



urlpatterns = [
    # Game related
    path("game/<int:pk>/", GameDetailView.as_view(), name="gameDetail"),
    path("game/<int:pk>/edit/", GameEditView.as_view(), name="gameEdit"),
    path("game/<int:pk>/delete/", GameDeleteView.as_view(), name="gameDelete"),
    path("game/new/", GameCreateView.as_view(), name="gameCreate"),
    path("", GameListView.as_view(), name="gameHome"),
    #
    # game / GameList related
    path("game/<int:pk>/files/", GameFileListView.as_view(), name="gameFileList"),
    path("game/<int:pk>/files/new/", GameFileCreateView.as_view(), name="gameFileCreate"),

    # GameList related
    path("game/file/<int:pk>", GameFileDetailView.as_view(), name="gameFileDetail"),
    path("game/ile/<int:pk>/delete/", GameFileDeleteView.as_view(), name="gameFileDelete"),
]

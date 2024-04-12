from django.urls import path

from .views import GameListView, GameDetailView, GameCreateView, GameEditView, GameDeleteView
from .views import GameFileListView, GameFileCreateView, GameFileDetailView, GameFileDeleteView
from .views import GameBuildView, GamePlayView



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
    path("game/file/<int:pk>/delete/", GameFileDeleteView.as_view(), name="gameFileDelete"),

    # Game building
    path("game/<int:pk>/build/", GameBuildView.as_view(), name="gameBuild"),

    # Game playing
    path("game/<int:pk>/play/", GamePlayView.as_view(), name="gamePlay"),
]

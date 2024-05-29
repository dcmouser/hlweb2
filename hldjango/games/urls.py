from django.urls import path

from .views import GameListView, GameDetailView, GameCreateView, GameEditView, GameDeleteView, GameGenerateView, GamePlayView
from .views import GameCreateFileView, GameFilesListView, GameFilesReconcileView, GameVersionFileListView
from .views import GameFileDetailView, GameFileEditView, GameFileDeleteView
#



urlpatterns = [

    # Game file related
    path("game/file/<int:pk>", GameFileDetailView.as_view(), name="gameFileDetail"),
    path("game/file/<int:pk>/edit/", GameFileEditView.as_view(), name="gameFileEdit"),
    path("game/file/<int:pk>/delete/", GameFileDeleteView.as_view(), name="gameFileDelete"),


    # Game related
    path("game/new/", GameCreateView.as_view(), name="gameCreate"),
    path("game/<slug:slug>/", GameDetailView.as_view(), name="gameDetail"),
    path("game/<slug:slug>/edit/", GameEditView.as_view(), name="gameEdit"),
    path("game/<slug:slug>/delete/", GameDeleteView.as_view(), name="gameDelete"),
    path("", GameListView.as_view(), name="gameHome"),
    #
    # game and gamefile File related
    path("game/<slug:slug>/files/", GameFilesListView.as_view(), name="gameFileList"),
    path("game/<slug:slug>/files/new/", GameCreateFileView.as_view(), name="gameFileCreate"),
    path("game/<slug:slug>/files/reconcile/", GameFilesReconcileView.as_view(), name="gameFileReconcile"),

    #
    # game/ new filelist related
    path("game/<slug:slug>/generate/", GameGenerateView.as_view(), name="gameGenerate"),
    path("game/<slug:slug>/versionfiles/", GameVersionFileListView.as_view(), name="gameVersionFileList"),

    # Game playing
    path("game/<slug:slug>/play/", GamePlayView.as_view(), name="gamePlay"),




]

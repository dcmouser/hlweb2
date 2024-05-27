from django.urls import path

from .views import GameListView, GameDetailView, GameCreateView, GameEditView, GameDeleteView
from .views import GameCreateFileView, GameFilesListView, GameGeneratedFileListView, GameFilesReconcileView, GameVersionFileListView
#
from .views import GameFileDetailView, GameFileEditView, GameFileDeleteView
#
from .views import GameBuildView, GamePlayView, GamePublishView



urlpatterns = [
    # Game related
    path("game/<int:pk>/", GameDetailView.as_view(), name="gameDetail"),
    path("game/<int:pk>/edit/", GameEditView.as_view(), name="gameEdit"),
    path("game/<int:pk>/delete/", GameDeleteView.as_view(), name="gameDelete"),
    path("game/new/", GameCreateView.as_view(), name="gameCreate"),
    path("", GameListView.as_view(), name="gameHome"),
    #
    # game and gamefile File related
    path("game/<int:pk>/files/", GameFilesListView.as_view(), name="gameFileList"),
    path("game/<int:pk>/files/new/", GameCreateFileView.as_view(), name="gameFileCreate"),
    path("game/<int:pk>/files/reconcile/", GameFilesReconcileView.as_view(), name="gameFileReconcile"),

    #
    # game/ new filelist related
    path("game/<int:pk>/generatedfiles/", GameGeneratedFileListView.as_view(), name="gameGeneratedFileList"),
    path("game/<int:pk>/versionfiles/", GameVersionFileListView.as_view(), name="gameVersionFileList"),

    
    # Game file related
    path("game/file/<int:pk>", GameFileDetailView.as_view(), name="gameFileDetail"),
    path("game/file/<int:pk>/edit/", GameFileEditView.as_view(), name="gameFileEdit"),
    path("game/file/<int:pk>/delete/", GameFileDeleteView.as_view(), name="gameFileDelete"),

    # Game building
    path("game/<int:pk>/build/", GameBuildView.as_view(), name="gameBuild"),
    # Game publishing
    path("game/<int:pk>/publish/", GamePublishView.as_view(), name="gamePublish"),

    # Game playing
    path("game/<int:pk>/play/", GamePlayView.as_view(), name="gamePlay"),
]

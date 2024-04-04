from django.urls import path

from .views import GameListView, GameDetailView, GameCreateView, GameEditView, GameDeleteView



urlpatterns = [
    path("game/<int:pk>/", GameDetailView.as_view(), name="gameDetail"),
    path("game/<int:pk>/edit/", GameEditView.as_view(), name="gameEdit"),
    path("game/<int:pk>/delete/", GameDeleteView.as_view(), name="gameDelete"),
    path("game/new/", GameCreateView.as_view(), name="gameCreate"),
    path("", GameListView.as_view(), name="home"),
]

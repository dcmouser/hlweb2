from django.urls import include, path

from .views import ProfileView, ProfileEditView



urlpatterns = [
    path("profile/edit", ProfileEditView.as_view(), name="accountEditProfile"),
    path("profile/edit/<int:pk>", ProfileEditView.as_view(), name="accountEditProfile"),
    path("profile", ProfileView.as_view(), name="accountProfile"),
    path("profile/<int:pk>", ProfileView.as_view(), name="accountProfile"),
]


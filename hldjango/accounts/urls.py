from django.urls import path

from .views import SignupView, ProfileView, ProfileEditView



urlpatterns = [
    path("signup/", SignupView.as_view(), name="accountSignup"),

    path("profile/<int:pk>/edit/", ProfileEditView.as_view(), name="accountEditProfile"),

    path("profile/<int:pk>/", ProfileView.as_view(), name="accountProfile"),
]

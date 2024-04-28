#from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm



class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "accounts/editprofile.html"

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (obj == self.request.user)

    def get_object(self):
        return getExplicitOrDefaultToLoggedInUser(self)


class ProfileView(DetailView):
    model = CustomUser
    template_name = "accounts/profile.html"

    def get_object(self):
        return getExplicitOrDefaultToLoggedInUser(self)



# helpers
def getExplicitOrDefaultToLoggedInUser(view):
        # Here w'll retrieve the correct object to update
        
        explicitPk = view.kwargs.get("pk", None)
        if (explicitPk is None):
             # defualt logged in user
            user = view.request.user
            return user
        
        # try to lookup user explicitly
        studiedUserPk = int(explicitPk)
        studiedUser = CustomUser.objects.get(pk=studiedUserPk)
        return studiedUser

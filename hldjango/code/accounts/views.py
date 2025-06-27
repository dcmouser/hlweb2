#from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import resolve_url
from django.http import Http404
from django.contrib.auth.views import redirect_to_login

from lib.jr import jrdfuncs

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm



class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "accounts/editprofile.html"

    def test_func(self):
        # ensure access to this view only if logged in user is the owner; works with UserPassesTestMixin
        obj = self.get_object()
        return (obj == self.request.user) or jrdfuncs.userIsAuthenticatedAndGadmin(self.request.user)

    def get_object(self):
        [user, errorResponse] = getExplicitOrDefaultToLoggedInUser(self)
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user_groups to the context, retrieving groups from the logged-in user
        context["userGroupString"] = ", ".join(group.name for group in self.request.user.groups.all())
        context["viewingUserHasGadamin"] = jrdfuncs.userIsAuthenticatedAndGadmin(self.request.user)
        return context


class ProfileView(UserPassesTestMixin, DetailView):
    model = CustomUser
    template_name = "accounts/profile.html"

    def test_func(self):
        # if they arent logged in and try to access an invalid user (themselves), we redirect
        [user, errorResponse] = getExplicitOrDefaultToLoggedInUser(self)
        if (errorResponse is not None):
            self.errorResponse = errorResponse
            return False
        # ok
        self.userObj = user
        return True

    def get_object(self):
        return self.userObj

    def handle_no_permission(self):
        # just redirect based on errorResponse set earlier
        return self.errorResponse

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user_groups to the context, retrieving groups from the logged-in user
        context["userGroupString"] = ", ".join(group.name for group in self.userObj.groups.all())
        context["viewingUserHasGadamin"] = jrdfuncs.userIsAuthenticatedAndGadmin(self.request.user)
        context["userBggUrl"] = self.userObj.calcBggUrl()
        return context



# helpers
def getExplicitOrDefaultToLoggedInUser(view):
        # Here w'll retrieve the correct object to update
        
        explicitPk = view.kwargs.get("pk", None)
        if (explicitPk is None):
             # defualt logged in user
            user = view.request.user
            if (user.id is None):
                errorResponse = redirectToLoginFirst(view)
                return [None, errorResponse]
            # logged in user
            return [user, None]
        
        # try to lookup user explicitly
        studiedUserPk = int(explicitPk)
        try:
            studiedUser = CustomUser.objects.get(pk=studiedUserPk)
        except Exception as e:
            raise Http404
        return [studiedUser, None]




# redirect to login
# from https://ccbv.co.uk/projects/Django/5.0/django.contrib.auth.mixins/LoginRequiredMixin/
def redirectToLoginFirst(view):
    path = view.request.build_absolute_uri()
    resolved_login_url = resolve_url(view.get_login_url())
    path = view.request.get_full_path()
    return redirect_to_login(
        path,
        resolved_login_url,
        view.get_redirect_field_name(),
    )

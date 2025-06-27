from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser

from allauth.account.forms import SignupForm as AllauthSignupForm
from allauth.account.adapter import DefaultAccountAdapter




class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("first_name", "last_name", "bggname","webpage",)

        #first_name = forms.CharField(max_length=30)
        #last_name = forms.CharField(max_length=30)


class CustomUserChangeForm(UserChangeForm):
#class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        #fields = "__all__"
        fields = ("username", "first_name", "last_name", "email", "bggname", "webpage",)
        #fields = UserChangeForm.Meta.fields + ("bggname",)





# NOT CURRENTLY USED
class MyCustomAllAuthSignupForm(AllauthSignupForm):
  bggname = forms.CharField(max_length=32)
  webpage = forms.CharField(max_length=256)


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, False)
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        if commit:
          user.save()
        return user
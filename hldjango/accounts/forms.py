from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("bgglink",)


#class CustomUserChangeForm(UserChangeForm):
class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = "__all__"
        fields = ("username", "first_name", "last_name", "email", "bgglink", )
        #fields = UserChangeForm.Meta.fields + ("bgglink",)



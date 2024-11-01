from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser



class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["username", "email", "bgglink", "is_staff",]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("bgglink",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("bgglink",)}),)



admin.site.register(CustomUser, CustomUserAdmin)

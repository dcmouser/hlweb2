from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as DefaultGroupAdmin
from django.utils.html import format_html

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(DefaultUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    ordering = ('-date_joined',)  # Sort by date_joined in descending order
    #list_display = ["username", "email", "date_joined", "first_name", "last_name", "bggname", "webpage", "is_staff", "groups", ]
    list_display = DefaultUserAdmin.list_display + ("date_joined", "bggname", "webpage", "is_staff", "group_list",)
    fieldsets = DefaultUserAdmin.fieldsets + ((None, {"fields": ("bggname","webpage",)}),)
    add_fieldsets = DefaultUserAdmin.add_fieldsets + ((None, {"fields": ("bggname","webpage",)}),)

    def get_queryset(self, request):
        # Annotate the queryset with the number of groups per user
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(groups_count=Count('groups'))
        return queryset

    def group_list(self, obj):
        # Retrieves all groups for the user and formats them as a comma-separated list.
        groups = obj.groups.all()
        if groups:
            return format_html("<br>".join([group.name for group in groups]))
        return "-"  # Return a placeholder or empty string if no groups
    # Add sorting capability to the formatted_groups column
    group_list.admin_order_field = 'groups_count'  # Allows sorting by the annotated field



# Unregister the original User admin and register the custom one
#admin.site.unregister(User)
#admin.site.register(User, UserAdmin)
#admin.site.unregister(CustomUser)
admin.site.register(CustomUser, CustomUserAdmin)





# add list of users in each group to the group admin page
class GroupAdmin(DefaultGroupAdmin):
    def users(self, obj):
        # Retrieves all users in the group and formats them as a comma-separated list.
        users = obj.user_set.all()
        return format_html("<br>".join([user.username for user in users]))

    # Adding the users method to list_display to show it in the admin list view
    list_display = DefaultGroupAdmin.list_display + ("users",)



# Unregister the original admin and register the custom one
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)



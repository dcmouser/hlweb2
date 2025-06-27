from django.contrib import admin

from .models import Game, GameFile




# this custom admin class is used to force the (readonly) view with these auto fields; otherwise the admin site hides them
class GameAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "modified",)
#
admin.site.register(Game, GameAdmin)
admin.site.register(GameFile)

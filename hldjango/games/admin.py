from django.contrib import admin

from .models import Game, GameFile

admin.site.register(Game)
admin.site.register(GameFile)
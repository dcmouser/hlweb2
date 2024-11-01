# django modules
from rest_framework.response import Response
from rest_framework.views import APIView

# user modules
from .models import Game, GameFile



class GameApiModDateByPkView(APIView):
    def get(self, request, gamePkListStr, format=None):
        # blank
        modifiedGameDates = {}

        # split the game Pk list
        gameList = gamePkListStr.split(",")
        for index, gamePk in enumerate(gameList):
            try:
                gamePk = int(gamePk)
                game = Game.objects.get(pk=gamePk)
                modifiedGameDates[gamePk] = {"secs": int(game.modified.timestamp())}
            except Exception as e:
                modifiedGameDates["error"] = "bad game pk at index {}".format(index)
                break;

        return Response(modifiedGameDates)



class GameApiModDateBySlugView(APIView):
    def get(self, request, gamePkListStr, format=None):
        # blank
        modifiedGameDates = {}

        # split the game Pk list
        gameList = gamePkListStr.split(",")
        for index, gameSlug in enumerate(gameList):
            try:
                game = Game.objects.get(slug=gameSlug)
                modifiedGameDates[gameSlug] = {"secs": int(game.modified.timestamp())}
            except Exception as e:
                modifiedGameDates["error"] = "bad game pk at index {}".format(index)
                break;

        return Response(modifiedGameDates)



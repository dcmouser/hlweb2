# django imports
from django import template
from django.template.defaultfilters import stringfilter
from django.db.models import Q

# user imports
from ..models import Game



# register template tags / functions
register = template.Library()


@register.inclusion_tag('games/templateInclusionUserGameList.html')
def userGameList(userPk, requestingUser):
  """Get the list of games made by the user which are public
  :param: pk of the user
  :return: list of games made by this user that are public
  """

  # show unpublic?
  flagShowUnpublic = False
  if (requestingUser.is_authenticated):
    if (requestingUser.pk == userPk):
      # they are viewing their own, so show unpublic
      flagShowUnpublic = True

  #
  if (flagShowUnpublic):
    games = Game.objects.filter(Q(author=userPk))
  else:
    games = Game.objects.filter(Q(author=userPk) & Q(ispublic=True))
  #
  game_list = games
  return {'game_list': game_list}

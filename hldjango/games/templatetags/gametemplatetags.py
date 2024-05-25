# django imports
from django import template
from django.template.defaultfilters import stringfilter
from django.db.models import Q
from django.utils import timezone

# user imports
from ..models import Game
from ..gamefilemanager import GameFileManager
from games.models import Game

# python
import json
import datetime

# helpers
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from lib.jr import jrdfuncs


# register template tags / functions
register = template.Library()


@register.inclusion_tag('games/templateInclusionUserGameList.html')
def userGameList(userPk, requestingUser):
  """Get the list of games made by the user which are public
  :param: pk of the user
  :return: list of games made by this user that are public
  """

  # show NonPublic?
  flagShowNonPublic = False
  if (requestingUser.is_authenticated):
    if (requestingUser.pk == userPk):
      # they are viewing their own, so show NonPublic
      flagShowNonPublic = True

  #
  if (flagShowNonPublic):
    games = Game.objects.filter(Q(owner=userPk))
  else:
    games = Game.objects.filter(Q(owner=userPk) & Q(isPublic=True))
  #
  game_list = games
  return {'game_list': game_list}





@register.inclusion_tag('games/templateInclusionFileUrlList.html')
def fileUrlList(requestingUser, gamePk, gameFileTypeName):
  """Build a list of files for a specific game of a specific type, with urls
  :param: requestingUser - user making the request; currently ignores
  :param: gamePk - the game pk
  :param: gameFileTypeName - the name of the game type  
  :return: list of gfiles with their urls
  """

  # get game
  game = Game.objects.get(pk=gamePk)
  if (game is None):
      raise Exception("Failed to find game pk={}.".format(gamePk))

  # show NonPublic?
  flagShowNonPublic = False
  if (requestingUser.is_authenticated):
    if (requestingUser.pk == game.owner):
      # they are viewing their own, so show NonPublic
      flagShowNonPublic = True

  # game file manager helper
  gameFileManager = GameFileManager(game)
  fileList = gameFileManager.buildFileList(gameFileTypeName)

  # build results
  buildResults = game.getBuildResultsAnnotated(gameFileTypeName)
  buildResultsHtml = formatBuildResultsForHtmlList(buildResults)

  return {"fileList": fileList, "buildResultsHtml": buildResultsHtml}




def formatBuildResultsForHtmlList(buildResults):
  listItems = list()
  queueStatus = jrfuncs.getDictValueOrDefault(buildResults, "queueStatus", None)
  if (queueStatus is None):
    return ""
  #
  queuedDateNiceStr = convertTimeStampForBuildResult(buildResults, "buildDateQueued")

  if (queueStatus == Game.GameQueueStatusEnum_Completed) or (queueStatus == Game.GameQueueStatusEnum_Errored):
    # queue is done running
    listItems.append({"key": "Status", "label": jrdfuncs.lookupDjangoChoiceLabel(queueStatus, Game.GameQueueStatusEnum)})
    if (queueStatus != Game.GameQueueStatusEnum_Completed):
      listItems.append({"key": "Queue status", "label": jrdfuncs.lookupDjangoChoiceLabel(queueStatus, Game.GameQueueStatusEnum), "errorLevel": 2})
    listItems.append({"key": "Originally queued on", "label": queuedDateNiceStr})
    # show how long it took to run
    durationQueued = calcNiceDurationStringForBuildResult(buildResults, "buildDateQueued", "buildDateEnd")
    durationBuild = calcNiceDurationStringForBuildResult(buildResults, "buildDateStart", "buildDateEnd")
    listItems.append({"key": "Total time in queue", "label": durationQueued})
    listItems.append({"key": "Actual time to build", "label": durationBuild})
  else:
    # incomplete queue
    listItems.append({"key": "Queue status", "label": jrdfuncs.lookupDjangoChoiceLabel(queueStatus, Game.GameQueueStatusEnum)})
    listItems.append({"key": "Queued on", "label": queuedDateNiceStr})
    listItems.append({"key": "Current time waiting in queue", "label": durationQueued})

  # add build info
  if (queueStatus != Game.GameQueueStatusEnum_None):
    buildVersion = jrfuncs.getDictValueOrDefault(buildResults, "buildVersion", "n/a")
    buildVersionDate = jrfuncs.getDictValueOrDefault(buildResults, "buildVersionDate", "n/a")
    buildVersionStr = "{} ({})".format(buildVersion, buildVersionDate)
    listItems.append({"key": "Version build", "label": buildVersionStr})
  #
  buildError = jrfuncs.getDictValueOrDefault(buildResults, "buildError", False)
  if (buildError):
    buildLog = jrfuncs.getDictValueOrDefault(buildResults, "buildLog", "n/a")
    listItems.append({"key": "ERRORS", "label": buildLog, "errorLevel": 2})
  #
  publishResult = jrfuncs.getDictValueOrDefault(buildResults, "publishResult", None)
  if (publishResult is not None):
    publishDateNiceStr = convertTimeStampForBuildResult(buildResults, "publishDate")
    #listItems.append({"key": "Published on", "label": publishDateNiceStr})
    publishErrored = jrfuncs.getDictValueOrDefault(buildResults, "publishErrored", False)
    listItems.append({"key": publishResult, "label": "on " + publishDateNiceStr, "errorLevel": 2 if publishErrored else 0})

  retHtml = formatDictListAsHtmlList(listItems)
  return retHtml



def formatDictListAsHtmlList(listItems):
  retHtml = ""
  for li in listItems:
    keyStr = li["key"]
    labelStr = li["label"]
    #
    errorLevel = li["errorLevel"] if ("errorLevel" in li) else 0
    if (errorLevel>0):
      labelStr = '<font color="red">' + labelStr + '</font>'
    #
    lineHtml = "<li><b>{}</b>: {}</li>\n".format(keyStr, labelStr)
    retHtml += lineHtml
  retHtml = "<ul>\n" + retHtml + "</ul>\n"
  return retHtml



def calcNiceDurationStringForBuildResult(buildResults, startKeyName, endKeyName):
  startTimestamp = jrfuncs.getDictValueOrDefault(buildResults, startKeyName, None)
  endTimestamp = jrfuncs.getDictValueOrDefault(buildResults, endKeyName, None)
  if (startTimestamp is None):
    return "n/a"
  if (endTimestamp is None):
    endTimestamp = timezone.now().timestamp()
  durationTimestamp = endTimestamp - startTimestamp
  durationNiceStr = jrfuncs.niceElapsedTimeStr(durationTimestamp)
  return durationNiceStr



def convertTimeStampForBuildResult(buildResults, timestampKeyName):
    timestamp = jrfuncs.getDictValueOrDefault(buildResults, timestampKeyName, None)
    if (timestamp is None):
      return "n/a"
    resultDateTime = datetime.datetime.fromtimestamp(timestamp)
    dateNiceStr = jrfuncs.getNiceDateTimeCompact(resultDateTime)
    return dateNiceStr



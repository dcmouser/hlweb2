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
  return {"game_list": game_list, "flagShowNonPublic": flagShowNonPublic}





@register.inclusion_tag('games/templateInclusionFileUrlList.html')
def fileUrlList(requestingUser, gamePk, gameFileTypeName, optionStr):
  """Build a list of files for a specific game of a specific type, with urls
  :param: requestingUser - user making the request; currently ignores
  :param: gamePk - the game pk
  :param: gameFileTypeName - the name of the game type  
  :return: list of gfiles with their urls
  """

  # options
  options = {}
  optionStrList = optionStr.split(",")
  if ("date" in optionStrList):
    options["showDate"] = True
  if ("noInfo" in optionStrList):
    options["noInfo"] = True

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
  fileList.sort(key = lambda x: sortBuiltFileListNicelyKeyFunc(x))

  # build results
  buildResults = game.getBuildResultsAnnotated(gameFileTypeName)
  buildResultsHtml = formatBuildResultsForHtmlList(game, buildResults)

  return {"fileList": fileList, "buildResultsHtml": buildResultsHtml, "options": options}




def formatBuildResultsForHtmlList(game, buildResults):
  listItems = list()
  queueStatus = jrfuncs.getDictValueOrDefault(buildResults, "queueStatus", None)
  if (queueStatus is None):
    return ""
  #
  queuedDateNiceStr = convertTimeStampForBuildResult(buildResults, "buildDateQueued")
  durationQueued = calcNiceDurationStringForBuildResult(buildResults, "buildDateQueued", "buildDateEnd")
  isCanceled = jrfuncs.getDictValueOrDefault(buildResults,"canceled", False)
  lastBuildDateStartTimestamp = jrfuncs.getDictValueOrDefault(buildResults, "lastBuildDateStart", 0)
  lastBuildVersion = jrfuncs.getDictValueOrDefault(buildResults, "lastBuildVersion", "")
  lastBuildVersionDate = jrfuncs.getDictValueOrDefault(buildResults, "lastBuildVersionDate", "")
  buildDateTimestamp = jrfuncs.getDictValueOrDefault(buildResults, "buildDateStart", None)
    
  if (queueStatus == Game.GameQueueStatusEnum_Completed) or (queueStatus == Game.GameQueueStatusEnum_Errored) or (queueStatus == Game.GameQueueStatusEnum_Aborted):
    # queue is done running
    statusStr = jrdfuncs.lookupDjangoChoiceLabel(queueStatus, Game.GameQueueStatusEnum)
    if (isCanceled):
      statusStr = "CANCELED ({})".format(statusStr)
    listItems.append({"key": "Status", "label": statusStr, "errorLevel": 2 if (isCanceled) or (queueStatus == Game.GameQueueStatusEnum_Errored) else 0})
    listItems.append({"key": "Originally queued on", "label": queuedDateNiceStr})
    # show how long it took to run
    durationBuild = calcNiceDurationStringForBuildResult(buildResults, "buildDateStart", "buildDateEnd")
    listItems.append({"key": "Total time in queue", "label": durationQueued})
    listItems.append({"key": "Actual time to build", "label": durationBuild})
  else:
    # incomplete queue
    statusStr = jrdfuncs.lookupDjangoChoiceLabel(queueStatus, Game.GameQueueStatusEnum)
    statusErrorLevel = 1
    if (isCanceled):
      if (queueStatus == Game.GameQueueStatusEnum_Running):
        statusStr = "CANCELED (but still running)"
      else:
        statusStr = "CANCELED"
      statusErrorLevel = 2
    #
    listItems.append({"key": "Queue status", "label": statusStr, "errorLevel": statusErrorLevel})
    listItems.append({"key": "Queued on", "label": queuedDateNiceStr})
    listItems.append({"key": "Current time waiting in queue", "label": durationQueued})


  # add build info
  if (queueStatus != Game.GameQueueStatusEnum_None):
    buildVersion = jrfuncs.getDictValueOrDefault(buildResults, "buildVersion", "n/a")
    buildVersionDate = jrfuncs.getDictValueOrDefault(buildResults, "buildVersionDate", "n/a")
    if (buildVersion == buildVersionDate):
      buildVersionStr = buildVersion
    else:
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
    listItems.append({"key": "Publish result", "label": publishResult + "on " + publishDateNiceStr, "errorLevel": 2 if publishErrored else 0})
  
  # is it out of date
  buildTextHash = jrfuncs.getDictValueOrDefault(buildResults, "buildTextHash", "")
  if (buildTextHash != game.textHash):
    # out of date
    lastEditDateTimestamp = game.textHashChangeDate.timestamp()

    if (buildDateTimestamp is not None):
      difSecs = lastEditDateTimestamp-buildDateTimestamp
      durationStr = jrfuncs.niceElapsedTimeStr(difSecs)
    elif (lastBuildDateStartTimestamp!=0):
      difSecs = lastEditDateTimestamp-lastBuildDateStartTimestamp
      durationStr = jrfuncs.niceElapsedTimeStr(difSecs)
    else:
      durationStr = "some time"
    listItems.append({"key": "OUT OF DATE", "label": "Game text was modified {} after this build.".format(durationStr), "errorLevel": 2})
  else:
    listItems.append({"key": "Up to date", "label": "Yes; built with latest game text edits."})


  # last build for aborts
  if True:
      if (lastBuildDateStartTimestamp!=0) and ((buildDateTimestamp is None) or (buildDateTimestamp != lastBuildDateStartTimestamp)):
        lastBuildDate = datetime.datetime.fromtimestamp(lastBuildDateStartTimestamp)
        listItems.append({"key": "Files last built", "label": jrfuncs.getNiceDateTime(lastBuildDate)})
        lastBuildVersionStr = "{} ({})".format(lastBuildVersion, lastBuildVersionDate)
        listItems.append({"key": "Version of files last built", "label": lastBuildVersionStr})

  retHtml = formatDictListAsHtmlList(listItems)
  return retHtml



def formatDictListAsHtmlList(listItems):
  retHtml = ""
  for li in listItems:
    keyStr = li["key"]
    labelStr = li["label"]
    #
    errorLevel = li["errorLevel"] if ("errorLevel" in li) else 0
    if (errorLevel==2):
      labelStr = '<font color="red">' + labelStr + '</font>'
    if (errorLevel>0):
      labelStr = '<font color="orange">' + labelStr + '</font>'
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



def sortBuiltFileListNicelyKeyFunc(fileEntry):
  # helper function for sorting thie file list nicely (zip at top, followed by summary, followed by filename alpha)
  fileName = fileEntry["name"]
  if (fileName.endswith(".zip")):
    prefix = "0"
  elif ("summary" in fileName):
    prefix = "1"
  else:
    prefix = "2"
  return prefix + "_" + fileName.lower()

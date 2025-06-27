# django imports
from django import template
from django.template.defaultfilters import stringfilter
from django.db.models import Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.conf import settings

# user imports
from ..models import Game
from .. import gamefilemanager
from ..gamefilemanager import GameFileManager
from games.models import Game


# python
import json
import datetime
import html

# helpers
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from lib.jr import jrdfuncs
from lib.casebook.casebookDefines import *

# attempt to peek huey
from huey.contrib.djhuey import HUEY as huey
from huey.constants import EmptyData

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
  flagMyGames = False
  if (requestingUser.is_authenticated):
    if (requestingUser.pk == userPk):
      # they are viewing their own, so show NonPublic
      flagMyGames = True
      flagShowNonPublic = True

  #
  if (flagShowNonPublic):
    games = Game.objects.filter(Q(owner=userPk))
  else:
    games = Game.objects.filter(Q(owner=userPk) & Q(isPublic=True))
  #
  game_list = games
  return {"game_list": game_list, "flagShowNonPublic": flagShowNonPublic, "flagMyGames": flagMyGames}





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
  if ("showDate" in optionStrList):
    options["showDate"] = True
  if ("noInfo" in optionStrList):
    options["noInfo"] = True

  # get game
  game = Game.objects.get(pk=gamePk)
  if (game is None):
      raise Exception("Failed to find game pk={}.".format(gamePk))

  # show NonPublic?
  flagShowNonPublic = jrdfuncs.userOwnsObjectOrStrongerPermission(game, requestingUser)
  #flagShowNonPublic = False
  #if (requestingUser.is_authenticated):
  #  if (requestingUser.pk == game.owner):
  #    # they are viewing their own, so show NonPublic
  #    flagShowNonPublic = True

  # game file manager helper
  gameFileManager = GameFileManager(game)
  fileList = gameFileManager.buildFileList(gameFileTypeName)

  if ("sortDate" in optionStrList):
    fileList.sort(key = lambda x: sortBuiltFileListByDate(x), reverse=True)
  else:
    fileList.sort(key = lambda x: sortBuiltFileListNicelyKeyFunc(x))

  if ("noCover" in optionStrList):
      fileList = list(filter(lambda x: ("_cover." not in x["name"]), fileList))

  # build results
  buildResults = game.getBuildResultsAnnotated(gameFileTypeName)
  buildResultsHtml = formatBuildResultsForHtmlList(game, gameFileTypeName, buildResults)

  buildError = jrfuncs.getDictValueOrDefault(buildResults, "buildError", False)

  return {"fileList": fileList, "buildResultsHtml": buildResultsHtml, "buildError": buildError, "options": options}






@register.simple_tag()
def gamePublishInfoString(game):
  # nice info string about publication data and ispublic
  buildResults = game.getBuildResultsAnnotated(gamefilemanager.EnumGameFileTypeName_Published)
  #
  publishResult = jrfuncs.getDictValueOrDefault(buildResults, "publishResult", None)
  if (publishResult is not None):
    publishDateNiceStr = convertTimeStampForBuildResult(buildResults, "publishDate")
    #listItems.append({"key": "Published on", "label": publishDateNiceStr})
    publishErrored = jrfuncs.getDictValueOrDefault(buildResults, "publishErrored", False)
    publishDateNiceStr = convertTimeStampForBuildResult(buildResults, "publishDate")
    retStr = publishDateNiceStr
    if (publishErrored):
      retStr += " - with errors"
  else:
    retStr = "no"
  
  if (game.isPublic):
    #retStr += " (public)"
    pass
  else:
    retStr += " (private)"

  return retStr







@register.simple_tag()
def jrconfirmRebuildIfNotNeeded(game, gameFileTypeName):
  # add a confirm onclick if the game is up to date
  buildResults = game.getBuildResultsAnnotated(gameFileTypeName)
  queueStatus = jrfuncs.getDictValueOrDefault(buildResults, "queueStatus", None)
  buildTextHash = jrfuncs.getDictValueOrDefault(buildResults, "buildTextHash", "")
  if (buildTextHash == game.textHash) and (queueStatus == Game.GameQueueStatusEnum_Completed):
    retStr = "onclick=\"return confirm('These files appear to be up to date; are you sure you want to rebuild?');\""
  elif (queueStatus == Game.GameQueueStatusEnum_Running):
    isCanceled = jrfuncs.getDictValueOrDefault(buildResults,"canceled", False)
    if (isCanceled):
      retStr = "onclick=\"return confirm('This job was previously canceled but is still processing; are you sure you want to restart the task before the prior job completes?');\""
    else:
      retStr = "onclick=\"return confirm('This job is currently running; are you sure you want to abort the current job and restart it?');\""
  else:
    retStr = ""
  #
  return mark_safe(retStr)




@register.filter(name="naifblank")
def naifblank(value):
    if (value is None) or (value==""):
      return "n/a"
    return value






@register.filter()
def isPublishedOutOfDateAndReady(game):
  # return true if the published files are OLDER than the draft files
  buildResultsPublished = game.getBuildResults(gamefilemanager.EnumGameFileTypeName_Published)
  buildResultsDraft = game.getBuildResults(gamefilemanager.EnumGameFileTypeName_DraftBuild)
  checkVarName = "buildDateEnd"
  buildPublishedCheckVar = jrfuncs.getDictValueOrDefault(buildResultsPublished, checkVarName, None)
  buildDraftCheckVar = jrfuncs.getDictValueOrDefault(buildResultsDraft, checkVarName, None)
  if (buildPublishedCheckVar != buildDraftCheckVar):
    buildDraftQueueStatus = jrfuncs.getDictValueOrDefault(buildResultsDraft, "queueStatus", None)
    if (buildDraftQueueStatus == Game.GameQueueStatusEnum_Completed):
      return True
  return False


@register.filter()
def isPublished(game):
  # return true if there are published files that can be "deleted"
  buildResults = game.getBuildResults(gamefilemanager.EnumGameFileTypeName_Published)
  queueStatus = jrfuncs.getDictValueOrDefault(buildResults, "queueStatus", None)
  if (queueStatus == None):
    # not published or previously delete
    return False
  # ATTN: TODO
  return True

@register.filter()
def isNotPublishedOrOutOfDate(game):
  # this can happen if there are no draft files
  return ((not isPublishedOutOfDateAndReady(game)) and (not isPublished(game)))



@register.filter
def jrwrapurl(url):
    """
    Prepend 'https://' to the URL if it doesn't already start with 'http://' or 'https://'.
    """
    if url and not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url


























def formatBuildResultsForHtmlList(game, gameFileTypeName, buildResults):

  # doesnt work properly; can't distinguish between running and lost processes
  optionTryDetectAbandonedHueys = False

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
  buildVersion = jrfuncs.getDictValueOrDefault(buildResults, "buildVersion", "")
  buildVersionDate = jrfuncs.getDictValueOrDefault(buildResults, "buildVersionDate", "")
  lastBuildTool = jrfuncs.getDictValueOrDefault(buildResults, "lastBuildTool", "")
  buildTool = jrfuncs.getDictValueOrDefault(buildResults, "buildTool", "")
  buildDateTimestamp = jrfuncs.getDictValueOrDefault(buildResults, "buildDateStart", None)
  leadStatsSummary = jrfuncs.getDictValueOrDefault(buildResults, "leadStatsSummary", "n/a")
  buildTextHash = jrfuncs.getDictValueOrDefault(buildResults, "buildTextHash", "")

  # is it out of date
  if (buildTextHash != game.textHash):
    # out of date
    isOutOfDate = True
    lastEditDateTimestamp = game.textHashChangeDate.timestamp() if (game.textHashChangeDate is not None) else 0
  else:
    isOutOfDate = False

  isRunning = (queueStatus == Game.GameQueueStatusEnum_Running)

  if (isRunning):
    # let's ask huey if its REALLY still running, or lost on a reboot, etc
    # ATTN: this doesnt currently work since huey seems to return EmptyData at start of task run
    if (optionTryDetectAbandonedHueys):
      taskid = jrfuncs.getDictValueOrDefault(buildResults, "taskId", "")
      if (taskid != ""):
        hueyStorage = huey.storage
        hasData = hueyStorage.has_data_for_key(taskid)
        if (not hasData):
          taskResult = huey.result(taskid, preserve=True)
          is_pending = (taskResult is not None)
          if (not is_pending) and False:
            queueStatus = Game.GameQueueStatusEnum_Aborted
            buildResults["queueStatus"] = queueStatus
            # force update
            game.setBuildResults(gameFileTypeName, buildResults)
            game.save()

  if (queueStatus == Game.GameQueueStatusEnum_Completed) or (queueStatus == Game.GameQueueStatusEnum_Errored) or (queueStatus == Game.GameQueueStatusEnum_Aborted):
    # queue is done running
    statusStr = jrdfuncs.lookupDjangoChoiceLabel(queueStatus, Game.GameQueueStatusEnum)
    if (isCanceled):
      statusStr = "CANCELED ({})".format(statusStr)
    if (queueStatus == Game.GameQueueStatusEnum_Errored):
      # modified statusStr if its out of date error
      if (isOutOfDate):
        statusStr += " on older source (needs rebuild)"

    listItems.append({"key": "Status", "label": statusStr, "errorLevel": 2 if (isCanceled) or (queueStatus == Game.GameQueueStatusEnum_Errored) else 0})
    listItems.append({"key": "Originally queued on", "label": queuedDateNiceStr})
    # show how long it took to run
    durationBuild = calcNiceDurationStringForBuildResult(buildResults, "buildDateStart", "buildDateEnd")
    listItems.append({"key": "Total time in queue", "label": durationQueued})
    listItems.append({"key": "Actual time to build", "label": durationBuild})
    listItems.append({"key": "Lead stats", "label": leadStatsSummary})
    showProgress = False
  else:
    # incomplete queue (running,etc.)

    statusStr = jrdfuncs.lookupDjangoChoiceLabel(queueStatus, Game.GameQueueStatusEnum)
    statusErrorLevel = 1
    if (isCanceled):
      if (isRunning):
        statusStr = "CANCELED (but waiting for task to finish)"
      else:
        statusStr = "CANCELED"
      statusErrorLevel = 2
    showProgress = True



    #
    listItems.append({"key": "Queue status", "label": statusStr, "errorLevel": statusErrorLevel})
    listItems.append({"key": "Queued on", "label": queuedDateNiceStr})
    listItems.append({"key": "Current time waiting in queue", "label": durationQueued})

    if (isRunning):
      # it's running
      durationRunning = calcNiceDurationStringForBuildResult(buildResults, "buildDateStart", None)
      listItems.append({"key": "Currently running for", "label": durationRunning})
    if (showProgress):
      progress = jrfuncs.getDictValueOrDefault(buildResults, "progress", 0)
      listItems.append({"key": "Current progress", "label": "{}%".format(int(progress*100))})

  #
  buildError = jrfuncs.getDictValueOrDefault(buildResults, "buildError", False)
  if (False):
    # use to handle errors here
    if (buildError):
      buildLog = jrfuncs.getDictValueOrDefault(buildResults, "buildLog", "n/a")
      listItems.append({"key": "ERRORS", "label": buildLog, "errorLevel": 2})
  #
  publishResult = jrfuncs.getDictValueOrDefault(buildResults, "publishResult", None)
  if (publishResult is not None):
    publishDateNiceStr = convertTimeStampForBuildResult(buildResults, "publishDate")
    #listItems.append({"key": "Published on", "label": publishDateNiceStr})
    publishErrored = jrfuncs.getDictValueOrDefault(buildResults, "publishErrored", False)
    listItems.append({"key": "Publish result", "label": publishResult + " on " + publishDateNiceStr, "errorLevel": 2 if publishErrored else 0})
  



  # always show last edit date?
  extraSourceInfo = ""
  lastEditDateTimestamp = game.textHashChangeDate.timestamp() if (game.textHashChangeDate is not None) else 0
  if (lastEditDateTimestamp!=0):
    editDate = datetime.datetime.fromtimestamp(lastEditDateTimestamp)
    extraSourceInfo = " ({})".format(jrfuncs.getNiceDateTime(editDate))


  if (not isRunning):
    # ATTN: im not sure we should ever look at lastBuildDateStartTimestamp
    durationStr = "at an undetermined time"
    if (lastEditDateTimestamp!=0) and ( (buildDateTimestamp is None) or (lastEditDateTimestamp>buildDateTimestamp)):
      # edited after last build
      if (buildDateTimestamp is None):
        # new build
        durationStr = " and needs building"
      elif (buildDateTimestamp is not None):
        # built previously but finished
        if (lastEditDateTimestamp>buildDateTimestamp):
          difSecs = lastEditDateTimestamp-buildDateTimestamp
          durationStr = jrfuncs.niceElapsedTimeStr(difSecs) + ' after latest build'
      #
      if (gameFileTypeName == gamefilemanager.EnumGameFileTypeName_Published):
        extraOutOfDate = " (draft rebuild needed)"
      else:
        extraOutOfDate = ""
      listItems.append({"key": "OUT OF DATE"+ extraOutOfDate, "label": "Game text was modified {}{}.".format(durationStr,extraSourceInfo), "errorLevel": 2})
    else:
      isOutOfDate = False
      if (buildError):
        listItems.append({"key": "Up to date", "label": "Errors were generated from latest game text edits{}.".format(extraSourceInfo)})
      else:
        listItems.append({"key": "Up to date", "label": "Yes; built with latest game text edits{}.".format(extraSourceInfo)})


  # last build for aborts
  if (buildDateTimestamp is not None):
      buildDate = datetime.datetime.fromtimestamp(buildDateTimestamp)
      if (isRunning):
        listItems.append({"key": "Started building files", "label": jrfuncs.getNiceDateTime(buildDate)})
      else:
        listItems.append({"key": "Files last built", "label": jrfuncs.getNiceDateTime(buildDate)})
      #
      if (isRunning):
        currentBuildVersionStr = "{} ({})".format(buildVersion, buildVersionDate)
        if (buildTool!=""):
          currentBuildVersionStr += " - building with " + buildTool
        listItems.append({"key": "Version of files being built", "label": "v" + currentBuildVersionStr})
      else:
        lastBuildVersionStr = "{} ({})".format(lastBuildVersion, lastBuildVersionDate)
        if (lastBuildTool!=""):
          lastBuildVersionStr += " - built with " + lastBuildTool
        listItems.append({"key": "Version of files last built", "label": "v" + lastBuildVersionStr})



  retHtml = formatDictListAsHtmlList(listItems)


  # NEW errors
  if (True):
    buildError = jrfuncs.getDictValueOrDefault(buildResults, "buildError", False)
    if (buildError):
      buildLog = jrfuncs.getDictValueOrDefault(buildResults, "buildLog", "n/a")
      if (isOutOfDate):
        errorCssClass = "buildLogErrorOld"
      else:
        errorCssClass = "buildLogError"
      # https://www.w3schools.com/tags/tag_textarea.asp
      logHtml = ""
      logHtml += '<textarea cols="200" rows="12" readonly="true" class="buildLog ' + errorCssClass + '">\n' + html.escape(buildLog) + '\n</textarea>\n'
      #
      retHtml += "\n" + logHtml + "\n"


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
  if (endKeyName is not None):
    endTimestamp = jrfuncs.getDictValueOrDefault(buildResults, endKeyName, None)
  else:
    endTimestamp = None
  #
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



def sortBuiltFileListByDate(fileEntry):
  # helper function for sorting thie file list nicely (zip at top, followed by summary, followed by filename alpha)
  return fileEntry["fileDateTime"]






@register.filter(is_safe=True)
def gameThumbnailForGameList(game):
  # we'd like to find a filename ending in _cover.jpg or _cover.png, if we find it image it
  optionLightbox = True

  # try to find a published cover image
  gameFileManager = GameFileManager(game)
  [imageFilePath, imageFileUrl] = gameFileManager.findCoverImage()

  if (imageFileUrl is None):
    # default to a generic thumbnail?
    optionLightbox = False
    imageFileUrl =  str(settings.STATIC_URL) + "images/" + settings.JR_DEF_FILENAME_IMAGE_MISSING
  
  if (imageFileUrl is None):
    html = "&nbsp;"
  else:
    html = '<img class = "gameThumbnail" src="{}" alt="game {} thumbnail"></img>'.format(imageFileUrl, game.name)
    if (optionLightbox):
      html = '<a href="' + imageFileUrl + '" data-toggle="lightbox">' + html + '</a>'

  return mark_safe(html)












@register.simple_tag()
def markdownGameInstructions(game):
  #
  import mistletoe
  instructions = game.instructions

  # ATTN: convert markdown to html
  if (instructions==""):
    html = "<p>No additional instructions.</p>"
  else:
    html = mistletoe.markdown(instructions)

  return mark_safe(html)

















@register.filter()
def userOwnsObjectOrStrongerPermission(obj, user):
  return jrdfuncs.userOwnsObjectOrStrongerPermission(obj, user)





@register.filter()
def niceGameDateFormat(dateObj):
  # this can happen if there are no draft files
  dateString = jrfuncs.getNiceDateTimeCompact(dateObj)
  return dateString



# see https://huey.readthedocs.io/en/latest/consumer.html
# see https://negativeepsilon.com/en/posts/huey-async-task-execution/


# django
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, db_task, task
from huey.contrib.djhuey import HUEY as huey
from django.utils import timezone

# python modules
from datetime import datetime
import os
import time
import traceback

# user modules
from lib.jr.jrfuncs import jrprint
from lib.jr import jrdfuncs
#from hueyconfig import huey
# casebook
from .casebookwrapper import CasebookWrapper

from lib.jr import jrfuncs















# module global funcs
# see https://huey.readthedocs.io/en/latest/api.html#Huey.task
@db_task(context=True)
def queueTaskBuildStoryPdf(gameModelPk, requestOptions, task=None):
    # imports needing in function to avoid circular?
    from games.models import Game
    from games import gamefilemanager
    from games.gamefilemanager import GameFileManager

    # starting time of run
    timeStart = time.time()
    # start time of build
    buildDateStart = timezone.now()

    # reset
    buildLog = ""
    buildErrorStatus = False
    flagCleanAfter = "minimal"

    # options
    buildMode = requestOptions["buildMode"]
    optionZipFiles = True


    # REload game instance AGAIN to save state, in case it has changed
    game = Game.get_or_none(pk=gameModelPk)
    if (game is None):
        raise Exception("Failed to find game pk={} for updating build results - stage 2.".format(gameModelPk))
        # can't continue below


    # previous settings -- NOTE that this REQUIRES caller to set these prior to initial run
    buildResultsPrevious = game.getBuildResults(buildMode)
    buildDateQueuedTimestamp = jrfuncs.getDictValueOrDefault(buildResultsPrevious, "buildDateQueued", None)
    buildDateQueued = jrdfuncs.convertTimeStampToDateTimeDefaultNow(buildDateQueuedTimestamp)
    isCanceled = jrfuncs.getDictValueOrDefault(buildResultsPrevious,"canceled", False)

    #
    # properties
    gameInternalName = game.name
    gameName = game.gameName
    gameText = game.text
    gameTextHash = game.textHash
    preferredFormatPaperSize = game.preferredFormatPaperSize
    preferredFormatLayout = game.preferredFormatLayout
    #
    # parsed values
    gameBuildVersion = game.version
    gameBuildVersionDate = game.versionDate


    # update build status and save
    buildResults = {
        "queueStatus": Game.GameQueueStatusEnum_Running,
        "buildDateQueued": buildDateQueued.timestamp(),
        "buildVersion": gameBuildVersion,
        "buildVersionDate": gameBuildVersionDate,
        "buildTextHash": gameTextHash,
        "buildDateStart": buildDateStart.timestamp(),
        }
    # add task info
    if (task is not None):
        buildResults["taskType"] = "huey"
        buildResults["taskId"] = task.id
    # copy over last build results that are important
    game.copyLastBuildResultsTo(buildResultsPrevious, buildResults)

    # sanity check -- this is not working?
    if (isCanceled):
        buildResults["queueStatus"] = Game.GameQueueStatusEnum_Aborted
        buildResults["canceled"] = True

    # set
    game.setBuildResults(buildMode, buildResults)
    #
    # save NOW early (and again later) since it will take some time and something else might run in meantime
    game.save()
    jrprint("Saving new huey job ({}) starting.".format(buildMode))

    # normally this wouildnt happen because a cancel would stop the task from even running
    # but its potentially possible for it to start running and then get canceled before it makes progress beyond here?
    if (False):
        if (isCanceled):
            return "Build aborted because task was canceled."


    # create new gamefilemanager; which will be intermediary for accessing game data
    gfmanager = GameFileManager(game)


    # what outputs do we want parser to build/generate
    buildList = []
    if (buildMode in ["buildPreferred"]):
        # build preferred format
        suffix = calcDefaultSuffixForBuildMode(buildMode)
        build = {"label": "preferred format build", "task": "latexBuildPdf", "exsuffix": suffix, "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "gameFileType": gamefilemanager.EnumGameFileTypeName_PreferredBuild, "outputPath": gfmanager.getDirectoryPathForGameType(gamefilemanager.EnumGameFileTypeName_PreferredBuild)}
        addCalculatedFieldsToBuild(build)
        buildList.append(build)
        if (optionZipFiles):
            # build zip
            zipBuild = {"label": "zipping built files", "task": "zipFiles", "suffix": suffix, "gameFileType": gamefilemanager.EnumGameFileTypeName_PreferredBuild, "outputPath": gfmanager.getDirectoryPathForGameType(gamefilemanager.EnumGameFileTypeName_PreferredBuild)}
            addCalculatedFieldsToBuild(zipBuild)
            buildList.append(zipBuild)
        flagCleanAfter = "minimal"
    if (buildMode in ["buildDebug"]):
        # build debug format
        suffix = calcDefaultSuffixForBuildMode(buildMode)
        build = {"label": "debug build", "task": "latexBuildPdf", "exsuffix": suffix, "reportMode": True, "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "gameFileType": gamefilemanager.EnumGameFileTypeName_Debug, "outputPath": gfmanager.getDirectoryPathForGameType(gamefilemanager.EnumGameFileTypeName_Debug)}
        addCalculatedFieldsToBuild(build)
        buildList.append(build)
        if (optionZipFiles):
            # build zip
            zipBuild = {"label": "zipping built files", "task": "zipFiles", "suffix": suffix, "gameFileType": gamefilemanager.EnumGameFileTypeName_Debug, "outputPath": gfmanager.getDirectoryPathForGameType(gamefilemanager.EnumGameFileTypeName_Debug)}
            addCalculatedFieldsToBuild(zipBuild)
            buildList.append(zipBuild)
        flagCleanAfter = "none"
    if (buildMode in ["buildDraft"]):
        suffix = calcDefaultSuffixForBuildMode(buildMode)
        # build complete list; all combinations of page size and layout
        buildList += generateCompleteBuildList(game, gfmanager)
        if (optionZipFiles):
            # build zip
            zipBuild = {"label": "zipping built files", "task": "zipFiles", "suffix": suffix, "gameFileType": gamefilemanager.EnumGameFileTypeName_DraftBuild, "outputPath": gfmanager.getDirectoryPathForGameType(gamefilemanager.EnumGameFileTypeName_DraftBuild)}
            addCalculatedFieldsToBuild(zipBuild)
            buildList.append(zipBuild)
        flagCleanAfter = "extra"
        #
    if (buildMode not in ["buildPreferred", "buildDebug", "buildDraft"]):
        raise Exception("Build mode not understood: '{}'.".format(buildMode))
    
    # initialize the directory of files, deleting any that exist previously
    gfmanager.deleteFilesInBuildListDirectories(buildList)



    # start the build log
    buildLog = "Building: '{}'...\n".format(buildMode)
















    # create options to pass to parser object
    buildOptions = {
        "localMediaDirectory" : gfmanager.getDirectoryPathForGameUploads(),
        "sharedMediaDirectory" : gfmanager.getSharedDirectory(),
        "baseFileName": gameName,
        }

    # DO THE ACTUAL BUILD
    # this may take a long time to run (minutes)

    try:
        casebook = CasebookWrapper() 
    except Exception as e:
        raise e

    # new attempt to use a progress callback
    progressCallback = lambda progressDict: progressCallbackTaskBuildFunc(gameModelPk, buildMode, progressDict)

    try:
        # parse text
        casebook.runBuilds(gameText, buildList, buildOptions, progressCallback)

    except Exception as e:
        msg = jrfuncs.exceptionPlusSimpleTraceback(e, "building storybook")
        jrprint(msg)
        buildLog += msg
        buildErrorStatus = True











    # add file generated list
    generatedFileList = casebook.getGeneratedFileList()
    if (len(generatedFileList)>0):
        if (buildLog != ""):
            buildLog += "\n\n-----\n\n"
        buildLog += "Generated file list:\n" + "\n".join(generatedFileList)


    # now store result in game model instance gameModelPk
    buildErrorStatus = (buildErrorStatus or casebook.isErrored())
    buildLogParser = casebook.getBuildLog()
    if (buildLogParser != ""):
        if (buildLog != ""):
            buildLog += "\n\n-----\n\n"
        buildLog += "Parser Build Log:\n" + buildLogParser

    gameLeadStatsSummary = casebook.getLeadStats()["summaryString"]

    # elapsed time
    # ATTN: this needs rewriting
    timeEnd = time.time()
    timeSecs = timeEnd - timeStart
    timeStr = jrfuncs.niceElapsedTimeStrMinsSecs(timeSecs)
    # wait time
    waitSecs = (timezone.now().timestamp() - buildDateQueued.timestamp())
    #waitSecs = (timezone.now() - buildDateQueued).total_seconds()
    waitStr = jrfuncs.niceElapsedTimeStrMinsSecs(waitSecs)
    #
    buildLog += "\nActual build time: {}.".format(timeStr)
    buildLog += "\nBuild wait time: {}.".format(waitStr)


    # REload game instance AGAIN to save state, in case it has changed
    game = Game.get_or_none(pk=gameModelPk)
    if (game is None):
        raise Exception("Failed to find game pk={} for updating build results - stage 2.".format(gameModelPk))
        # can't continue below

    buildResultsPrevious = game.getBuildResults(buildMode)
    isCanceled = jrfuncs.getDictValueOrDefault(buildResultsPrevious,"canceled", False)

    # ATTN: a nice sanity check here would be to see if game text has changed
    # ATTN: we may not need to do this anymore, as long as we report when displaying that text hash has changed so its out of date
    if (False) and (game.textHash != gameTextHash):
        # ERROR
        buildErrorStatus = True
        buildLog += "ERROR: Game model text modified by author during build; needs rebuild."

    queueStatus = jrfuncs.getDictValueOrDefault(buildResultsPrevious, "queueStatus", None)
    if (queueStatus != Game.GameQueueStatusEnum_Running):
        # a new job has replaced us while we were running, so abort
        return "Aborted saving of build results because job was requeued while running."
    
    # queue status
    if (isCanceled):
        queueStatus = Game.GameQueueStatusEnum_Aborted
    elif (buildErrorStatus):
        queueStatus = Game.GameQueueStatusEnum_Errored
    else:
        queueStatus = Game.GameQueueStatusEnum_Completed

    # update build status with results of build, AND with the version we actually built (which may go out of date later)
    buildDateEnd = timezone.now()
    buildResults = {
        "queueStatus": queueStatus,
        "buildDateQueued": buildDateQueued.timestamp(),
        "buildDateStart": buildDateStart.timestamp(),
        "buildDateEnd": buildDateEnd.timestamp(),
        "buildVersion": gameBuildVersion,
        "buildVersionDate": gameBuildVersionDate,
        "buildTextHash": gameTextHash,
        "buildError": buildErrorStatus,
        "buildLog": buildLog,
        "canceled": isCanceled,
        "lastBuildDateStart": buildDateStart.timestamp(),
        "lastBuildVersion": gameBuildVersion,
        "lastBuildVersionDate": gameBuildVersionDate,
        "leadStatsSummary": gameLeadStatsSummary
    }
    # add task info
    if (task is not None):
        buildResults["taskType"] = "huey"
        buildResults["taskId"] = task.id

    # set build results buildlog
    game.setBuildResults(buildMode, buildResults)

    # log
    # jrprint("Updated model game {} after completion of queueTaskBuildStoryPdf with queuestats = {}.".format(gameModelPk, game.queueStatus))

    # result for instant run
    if (buildErrorStatus):
        retv = "Errors during build"
    else:
        retv = "Build was successful"
    #

    # store last build log into main game buildLog
    niceDateStr = jrfuncs.getNiceDateTime(buildDateStart)
    game.lastBuildLog = retv + " on {}.\n".format(niceDateStr) + buildLog
    if (not buildErrorStatus):
        game.lastBuildLog += "\n" + game.leadStats

    # save game
    game.save()

    jrprint("Finished huey job '{}'; status = '{}'.".format(buildMode, queueStatus))

    return retv

def calcDefaultSuffixForBuildMode(buildMode):
    # remove the word "build", lowercase first letter, prefix with "_"
    label = buildMode.replace("build","")
    label = label.lower()
    label = "_"+ label
    return label








def generateCompleteBuildList(game, gfmanager):
    # loop twice, the first time just calculate buildCount
    # imports needing in function to avoid circular?
    from games.models import Game
    from games import gamefilemanager

    optionBuildCover = True
    optionBuildDebug = False

    buildList = []
    index = 0
    buildCount = 0
    # summary and debug
    if (optionBuildCover):
        buildCount += 1
    if (optionBuildDebug):
        buildCount += 1
    # customs
    buildCount += 1
    #
    preferredFormatPaperSize = game.preferredFormatPaperSize
    preferredFormatLayout = game.preferredFormatLayout
    # properties
    gameInternalName = game.name
    gameName = game.gameName
    gameFileType = gamefilemanager.EnumGameFileTypeName_DraftBuild
    #

    if (True):
        # programmatic
        # we make two passes since the first pass can just count the builds needed
        for stage in ["precount","run"]:
            for paperSize in Game.GameFormatPaperSizeCompleteList:
                for layout in Game.GameFormatLayoutCompleteList:
                    # skip certain configurations
                    columns = calcColumnsFromLayout(layout)
                    maxColumns = calcMaxColumnsFromPaperSize(paperSize)
                    if (columns>maxColumns):
                        # skip it
                        continue
                    if (stage=="precount"):
                        buildCount += 1
                        continue
                    # add the build
                    index += 1
                    label = "complete build {} of {} ({} x {})".format(index, buildCount, layout, paperSize)
                    #
                    build = {"label": label, "task": "latexBuildPdf", "cleanExtras": True, "paperSize": paperSize, "layout": layout, "gameFileType": gameFileType, "gameFileType": gameFileType, "outputPath": gfmanager.getDirectoryPathForGameType(gameFileType)}
                    addCalculatedFieldsToBuild(build)
                    buildList.append(build)

    # summary in letter format?
    if (optionBuildCover):
        index += 1
        label = "complete build {} of {} (cover)".format(index, buildCount)
        paperSize = Game.GamePreferredFormatPaperSize_Letter
        #
        coverImageExtension = "jpg"
        build = {"label": label, "task": "latexBuildPdf", "cleanExtras": True, "paperSize": paperSize, "layout": Game.GamePreferredFormatLayout_Solo, "variant": "cover", "convert": coverImageExtension, "gameFileType": gameFileType, "outputPath": gfmanager.getDirectoryPathForGameType(gameFileType), }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)

    if (True):
        # customs
        index += 1
        label = "complete build {} of {} (custom_soloprn_letter_largefont)".format(index, buildCount)
        build = {"label": label, "task": "latexBuildPdf", "cleanExtras": True, "exsuffix": "_largefont", "paperSize": Game.GamePreferredFormatPaperSize_Letter, "layout": Game.GamePreferredFormatLayout_Solo, "fontSize": "16", "gameFileType": gameFileType, "outputPath": gfmanager.getDirectoryPathForGameType(gameFileType) }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)

    # also debug, in preferred format
    if (optionBuildDebug):
        index += 1
        label = "complete build {} of {} (debug)".format(index, buildCount)
        build = {"label": label, "task": "latexBuildPdf", "cleanExtras": True, "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "debug", "gameFileType": gameFileType, "outputPath": gfmanager.getDirectoryPathForGameType(gameFileType), }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)
    #


    return buildList
# ---------------------------------------------------------------------------















# ---------------------------------------------------------------------------
def publishGameFiles(game):
    # imports needing in function to avoid circular?
    from games.models import Game, calculateGameFilePathRuntime
    from games import gamefilemanager
    from games.gamefilemanager import GameFileManager

    # create new gamefilemanager; which will be intermediary for accessing game data
    gameFileManager = GameFileManager(game)
    
    # publish files
    publishErrored = False
    currentDate = timezone.now()
    try:
        publishResult = gameFileManager.copyPublishFiles(gamefilemanager.EnumGameFileTypeName_DraftBuild, gamefilemanager.EnumGameFileTypeName_Published)
    except Exception as e:
        msg = jrfuncs.exceptionPlusSimpleTraceback(e, "trying to copy publish files")
        jrprint(msg)
        publishResult = msg
        publishErrored = True

    if (not publishErrored):
        # update states and save
        publishResult = "Published (promoted from draft)"
        game.publishDate = currentDate
        # set generic game lead stats for listing on game listing, etc.
        buildResultsDraft = game.getBuildResults(gamefilemanager.EnumGameFileTypeName_DraftBuild)
        gameLeadStatsSummary = jrfuncs.getDictValueOrDefault(buildResultsDraft, "leadStatsSummary", "n/a")
        game.leadStats = gameLeadStatsSummary

    # update
    # this is different from build, we are essentially copying from draft
    overrideResults = {
        "publishResult": publishResult,
        "publishErrored": publishErrored,
        "publishDate": currentDate.timestamp(),
        "queueStatus": Game.GameQueueStatusEnum_Completed,
        "canceled": False,
        }
    game.copyBuildResults("published", "buildDraft", overrideResults)

    # save
    game.save()

    return publishResult



def unpublishGameFiles(game):
    # imports needing in function to avoid circular?
    from games.models import Game, calculateGameFilePathRuntime
    from games import gamefilemanager
    from games.gamefilemanager import GameFileManager

    # create new gamefilemanager; which will be intermediary for accessing game data
    gameFileManager = GameFileManager(game)
    
    # publish files
    publishErrored = False
    currentDate = timezone.now()
    try:
        publishResult = gameFileManager.prepareEmptyFileDirectoryForGameType(gamefilemanager.EnumGameFileTypeName_Published)
    except Exception as e:
        msg = jrfuncs.exceptionPlusSimpleTraceback(e, "trying to remove previously published game files")
        jrprint(msg)
        publishResult = msg
        publishErrored = True

    if (not publishErrored):
        # update states and save
        publishResult = "Successfully removed previously published files"

    buildResults = {
        "publishResult": publishResult,
        "publishErrored": publishErrored,
        "publishDate": currentDate.timestamp(),
        "queueStatus": None, #Game.GameQueueStatusEnum_None,
        "canceled": False,
        "buildDateQueued": None,
        "buildVersion": None,
        "buildVersionDate": None,
        "buildTextHash": None,
        }
    # set
    game.setBuildResults("published", buildResults)
    # clear leadstats
    game.leadStats = "n/a"

    # save
    game.save()

    return publishResult
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
def checkBuildFiles(buildDir, buildList):
    errorMessage = ""
    for build in buildList:
        filePathBuild = buildDir + "/" + build["gameName"] + build["suffix"] + ".pdf"
        if (not jrfuncs.pathExists(filePathBuild)):
            errorMessage += "Missing file '{}'.\n".format(filePathBuild)
    if (errorMessage!=""):
        return errorMessage
    return None


def publishBuildFiles(buildDir, buildList, publishDir):
    errorMessage = ""
    for build in buildList:
        filePathBuild = buildDir + "/" + build["gameName"] + build["suffix"] + ".pdf"
        if (not jrfuncs.pathExists(filePathBuild)):
            errorMessage += "Missing file '{}'.\n".format(filePathBuild)
        else:
            filePathPublish = publishDir + "/" + build["gameName"] + build["suffix"] + ".pdf"
            jrfuncs.copyFilePath(filePathBuild, filePathPublish)
    if (errorMessage!=""):
        return errorMessage
    return None
# ---------------------------------------------------------------------------























# ---------------------------------------------------------------------------
# helpers


def addCalculatedFieldsToBuild(build):
    #
    task = build["task"]
    if (task == "zipFiles"):
        # done
        return

    if ("suffix" not in build):
        suffix = calcBuildNameSuffixForVariant(build)
        build["suffix"] = suffix

    if ("exsuffix" in build):
        # add
        exsuffix = build["exsuffix"]
        build["suffix"] = exsuffix + build["suffix"]

    layout = build["layout"]
    #
    paperSize = build['paperSize']
    latexPaperSize = build['latexPaperSize'] if ('latexPaperSize' in build) else calcPaperSizeLatexFromPaperSize(paperSize)
    fontSize = build['fontSize'] if ('fontSize' in build) else calcFontSizeFromPaperSize(paperSize)
    doubleSided = build['doubleSided'] if ('doubleSided' in build) else calcDoubledSidednessFromLayout(layout)
    leadColumns = build['leadColumns'] if ('leadColumns' in build) else calcColumnsFromLayout(layout)
    leadBreak = build['leadBreak'] if ('leadBreak' in build) else calcLeadBreakFromLayout(layout)
    #

    build["latexfontSize"] = fontSize
    build["latexPaperSize"] = latexPaperSize
    build["doubleSided"] = doubleSided
    build["leadColumns"] = leadColumns
    build["leadBreak"] = leadBreak



def calcBuildNameSuffixForVariant(build):
    buildVariant = build["variant"] if ("variant" in build) else None
    if (buildVariant=="zip"):
        return ""
    label = build["label"]
    paperSize = build["paperSize"] if ("paperSize" in build) else "na"
    layout = build["layout"]

    #
    if (buildVariant is None):
        suffix = "_{}_{}".format(layout.lower(), paperSize.lower())
    elif (buildVariant=="debug"):
        suffix = "_{}_{}_{}".format("debug", layout.lower(), paperSize.lower())
    elif (buildVariant=="cover"):
        suffix = "_cover"
    else:
        raise Exception("Variant mode '{}' not understood in runBuildList for label '{}'".format(buildVariant, label))
    #
    return suffix



def calcFontSizeFromPaperSize(paperSize):
    # imports needing in function to avoid circular?
    from games.models import Game
    #
    paperSizeToFontMap = {
        Game.GamePreferredFormatPaperSize_Letter: "10",
        Game.GamePreferredFormatPaperSize_A4: "10",
        Game.GamePreferredFormatPaperSize_B5: "8",
        Game.GamePreferredFormatPaperSize_A5: "8",            
    }
    return paperSizeToFontMap[paperSize]


def calcPaperSizeLatexFromPaperSize(paperSize):
    # imports needing in function to avoid circular?
    from games.models import Game
    #
    paperSizeToLatexPaperSizeMap = {
        Game.GamePreferredFormatPaperSize_Letter: "letter",
        Game.GamePreferredFormatPaperSize_A4: "a4",
        Game.GamePreferredFormatPaperSize_B5: "b5",
        Game.GamePreferredFormatPaperSize_A5: "a5",            
    }
    return paperSizeToLatexPaperSizeMap[paperSize]


def calcDoubledSidednessFromLayout(layout):
    # imports needing in function to avoid circular?
    from games.models import Game
    #
    layoutToDoubleSidednessMap = {
        Game.GamePreferredFormatLayout_Solo: False,
        Game.GamePreferredFormatLayout_SoloPrint: True,
        Game.GamePreferredFormatLayout_OneCol: True,
        Game.GamePreferredFormatLayout_TwoCol: True,            
    }
    return layoutToDoubleSidednessMap[layout]


def calcColumnsFromLayout(layout):
    # imports needing in function to avoid circular?
    from games.models import Game
    #
    layoutToColumnsMap = {
        Game.GamePreferredFormatLayout_Solo: 1,
        Game.GamePreferredFormatLayout_SoloPrint: 1,
        Game.GamePreferredFormatLayout_OneCol: 1,
        Game.GamePreferredFormatLayout_TwoCol: 2,            
    }
    return layoutToColumnsMap[layout]


def calcLeadBreakFromLayout(layout):
    # imports needing in function to avoid circular?
    from games.models import Game
    #
    layoutToLeadBreakMap = {
        Game.GamePreferredFormatLayout_Solo: "solo",
        Game.GamePreferredFormatLayout_SoloPrint: "solo",
        Game.GamePreferredFormatLayout_OneCol: "none",
        Game.GamePreferredFormatLayout_TwoCol: "none",
    }
    return layoutToLeadBreakMap[layout]


def calcMaxColumnsFromPaperSize(paperSize):
    # imports needing in function to avoid circular?
    from games.models import Game
    #
    paperSizeToMaxColumnsMap = {
        Game.GamePreferredFormatPaperSize_Letter: 2,
        Game.GamePreferredFormatPaperSize_A4: 2,
        Game.GamePreferredFormatPaperSize_B5: 2,
        Game.GamePreferredFormatPaperSize_A5: 1,            
    }
    return paperSizeToMaxColumnsMap[paperSize]
# ---------------------------------------------------------------------------























# ---------------------------------------------------------------------------
def isTaskCanceled(taskType, taskId):
    if (taskType is None) or (taskId is None):
        return False
    return huey.is_revoked(taskId)

def cancelPreviousQueuedTask(taskType, taskId):
    if (taskType=="huey"):
        isRevoked = huey.is_revoked(taskId)
        if (isRevoked):
            return False
        retv = huey.revoke_by_id(taskId)
        return True
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def progressCallbackTaskBuildFunc(gameModelPk, buildMode, progressDict):
    # return True to continue, False to abort
    from games.models import Game
    optionUpdatePercentageComplete = True

    # fetch current results area
    game = Game.get_or_none(pk=gameModelPk)
    if (game is None):
        raise Exception("Failed to find game pk={} for updating build results - stage 2.".format(gameModelPk))
        # can't continue below
    # previous settings -- NOTE that this REQUIRES caller to set these prior to initial run
    buildResults = game.getBuildResults(buildMode)
    isCanceled = jrfuncs.getDictValueOrDefault(buildResults,"canceled", False)
    if (isCanceled):
        # return false saying to abort
        return False
    queueStatus = jrfuncs.getDictValueOrDefault(buildResults, "queueStatus", None)
    if (queueStatus != Game.GameQueueStatusEnum_Running):
        # a new job has replaced us while we were running, so abort
        return False


    if (optionUpdatePercentageComplete):
        if (queueStatus == Game.GameQueueStatusEnum_Running):
            # update progress
            # ATTN: it would be nice to do a sanity check on the task id
            buildResults["progress"] = progressDict["progress"]
            # set and update
            game.setBuildResults(buildMode, buildResults)
            game.save()

    # tell caller to continue
    return True
# ---------------------------------------------------------------------------



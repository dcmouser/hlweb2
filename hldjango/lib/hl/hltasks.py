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
from hueyconfig import huey
from lib.hl import hlparser
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
    jrprint("!!!! saving new huey job ({}) starting.".format(buildMode))

    # normally this wouildnt happen because a cancel would stop the task from even running
    # but its potentially possible for it to start running and then get canceled before it makes progress beyond here?
    if (False):
        if (isCanceled):
            return "Build aborted because task was canceled."


    # create new gamefilemanager; which will be intermediary for accessing game data
    gameFileManager = GameFileManager(game)


    # what outputs do we want parser to build/generate
    buildList = []
    if (buildMode in ["buildPreferred"]):
        # build preferred format
        build = {"label": "preferred format build", "gameName": gameName, "format": "pdf", "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "normal", "gameFileType": gamefilemanager.EnumGameFileTypeName_PreferredBuild, }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)
        if (True):
            # build zip
            zipBuild = {"label": "zipping built files", "gameName": gameName, "variant": "zip", "layout": None, "gameFileType": gamefilemanager.EnumGameFileTypeName_PreferredBuild}
            buildList.append(zipBuild)
        flagCleanAfter = "minimal"
    if (buildMode in ["buildDebug"]):
        # build debug format
        build = {"label": "debug build", "gameName": gameName, "format": "pdf", "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "debug", "gameFileType": gamefilemanager.EnumGameFileTypeName_Debug, }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)
        if (True):
            # build zip
            zipBuild = {"label": "zipping built files", "gameName": gameName, "variant": "zip", "layout": None, "gameFileType": gamefilemanager.EnumGameFileTypeName_Debug}
            buildList.append(zipBuild)
        flagCleanAfter = "none"
    if (buildMode in ["buildDraft"]):
        # build complete list; all combinations of page size and layout
        buildList += generateCompleteBuildList(game, False)
        if (True):
            # build zip
            zipBuild = {"label": "zipping built files", "gameName": gameName, "variant": "zip", "layout": None, "gameFileType": gamefilemanager.EnumGameFileTypeName_DraftBuild}
            buildList.append(zipBuild)
        flagCleanAfter = "extra"
        #
    if (buildMode not in ["buildPreferred", "buildDebug", "buildDraft"]):
        raise Exception("Build mode not understood: '{}'.".format(buildMode))
    
    # initialize the directory of files, deleting any that exist previously
    gameFileManager.deleteFilesInBuildListDirectories(buildList)

    # create options
    hlDirPath = os.path.abspath(os.path.dirname(__file__))
    optionsDirPath = hlDirPath + "/options"
    dataDirPath = hlDirPath + "/hldata"
    templateDirPath = hlDirPath + "/templates"
    overrideOptions = {
        "hlDataDir": dataDirPath,
        "templatedir": templateDirPath,
        "buildList": buildList,
        "gameFileManager": gameFileManager,
        }

    # DO THE ACTUAL BUILD
    # this may take a long time to run (minutes)

    # start the build log
    buildLog = "Building: '{}'...\n".format(buildMode)

    try:
        # create hl parser
        hlParser = hlparser.HlParser(optionsDirPath, overrideOptions)

        # parse text
        hlParser.parseStoryTextIntoBlocks(gameText, 'hlweb2')

        # run pdf generation
        retv = hlParser.runBuildList(flagCleanAfter)
    
    except Exception as e:
        msg = jrfuncs.exceptionPlusSimpleTraceback(e, "building storybook")
        jrprint(msg)
        buildLog += msg
        buildErrorStatus = True


    # add file generated list
    generatedFileList = hlParser.getGeneratedFileList()
    if (len(generatedFileList)>0):
        if (buildLog != ""):
            buildLog += "\n\n-----\n\n"
        buildLog += "Generated file list:\n" + "\n".join(generatedFileList)


    # now store result in game model instance gameModelPk
    buildErrorStatus = (buildErrorStatus or hlParser.getBuildErrorStatus())
    buildLogParser = hlParser.getBuildLog()
    if (buildLogParser != ""):
        if (buildLog != ""):
            buildLog += "\n\n-----\n\n"
        buildLog += "Parser Build Log:\n" + buildLogParser



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
        buildLog = "ERROR: Game model text modified by author during build; needs rebuild."

    # queue status
    if (buildErrorStatus):
        queueStatus = Game.GameQueueStatusEnum_Errored
    elif (isCanceled):
        queueStatus = Game.GameQueueStatusEnum_Aborted
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
        # update lead stats on successful build
        game.leadStats = hlParser.getLeadStats()["summaryString"]
    #

    # store last build log into main game buildLog
    niceDateStr = jrfuncs.getNiceDateTime(buildDateStart)
    game.lastBuildLog = retv + " on {}.\n".format(niceDateStr) + buildLog
    if (not buildErrorStatus):
        game.lastBuildLog += "\n" + game.leadStats

    # save game
    game.save()

    jrprint("Finished huey job '{}'; status = '{}' !!!!".format(buildMode, queueStatus))

    return retv







def generateCompleteBuildList(game, flagDebugIncluded):
    # loop twice, the first time just calculate buildCount
    # imports needing in function to avoid circular?
    from games.models import Game
    from games import gamefilemanager

    buildList = []
    index = 0
    buildCount = 0
    # summary and debug
    buildCount += 1
    if (flagDebugIncluded):
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
        # customs
        index += 1
        build = {"label": "SOLOPRN_LETTER_LargeFont", "gameName": gameName, "suffix": "_SOLOPRN_LETTER_LargeFont", "format": "pdf", "paperSize": Game.GamePreferredFormatPaperSize_Letter, "layout": Game.GamePreferredFormatLayout_Solo, "variant": "normal", "fontSize": "16pt", "gameFileType": gameFileType, }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)

    if (True):
        # programmatic
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
                    build = {"label": label, "gameName": gameName, "format": "pdf", "paperSize": paperSize, "layout": layout, "variant": "normal", "gameFileType": gameFileType, }
                    addCalculatedFieldsToBuild(build)
                    buildList.append(build)

    # also debug, in preferred format
    if (flagDebugIncluded):
        index += 1
        label = "complete build {} of {} (debug)".format(index, buildCount)
        build = {"label": label, "gameName": gameName, "format": "pdf", "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "debug", "gameFileType": gameFileType, }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)
    #
    # summary in letter format
    index += 1
    label = "complete build {} of {} (summary)".format(index, buildCount)
    paperSize = Game.GamePreferredFormatPaperSize_Letter
    #
    build = {"label": label, "gameName": gameName, "format": "pdf", "paperSize": paperSize, "layout": Game.GamePreferredFormatLayout_Solo, "variant": "summary", "gameFileType": gameFileType, }
    addCalculatedFieldsToBuild(build)
    buildList.append(build)

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
        publishResult = "Successfully published"
        game.publishDate = currentDate

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
    paperSize = build["paperSize"]
    layout = build["layout"]
    #
    fontSize = build['fontSize'] if ('fontSize' in build) else calcFontSizeFromPaperSize(paperSize)
    paperSizeLatex = build['paperSizeLatex'] if ('paperSizeLatex' in build) else calcPaperSizeLatexFromPaperSize(paperSize)
    doubleSided = build['doubleSided'] if ('doubleSided' in build) else calcDoubledSidednessFromLayout(layout)
    columns = build['columns'] if ('columns' in build) else calcColumnsFromLayout(layout)
    solo = build['solo'] if ('solo' in build) else calcSoloFromLayout(layout)
    #
    if ("suffix" not in build):
        suffix = calcBuildNameSuffixForVariant(build)
        build["suffix"] = suffix
    build["fontSize"] = fontSize
    build["paperSizeLatex"] = paperSizeLatex
    build["doubleSided"] = doubleSided
    build["columns"] = columns
    build["solo"] = solo



def calcBuildNameSuffixForVariant(build):
    label = build["label"]
    format = build["format"]
    paperSize = build["paperSize"]
    layout = build["layout"]
    buildVariant = build["variant"]    
    #
    if (buildVariant=="normal"):
        suffix = "_{}_{}".format(layout, paperSize)
    elif (buildVariant=="debug"):
        suffix = "_{}_{}_{}".format("debug", layout, paperSize)
    elif (buildVariant=="summary"):
        suffix = "_summary"
    else:
        raise Exception("Variant mode '{}' not understood in runBuildList for label '{}'".format(buildVariant, label))
    #
    return suffix



def calcFontSizeFromPaperSize(paperSize):
    # imports needing in function to avoid circular?
    from games.models import Game
    #
    paperSizeToFontMap = {
        Game.GamePreferredFormatPaperSize_Letter: "10pt",
        Game.GamePreferredFormatPaperSize_A4: "10pt",
        Game.GamePreferredFormatPaperSize_B5: "8pt",
        Game.GamePreferredFormatPaperSize_A5: "8pt",            
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


def calcSoloFromLayout(layout):
    # imports needing in function to avoid circular?
    from games.models import Game
    #
    layoutToSoloMap = {
        Game.GamePreferredFormatLayout_Solo: True,
        Game.GamePreferredFormatLayout_SoloPrint: True,
        Game.GamePreferredFormatLayout_OneCol: False,
        Game.GamePreferredFormatLayout_TwoCol: False,
    }
    return layoutToSoloMap[layout]


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

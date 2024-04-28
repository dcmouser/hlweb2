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
from hueyconfig import huey
from lib.hl import hlparser
from lib.jr import jrfuncs

















# module global funcs
@db_task()
def queueTaskBuildStoryPdf(game, requestOptions):
    # starting time
    timeStart = time.time()

    # reset
    buildLog = ""
    buildErrorStatus = False
    flagCleanAfter = True

    # options
    buildMode = requestOptions["buildMode"]

    # imports needing in function to avoid circular?
    from games.models import Game, calculateGameFilePathRuntime

    # update model queue status before we start
    game.queueStatus = Game.GameQueueStatusEnum_Running
    # save
    game.save()


    # properties
    gameModelPk = game.pk
    gameInternalName = game.name
    gameName = game.gameName
    gameText = game.text
    preferredFormatPaperSize = game.preferredFormatPaperSize
    preferredFormatLayout = game.preferredFormatLayout


    # what outputs do we want parser to build/generate
    optionBuildZip = True
    optionZipSuffix = ''
    buildList = []
    if (buildMode == "buildPreferred"):
        # build preferred format
        build = {"label": "preferred format build", "gameName": gameName, "format": "pdf", "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "normal", }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)
        optionZipSuffix = '_preferred'
    elif (buildMode == "buildDebug"):
        # build debug format
        build = {"label": "debug build", "gameName": gameName, "format": "pdf", "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "debug", }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)
        optionZipSuffix = '_debug'
    elif (buildMode == "buildComplete"):
        # build complete list; all combinations of page size and layout
        buildList = generateCompleteBuildList(game, True)
        optionBuildZip = True
        optionZipSuffix = '_complete'
        #
    elif (buildMode == "buildPublish") and (False):
        # this is trickier; first we would like to build anything that needs building and THEN publish
        # ATTN: TODO; for now we want caller to handle this differently
        pass
    else:
        raise Exception("Build mode not understood: '{}'.".format(buildMode))


    # directories
    buildDir = calculateGameFilePathRuntime(game, "build", False)
    imageDir = calculateGameFilePathRuntime(game, "uploads", False)
    # create build directory if it doesn't exist yet
    jrfuncs.createDirIfMissing(buildDir)

    # create options
    hlDirPath = os.path.abspath(os.path.dirname(__file__))
    optionsDirPath = hlDirPath + "/options"
    dataDirPath = hlDirPath + "/hldata"
    templateDirPath = hlDirPath + "/templates"
    overrideOptions = {
        "workingdir": buildDir,
        "storyDirectories": ["$workingdir"],
        "hlDataDir": dataDirPath,
        "templatedir": templateDirPath,
        "savedir": buildDir,
        "imagedir": imageDir,
        "buildList": buildList,
        "optionBuildZip": optionBuildZip,
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
        if (False):
            # OLD:
            hlParser.runAllSteps()
        else:
            # NEW
            retv = hlParser.runBuildList(flagCleanAfter)
    except Exception as e:
        #msg = "ERROR: Exception while building storybook. Exception = " + str(e)
        #msg = "ERROR: Exception while building storybook. Exception = " + traceback.format_exc(e)
        msg = "ERROR: Exception while building storybook. Exception = " + repr(e)
        msg += "; " + traceback.format_exc()
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




    # ATTN: a nice sanity check here would be to see if game text has changed
    if (game.text != gameText):
        # ERROR
        buildErrorStatus = True
        buildLog = "ERROR: Game model text modified by author during build; needs rebuild."


    if (not buildErrorStatus):
        # success, should we zip?
        if (optionBuildZip) and (len(generatedFileList)>0):
            zipFilePath = jrfuncs.makeZipFile(generatedFileList, buildDir, gameName + optionZipSuffix)


    # elapsed time
    timeEnd = time.time()
    timeSecs = timeEnd - timeStart
    timeStr = jrfuncs.niceElapsedTimeStrMinsSecs(timeSecs)
    # wait time
    waitSecs = (timezone.now() - game.queueDate).total_seconds()
    waitStr = jrfuncs.niceElapsedTimeStrMinsSecs(waitSecs)
    #
    buildLog += "\nActual build time: {}.".format(timeStr)
    buildLog += "\nBuild wait time: {}.".format(waitStr)


    # REload game instance AGAIN to save state, in case it has changed
    from games.models import Game
    game = Game.objects.get(pk=gameModelPk)
    if (game is None):
        raise Exception("Failed to find game pk={} for updating build results - stage 2.".format(gameModelPk))
        # can't continue below


    # update
    game.buildLog = buildLog
    game.buildDate = timezone.now()
    game.isBuildErrored = buildErrorStatus
    if (game.isBuildErrored):
        game.queueStatus = Game.GameQueueStatusEnum_Errored
        game.needsBuild = True
    else:
        game.queueStatus = Game.GameQueueStatusEnum_Completed
        game.needsBuild = False
    #
    game.buildStats = hlParser.getLeadStats()["summaryString"]

    # save
    game.save()

    # log
    jrprint("Updated model game {} after completion of queueTaskBuildStoryPdf with queuestats = {}.".format(gameModelPk, game.queueStatus))

    # result for instant run
    if (game.isBuildErrored):
        retv = "Errors during build"
    else:
        retv = "Build was successful"
    #
    return retv




def generateCompleteBuildList(game, flagDebugIncluded):
    # loop twice, the first time just calculate buildCount
    # imports needing in function to avoid circular?
    from games.models import Game, calculateGameFilePathRuntime

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
    #
    if (True):
        # customs
        index += 1
        build = {"label": "SOLOPRN_LETTER_LargeFont", "gameName": gameName, "suffix": "_SOLOPRN_LETTER_LargeFont", "format": "pdf", "paperSize": Game.GamePreferredFormatPaperSize_Letter, "layout": Game.GamePreferredFormatLayout_Solo, "variant": "normal", "fontSize": "16pt",}
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
                    build = {"label": label, "gameName": gameName, "format": "pdf", "paperSize": paperSize, "layout": layout, "variant": "normal", }
                    addCalculatedFieldsToBuild(build)
                    buildList.append(build)

    # also debug, in preferred format
    if (flagDebugIncluded):
        index += 1
        label = "complete build {} of {} (debug)".format(index, buildCount)
        build = {"label": label, "gameName": gameName, "format": "pdf", "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "debug", }
        addCalculatedFieldsToBuild(build)
        buildList.append(build)
    #
    # summary in letter format
    index += 1
    label = "complete build {} of {} (summary)".format(index, buildCount)
    paperSize = Game.GamePreferredFormatPaperSize_Letter
    #
    build = {"label": label, "gameName": gameName, "format": "pdf", "paperSize": paperSize, "layout": Game.GamePreferredFormatLayout_Solo, "variant": "summary"}
    addCalculatedFieldsToBuild(build)
    buildList.append(build)

    return buildList
# ---------------------------------------------------------------------------















# ---------------------------------------------------------------------------
def publishGameFiles(game):
    # imports needing in function to avoid circular?
    from games.models import Game, calculateGameFilePathRuntime

    buildList = generateCompleteBuildList(game, False)
    optionBuildZip = False
    optionZipSuffix = '_complete'

    buildDir = calculateGameFilePathRuntime(game, "build", False)
    publishDir = calculateGameFilePathRuntime(game, "publish", False)
    # create publish directory if it doesn't exist yet
    jrfuncs.createDirIfMissing(publishDir)

    # now make sure the build dir files exist
    buildCheckMessage = checkBuildFiles(buildDir, buildList)

    if (buildCheckMessage is not None):
        raise Exception("ERROR: Could not publish files: {}.".format(buildCheckMessage))

    # and now COPY from build dir to publish dir
    publishRunMessage = publishBuildFiles(buildDir, buildList, publishDir)

    if (publishRunMessage is None):
        if (optionBuildZip):
            filePathBuild = buildDir + "/" + game.gameName + optionZipSuffix + ".zip"
            filePathPublish = publishDir + "/" + game.gameName + optionZipSuffix + ".zip"
            jrfuncs.copyFilePath(filePathBuild, filePathPublish)

    if (publishRunMessage is not None):
        raise Exception("ERROR: Could not publish files: {}.".format(publishRunMessage))
    #
    msg = "{} game files published.".format(len(buildList))
    return msg
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

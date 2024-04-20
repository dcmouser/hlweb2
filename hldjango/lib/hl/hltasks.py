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

from lib.hl.hlparser import calcColumnsFromLayout, calcMaxColumnsFromPaperSize
















# module global funcs
@db_task()
def queueTaskBuildStoryPdf(gameModelPk, requestOptions):
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

    # before we start get properties and update queue status
    game = Game.objects.get(pk=gameModelPk)
    if (game is None):
        raise Exception("Failed to find game pk={} for building - stage 1.".format(gameModelPk))
        # can't continue below

    # update model queue status before we start
    game.queueStatus = Game.GameQueueStatusEnum_Running
    # save
    game.save()


    # properties
    gameName = game.name
    gameText = game.text
    preferredFormatPaperSize = game.preferredFormatPaperSize
    preferredFormatLayout = game.preferredFormatLayout


    # what outputs do we want parser to build/generate
    optionBuildZip = True
    optionZipSuffix = ''
    buildList = []
    if (buildMode == "buildPreferred"):
        # build preferred format
        buildList.append({"label": "preferred format build", "format": "pdf", "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "normal", })
        optionZipSuffix = '_preferred'
    elif (buildMode == "buildDebug"):
        # build debug format
        buildList.append({"label": "debug build", "format": "pdf", "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "debug", })
        optionZipSuffix = '_debug'
    elif (buildMode == "buildComplete"):
        # build complete list; all combinations of page size and layout
        buildList = generateCompleteBuildList(game)
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

    # save
    game.save()

    # log
    jrprint("Updated model game {} after completion of queueTaskBuildStoryPdf with queuestats = {}.".format(gameModelPk, game.queueStatus))

    # result for instant run
    if (game.isBuildErrored):
        retv = "Errors during build."
    else:
        retv = "Build was successful."
    #
    return retv




def generateCompleteBuildList(game):
    # loop twice, the first time just calculate buildCount
    # imports needing in function to avoid circular?
    from games.models import Game, calculateGameFilePathRuntime

    buildList = []
    index = 0
    buildCount = 0
    # summary and debug
    buildCount += 2
    # customs
    buildCount += 1
    #
    preferredFormatPaperSize = game.preferredFormatPaperSize
    preferredFormatLayout = game.preferredFormatLayout
    #
    if (True):
        # customs
        index += 1
        buildList.append({"label": "_SOLOPRN_LETTER_LargeFont", "suffix": "SOLOPRN_LETTER_LargeFont", "format": "pdf", "paperSize": Game.GamePreferredFormatPaperSize_Letter, "layout": Game.GamePreferredFormatLayout_Solo, "variant": "normal", "fontSize": "16pt",})

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
                    buildList.append({"label": label, "format": "pdf", "paperSize": paperSize, "layout": layout, "variant": "normal", })

    # also debug, in preferred format
    index += 1
    label = "complete build {} of {} (debug)".format(index, buildCount)
    buildList.append({"label": label, "format": "pdf", "paperSize": preferredFormatPaperSize, "layout": preferredFormatLayout, "variant": "debug", })
    #
    # summary in letter format
    index += 1
    label = "complete build {} of {} (summary)".format(index, buildCount)
    paperSize = Game.GamePreferredFormatPaperSize_Letter
    buildList.append({"label": label, "format": "pdf", "paperSize": paperSize, "layout": Game.GamePreferredFormatLayout_Solo, "variant": "summary", })

    return buildList

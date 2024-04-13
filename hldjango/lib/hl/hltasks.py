# see https://huey.readthedocs.io/en/latest/consumer.html
# see https://negativeepsilon.com/en/posts/huey-async-task-execution/


# django
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, db_task, task
from huey.contrib.djhuey import HUEY as huey
from django.utils import timezone

# python modules
from datetime import datetime

# user modules
from lib.jr.jrfuncs import jrprint
from hueyconfig import huey
from lib.hl import hlparser


# module global funcs
@db_task()
def queueTaskBuildStoryPdf(gameModelPk, text, optionsDirPath, overrideOptions):
    # this may take a long time to run (minutes)
    buildLog = ""
    buildErrorStatus = False

    # update model before we start
    from games.models import Game
    game = Game.objects.get(pk=gameModelPk)
    if (game is None):
        raise Exception("Failed to find game pk={} for updating build results - stage 1.".format(gameModelPk))
        # can't continue below
    # update
    game.queueStatus = "Running..."
    # save
    game.save()





    try:
        # create hl parser
        hlParser = hlparser.HlParser(optionsDirPath, overrideOptions)

        # parse text
        hlParser.parseStoryTextIntoBlocks(text, 'hlweb2')

        # run pdf generation
        hlParser.runAllSteps()
    except Exception as e:
        buildLog += "ERROR: Exception while building storybook: " + str(e)
        buildErrorStatus = True

    # now store result in game model instance gameModelPk
    buildErrorStatus = (buildErrorStatus or hlParser.getBuildErrorStatus())
    buildLogParser = hlParser.getBuildLog()
    if (buildLogParser != ""):
        if (buildLog != ""):
            buildLog += "\n\n-----\n\n"
        buildLog += "Parser Build Log:\n" + buildLogParser

    # set the build log in the game model
    # buildErrorStatus, buildLog

    # load game instance
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
        game.queueStatus = "Errored"
        game.needsBuild = True
    else:
        game.queueStatus = "Completed"
        game.needsBuild = False
    # save
    game.save()

    # log
    jrprint("Updated model game {} after completion of queueTaskBuildStoryPdf with queuestats = {}.".format(gameModelPk, game.queueStatus))

    # success
    return True



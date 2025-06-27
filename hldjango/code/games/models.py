# django modules
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.core import validators
from django.contrib.auth.models import User

# user modules
from .validators import validateGameFile

# storybook modules
from lib.jr import jrdfuncs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from lib.casebook.cbhelpers import fastKludgeParseGameSettingsFromText
from .gametasks import queueTaskBuildStoryPdf, publishGameFiles, unpublishGameFiles, isTaskCanceled, cancelPreviousQueuedTask

# helpers
from . import gamefilemanager
from .gamefilemanager import calculateGameFilePathRuntime, calculateAbsoluteMediaPathForRelativePath, calculateGameFileUploadPathRuntimeRelative
from lib.jreffects.jreffect import JrImageEffects

# python modules
import hashlib
import traceback
import json
import os
import datetime
import uuid
import logging










class Game(models.Model):
    """Game object manages individual games/chapters/storybooks"""


    # enum for game queue status
    GameQueueStatusEnum_None = "NON"
    GameQueueStatusEnum_Running = "RUN"
    GameQueueStatusEnum_Queued = "QUE"
    GameQueueStatusEnum_Errored = "ERR"
    GameQueueStatusEnum_Completed = "COM"
    GameQueueStatusEnum_Aborted = "ABO"
    GameQueueStatusEnum = [
        (GameQueueStatusEnum_None, "None"),
        (GameQueueStatusEnum_Running, "Running"),
        (GameQueueStatusEnum_Queued, "Queued"),
        (GameQueueStatusEnum_Errored, "Errored"),
        (GameQueueStatusEnum_Completed, "Completed"),
        (GameQueueStatusEnum_Aborted, "Aborted"),
    ]


    # enum for storybook formats
    GamePreferredFormatPaperSize_Letter = "LETTER"
    GamePreferredFormatPaperSize_A4 = "A4"
    GamePreferredFormatPaperSize_B5 = "B5"
    GamePreferredFormatPaperSize_A5 = "A5"
    GamePreferredFormatPaperSize = [
        (GamePreferredFormatPaperSize_Letter, "Letter (8.5 x 11 inches)"),
        (GamePreferredFormatPaperSize_A4, "A4 (210 x 297 mm)"),
        (GamePreferredFormatPaperSize_B5, "B5 (176 × 250 mm)"),
        (GamePreferredFormatPaperSize_A5, "A5 (148 x 210 mm)"),
    ]

    #GameFormatPaperSizeCompleteList = [GamePreferredFormatPaperSize_Letter, GamePreferredFormatPaperSize_A4, GamePreferredFormatPaperSize_B5, GamePreferredFormatPaperSize_A5]
    GameFormatPaperSizeCompleteList = [GamePreferredFormatPaperSize_Letter, GamePreferredFormatPaperSize_A4, ]

    #
    GamePreferredFormatLayout_Solo = "SOLOSCR"
    GamePreferredFormatLayout_SoloPrint = "SOLOPRN"
    GamePreferredFormatLayout_OneCol = "ONECOL"
    GamePreferredFormatLayout_TwoCol = "TWOCOL"
    GamePreferredFormatLayout = [
        (GamePreferredFormatLayout_Solo, "Solo for screen (one lead per page; single-sided)"),
        (GamePreferredFormatLayout_SoloPrint, "Solo for print (one lead per page; double-sided)"),
        (GamePreferredFormatLayout_OneCol, "One column per page (double-sided)"),
        (GamePreferredFormatLayout_TwoCol, "Two columns per page (double-sided)"),
    ]
    #GameFormatLayoutCompleteList = [GamePreferredFormatLayout_Solo, GamePreferredFormatLayout_SoloPrint, GamePreferredFormatLayout_OneCol, GamePreferredFormatLayout_TwoCol]
    GameFormatLayoutCompleteList = [GamePreferredFormatLayout_Solo, GamePreferredFormatLayout_TwoCol]


    # tracking creation and modification dates
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)


    # new unique slug (we allow blank==true just so that it passes clean operation, we will set it ourselves)
    slug = models.SlugField(help_text="Unique slug id of the game", max_length=128, unique=True, blank=True, verbose_name="Url slug name")
    # dirname is set once at start, and governs the path where files are created; an admin could force it
    subdirname = models.CharField(max_length=64, blank=False, unique=True, default=jrdfuncs.shortUuidAsStringWithPkPrefix, validators = [jrdfuncs.validateName], verbose_name="Subdirectory name")

    # owner provides this info
    name = models.CharField(max_length=50, verbose_name="Short name", help_text="Internal name of the game; not used for urls or files; just for author info", blank=False, validators = [jrdfuncs.validateName])
    text = models.TextField(verbose_name="Full game text", help_text="Game text using custom storybook markdown formatting; all other settings are parsed from this.  See docs for syntax.", default="", blank=True,)
    textHash = models.CharField(max_length=80, help_text="Automatically calculated hash of game text; used to detect when game needs rebuilding.", default="", blank=True)
    textHashChangeDate = models.DateTimeField(help_text="Automatically updated date game text was last changed", null=True, blank=True)

    # is the game public
    isPublic = models.BooleanField(verbose_name="Is game public", help_text="Is game publicly visible? If unchecked the game will not be listed on public list of games.")

    # foreign keys
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )

    # new (12/30/24); allowing multiple editors
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="editable_objects", verbose_name="Allow these additional users to edit this game", blank=True)


    instructions = models.TextField(verbose_name="Additional requirements and instructions (markdown)", help_text="List of additional instructions and downloads needed to play, in Markdown format.", default="", blank=True,)

    # these properties should be extracted from the text and cannot be edited manually
    gameName = models.CharField(max_length=80, help_text="Public name of game (parsed from game text)", default="", blank=True)

    title = models.CharField(max_length=255, help_text="Title of game (parsed from game text)", default="", blank=True)
    subtitle = models.CharField(max_length=255, help_text="Subtitle of game (parsed from game text)", default="", blank=True)
    authors = models.CharField(max_length=255, help_text="Author(s) of game w/emails (parsed from game text)", default="", blank=True)
    summary = models.TextField(help_text="Short description (parsed from game text)", default="", blank=True)
    version = models.CharField(max_length=32, help_text="Version information (parsed from game text)", default="", blank=True)
    versionDate = models.CharField(max_length=64, help_text="Version date (parsed from game text)", default="", blank=True)
    status = models.CharField(max_length=80, help_text="Status (parsed from game text)", default="", blank=True)
    difficulty = models.CharField(max_length=32, help_text="Difficulty (parsed from game text)", default="", blank=True)
    cautions = models.CharField(max_length=255, help_text="Age rage, etc. (parsed from game text)", default="", blank=True)
    duration = models.CharField(max_length=32, help_text="Expected playtime (parsed from game text)", default="", blank=True)
    url = models.CharField(max_length=255, help_text="Homepage url (parsed from game text)", default="", blank=True)
 
    extraInfo = models.TextField(help_text="Extra information (parsed from game text)", default="", blank=True)
    extraCredits = models.TextField(help_text="Extra credits (parsed from game text)", default="", blank=True)

    copyright = models.CharField(max_length=255, help_text="Copyright (parsed from game text)", default="", blank=True)

    gameSystem = models.CharField(max_length=64, help_text="Game system (parsed from game text)", default="", blank=True)
    gameDate = models.CharField(max_length=64, help_text="Game date (parsed from game text)", default="", blank=True)

    campaignName = models.CharField(max_length=64, help_text="Part of this campaign (parsed from game text)", default="", blank=True)
    campaignPosition = models.CharField(max_length=64, help_text="Case position in campaign (parsed from game text)", default="", blank=True)

    # preferred format details
    preferredFormatPaperSize =  models.CharField(max_length=8, verbose_name="Preferred paper size; what you set here is what is used when performing the build preferred action.", choices=GamePreferredFormatPaperSize, default=GamePreferredFormatPaperSize_Letter)
    preferredFormatLayout =  models.CharField(max_length=8, verbose_name="Preferred Layout; what you set here is what is used when performing the build preferred action.", choices=GamePreferredFormatLayout, default=GamePreferredFormatLayout_Solo)


    # settings parsing
    #settingsStatus = models.TextField(help_text="Parsed settings status (see here for details of error when attempting to parse settings)", default="", blank=True)
    isErrorInSettings = models.BooleanField(help_text="Was there an error parsing settings?")

    # computed from last build
    leadStats = models.CharField(max_length=255, verbose_name="Build statistics", help_text="Computed build statistics", default="", blank=True)

    # date we published (different from date built)
    publishDate = models.DateTimeField(help_text="When was story last published?", null=True, blank=True)

    # tracking builds being out of date, etc
    buildResultsJsonField = models.JSONField(help_text="All build results as json; this is internal field you should not mess with.", default=dict, blank=True, null=True) # , encoder=DjangoJSONEncoder, decoder=DjangoJSONEncoder)



    # result of building
    # OLD method, one value per model; now we store in buildResults
    lastBuildLog = models.TextField(help_text="Results of last build; check here for errors.", default="", blank=True)

    adminSortKey = models.CharField(max_length=32, blank=True, null=True, help_text="alphanumeric field to control default sorting when presenting game list")



    # helpers
    @staticmethod
    def get_or_none(**kwargs):
        try:
            return Game.objects.get(**kwargs)
        except Game.DoesNotExist:
            return None

    def __str__(self):
        return "{} ({})".format(self.title, self.name)

    def get_absolute_url(self):
        return reverse("gameDetail", kwargs={"slug": self.slug})

    # override clean to parse hash
    def clean(self):
        # called automatically on edit
        # update text hash
        #
        # calc text hash and return if it is unchanged AND there was no error parsing settings last time
        textHashNew = calculateTextHashWithVersion(self.text)
        if (textHashNew == self.textHash) and (not self.isErrorInSettings):
            # text hash does not change and there is no error, nothing needs updating
            return
        #
        # update settings and schedule rebuild?
        if (textHashNew != self.textHash):
            # user has changed text
            self.textHash = textHashNew
            self.textHashChangeDate = timezone.now()
            # set this non-db field which we will check for when we save
            self.flagSaveVersionedGameText = True

        # this will happen even if text has not changed, as long as there was a previous error
        self.parseSettingsFromTextAndSetFields()

    
    # override save to set slug
    def save(self, **kwargs):

        # slug use
        if (self.slug is None) or (self.slug=="") or (hasattr(self,"flagSlugChanged") and (self.flagSlugChanged)):
            # automatic uniqueification of slug; for efficiency, only do this if user has edited slug (which we record in edit form) or if its blank
            if (self.slug is None) or (self.slug==""):
                # default new slug value based on name; used for NEW game or when we reset it to blank if user changes self.name
                slugStr = self.name
            else:
                # start with previous value of slug!
                slugStr = self.slug
            # dont let slugname confuse our url paths
            if (slugStr.lower() in ["file","new"]):
                slugStr += "game"
            # this will do the actual setting of self.slug
            jrdfuncs.jrdUniquifySlug(self, slugStr)

        # call super class
        super(Game, self).save(**kwargs)

        # after we have saved an object (and assigned it a pk); check if we should save versionedText
        if (hasattr(self,"flagSaveVersionedGameText") and self.flagSaveVersionedGameText):
            # save versioned game text
            self.saveVersionedGameText()


    # override for deleting
#    def delete(self):
#        self.deleteUserGameDirectories()
#        return super(Game, self).delete()











    # storybook helpers
    def parseSettingsFromTextAndSetFields(self):
        niceDateStr = jrfuncs.getNiceCurrentDateTime()
        errorList = []
        try:
            settings = fastKludgeParseGameSettingsFromText(self.text, errorList)
            info = jrfuncs.getDictValue(settings, "info")
            summary = jrfuncs.getDictValue(settings, "summary")
            infoExtra = jrfuncs.getDictValue(settings, "infoExtra")
            campaign = jrfuncs.getDictValue(settings, "campaign")
            if ((info is None) or (len(info)==0)) and (len(errorList)==0):
                errorList.append("No value set for required property group 'info'.")

            # set info properties
            self.setPropertyByName("name", "gameName", info, errorList)
            self.setPropertyByName("title", None, info, errorList)
            self.setPropertyByName("subtitle", None, info, errorList, False)
            self.setPropertyByName("authors", None, info, errorList)
            self.setPropertyByName("version", None, info, errorList)
            self.setPropertyByName("versionDate", None, info, errorList)
            self.setPropertyByName("status", None, info, errorList)
            self.setPropertyByName("difficulty", None, info, errorList)
            self.setPropertyByName("duration", None, info, errorList)
            #
            self.setPropertyByName("summary", None, summary, errorList)
            #
            self.setPropertyByName("cautions", None, infoExtra, errorList, False)
            self.setPropertyByName("extraCredits", None, infoExtra, errorList, False)
            self.setPropertyByName("url", None, infoExtra, errorList, False)
            self.setPropertyByName("copyright", None, infoExtra, errorList, False)
            #
            self.setPropertyByName("gameSystem", None, infoExtra, errorList, False)
            self.setPropertyByName("gameDate", None, infoExtra, errorList, False)
            #
            self.setPropertyByName("name", "campaignName", campaign, errorList, False)
            self.setPropertyByName("position", "campaignPosition", campaign, errorList, False)
            #
            if (len(errorList)==0):
                self.setSettingStatus(False, "Successfully updated settings on {}.".format(niceDateStr))
            else:
                self.setSettingStatus(True, "Errors parsing game text settings: {}.".format("; ".join(errorList)))
        except Exception as e:
            msg = jrfuncs.exceptionPlusSimpleTraceback(e,"parsing game text settings")
            self.setSettingStatus(True, msg)






    def setPropertyByName(self, propName, storeName, propDict, errorList, flagErrorIfMissing = True, defaultVal = None):
        if (propDict is None):
            return
        if (storeName is None):
            storeName = propName
        if (propName in propDict):
            value = propDict[propName]
            setattr(self, storeName, value)
        else:
            if (flagErrorIfMissing):
                if (len(errorList)==0):
                    # only bother with this error if there are no other errors
                    errorList.append("No value set for required setting property '{}'".format(propName))
            else:
                if (defaultVal is not None):
                    setattr(self, storeName, defaultVal)
                else:
                    setattr(self, storeName, "")





    def setSettingStatus(self, isError, msg):
        #self.settingsStatus = msg
        self.isErrorInSettings = isError
        if (isError):
            self.lastBuildLog = msg
        else:
            self.lastBuildLog = "Game text settings parsed: " + msg



    # results helpers
    def getBuildResultsAsObject(self):
        if (True):
            retv = self.buildResultsJsonField
            if (retv==""):
                retv = {}
            return retv
        #
        if (self.buildResultsJson==""):
            return {}
        return json.loads(self.buildResultsJson, cls=DjangoJSONEncoder)

    def setBuildResultsAsObject(self, allResultsObject):
        if (True):
            self.buildResultsJsonField = allResultsObject
            return
        # we need to use DjangoJSONEncoder to handle date objects
        #self.buildResultsJson= json.dumps(allResultsObject)
        self.buildResultsJson = json.dumps(allResultsObject, cls=DjangoJSONEncoder)


    def setBuildResults(self, gameFileTypeStr, resultObject):
        # update appropriate model field with data and hash of build
        allResultsObj = self.getBuildResultsAsObject()
        allResultsObj[gameFileTypeStr] = resultObject
        self.setBuildResultsAsObject(allResultsObj)

    def getBuildResults(self, gameFileTypeStr):
        # update appropriate model field with data and hash of build
        allResultsObj = self.getBuildResultsAsObject()
        if (gameFileTypeStr in allResultsObj):
            return allResultsObj[gameFileTypeStr]
        else:
            return {}


    def getBuildResultsAnnotated(self, gameFileTypeStr):
        resultsObj = self.getBuildResults(gameFileTypeStr)
        # annotate it for easier display?
        # ATTN: unfinished
        return resultsObj


    def copyBuildResults(self, destinationGameTypeStr, sourceGameTypeStr, overrideResults):
        buildResults = jrfuncs.deepCopyListDict(self.getBuildResults(sourceGameTypeStr))
        buildResults = jrfuncs.deepMergeOverwriteA(buildResults, overrideResults)
        self.setBuildResults(destinationGameTypeStr, buildResults)

    def modifyBuildResults(self, gameFileTypeStr, overrideResults):
        buildResults = self.getBuildResults(gameFileTypeStr)
        buildResults = jrfuncs.deepMergeOverwriteA(buildResults, overrideResults)
        self.setBuildResults(gameFileTypeStr, buildResults)


    def compareBuildHashWithCurrentText(self, buildHash):
        # return tuple saying whether text content is different, and if not, whether the system update requires rebuild
        # ATTN: version same not implemented yet
        if (buildHash == self.textHash):
            textSame = True
            versionSame = True
        else:
            textSame = False
            versionSame = False
        return [textSame, versionSame]


    def extractLastBuildResult(self):
        # look at all build results and get the latest one; this can be useful for showing author a quick latest build log
        latestBuildDateEnd = -1
        latestBuildResult = None
        allResultsObj = self.getBuildResultsAsObject()
        for k,v in allResultsObj.items():
            if ("buildDateEnd" in v):
                buildDateEnd = v["buildDateEnd"]
                if (buildDateEnd > latestBuildDateEnd):
                    latestBuildResult = v
        return latestBuildResult







    # ATTN: TODO - i think these two functions need to be consolidated with the gamefilemanager functions
    def deleteExistingFileIfFound(self, fileName, flagDeleteModel, editingGameFile):
        # this is called during uploading so that author can reupload a new version of an image and it will just overwrite existing
        gameFileImageDirectoryRelative = calculateGameFilePathRuntime(self, gamefilemanager.EnumGameFileTypeName_StoryUpload, True)
        filePath = gameFileImageDirectoryRelative + "/" + fileName

        # we do NOT want to just delete the file on the disk
        # instead we want to delete the file model which should chain delete the actual file
        if (flagDeleteModel):
            try:
                gameFile = GameFile.objects.get(filefield=filePath)
                # delete existing file; but only if its not editingGameFile (in other words this is going to catch the case where we might be editing one gameFILE and matching the image file name to another, which will then be deleted to make way)
                if (editingGameFile is None) or (editingGameFile.pk != gameFile.pk):
                    gameFile.delete()
            except Exception as e:
                # existing file not found -- not an error
                #jrprint("deleteExistingFileIfFound exception: {}.".format(str(e)))
                pass

        if (True):
            # delete existing pure file if it exists, because it is going to be replaced
            gameFileImageDirectoryAbsolute = calculateGameFilePathRuntime(self, gamefilemanager.EnumGameFileTypeName_StoryUpload, False)
            filePath = gameFileImageDirectoryAbsolute + "/" + fileName
            try:
                jrfuncs.deleteFilePathIfExists(filePath)
            except Exception as e:
                # existing file not found
                jrprint("deleteFilePathIfExists exception: {}.".format(str(e)))
                pass                

        return True



    def deleteExistingMediaPathedFileIfFound(self, relativeFileName):
        # this is called during uploading so that author can reupload a new version of an image and it will just overwrite existing
        # note that this does NOT delete any associated GAMEFILE model
        filePath = calculateAbsoluteMediaPathForRelativePath(relativeFileName)
        try:
            jrfuncs.deleteFilePathIfExists(filePath)
        except Exception as e:
            # existing file not found
            jrprint("deleteExistingMediaPathedFileIfFound for '{}' exception: {}.".format(filePath, str(e)))
            pass

        return True












    def buildGame(self, request, forceType):
        # what type of build
        if (forceType=="buildPreferred") or ("buildPreferred" in request.POST):
            buildMode = "buildPreferred"
            buildModeNice = "preferred pdf build"
        elif (forceType=="buildDebug") or ("buildDebug" in request.POST):
            buildMode = "buildDebug"
            buildModeNice = "debug build"
        elif (forceType=="buildDraft") or ("buildDraft" in request.POST):
            buildMode = "buildDraft"
            buildModeNice = "draft pdf set build"
        elif (forceType=="cancelBuildTasks") or ("cancelBuildTasks" in request.POST):
            # cancel all queued builds
            retv = self.cancelAllPendingBuilds(request)
            self.save()
            return
        elif (forceType=="publish") or ("publish" in request.POST):
            # publish request
            return self.publishGame(request)
        elif (forceType=="unpublish") or ("unpublish" in request.POST):
            # publish request
            return self.unpublishGame(request)
        else:
            raise Exception("Unspecified build mode.")

        # build options
        requestOptions = {"buildMode": buildMode}

        # do the build (queued or immediate)
        result = None

        # delete any PREVIOUSLY QUEUED job for THIS build
        self.cancelPendingBuildIfPresent(request, buildMode)

        # i think we need to set this before we queue task so it doesnt see old build reesults if it runs immediately
        buildResultsPrevious = self.getBuildResults(buildMode)
        #
        buildResults = {
                "queueStatus": Game.GameQueueStatusEnum_Queued,
                "buildDateQueued": timezone.now().timestamp(),
            }
        self.copyLastBuildResultsTo(buildResultsPrevious, buildResults)
        self.setBuildResults(buildMode, buildResults)
        # we better save to db so that task queue db sees this is if it checks right away
        self.save()

        # log the queuing of a task
        logger = logging.getLogger("app")
        msg = "{} Queueing game task for game id#{} '{}/{}' ({})".format(request.user.username, self.pk, self.name, self.gameName, buildMode)
        logger.info(msg)

        # this will QUEUE or run immediately the game build if neeed
        # but note that right now we are saving the entire TEXT in the function call queue, alternatively we could avoid passing text and grab it only when build triggers
        # ATTN: eventually move all this to the function that actually builds
        taskRetv = queueTaskBuildStoryPdf(self.pk, requestOptions)
        try:
            result = taskRetv.get()
        except Exception as e:
            # exception here may mean file in use could not build
            msg = jrfuncs.exceptionPlusSimpleTraceback(e, "trying to build pdf")
            result = msg
            message = "Result of {} for game '{}': {}.".format(buildModeNice, self.name, result)
            jrdfuncs.addFlashMessage(request, message, True)
            # force error build results
            buildResults = {
                "queueStatus": Game.GameQueueStatusEnum_Errored,
                "buildDateQueued": timezone.now().timestamp(),
                "buildError": result,
                "buildLog": result,
            }
            # copy over last build results that are important
            self.copyLastBuildResultsTo(buildResultsPrevious, buildResults)
            self.setBuildResults(buildMode, buildResults)
            #
            self.save()
            return

        # send to detail view with flash message
        if (isinstance(result, str)):
            # immediate run
            message = "Result of {} for game '{}': {}.".format(buildModeNice, self.name, result)
            # no need to save since the queutask will save
        else:
            # queued
            message = "Generation of {} for game '{}' has been queued for delayed build.".format(buildModeNice, self.name)
            # we are queueing, so update status.. should we reload in case it changed?
            buildResults = {
                "queueStatus": Game.GameQueueStatusEnum_Queued,
                "buildDateQueued": timezone.now().timestamp(),
                "taskType": "huey",
                "taskId": taskRetv.id,
                }
            # copy over last build results that are important
            self.copyLastBuildResultsTo(buildResultsPrevious, buildResults)
            self.setBuildResults(buildMode, buildResults)
            #
            self.save()

        jrdfuncs.addFlashMessage(request, message, False)










    def publishGame(self, request):
        msg = None
        if (True):
            # non queued publish
            try:
                result = publishGameFiles(self)
            except Exception as e:
                msg = jrfuncs.exceptionPlusSimpleTraceback(e, "publishing game")
            if (msg is None):
                msg = "Successfully published."
                #
                # log
                logger = logging.getLogger("app")
                msg = "{} Published game files for game id#{} '{}/{}'".format(request.user.username, self.pk, self.name, self.gameName)
                logger.info(msg)

        jrdfuncs.addFlashMessage(request, msg, False)


    def unpublishGame(self, request):
        msg = None
        if (True):
            # non queued publish
            try:
                result = unpublishGameFiles(self)
            except Exception as e:
                msg = jrfuncs.exceptionPlusSimpleTraceback(e, "deleting published files for game")
            if (msg is None):
                msg = "Published files have been deleted."
                # log
                logger = logging.getLogger("app")
                msg = "{} UNpublished game files for game id#{} '{}/{}'".format(request.user.username, self.pk, self.name, self.gameName)
                logger.info(msg)

        jrdfuncs.addFlashMessage(request, msg, False)







    def reconcileFiles(self, request):
        # walk through upload directory, add all files that don't already exist as if they were uploaded; remove all file models that do NOT exist
        # set flash messages
        msgList = []

        # get upload directory
        gameFileType = gamefilemanager.EnumGameFileTypeName_StoryUpload
        gameFileManager = gamefilemanager.GameFileManager(self)
        directoryPath = gameFileManager.getDirectoryPathForGameType(gameFileType)
        relativeRoot = gameFileManager.getMediaSubDirectoryPathForGameType(gameFileType)

        # now walk list of files
        filePathList = self.collectFilesInUploadDirectory()

        # ok now for each one, see if its already listed
        msgList.append("Found {} files in game upload directory.".format(len(filePathList)))
        removedFileCount = 0
        addedFileCount = 0


        # step 1, DELETE all model files that do not exist FOR THIS GAME
        # get all gameFile models
        gameFileQuerySet = GameFile.objects.filter(game=self)
        for gameFileEntry in gameFileQuerySet:
            mediaFilePath = gameFileEntry.filefield.name
            absoluteFilePath = "/".join([str(settings.MEDIA_ROOT), mediaFilePath])
            absoluteFilePath = jrfuncs.canonicalFilePath(absoluteFilePath)
            jrprint("Checking '{}' at '{}'".format(mediaFilePath, absoluteFilePath))
            if (not jrfuncs.pathExists(absoluteFilePath)):
                gameFileEntry.delete()
                msgList.append("Removed file model for missing upload file '{}' ({}).".format(mediaFilePath,absoluteFilePath))
                removedFileCount += 1

        # step 2, ADD new files
        for filePath in filePathList:
            try:
                relativePath = filePath.replace(directoryPath,relativeRoot)
                gameFile = GameFile.get_or_none(filefield=relativePath)
                # delete existing file; but only if its not editingGameFile (in other words this is going to catch the case where we might be editing one gameFILE and matching the image file name to another, which will then be deleted to make way)
                if (gameFile is None):
                    # doesnt exist, add it
                    gameFile = GameFile(owner=request.user, game=self, gameFileType = gameFileType, note="")
                    # remove absolute part of path
                    relativePath = filePath.replace(directoryPath,relativeRoot)
                    gameFile.filefield.name = relativePath
                    gameFile.save()
                    msgList.append("Added file model for found file '{}'.".format(filePath))
                    addedFileCount += 1
            except Exception as e:
                # existing file not found -- not an error
                msg = jrfuncs.exceptionPlusSimpleTraceback(e, "trying to add file '{}'".format(filePath))
                msgList.append(msg)
                pass

        # combine messages
        msgList.append("Added {} found files, and removed {} missing files.".format(addedFileCount, removedFileCount))
        retv = "\n".join(msgList)
        return retv


    def collectFilesInUploadDirectory(self):
        gameFileType = gamefilemanager.EnumGameFileTypeName_StoryUpload
        gameFileManager = gamefilemanager.GameFileManager(self)
        directoryPath = gameFileManager.getDirectoryPathForGameType(gameFileType)

        # now walk list of files
        filePathList = []
        jrfuncs.createDirIfMissing(directoryPath)
        obj = os.scandir(directoryPath)
        for entry in obj:
            if not entry.is_file():
                continue
            filePath = entry.path
            filePath = jrfuncs.canonicalFilePath(filePath)
            filePathList.append(filePath)
        #
        return filePathList




    def addOrReconcileGameFile(self, filePath):
        # given a path, add it if needed or return existing gamefile
        gameFileType = gamefilemanager.EnumGameFileTypeName_StoryUpload
        gameFileManager = gamefilemanager.GameFileManager(self)
        directoryPath = gameFileManager.getDirectoryPathForGameType(gameFileType)
        relativeRoot = gameFileManager.getMediaSubDirectoryPathForGameType(gameFileType)
        filePath = jrfuncs.canonicalFilePath(filePath)
        relativePath = filePath.replace(directoryPath, relativeRoot)
        gameFile = None

        if (not jrfuncs.pathExists(filePath)):
            message = "Could not find an existing file at '{}'.".format(filePath)
            retv = False
            return {"success": retv, "message": message, "gameFile": gameFile}      

        try:
            relativePath = filePath.replace(directoryPath,relativeRoot)
            gameFile = GameFile.get_or_none(filefield=relativePath)
            # delete existing file; but only if its not editingGameFile (in other words this is going to catch the case where we might be editing one gameFILE and matching the image file name to another, which will then be deleted to make way)
            if (gameFile is None):
                # doesnt exist, add it, making game owner the owner of the file
                gameFile = GameFile(owner=self.owner, game=self, gameFileType = gameFileType, note="")
                # remove absolute part of path
                relativePath = filePath.replace(directoryPath, relativeRoot)
                gameFile.filefield.name = relativePath
                gameFile.save()
                message = "Added new file to game."
                retv = True
            else:
                message = "Existing file replaced."
                retv = True
        except Exception as e:
            # existing file not found -- not an error
            message = jrfuncs.exceptionPlusSimpleTraceback(e, "trying to add file '{}'".format(filePath))
            retv = False

        return {"success": retv, "message": message, "gameFile": gameFile}




    def zipImageFilesIntoDebugDirectory(self, request):
        # walk through upload directory, make a zip of all files, put the zip in the debug directory
        # return a dictionary with zip filePath, fileName, error

        # the output directory
        gameFileManager = gamefilemanager.GameFileManager(self)
        directoryPath = gameFileManager.getDirectoryPathForGameType(gamefilemanager.EnumGameFileTypeName_Debug)
        gameFileManager.createFileDirectoryForGameTypeIfNeeded(gamefilemanager.EnumGameFileTypeName_Debug)

        # base file name
        fileNameSuffix = "_uploadedFiles"
        gameName = self.name
        fileName = jrfuncs.safeCharsForFilename(gameName+fileNameSuffix)

        # get file list
        filePathList = self.collectFilesInUploadDirectory()

        # create the zip file!
        try:
            zipFileOutputPath = jrfuncs.makeZipFile(filePathList, directoryPath, fileName)
        except Exception as e:
            error = str(e)
            return {"error": error}
        if (not jrfuncs.pathExists(zipFileOutputPath)):
            error = "Tried to zip {} files, but zip file was not successfully created at '{}'.".format(len(filePathList), zipFileOutputPath)
            return {"error": error}
        # success
        return {"filePath": zipFileOutputPath, "fileName":fileName + ".zip"}






    def saveVersionedGameText(self):
        # base directory for game
        gameFileType = gamefilemanager.EnumGameFileTypeName_VersionedGame
        gameFileManager = gamefilemanager.GameFileManager(self)
        directoryPath = gameFileManager.getDirectoryPathForGameType(gameFileType)
        # add to filename
        versionStr = self.version
        versionStr = versionStr.replace(".", "p")
        nowTime = datetime.datetime.now()
        currentDateStr = nowTime.strftime('_%Y%m%d_%H%M%S')
        #fileNameSuffix = "_gameText_v{}_{}".format(versionStr, currentDateStr)
        fileNameSuffix = "_gameText_{}_v{}".format(currentDateStr, versionStr)
        gameName = self.name
        fileName = jrfuncs.safeCharsForFilename(gameName+fileNameSuffix)
        fullFilePath = "{}/{}.txt".format(directoryPath, fileName)
        encoding = "utf-8"
        jrfuncs.createDirIfMissing(directoryPath)
        # strange double newlines unless we do this (see https://stackoverflow.com/questions/63004501/newlines-in-textarea-are-doubled-in-number-when-saved)
        textOut = self.text
        textOut = '\n'.join(textOut.splitlines())
        jrfuncs.saveTxtToFile(fullFilePath, textOut, encoding=encoding)






    def cancelPendingBuildIfPresent(self, request, gameFileType):
        buildResults = self.getBuildResults(gameFileType)
        queueStatus = jrfuncs.getDictValueOrDefault(buildResults, "queueStatus", None)
        isCanceled = jrfuncs.getDictValueOrDefault(buildResults,"canceled", False)
        if (queueStatus is None) or (isCanceled) or (queueStatus == Game.GameQueueStatusEnum_Completed) or (queueStatus == Game.GameQueueStatusEnum_Errored) or (queueStatus == Game.GameQueueStatusEnum_Aborted):
            return False
        taskType = jrfuncs.getDictValueOrDefault(buildResults, "taskType", None)
        taskId = jrfuncs.getDictValueOrDefault(buildResults, "taskId", None)
        if (isTaskCanceled(taskType, taskId)):
            buildResults["canceled"] = True
            return False
        retv = cancelPreviousQueuedTask(taskType, taskId)
        if (retv):
            jrdfuncs.addFlashMessage(request, "Canceling previously queued {} task #{}.".format(taskType, taskId), True)
            # update build state (caller will have to save())
            buildResults["canceled"] = True
            # change queue status, (unless it is running in which case it completed)
            if (queueStatus != Game.GameQueueStatusEnum_Running):
                buildResults["queueStatus"] = Game.GameQueueStatusEnum_Aborted
            self.setBuildResults(gameFileType, buildResults)
        return retv


    def cancelAllPendingBuilds(self, request):
        canceledTaskCount = 0
        allResultsObj = self.getBuildResultsAsObject()
        for gameFileType, buildResults in allResultsObj.items():
            retv = self.cancelPendingBuildIfPresent(request, gameFileType)
            if (retv):
                canceledTaskCount += 1
        if (canceledTaskCount==0):
            jrdfuncs.addFlashMessage(request, "No queued tasks to cancel.", True)



    def copyLastBuildResultsTo(self, buildResultsPrevious, buildResults):
        lastBuildDateStart = jrfuncs.getDictValueOrDefault(buildResultsPrevious, "lastBuildDateStart", 0)
        lastBuildVersion = jrfuncs.getDictValueOrDefault(buildResultsPrevious, "lastBuildVersion", "")
        lastBuildVersionDate = jrfuncs.getDictValueOrDefault(buildResultsPrevious, "lastBuildVersionDate", "")
        lastBuildTool = jrfuncs.getDictValueOrDefault(buildResultsPrevious, "lastBuildTool", "")
        buildResults["lastBuildDateStart"] = lastBuildDateStart
        buildResults["lastBuildVersion"] = lastBuildVersion
        buildResults["lastBuildVersionDate"] = lastBuildVersionDate
        buildResults["lastBuildTool"] = lastBuildTool




    def deleteUserGameDirectories(self, request):
        # delete (or rename the user directory for game )
        gameFileManager = gamefilemanager.GameFileManager(self)
        if (settings.DELETE_USER_GAMEFOLDER_METHOD=="realDelete"):
            retvMessage = gameFileManager.deleteBaseDirectory()
        elif (settings.DELETE_USER_GAMEFOLDER_METHOD=="rename"):
            retvMessage = gameFileManager.deleteBaseDirectoryByRenaming()
        elif (settings.DELETE_USER_GAMEFOLDER_METHOD=="nothing"):
            pass
        else:
            raise Exception("Unknown settings.DELETE_USER_GAMEFOLDER_METHOD was '{}' should be from [realDelete, rename, nothing]".format(settings.DELETE_USER_GAMEFOLDER_METHOD))

        jrdfuncs.addFlashMessage(request, retvMessage, False)


    def renameDirectoryFrom(self, request, oldDir):
        gameFileManager = gamefilemanager.GameFileManager(self)
        retvMessage = gameFileManager.renameBaseDirectoryFrom(oldDir)
        jrdfuncs.addFlashMessage(request, retvMessage, False)



    def runEffectOnImageFileAddOrReplaceGameFile(self, effectKey, path, suffixKey, pathIsRelative):
        # image effect helper
        jreffector = JrImageEffects()

        # get effect options
        effectOptions = jreffector.calcEffectOptionsByKey(effectKey)
        if (effectOptions is None):
            message = "Effect not known: '{}'.".format(effectKey)
            return {"success": False, "message": message}

        # absolute paths for input and output
        if (pathIsRelative):
            absoluteFilePath = "/".join([str(settings.MEDIA_ROOT), path])
        else:
            absoluteFilePath = path
        outPath = jreffector.suffixFilePath(absoluteFilePath, effectKey, suffixKey)

        # run it
        retv = jreffector.run(absoluteFilePath, outPath, effectOptions)

        if (not retv["success"]):
            # failure
            errorMessage = retv["message"]
            message = "Failed to run effect on file: {}".format(errorMessage)
            return {"success": False, "message": message}

        # success
        # now we need to ADD the new file as an object; or just return the existing one if it already exists
        # and set newGameFile to the new one, so we open that one
        newBaseName = jrfuncs.getBaseFileName(outPath)
        retv = self.addOrReconcileGameFile(outPath)
        reconcileMessage = retv["message"]
        if (not retv["success"]):
            message = "Failed to add new {} image file to game ({}): {}.".format(effectOptions["label"], newBaseName, reconcileMessage)
            return {"success": False, "message": message}

        # success
        gameFile = retv["gameFile"]
        message = "Successfully added new {} image file to game ({}): {}.".format(effectOptions["label"], newBaseName, reconcileMessage)
        return {"success": True, "message": message, "outPath": outPath, "gameFile": gameFile}





























# GAME FILE STUFF






























class GameFile(models.Model):
    """File object manages files attached to games"""

    # ATTN: TODO: see https://file-validator.github.io/docs/intro for more involved validation library

    # foreign keys
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    # game filetype
    gameFileType = models.CharField(max_length=32, choices=gamefilemanager.GameFileTypeDbFieldChoices, default=gamefilemanager.EnumGameFileTypeName_StoryUpload)

    # django file field helper
    # note we use a validator, but we ALSO do a separate validation for file size after the file is uploaded
    filefield = models.FileField(
        upload_to = calculateGameFileUploadPathRuntimeRelative, validators=[validateGameFile]
    )


    # optinal label
    note = models.CharField(
        max_length=80, help_text="Internal comments (optional)", default="", blank=True
    )



    # helpers
    @staticmethod
    def get_or_none(**kwargs):
        try:
            return GameFile.objects.get(**kwargs)
        except GameFile.DoesNotExist:
            return None

    def __str__(self):
        return self.filefield.name

    def get_absolute_url(self):
        return reverse("gameFileDetail", kwargs={"pk": self.pk})


    # override delete func
    # when we delete a GameFile, we want to delete the actual file on disk
    # note django resources on web have various auto smart ways to do this using signals, but this seems most straightforward for simple case
    def delete(self, *args, **kwargs):
        self.filefield.delete()
        super(GameFile, self).delete(*args, **kwargs)

    def clean(self):
        # custom file validators that must be run here when the file is available; separate from file extension tests

        # file size
        maxFilesize = settings.JR_MAXUPLOADGAMEFILESIZE
        fileSize = self.filefield.file.size
        if fileSize > maxFilesize:
            raise ValidationError(
                "Uploaded file is too large ({:.2f}mb > {:.2f}mb)".format(
                    fileSize / 1000000, maxFilesize / 1000000
                )
            )

    def getPath(self):
        return self.filefield.name









# non-class helper functions

def calculateTextHashWithVersion(text):
    h = hashlib.new("sha256")
    h.update(text.encode())
    hashValue = h.hexdigest() + "_" + settings.JR_STORYBUILDVERSION
    return hashValue

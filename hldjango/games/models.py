# django modules
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone

# user modules
from .validators import validateGameFile

# storybook modules
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from lib.hl.hlparser import fastExtractSettingsDictionary
from lib.hl.hltasks import queueTaskBuildStoryPdf, publishGameFiles

# python modules
import hashlib

#
TGameFileTypes = {0: "imageUpload", 1: "builtFile"}





class Game(models.Model):
    """Game object manages individual games/chapters/storybooks"""

    # enum for game queue status
    GameQueueStatusEnum_None = "NON"
    GameQueueStatusEnum_Running = "RUN"
    GameQueueStatusEnum_Queued = "QUE"
    GameQueueStatusEnum_Errored = "ERR"
    GameQueueStatusEnum_Completed = "COM"
    GameQueueStatusEnum = [
        (GameQueueStatusEnum_None, "None"),
        (GameQueueStatusEnum_Running, "Running"),
        (GameQueueStatusEnum_Queued, "Queued"),
        (GameQueueStatusEnum_Errored, "Errored"),
        (GameQueueStatusEnum_Completed, "Completed"),
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
    GameFormatPaperSizeCompleteList = [GamePreferredFormatPaperSize_Letter, GamePreferredFormatPaperSize_A4, GamePreferredFormatPaperSize_B5, GamePreferredFormatPaperSize_A5]
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
    GameFormatLayoutCompleteList = [GamePreferredFormatLayout_Solo, GamePreferredFormatLayout_SoloPrint, GamePreferredFormatLayout_OneCol, GamePreferredFormatLayout_TwoCol]


    # owner provides this info
    name = models.CharField(max_length=50, verbose_name="Short name", help_text="Internal name of the game")
    text = models.TextField(verbose_name="Full game text", help_text="Game text", default="", blank=True)
    textHash = models.CharField(
        max_length=80, help_text="Hash of text", default="", blank=True
    )

    # is the game public
    isPublic = models.BooleanField(verbose_name="Is game public?", help_text="Is game publicly visible?")

    # foreign keys
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )

    # computed stats from last build
    buildStats = models.CharField(max_length=255, verbose_name="Build statistics", help_text="Computed build statistics", default="", blank=True)
    



    # these properties should be extracted from the text
    gameName = models.CharField(
        max_length=80, help_text="Public name of game", default="", blank=True
    )

    title = models.CharField(
        max_length=80, help_text="Title of game", default="", blank=True
    )
    subtitle = models.CharField(
        max_length=80, help_text="Subtitle of game", default="", blank=True
    )
    authors = models.CharField(
        max_length=255, help_text="Author(s) of game (w/emails)", default="", blank=True
    )
    summary = models.TextField(help_text="Short description", default="", blank=True)
    version = models.CharField(
        max_length=32, help_text="Version information", default="", blank=True
    )
    versionDate = models.CharField(
        max_length=64, help_text="Version date", default="", blank=True
    )
    difficulty = models.CharField(
        max_length=32, help_text="Difficulty", default="", blank=True
    )
    cautions = models.CharField(
        max_length=32, help_text="Age rage, etc.", default="", blank=True
    )
    duration = models.CharField(
        max_length=32, help_text="Expected playtime", default="", blank=True
    )
    url = models.CharField(
        max_length=255, help_text="Homepage url", default="", blank=True
    )
    extraInfo = models.TextField(
        help_text="Extra information (credits, links, etc.)", default="", blank=True
    )



    # result of building
    buildLog = models.TextField(help_text="Build Log", default="", blank=True)
    needsBuild = models.BooleanField(help_text="Game was updated and needs rebuild")
    # game filetype
    queueStatus =  models.CharField(max_length=3, choices=GameQueueStatusEnum, default=GameQueueStatusEnum_None)
    isBuildErrored = models.BooleanField(
        help_text="Was there an error on the last build?"
    )
    buildDate = models.DateTimeField(
        help_text="When was story last built?", null=True, blank=True
    )
    queueDate = models.DateTimeField(
        help_text="When was build queued?", null=True, blank=True
    )


    # format
    preferredFormatPaperSize =  models.CharField(max_length=8, verbose_name="Preferred paper size", choices=GamePreferredFormatPaperSize, default=GamePreferredFormatPaperSize_Letter)
    preferredFormatLayout =  models.CharField(max_length=8, verbose_name="Preferred Layout", choices=GamePreferredFormatLayout, default=GamePreferredFormatLayout_Solo)








    # helpers
    def __str__(self):
        return "{} ({})".format(self.title, self.name)

    def get_absolute_url(self):
        return reverse("gameDetail", kwargs={"pk": self.pk})

    def clean(self):
        # called automatically on edit
        # update text hash
        flagForceRebuild = True
        #
        h = hashlib.new("sha256")
        h.update(self.text.encode())
        textHashNew = h.hexdigest() + "_" + settings.JR_STORYBUILDVERSION
        if (textHashNew == self.textHash) and (not flagForceRebuild):
            # text hash does not change, nothing needs updating
            return
        #
        # update settings and schedule rebuild?
        self.textHash = textHashNew
        self.parseSettingsFromTextAndSetFields()


    # storybook helpers
    def parseSettingsFromTextAndSetFields(self):
        niceDateStr = jrfuncs.getNiceCurrentDateTime()
        try:
            settings = fastExtractSettingsDictionary(self.text)
            # set settings
            errorList = []
            if ("info" in settings):
                info = settings["info"]
            else:
                info = {}
                errorList.append("No value set for required property group 'info'.")

            # set info properties
            self.setPropertyByName("name", "gameName", info, errorList)
            self.setPropertyByName("title", None, info, errorList)
            self.setPropertyByName("subtitle", None, info, errorList, False)
            self.setPropertyByName("authors", None, info, errorList)
            self.setPropertyByName("version", None, info, errorList)
            self.setPropertyByName("versionDate", None, info, errorList)
            self.setPropertyByName("difficulty", None, info, errorList)
            self.setPropertyByName("duration", None, info, errorList)
            self.setPropertyByName("cautions", None, info, errorList, False)
            self.setPropertyByName("summary", None, info, errorList)
            self.setPropertyByName("extraInfo, None", info, errorList, False)
            self.setPropertyByName("url", None, info, errorList, False)

            #
            if (len(errorList)==0):
                self.buildLog = "Successfully updated settings on {}; needs rebuild.".format(niceDateStr)
                self.isBuildErrored = False
            else:
                self.buildLog = "Errors in settings from {}: {}.".format(niceDateStr, "; ".join(errorList))
                self.isBuildErrored = True
        except Exception as e:
            self.buildLog = "Error parsing settings on{}: Exception {}".format(niceDateStr, str(e))
            self.isBuildErrored = True
        # mark it needing rebuild
        self.needsBuild = True


    def setPropertyByName(self, propName, storeName, propDict, errorList, flagErrorIfMissing = True, defaultVal = None):
        if (storeName is None):
            storeName = propName
        if (propName in propDict):
            value = propDict[propName]
            setattr(self, storeName, value)
        else:
            if (flagErrorIfMissing):
                errorList.append("No value set for required setting property '{}'".format(propName))
            else:
                if (defaultVal is not None):
                    setattr(self, storeName, defaultVal)
                else:
                    setattr(self, storeName, "")






    def deleteExistingFileIfFound(self, fileName, flagDeleteModel, editingGameFile):
        # this is called during uploading so that author can reupload a new version of an image and it will just overwrite existing
        gameFileImageDirectoryRelative = calculateGameFilePathRuntime(self, "uploads", True)
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
            gameFileImageDirectoryAbsolute = calculateGameFilePathRuntime(self, "uploads", False)
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
        filePath = calculateAbsoluteMediaPathForRelativePath(relativeFileName)
        try:
            jrfuncs.deleteFilePathIfExists(filePath)
        except Exception as e:
            # existing file not found
            jrprint("deleteExistingMediaPathedFileIfFound for '{}' exception: {}.".format(filePath, str(e)))
            pass

        return True








    def buildGame(self, request):

        # update model to show it needs building
        self.queueStatus = Game.GameQueueStatusEnum_Queued
        self.needsBuild = True
        self.isBuildErrored = False
        self.buildLog = ""
        self.queueDate = timezone.now()
        self.save()

        # what type of build
        if ("buildPreferred" in request.POST):
            buildMode = "buildPreferred"
        elif ("buildDebug" in request.POST):
            buildMode = "buildDebug"
        elif ("buildComplete" in request.POST):
            buildMode = "buildComplete"
        else:
            raise Exception("Unspecified build mode.")

        # build options
        requestOptions = {"buildMode": buildMode}


        # do the build (queued or immediate)
        result = None
        if (True):
            # this will QUEUE or run immediately the game build if neeed
            # but note that right now we are saving the entire TEXT in the function call queue, alternatively we could avoid passing text and grab it only when build triggers
            # ATTN: eventually move all this to the function that actually builds
            retv = queueTaskBuildStoryPdf(self, requestOptions)
            result = retv.get()


        # send to detail view with flash message
        if (isinstance(result, str)):
            message = "Result of storybook pdf build for game '{}': {}.".format(self.name, result)
        else:
            message = "Generations of storybook pdf for game '{}' has been queued for delayed build.".format(self.name)

        messages.add_message(request, messages.INFO, message)








    def publishGame(self, request):
        result = None
        if (True):
            # non queued publish
            try:
                result = publishGameFiles(self)
            except Exception as e:
                result = "Error Publishing: {}.".format (str(e))
            if (result is None):
                result = "Successfully published."

        messages.add_message(request, messages.INFO, result)


























    # ---------------------------------------------------------------------------
    def deletePublishedFiles(self):
        # delete the files for this game in the 
        pass
    # ---------------------------------------------------------------------------

































# GAME FILE STUFF







# helper
def calculateGameFilePathRuntime(game, subdir, flagRelative):
    gamePk = game.pk
    if (flagRelative):
        path = "/".join(["games", str(gamePk), subdir])
    else:
        path = "/".join([str(settings.MEDIA_ROOT), "games", str(gamePk), subdir])
    return path

def calculateGameFileUploadPathRuntimeRelative(instance, filename):
    basePath = calculateGameFilePathRuntime(instance.game, "uploads", True)
    return "/".join([basePath, filename])

def calculateAbsoluteMediaPathForRelativePath(relativePath):
    path = "/".join([str(settings.MEDIA_ROOT), relativePath])
    return path


class GameFile(models.Model):
    """File object manages files attached to games"""

    # enum for game file type
    GameFileType_Up = "UP"
    GameFileType_Built = "BT"
    GameFileTypeEnum = [
        (GameFileType_Up, "User Upload"),
        (GameFileType_Built, "Built"),
    ]


    # ATTN: TODO: see https://file-validator.github.io/docs/intro for more involved validation library


    # foreign keys
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    # game filetype
    gameFileType = models.CharField(max_length=3, choices=GameFileTypeEnum, default=GameFileType_Up)

    # django file field helper
    # note we use a validator, but we ALSO do a separate validation for file size after the file is uploaded
    filefield = models.FileField(
        upload_to = calculateGameFileUploadPathRuntimeRelative, validators=[validateGameFile]
    )


    # optinal label
    note = models.CharField(
        max_length=80, help_text="Internal comments (optional)", default="", blank=True
    )


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

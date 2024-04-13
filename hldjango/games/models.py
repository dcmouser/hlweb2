# django modules
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib import messages

# user modules
from .validators import validateGameFile

# storybook modules
from lib.hl.hlstory import HlStory
from lib.jr import jrfuncs

# python modules
import hashlib


# defines
DefMaxUploadGameFileSize = 10000000


class Game(models.Model):
    """Game object manages individual games/chapters/storybooks"""

    # owner provides this info
    name = models.CharField(max_length=50, help_text="Internal name of the game")
    text = models.TextField(help_text="Game text", default="", blank=True)
    textHash = models.CharField(
        max_length=80, help_text="Hash of text", default="", blank=True
    )

    # is the game public
    isPublic = models.BooleanField(help_text="Is game publicly visible?")

    # foreign keys
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )

    # these properties should be extracted from the text
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
    queueStatus = models.CharField(
        max_length=32, help_text="Internal build queue stage", default="", blank=True
    )
    isBuildErrored = models.BooleanField(
        help_text="Was there an error on the last build?"
    )
    buildDate = models.DateTimeField(
        help_text="When was story last built?", null=True, blank=True
    )

    # helpers
    def __str__(self):
        return "{} ({})".format(self.title, self.name)

    def get_absolute_url(self):
        return reverse("gameDetail", kwargs={"pk": self.pk})

    def clean(self):
        # called automatically on edit
        # update text hash
        flagForceRebuild = True
        h = hashlib.new("sha256")
        h.update(self.text.encode())
        textHashNew = h.hexdigest()
        if (textHashNew == self.textHash) and (not flagForceRebuild):
            # text hash does not change, nothing needs updating
            return
        # update settings and schedule rebuild?
        self.textHash = textHashNew
        self.parseSettingsFromTextAndSetFields()


    # storybook helpers
    def parseSettingsFromTextAndSetFields(self):
        hlstory = HlStory()
        niceDateStr = jrfuncs.getNiceCurrentDateTime()
        try:
            settings = hlstory.extractSettingsDictionary(self.text)
            # set settings
            errorList = []
            if ("info" in settings):
                info = settings["info"]
            else:
                info = {}
                errorList.append("No value set for required property group 'info'.")

            # set info properties
            self.setPropertyByName("title", info, errorList)
            self.setPropertyByName("subtitle", info, errorList, False)
            self.setPropertyByName("authors", info, errorList)
            self.setPropertyByName("version", info, errorList)
            self.setPropertyByName("versionDate", info, errorList)
            self.setPropertyByName("difficulty", info, errorList)
            self.setPropertyByName("duration", info, errorList)
            self.setPropertyByName("cautions", info, errorList, False)
            self.setPropertyByName("summary", info, errorList)
            self.setPropertyByName("extraInfo", info, errorList, False)
            self.setPropertyByName("url", info, errorList, False)

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


    def setPropertyByName(self, propName, propDict, errorList, flagErrorIfMissing = True, defaultVal = None):
        if (propName in propDict):
            value = propDict[propName]
            setattr(self, propName, value)
        else:
            if (flagErrorIfMissing):
                errorList.append("No value set for required setting property '{}'".format(propName))
            else:
                if (defaultVal is not None):
                    setattr(self, propName, defaultVal)
                else:
                    setattr(self, propName, "")



    def buildGame(self, request):
        gameFileBuildDirectoryAbsolute = calculateGameFilePathRuntime(self, "build", False)
        gameFileImageDirectoryAbsolute = calculateGameFilePathRuntime(self, "uploads", False)
        buildOptions = {
            "buildDir": gameFileBuildDirectoryAbsolute,
            "imageDir": gameFileImageDirectoryAbsolute,
        }

        # hlstory object manages our story
        hlstory = HlStory()
        retv = hlstory.buildGame(self.pk, buildOptions, self.text)

        # send to detail view with flash message
        message = retv["message"]
        messages.add_message(request, messages.INFO, message)













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


class GameFile(models.Model):
    """File object manages files attached to games"""

    # ATTN: TODO: see https://file-validator.github.io/docs/intro for more involved validation library

    # optinal label
    label = models.CharField(
        max_length=80, help_text="File label", default="", blank=True
    )

    # django file field helper
    # note we use a validator, but we ALSO do a separate validation for file size after the file is uploaded
    filefield = models.FileField(
        upload_to = calculateGameFileUploadPathRuntimeRelative, validators=[validateGameFile]
    )

    # foreign keys
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

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
        fileSize = self.filefield.file.size
        if fileSize > DefMaxUploadGameFileSize:
            raise ValidationError(
                "Uploaded file is too large ({:.2f}mb > {:.2f}mb)".format(
                    fileSize / 1000000, DefMaxUploadGameFileSize / 1000000
                )
            )

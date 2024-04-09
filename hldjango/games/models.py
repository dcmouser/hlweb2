from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError

from .validators import validateGameFile





# defines
DefMaxUploadGameFileSize = 10000000






class Game(models.Model):
    """Game object manages individual games/chapters/storybooks"""

    # author provides this info
    name = models.CharField(max_length=50, help_text="Name of the game")
    text = models.TextField(help_text="Game text", default="", blank=True)

    # is the game public
    ispublic = models.BooleanField(help_text="Is game publicly visible?")

    # foreign keys
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    # these properties should be extracted from the text
    title = models.CharField(max_length=50, help_text="Title of the game", default="", blank=True)
    summary = models.TextField(help_text="Short description", default="", blank=True)
    information = models.TextField(help_text="Long description, credits, links", default="", blank=True)
    version = models.CharField(max_length=32, help_text="Version information", default="", blank=True)
    difficulty = models.CharField(max_length=32, help_text="Difficulty", default="", blank=True)
    cautions = models.CharField(max_length=32, help_text="Age rage, etc.", default="", blank=True)
    duration = models.CharField(max_length=32, help_text="Expected playtime", default="", blank=True)

    # result of building
    buildLog = models.TextField(help_text="Build Log", default="", blank=True)


    # helpers
    def __str__(self):
        return "{} ({})".format(self.title, self.name)

    def get_absolute_url(self):
        return reverse("gameDetail", kwargs={"pk": self.pk})








# helper
def calculateGameFileUploadPathRuntime(instance, filename):
    game = instance.game
    gamePk = game.pk
    return '/'.join(['games', str(gamePk), 'uploads', filename])





class GameFile(models.Model):
    """File object manages files attached to games"""
    # ATTN: TODO: see https://file-validator.github.io/docs/intro for more involved validation library

    # optinal label
    label = models.CharField(max_length=80, help_text="File label", default="", blank=True)


    # django file field helper
    # note we use a validator, but we ALSO do a separate validation for file size after the file is uploaded
    filefield = models.FileField(upload_to=calculateGameFileUploadPathRuntime, validators=[validateGameFile])

    # foreign keys
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)


    def __str__(self):
        return self.filefield.name
    
    def get_absolute_url(self):
        return reverse("gameFileDetail", kwargs={'pk':self.pk})


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
        if (fileSize > DefMaxUploadGameFileSize):
            raise ValidationError("Uploaded file is too large ({:.2f}mb > {:.2f}mb)".format(fileSize/1000000, DefMaxUploadGameFileSize/1000000))



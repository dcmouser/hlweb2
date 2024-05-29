# django
from django import forms

# ace editor widget
from django_ace import AceWidget

# user
from .models import Game, GameFile








# see https://stackoverflow.com/questions/77212709/django-clearablefileinput-does-not-support-uploading-multiple-files-error
# see https://docs.djangoproject.com/en/5.0/topics/http/file-uploads/#:~:text=If%20you%20want%20to%20upload,also%20have%20to%20subclass%20FileField%20.
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class GameFileMultipleUploadForm(forms.Form):
    # see GameFile model for where these map; note we are not deriving from modelForm 
    files = MultipleFileField(label='Select files', required=True)
    note = forms.CharField(max_length=80, help_text="Internal comments (optional)", required=False)



class GameFormForEdit(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["name", "slug", "preferredFormatPaperSize", "preferredFormatLayout", "isPublic", "text", "gameName", "lastBuildLog", "title", "subtitle", "authors", "version", "versionDate", "summary", "difficulty", "cautions", "duration", "extraInfo", "url", "textHash", "textHashChangeDate", "publishDate", "leadStats", "settingsStatus", "buildResultsJsonField", ]
        # or any other fields you want on the form
        widgets = {
            "text": AceWidget(mode="markdown", width="100%", height="300px", wordwrap=True, showprintmargin=False,)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        myReadOnlyFieldList = ["lastBuildLog", "gameName", "title", "subtitle", "authors", "version", "versionDate", "summary", "difficulty", "cautions", "duration", "extraInfo", "url", "textHash", "textHashChangeDate", "publishDate", "leadStats", "settingsStatus", "buildResultsJsonField"]
        for fieldName in myReadOnlyFieldList:
            self.fields[fieldName].disabled = True




class GameFormForCreate(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["name", "preferredFormatPaperSize", "preferredFormatLayout", "isPublic", "text"]
        # or any other fields you want on the form
        widgets = {
            "text": AceWidget(mode="markdown", width="100%", height="300px", wordwrap=True, showprintmargin=False,),
        }

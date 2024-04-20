from django import forms

from .models import Game, GameFile



class BuildGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = "__all__"





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



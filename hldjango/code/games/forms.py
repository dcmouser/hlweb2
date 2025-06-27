# django
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.auth import get_user_model
#
from crispy_forms.helper import FormHelper

# ace editor widget
from django_ace import AceWidget

# user
from .models import Game, GameFile


# helpers
from lib.jr import jrfuncs, jrdfuncs







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
    note = forms.CharField(max_length=80, help_text="Internal comments (leave blank)", required=False)



class GameFormForEdit(forms.ModelForm):
    class Meta:
        model = Game
        #fields = ["name", "slug", "subdirname", "preferredFormatPaperSize", "preferredFormatLayout", "isPublic", "text", "gameName", "lastBuildLog", "title", "subtitle", "authors", "version", "versionDate", "status", "summary", "difficulty", "cautions", "duration", "extraInfo", "extraCredits", "url", "copyright", "textHash", "textHashChangeDate", "publishDate", "leadStats",]
        fields = ["name", "slug", "subdirname", "isPublic", "preferredFormatPaperSize", "preferredFormatLayout", "text", "instructions", "gameName", "lastBuildLog", "adminSortKey", "title", "subtitle", "authors", "version", "versionDate", "status", "summary", "difficulty", "cautions", "duration", "extraCredits", "url", "copyright", "gameSystem", "gameDate", "campaignName", "campaignPosition", "textHash", "textHashChangeDate", "publishDate", "leadStats","editors", ]
        myReadOnlyFieldList = ["subdirname", "lastBuildLog", "gameName", "title", "subtitle", "authors", "version", "versionDate", "status", "summary", "difficulty", "cautions", "duration", "extraCredits", "url", "copyright", "gameSystem", "gameDate", "campaignName", "campaignPosition", "textHash", "textHashChangeDate", "publishDate", "leadStats" ]
        # tryint to set exclude 
        exclude = myReadOnlyFieldList

        # or any other fields you want on the form
        # see https://github.com/django-ace/django-ace
        widgets = {
            "text": AceWidget(mode="markdown", width="100%", height="600px", wordwrap=True, showprintmargin=False, fontsize="12pt"),
            "instructions": forms.Textarea(attrs={"rows": 4}), # custom in order to reduce height
            #'name': forms.TextInput(attrs={'class': 'jrinlineField'}),
            #'slug': forms.TextInput(attrs={'class': 'jrinlineField'}),
            #'subdirname': forms.TextInput(attrs={'class': 'jrinlineField'}),
            #"editors": forms.ModelMultipleChoiceField(queryset=get_user_model().objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
            "editors": forms.CheckboxSelectMultiple(attrs={'required': False}),
        }
        labels = jrdfuncs.jrPopoverLabels(model, fields)
        help_texts = jrdfuncs.jrBlankFields(model, fields)

    def __init__(self, *args, **kwargs):
        # note that this requires we customize the editView class to pass in ownerId to this form's kwargs (see views.py)
        # and we need to REMOVE (POP) it otherwise the super class will complain
        ownerId = kwargs.pop('ownerId', None)  # Retrieve and remove owner_id from kwargs
        requestUser = kwargs.pop('requestUser', None) # retrieve requst ueser

        super().__init__(*args, **kwargs)

        UserModel = get_user_model()

        if (False):
            #myReadOnlyFieldList = ["subdirname", "lastBuildLog", "gameName", "title", "subtitle", "authors", "version", "versionDate", "status", "summary", "difficulty", "cautions", "duration", "extraInfo", "extraCredits", "url", "copyright", "textHash", "textHashChangeDate", "publishDate", "leadStats",  ]
            myReadOnlyFieldList = self._meta.myReadOnlyFieldList  
            for fieldName in myReadOnlyFieldList:
                self.fields[fieldName].disabled = True
                # ATTN: my attempt to ignore certain fields since they are auto set
                # without this we have a terrible thing that can happen where user saves a game, a calculated value (like caution) is too long, but it saves anyway, then throws any error attempting to save it, even though the value in form is ignored
                if (fieldName in self.errors):
                    del self.errors[fieldName]
                    # for safety reasons it would be nice to force this value to blank in the form just in case we are wrong about it being readonly
                    del self.fields[fieldName]

        # Disable the field if the user is not in the allowed group
        if (not jrdfuncs.userIsAuthenticatedAndGadmin(requestUser)):
            self.fields['adminSortKey'].disabled = True

        # add error class to buildLog if appropriate; kludgey
        lastBuildLog = self.initial.get("lastBuildLog", "")
        if ("Errors" in lastBuildLog):
            self.fields["lastBuildLog"].widget.attrs["class"] = "textErrored"

        # limit the editors list to only users with the permission to edit games (thanks chatgpt)

        permissionId = settings.JR_PERMISSIONNAME_CANPUBLISHGAMES
        queryset = UserModel.objects.filter(groups__permissions__codename=permissionId)
        # exclude the owner from this additional list
        if ownerId:
            queryset = queryset.exclude(id=ownerId)
        self.fields['editors'].queryset = queryset





class GameFormForCreate(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["name", "preferredFormatPaperSize", "preferredFormatLayout", "isPublic", "text", "instructions"]
        # or any other fields you want on the form
        widgets = {
            "text": AceWidget(mode="markdown", width="100%", height="600px", wordwrap=True, showprintmargin=False, fontsize="12pt"),
            "instructions": forms.Textarea(attrs={"rows": 4}), # custom in order to reduce height
        }
        labels = jrdfuncs.jrPopoverLabels(model, fields)
        help_texts = jrdfuncs.jrBlankFields(model, fields)





class GameFormForChangeDir(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["subdirname", ]
        labels = jrdfuncs.jrPopoverLabels(model, fields)
        help_texts = jrdfuncs.jrBlankFields(model, fields)







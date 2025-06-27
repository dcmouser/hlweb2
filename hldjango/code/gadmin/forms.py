from django import forms
# ace editor widget
from django_ace import AceWidget

from crispy_forms.helper import FormHelper


from .models import GlobalSettings

class GlobalSettingsForm(forms.ModelForm):
    class Meta:
        model = GlobalSettings
        fields = ["homePageHtml", "aboutPageHtml", "downloadPageHtml"]
        # or any other fields you want on the form
        # see https://github.com/django-ace/django-ace
        widgets = {
            "aboutPageHtml": AceWidget(mode="html", width="100%", height="200px", wordwrap=True, showprintmargin=False, fontsize="10pt"),
            "homePageHtml": AceWidget(mode="html", width="100%", height="200px", wordwrap=True, showprintmargin=False, fontsize="10pt"),
            "downloadPageHtml": AceWidget(mode="html", width="100%", height="200px", wordwrap=True, showprintmargin=False, fontsize="10pt"),
        }

# django
from django.utils import timezone
from django.contrib import messages

# python modules
from datetime import datetime


def convertTimeStampToDateTimeDefaultNow(timeStamp):
    if (timeStamp is None):
        return timezone.now()
    return datetime.fromtimestamp(timeStamp)



def lookupDjangoChoiceLabel(enumKey, enumList):
    for enumItem in enumList:
        if (enumItem[0]==enumKey):
            return enumItem[1]
    # not found
    return enumKey






def addFlashMessage(request, str, flagIsError):
    if flagIsError or ("error" in str.lower()):
        messages.add_message(request, messages.ERROR, str)
    else:
        messages.add_message(request, messages.INFO, str)


def addFlashMessages(request, strList):
    for str in strList:
        addFlashMessage(request, str, False)

# django
from django.utils import timezone

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

# class that manages days in a case, when they start and end, etc.

from .casebookDefines import *

from lib.jr import jrfuncs

from datetime import datetime, timedelta

# translation
from .cblocale import _




class CbDayManager:
    def __init__(self):
        self.dayDict = {}
    def findDayByNumber(self, dayNumber, flagAllowTempCalculatedDay):
        if (dayNumber in self.dayDict):
            return self.dayDict[dayNumber]
        elif (flagAllowTempCalculatedDay):
            # temp created day, this allows us to generate things like day of week for day -2 (2 days before 1st day, etc.)
            # get first day
            dayOne = self.findDayByNumber(1, False)
            if (dayNumber<0):
                dayPlus = dayNumber
            else:
                dayPlus = dayNumber - 1
            # make copy
            dayCalculated = dayOne.makeCopy()
            # adjust day
            dayCalculated.dayNumber = dayCalculated.dayNumber + dayPlus
            dayCalculated.dayDate = dayCalculated.dayDate + timedelta(dayPlus)
            return dayCalculated
        return None
    def addDay(self, day):
        self.dayDict[day.getDayNumber()] = day
    def getDayDict(self):
        return self.dayDict
    def getDayCount(self):
        return len(self.dayDict)









class CbDay:
    def __init__(self, dayNumber, dayType, dayDate, startTime, endTime, freeAlly, freeAllyStartTime, freeAllyEndTime):
        self.dayNumber = dayNumber
        self.dayType = dayType
        self.startTime = jrfuncs.convertStringToHoursMinsNumberIfNeeded(startTime)
        self.endTime = jrfuncs.convertStringToHoursMinsNumberIfNeeded(endTime)
        self.freeAlly = freeAlly
        self.freeAllyStartTime = jrfuncs.convertStringToHoursMinsNumberIfNeeded(freeAllyStartTime)
        self.freeAllyEndTime = jrfuncs.convertStringToHoursMinsNumberIfNeeded(freeAllyEndTime)
        if (isinstance(dayDate,str)):
            self.dayDate = datetime.strptime(dayDate,DefCbDefine_ParseDayConfigureDate)
            self.dayDate = jrfuncs.replaceFractionalHourTime(self.dayDate, self.startTime)
        else:
            self.dayDate = dayDate


    def getDayNumber(self):
        return self.dayNumber

    def getMindMapNodeInfo(self):
        mmInfo = {
            "id": "DAY." + str(self.dayNumber),
            "label": "Day" + str(self.dayNumber),
            "type": "day",
            "pointer": self,
            "mStyle": None,
            "showDefault": True,
            }
        return mmInfo

    def getStartTime(self):
        return self.startTime
    def getEndTime(self):
        return self.endTime

    def getFreeAlly(self):
        return self.freeAlly
    def getFreeAllyStartTime(self):
        return self.freeAllyStartTime
    def getFreeAllyEndTime(self):
        return self.freeAllyEndTime
    def getDayNumber(self):
        return self.dayNumber

    def getDate(self):
        return self.dayDate

    def getDayOfWeek(self):
        return self.dayDate.strftime("%A")
    def getDayOfWeekShort(self):
        return self.dayDate.strftime("%a")

    def getDayNumberDateShortNoYear(self):
        dayDateStr = self.dayDate.strftime("%a %b ") + self.dayDate.strftime("%d").lstrip("0")
        text = "{} {} ({})".format(_("day"), self.dayNumber, dayDateStr)
        return text

    def getDayNumberDateLong(self):
        dayDateStr = self.dayDate.strftime("%A %B %d, %Y")
        text = "{} {} ({})".format(_("day"), self.dayNumber, dayDateStr)
        return text


    def makeCopy(self):
        newDay = CbDay(self.dayNumber, self.dayType, self.dayDate, self.startTime, self.endTime, self.freeAlly, self.freeAllyStartTime, self.freeAllyEndTime)
        return newDay



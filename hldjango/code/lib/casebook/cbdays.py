# class that manages days in a case, when they start and end, etc.




class CbDayManager:
    def __init__(self):
        self.dayDict = {}
    def findDayByNumber(self, dayNumber):
        if (dayNumber in self.dayDict):
            return self.dayDict[dayNumber]
        return None
    def addDay(self, day):
        self.dayDict[day.getDayNumber()] = day
    def getDayDict(self):
        return self.dayDict









class CbDay:
    def __init__(self, dayNumber, dayType, startTime, endTime, freeAlly, freeAllyStartTime, freeAllyEndTime):
        self.dayNumber = dayNumber
        self.dayType = dayType
        self.startTime = startTime
        self.endTime = endTime
        self.freeAlly = freeAlly
        self.freeAllyStartTime = freeAllyStartTime
        self.freeAllyEndTime = freeAllyEndTime

    def getDayNumber(self):
        return self.dayNumber

    def getMindMapNodeInfo(self):
        mmInfo = {
            "id": "DAY." + str(self.dayNumber),
            "label": "Day" + str(self.dayNumber),
            "type": "day",
            "pointer": self,
            "mStyle": None,
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
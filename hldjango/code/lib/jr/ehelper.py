from . import jrfuncs
from .jrfuncs import jrprint


# Class to help track errors, warnings, etc.
class EHelper():
    def __init__(self):
        self.clearErrorsAndWarnings()
        self.setConsoleShowOptions(False, False, False)


    def setConsoleShowOptions(self, consoleShowInfos, consoleShowWarnings, consoleShowErrors):
        self.consoleShowInfos = consoleShowInfos
        self.consoleShowWarnings = consoleShowWarnings
        self.consoleShowErrors = consoleShowErrors

    def clearErrorsAndWarnings(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def getErrors(self):
        return self.errors
    def getErrorCount(self):
        return len(self.errors)

    def isErrored(self):
        return (self.getErrorCount()>0)

    def getWarnings(self):
        return self.warnings
    def getWarningCount(self):
        return len(self.warnings)

    def getInfos(self):
        return self.infos
    def getInfoCount(self):
        return len(self.infos)


    def addError(self, msg):
        self.errors.append(msg)
        if (self.consoleShowErrors):
            jrprint("ERROR: " + msg)

    def addWarning(self, msg):
        self.warnings.append(msg)
        if (self.consoleShowWarnings):
            jrprint("WARNING: " + msg)

    def addInfo(self, msg):
        self.infos.append(msg)
        if (self.consoleShowInfos):
            jrprint("INFO: " + msg)


    def addException(self, e, contextStr):
        # add exception as an error
        msg = jrfuncs.exceptionPlusSimpleTraceback(e, contextStr)
        self.addError(msg)


    def getErrorWarningLog(self):
        text = ""
        text += self.getListWithHeading("Errors", self.errors)
        text += self.getListWithHeading("Warnings", self.warnings)
        text += self.getListWithHeading("Info", self.infos)
        return text
    
    def getListWithHeading(self, label, itemList):
        if (len(itemList)==0):
            return ""
        text = label +"\n"
        text += "\n".join(itemList)
        return text

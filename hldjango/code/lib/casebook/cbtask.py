
# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint

# render run modes
DefRmodeRun = "run"
DefRmodeRender = "render"



class CbTask:
    def __init__(self, interp, taskId, taskOptions, rMode):
        self.interp = interp
        self.taskId = taskId
        self.rMode = rMode
        self.renderer = None
        self.renderFormat = None
        #
        self.taskOptions = taskOptions
        #
        self.reportMode = jrfuncs.getDictValueOrDefault(taskOptions, "reportMode", False)
        #
        self.log = ""

    def getTaskId(self):
        return self.taskId
    def getRmode(self):
        return self.rMode
    def getRenderFormat(self):
        return self.renderFormat
    def setRenderFormat(self, renderFormat):
        self.renderFormat = renderFormat
    def setRenderer(self, renderer):
        self.renderer = renderer
    def getRenderer(self):
        return self.renderer
    def setInterp(self, interp):
        self.interp = interp
    def getInterp(self):
        return self.interp
    def getOption(self, key, defaultVal=None):
        return jrfuncs.getDictValueOrDefault(self.taskOptions, key, defaultVal)

    def setReportMode(self, reportMode):
        self.reportMode = reportMode
    def getReportMode(self):
        return self.reportMode
    
    def addTextToLog(self, text):
        self.log += text + "\n"
    def getLog(self):
        return self.log

    def getEnvironment(self):
        return self.getInterp().getEnvironment()


    def printDebug(self, env):
        self.getRenderer().printDebug(env)





    def calcMakeSuffixedOutputDirectory(self):
        outputPath = self.getOption("outputPath", None)
        outputSubdir = self.getOption("outputSubdir", None)
        if (outputSubdir!=""):
            suffixedOutputPath =  outputPath + "/" + outputSubdir
        else:
            suffixedOutputPath =  outputPath
        jrfuncs.createDirIfMissing(suffixedOutputPath)
        return suffixedOutputPath

    def calcBaseFileName(self):
        baseFileName = self.getOption("baseFileName", None)
        return baseFileName

    def calcSuffixedBaseFileName(self):
        baseFileName = self.calcBaseFileName()
        outputSuffix = self.getOption("outputSuffix", None)
        suffixedFileName = baseFileName + outputSuffix
        return suffixedFileName



# this class manages interaction with casebook interpretter

# interpreter
from lib.casebook.jrinterpCasebook import JrInterpreterCasebook
#
from lib.casebook.casebookDefines import *

from lib.jr.jrfuncs import jrprint
from lib.jr import jrfuncs




class CasebookWrapper:
    def __init__(self, debugMode):
        self.debugMode = debugMode
        self.continueOnException = False
        #
        # grammar file is in a subdirectory of our casebook interpretter called ./grammardaata
        self.grammarFilePath = "$GRAMMARDATA/casebook_grammar.lark"
        #
        self.jrinterp = JrInterpreterCasebook(self.debugMode, False)


    def getGeneratedFileList(self):
        return self.jrinterp.getGeneratedFileList()

    def getBuildLog(self):
        text = self.jrinterp.getBuildLog()
        return text

    def getDebugMode(self):
        return self.debugMode
    
    def getLeadStats(self):
        # get stats from last renderer run
        env = self.jrinterp.getEnvironment()
        renderer = env.getRenderer()
        if (renderer):
            leadStatsString = renderer.calcLeadStatsString(env)
        else:
            leadStatsString = "n/a"
        #
        leadStats = {
            "summaryString": leadStatsString
        }
        return leadStats

    def isErrored(self):
        return self.jrinterp.isErrored()
    def clearErrorsAndWarnings(self):
        self.jrinterp.clearErrorsAndWarnings()



    def runBuilds(self, gameText, buildList, options, progressCallback):
        self.clearErrorsAndWarnings()
        #
        parserOptions =  {
            "grammarFilePath": self.grammarFilePath,
            "startSymbol": "start",
            "encoding": "utf-8",
            #"sourceFilePath": sourceFilePath,
            "sourceFileText": gameText,
            "autoRunEarly": True,
        }
        # general options
        generalOptions = {
            "debugMode": self.debugMode,
            "continueOnException": self.continueOnException,
            # media directories for loading in files
            "localMediaDirectory": options["localMediaDirectory"],
            "sharedMediaDirectory": options["sharedMediaDirectory"],
        }
        #
        baseFileName = options["baseFileName"]

        # jobs
        taskList = []
        for build in buildList:
            variantType = jrfuncs.getDictValueOrDefault(build,"variant","")
            reportMode = jrfuncs.getDictValueOrDefault(build,"reportMode",False)
            task = {
                "label": build["label"],
                "taskName": build["task"],
                "outputPath": build["outputPath"],
                "reportMode": reportMode,
                "variant": variantType,
                #
                "baseFileName": baseFileName,
                "outputSuffix": jrfuncs.getDictValueOrDefault(build,"suffix",""),
                "outputSubdir": "",
                #
                # extra stuff to do
                "taskGenerateMindMap": reportMode,
                "taskSaveLeadJsons": reportMode,
                "taskSaveHtmlSource": reportMode,
                #
                # no longer zip files as part of task but rather as a separate task
                "taskZipFiles": False,
                #
                "cleanExtras": jrfuncs.getDictValueOrDefault(build,"cleanExtras",None),
                "convert": jrfuncs.getDictValueOrDefault(build,"convert",None),
                "convertSuffix": jrfuncs.getDictValueOrDefault(build,"convertSuffix",None),
                # gamepk
                "gamePk": jrfuncs.getDictValueOrDefault(build,"gamePk",None),
            }
            # copy in render Options
            if ("renderOptions" in build):
                # copy all renderOptions
                jrfuncs.deepMergeOverwriteA(task, build["renderOptions"])
            taskList.append(task)

        #
        job = {
            "label": "hlweb game build",
            "tasks": taskList,
            "parserOptions": parserOptions,
            "generalOptions": generalOptions,
            }

        # run the job
        self.jrinterp.runJobs([job], progressCallback)
        #
        isErrored = self.jrinterp.isErrored()
        if (self.getDebugMode()):
            jrprint("Done runnning tasks{}.".format(" (ERRORS)" if (self.isErrored()) else ""))

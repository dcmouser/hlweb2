# this class manages interaction with casebook interpretter

# interpreter
from lib.casebook.jrinterpCasebook import JrInterpreterCasebook
from lib.casebook.cbtasks import CbTaskLatex
#
from lib.casebook.casebookDefines import *

from lib.jr.jrfuncs import jrprint




class CasebookWrapper:
    def __init__(self):
        self.debugMode = True
        self.continueOnException = False
        #
        # grammar file is in a subdirectory of our casebook interpretter called ./grammardaata
        self.grammarFilePath = "$GRAMMARDATA/casebook_grammar.lark"
        #
        self.jrinterp = JrInterpreterCasebook(self.debugMode, False)


    def getGeneratedFileList(self):
        return self.jrinterp.getGeneratedFileList()

    def getBuildLog(self):
        return "Build log for jrinterp not implemented yet."
    
    def getLeadStats(self):
        # get stats from last renderer run
        renderer = self.jrinterp.getEnvironment().getRenderer()
        if (renderer):
            leadStatsString = renderer.calcLeadStatsString()
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
            variantType = build["variant"] if ("variant" in build) else ""
            reportMode = build["reportMode"] if ("reportMode" in build) else False
            task = {
                "label": build["label"],
                "taskName": build["task"],
                "outputPath": build["outputPath"],
                "reportMode": reportMode,
                "variant": variantType,
                #
                "baseFileName": baseFileName,
                "outputSuffix": build["suffix"] if ("suffix" in build) else "",
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
                # render options
                "latexPaperSize": build["latexPaperSize"] if ("latexPaperSize" in build) else None,
                "latexFontSize": build["latexfontSize"] if ("latexfontSize" in build) else None,
                "doubleSided": build["doubleSided"] if ("doubleSided" in build) else None,
                "leadColumns": build["leadColumns"] if ("leadColumns" in build) else None,
                "leadBreak": build["leadBreak"] if ("leadBreak" in build) else None,
                "convert": build["convert"] if ("convert" in build) else None,
                #
                "cleanExtras": build["cleanExtras"] if ("cleanExtras" in build) else None,
            }
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
        jrprint("Done runnning tasks{}.".format(" (ERRORS)" if (self.isErrored()) else ""))

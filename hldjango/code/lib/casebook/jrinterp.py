# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from lib.jr.ehelper import EHelper

# jesse lark parser
from lib.jrlark import jrlark

from lib.casebook.cbenvironment import JrCbEnvironment
from .cbplugin import CbPluginManager

# python modules
import traceback
from pathlib import Path




class JrInterpreter:
    def __init__(self, debugMode):
        from .cbdeepsource import CbDeepSource
        #
        self.eHelper = EHelper()
        self.setDebugMode(debugMode)

        self.continueOnException = False
        self.exceptionTracebackLimit = 1
        #
        self.notes = []
        #
        # Context and Environment
        self.environment = JrCbEnvironment(self, None)
        #
        # manage source
        self.deepSource = CbDeepSource()
        #
        # lead processing plugins, etc.
        self.pluginManager = CbPluginManager(self)
        #
        # parser
        self.jrparser = jrlark.JrParserEngineLark()
        #
        # derived class needs to do this
        self.ast = None
        #
        self.generatedFiles = []
        self.getGeneratedFilesForZip = []

    def isErrored(self):
        return self.eHelper.isErrored()
    def clearErrorsAndWarnings(self):
        self.eHelper.clearErrorsAndWarnings()

    def getPluginManager(self):
        return self.pluginManager

    def getEnvironment(self):
        return self.environment

    def setDebugMode(self, debugMode):
        self.debugMode = debugMode
        self.eHelper.setConsoleShowOptions(debugMode, debugMode, debugMode)

    def getDebugMode(self):
        return self.debugMode

    def setContinueOnException(self, val):
        self.continueOnException = val
    def getFlagContinueOnException(self):
        return self.continueOnException

    def getAstRoot(self):
        return self.ast

    def getDeepSource(self):
        return self.deepSource

    def displayException(self, e, flagContinuing):
        tracebackLimit = self.exceptionTracebackLimit
        if (tracebackLimit >= 0):
            tracebackLines = traceback.format_exception(e, limit = tracebackLimit)
            tracebackText = "\n".join(tracebackLines)
        else:
            tracebackText = "disabled"
        #
        if (flagContinuing):
            jrprint("CONTINUING AFTER EXCEPTION: {}.  Traceback: {}.".format(repr(e), tracebackText))


    def addNote(self, note):
        self.notes.append(note)
    def getNotes(self):
        return self.notes
    def getNotesFiltered(self, filterLead, filterTypeStr):
        filteredNoteList = []
        for note in self.notes:
            if (filterLead is not None):
                if (filterLead != note.lead):
                    continue
            if (filterTypeStr is not None):
                if (filterTypeStr != note.typeStr):
                    continue
            filteredNoteList.append(note)
        return filteredNoteList


    def getEhelper(self):
        return self.eHelper
    def addError(self, msg):
        return self.eHelper.addError(msg)
    def addWarning(self, msg):
        return self.eHelper.addWarning(msg)
    def addInfo(self, msg):
        return self.eHelper.addInfo(msg)
    def addException(self, e, contextStr):
        return self.eHelper.addException(e, contextStr)
    def clearEHelper(self):
        self.eHelper.clear()

    def getThisSourceDirectory(self):
        source_path = Path(__file__).resolve()
        source_dir = source_path.parent
        return str(source_dir)


    def loadGrammarParseSourceFile(self, grammarFilePath, sourceFilePath, sourceFileText, startSymbol, encoding):
        # set case file path stuff
        env = self.getEnvironment()
        # PART 1: Load casebook grammar from .lark file
        self.jrparser.loadGrammarFileFromPath(env, grammarFilePath, encoding)
        # PART 2: Load main text file to parse
        self.deepSource.loadSourceFromFilePathOrText(sourceFilePath, sourceFileText, encoding, "")
        # PART 2b: expand macros in source
        self.deepSource.runMacros(env)
        # PART 3: parse source text
        parseTree = self.jrparser.parseText(env, self.deepSource, startSymbol)




    def runJobEarlyGenerics(self, job):
        # general options
        generalOptions = jrfuncs.getDictValueOrDefault(job, "generalOptions", None)
        if (generalOptions is not None):
            debugMode = jrfuncs.getDictValueOrDefault(generalOptions, "debugMode", None)
            if (debugMode is not None):
                self.setDebugMode(debugMode)
            continueOnException = jrfuncs.getDictValueOrDefault(generalOptions, "continueOnException", None)
            if (continueOnException is not None):
                self.setContinueOnException(continueOnException)
            #
            # local and shared media
            sharedMediaDirectory = jrfuncs.getDictValueOrDefault(generalOptions, "sharedMediaDirectory", None)
            localMediaDirectory = jrfuncs.getDictValueOrDefault(generalOptions, "localMediaDirectory", None)
            self.setupMediaDirectories(sharedMediaDirectory, localMediaDirectory)

        # parsing options
        parserOptions = jrfuncs.getDictValueOrDefault(job, "parserOptions", None)
        if (parserOptions is not None):
            autoRunEarly = jrfuncs.getDictValueOrDefault(parserOptions, "autoRunEarly", True)
            if (autoRunEarly):
                self.runJobEarlyGenericsParser(job)


    def runJobEarlyGenericsParser(self, job):
        parserOptions = jrfuncs.getDictValueOrDefault(job, "parserOptions", None)
        if (parserOptions is not None):
            if (True):
                # parse a source file
                # ATTN: in future we would like to skip this if the file has ALREADY been parsed
                grammarFilePath = jrfuncs.getDictValueOrDefault(parserOptions, "grammarFilePath", None)
                grammarFilePath = grammarFilePath.replace("$GRAMMARDATA", self.getThisSourceDirectory()+"/grammardata")
                sourceFilePath = jrfuncs.getDictValueOrDefault(parserOptions, "sourceFilePath", None)
                sourceFileText = jrfuncs.getDictValueOrDefault(parserOptions, "sourceFileText", None)
                startSymbol = jrfuncs.getDictValueOrDefault(parserOptions, "startSymbol", None)
                encoding = jrfuncs.getDictValueOrDefault(parserOptions, "encoding", None)
                try:
                    # PART 1: Ask interpretter to parse
                    self.loadGrammarParseSourceFile(grammarFilePath, sourceFilePath, sourceFileText, startSymbol, encoding)
                except Exception as e:
                    self.addException(e, "Lark-parsing source")
                    # pass the exception up?
                    raise e

                # PART 2: Convert parse tree to our interpretter AST class
                self.convertParseTreeToAst()



    def setupMediaDirectories(self, sharedMediaDirectory, localMediaDirectory):
        if (sharedMediaDirectory is not None):
            self.sharedMediaDirectory = sharedMediaDirectory.replace("\\","/")
        if (localMediaDirectory is not None):
            self.localMediaDirectory = localMediaDirectory.replace("\\","/")




    def runJobs(self, jobList, progressCallback):
        for job in jobList:
            self.runJob(job, progressCallback)
            if (self.isErrored()):
                break


    def runJob(self, job, progressCallback):
        #
        # TEST
        if (False):
            import json
            jobCopy = jrfuncs.deepCopyListDict(job)
            jobCopy["parserOptions"]["sourceFileText"] = ""
            jrfuncs.jrprint(json.dumps(jobCopy, indent=5))

        jobLabel = job["label"]
        runTimer = jrfuncs.JrPerfTimer("job '{}'".format(jobLabel), self.getDebugMode())
        # run a job
        # early
        self.runJobEarlyGenerics(job)
        # main
        tasks = jrfuncs.getDictValueOrDefault(job, "tasks", None)
        if (tasks is not None):
            taskCount = len(tasks)
            taskIndex = 0
            for taskOptions in tasks:
                taskIndex += 1
                taskLabel = jrfuncs.getDictValueOrDefault(taskOptions, "label", "anonymous")
                taskName = jrfuncs.getDictValueOrDefault(taskOptions, "taskName", None)
                retv = self.runJobTask(self.getEnvironment(), job, taskName, taskOptions)
                if (not retv):
                    self.eHelper.addError("Error returned from runJobTask ({}/{}).".format(taskName, taskLabel))
                    break
                progressPercent = taskIndex / taskCount
                if (progressCallback is not None) and (taskIndex<taskCount):
                    retv = progressCallback({"progress":progressPercent})
                    if (not retv):
                        self.eHelper.addError("Task aborted after completing {}%".format(int(progressPercent*100)))
                        break
        # late
        if (not self.isErrored()):
            self.runJobLateGenerics(job)
        #
        if (self.getDebugMode()):
            runTimer.printElapsedTime()
    


    def runJobLateGenerics(self, job):
        # nothing to do?
        pass

    def preBuildPreRender(self):
        # run the pre build for all plugins
        self.getPluginManager().preBuildPreRender(self.getEnvironment())

    def postBuildPreRender(self):
        # run the post build for all plugins
        self.getPluginManager().postBuildPreRender(self.getEnvironment())







    def addGeneratedFile(self, filePath, flagAddZipList = True):
        self.generatedFiles.append(filePath)
        if (flagAddZipList):
            self.getGeneratedFilesForZip.append(filePath)

    def removeGeneratedFile(self, filePath):
        self.generatedFiles.remove(filePath)
        self.getGeneratedFilesForZip.remove(filePath)

    def getGeneratedFileList(self):
        return self.generatedFiles
    def getGeneratedFileListForZip(self):
        return self.getGeneratedFilesForZip

    def clearGeneratedFileListForZip(self):
        self.getGeneratedFilesForZip = []

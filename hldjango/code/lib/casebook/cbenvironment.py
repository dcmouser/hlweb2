# jrast
from .jrastfuncs import wrapValIfNotAlreadyWrapped, unwrapIfWrappedVal
from .jrastvals import AstValObject
from .jriexception import *
from .jrastutilclasses import JrINote

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint


# A note on JrAstContext vs JrCbEnvironment

# an Environment object is a storage of state information -- variable assignments
# it is hierarchical so supports SCOPED resolution of variables where we may have a chain of scopes and want to find a variable in the closest scope
# as such, it is a RUNTIME data structure; it is the primary data structure that we pass around the hierarchy when we are executing code
# and we may create new child environments on the fly
# you could even imagine (though we do not do it currently) running multiple functions in parallel with different environments using the same ast tree

from .casebookDefines import *

# python modules
import difflib




# An environment is a dictionary of variable assignments, with a pointer to parent enclosing environment
class JrCbEnvironment:
    def __init__(self, interp, parentEnv):
        self.parentEnv = parentEnv
        #
        # we can avoid storing context in every sub child environment if we like, to save memory space?
        if (parentEnv is None):
            self.interp = interp
        #
        self.envDict = {}
        #
        # create root task variable which will be set by task
        if (parentEnv is None):
            self.declareEnvVar(None, "task", "", None, True)


    def getDebugMode(self):
        interp = self.getInterp()
        return interp.getDebugMode()
    def getReportMode(self):
        return self.getTask().getReportMode()

    def getFlagContinueOnException(self):
        return self.getInterp().getFlagContinueOnException()
    
    def getEnvDict(self):
        return self.envDict


    # environmental variables (note that on set we just overwrite)

    # NOTE: identifier names can be DOTTED hierarchies inside objects; we need to handle that

    # lookup env var and go up hierarchy if needed
    def lookupJrEnvVar(self, sloc, identifierName, flagGoUpHierarchy):
        # return [envVar, baseName, partList]

        # split identifier into base and parts
        [baseVarName, propertyParts] = self.splitIndentifierParts(identifierName)

        if (baseVarName in self.envDict):
            # its defined locally; return the triplet
            return [self.envDict[baseVarName], baseVarName, propertyParts]
        if (flagGoUpHierarchy) and (self.parentEnv is not None):
            # search up hierarchy of environments
            return self.parentEnv.lookupJrEnvVar(sloc, identifierName, True)

        # not found
        return [None, None, None]


    def splitIndentifierParts(self, identifierName):
        parts = identifierName.split(".")
        if (len(parts)==0):
            return [None, None]
        if (len(parts)==1):
            return [parts[0], None]
        return [ parts[0], parts[1:] ]


    # declare var in THIS env scope
    def declareEnvVar(self, sloc, identifierName, description, val, isConstant):
        [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, False)
        # first, complain if they try to DECLARE a dotted name
        if (partList is not None):
            raise self.makeEnvException("Error; dotted object identifiers ({}) cannot be declared".format(identifierName), sloc)
        if (envVar is not None):
            # error already exists
            raise self.makeEnvExceptionWithPreviousValue("Runtime error; identifier '{}' already exists in current environment scope and so cannot be redeclared".format(identifierName), sloc, envVar)
        # ATTN: note that we dont complain if we are shadowing a parent env variable, but we COULD add a warning for it if we wanted
        if (True):
            [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, True)
            if (envVar is not None):
                # warning
                self.logEnvWarningWithPreviousValue("Runtime warning; declaring a variable '{}' which will shadow an existing variable in parent scope".format(identifierName), sloc, envVar)
        # create it
        self.createEnvVar(sloc, identifierName, description, val, isConstant)

    def createEnvVar(self, sloc, identifierName, description, val, isConstant):
        self.envDict[identifierName] = JrEnvVar(sloc, identifierName, description, val, isConstant)

    # set a value; NOTE we require all variables to be declared before use so this is an error if it cannot be found in scope -- it won't be creatded
    def setEnvValue(self, sloc, identifierName, val, flagCheckConst):
        [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, True)
        if (not envVar):
            # error does not exist
            raise self.makeEnvException("Runtime error; identifier '{}' has not been declared in this or any parent scope".format(identifierName), sloc)
        if (flagCheckConst and envVar.getIsConstant()):
            raise self.makeEnvExceptionWithPreviousValue("Runtime error; identifier {} has been declared constant and so cannot be reassigned".format(identifierName), sloc, envVar)
        # set the non-const value
        envVar.setValue(sloc, partList, val, flagCheckConst)


    # set a value; NOTE we require all variables to be declared before use so this is an error if it cannot be found in scope -- it won't be creatded
    def setCreateEnvValue(self, sloc, identifierName, val, flagCheckConst, isConstant):
        [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, True)
        if (not envVar):
            return self.declareEnvVar(sloc, identifierName, "description n/a", val, isConstant)
        if (flagCheckConst and envVar.getIsConstant()):
            raise self.makeEnvExceptionWithPreviousValue("Runtime error; identifier {} has been declared constant and so cannot be reassigned".format(identifierName), sloc, envVar)
        # set the non-const value
        envVar.setValue(sloc, partList, val, flagCheckConst)



    def getEnvValue(self, sloc, identifierName, defaultVal):
        [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, True)
        if (envVar is None):
            # not found
            return defaultVal
        # ask the envvar for its value
        retVal = envVar.getWrappedValue(sloc, partList)
        return retVal


    def getEnvValueUnwrapped(self, sloc, identifierName, defaultVal):
        [envVar, baseName, partList] = self.lookupJrEnvVar(sloc, identifierName, True)
        if (envVar is None):
            # not found
            return defaultVal
        retVal = envVar.getUnWrappedValue(sloc, partList)
        return retVal




    def loadFuncsFromModule(self, sloc, module):
        functionList = module.buildFunctionList()
        self.loadFuncsFromList(sloc, functionList)

    def loadFuncsFromList(self, sloc, functionList):
        from .jrastvals import AstValFunction

        for func in functionList:
            funcName = func.getName()
            funcVal = AstValFunction(None, None, func)
            funcDescription = funcVal.getDescription()
            self.declareEnvVar(sloc, funcName, funcDescription, funcVal, False)

    def getInterp(self):
        # this code allows us to ONLY store context with top level global env
        if (hasattr(self, "interp")):
            return self.interp
        if (self.parentEnv is not None):
            # recurse up to get context
            return self.parentEnv.getInterp()
        # not found
        raise Exception("Internal error: Environment .interp not found.")
        return None

    def makeChildEnv(self):
        # create a child environment
        childEnv = JrCbEnvironment(self.getInterp(), self)
        return childEnv



    def makeEnvException(self, msg, sloc):
        return makeJriException(msg, sloc)

    def makeEnvExceptionWithPreviousValue(self, msg, sloc, prevEnvVar):
        # ATTN: ADD source info from prevEnvVar
        return makeJriException(msg, [sloc, prevEnvVar.getSloc()])

    def logEnvWarningWithPreviousValue(self, sloc, msg, prevEnvVar):
        # ATTN: ADD source info from prevEnvVar and source info, etc.
        logJriWarning(msg, [sloc, prevEnvVar.getSloc()], self)



    def getTask(self):
        task = self.getEnvValue(None, "task", None)
        if (task is None):
            return None
        return task.getWrapped()
    def setTask(self, task):
        return self.setEnvValue(None, "task", task, False)

    def getRenderer(self):
        # ATTN: the renderer is handled by the task (for now)
        return self.getTask().getRenderer()

    def getPluginManager(self):
        return self.getInterp().getPluginManager()
    
    def getTagManager(self):
        return self.getInterp().getTagManager()

    def getConceptManager(self):
        return self.getInterp().getConceptManager()

    def getCheckboxManager(self):
        return self.getInterp().getCheckboxManager()

    def getBuildString(self):
        val = self.getInterp().getBuildString()
        return val

    def getQuestionManager(self):
        return self.getInterp().getQuestionManager()


    def getTypesetString(self, optionSimplified):
        # add latex compiler info
        task = self.getTask()
        if (task is None):
            return "n/a"
        taskOptions = task.getTaskOptions()
        #
        doubledSided = jrfuncs.getDictValueOrDefault(taskOptions, "doubleSided", "sided")
        latexPaperSize = jrfuncs.getDictValueOrDefault(taskOptions, "latexPaperSize", "papersize")
        latexFontSize = jrfuncs.getDictValueOrDefault(taskOptions, "latexFontSize", "fontsize ")
        taskBuildLabel = jrfuncs.getDictValueOrDefault(taskOptions, "label", "unlabeled")
        latexCompiler = jrfuncs.getDictValueOrDefault(taskOptions, "latexCompiler", "unknown latex compiler")
        if (doubledSided):
            sidedLatex = "twosided"
        else:
            sidedLatex = "oneside"

        if (optionSimplified):
            val = "{}pt {} {} ({})".format(latexFontSize, latexPaperSize, sidedLatex, latexCompiler)
        else:
            val = "{}pt {} {} - {} ({})".format(latexFontSize, latexPaperSize, sidedLatex, taskBuildLabel, latexCompiler)
        #
        return val


    def getFileManagerImagesCase(self):
        retv = self.getFileManager(DefFileManagerNameImagesCase)
        return retv
    #
    def getFileManagerImagesShared(self):
        retv = self.getFileManager(DefFileManagerNameImagesShared)
        return retv
    #
    def getFileManagerPdfsCase(self):
        retv = self.getFileManager(DefFileManagerNamePdfsCase)
        return retv
    #
    def getFileManagerPdfsShared(self):
        retv = self.getFileManager(DefFileManagerNamePdfsShared)
        return retv
    #
    def getFileManagerFontsShared(self):
        retv = self.getFileManager(DefFileManagerNameFontsShared)
        return retv
    #
    def getFileManager(self, fileManagerTypeStr):
        retv = self.getInterp().getFileManager(fileManagerTypeStr)
        return retv



    def getGameModel(self):
        task = self.getTask()
        if (task is None):
            return None
        taskOptions = task.getTaskOptions()
        gamePk = jrfuncs.getDictValueOrDefault(taskOptions, "gamePk", None)
        # instantiate it from django
        # ATTN: this is awkward, since normally casebook has no connection to django data
        from games.models import Game
        gameModel = Game.objects.get(pk=gamePk)
        return gameModel






    def findEntryByIdPath(self, id, astloc):
        astRoot = self.getInterp().getAstRoot()
        return astRoot.findEntryByIdPath(id, astloc)

    def getDayManager(self):
        return self.getInterp().getDayManager()
    #
    def getMindManager(self):
        return self.getInterp().getMindManager()

    def addNote(self, note):
        self.getInterp().addNote(note)
    def getNotes(self):
        return self.getInterp().getNotes()










    def getFlatEntryList(self):
        retList = []

        interp = self.getInterp()
        if (interp is None):
            return None
        astRoot = interp.getAstRoot()
        astRoot.entries.addFlatEntries(retList)
        return retList


    # game info shortcuts
    def calcCasebookGameName(self):
        return self.getEnvValueUnwrapped(None, "info.name", None)
    #
    def calcSafeGameVersionStr(self):
        versionstr = self.getEnvValueUnwrapped(None, "info.version", "")
        if (versionstr==""):
            return versionstr
        versionStrSafe = "v"+jrfuncs.safeCharsForFilename(versionstr)
        return versionStrSafe


    def findTagOrConcept(self, tagId, flagExceptionIfNotFound):
        tagManager = self.getTagManager()
        tag = tagManager.findTagById(tagId)
        if (tag is not None):
            return tag
        tagManager = self.getConceptManager()
        tag = tagManager.findTagById(tagId)
        if (tag is not None):
            return tag 
        # not found
        if (flagExceptionIfNotFound):
            raise makeJriException("Tag not found '{}'.".format(tagId), None)
        return None


    def findDidYouMeanFunction(self, identifierName):
        # return a string with a function name that they might have meant, with case ignored, etc. to suggest on error
        # return NONE if none found

        # split identifier into base and parts
        [baseVarName, propertyParts] = self.splitIndentifierParts(identifierName)
        baseVarNameLc = baseVarName.lower()

        # try case insensitive
        env = self
        while (env is not None):
            for k,v in env.envDict.items():
                klc = k.lower()
                if (klc == baseVarNameLc):
                    return "'{}' (identifiers are case sensitive)".format(k)
            env = env.parentEnv
  
        # try similar
        env = self
        bestSimilarity = 0
        while (env is not None):
            for k,v in env.envDict.items():
                klc = k.lower()
                matcher = difflib.SequenceMatcher(None, klc, baseVarNameLc)
                # Get the ratio of similarity
                similarity = matcher.ratio()
                if (similarity > bestSimilarity):
                    bestSimilarity = similarity
                    bestIdentifier = v
            env = env.parentEnv
        
        if (bestSimilarity>0):
            return "{} (nearest match; {})".format(bestIdentifier.name, bestIdentifier.description)

        return None




#---------------------------------------------------------------------------
# image file helper

    def locateManagerFileWithUseNote(self, managerIdList, path, noteMessage, noteTypeStr, leadp, env, astloc, allowMissingFileJustWarn):
        # find an image, return its path
        # add a note about its use
        # possibly support a warning without adding it

        warningText = None
        flagMarkUsage = True

        # walk file manager helpers, take first find (usually case then fallback to shared)
        fileFullPath = None
        manager = None
        for managerId in managerIdList:
            manager = self.getFileManager(managerId)
            fileFullPath = manager.findFullPath(path, flagMarkUsage)
            if (fileFullPath is not None):
                break

        if (fileFullPath is None):
            if (allowMissingFileJustWarn):
                msg = "CASEBOOK WARNING: FILE MISSING for {} at '{}' in searched directories ({}), OPTIONS CONFIGURED TO SHOW WARNING: ".format(noteMessage, path, managerIdList)
                warningText = msg
            else:
                raise makeJriException("File not found for {} at '{}' in searched directories ({}).".format(noteMessage, path, managerIdList), astloc)

        # for debugging, whether it is local or shared
        locationClass = manager.getLocationClass()
        notePath = locationClass + "/" + path

        # add note for debug report
        if (noteTypeStr is not None):
            msg = noteMessage + ': "{}"'.format(notePath)
            msgLatex = noteMessage + ': "\\path{' + notePath + '}"'
            extras = {"filePath": fileFullPath}
            note = JrINote(noteTypeStr, leadp, msg, msgLatex, extras)
            env.addNote(note)

        return [fileFullPath, warningText]


    def calcManagerIdListImage(self):
        return [DefFileManagerNameImagesCase, DefFileManagerNameImagesShared]

    def calcManagerIdListImageOrPdf(self):
        return [DefFileManagerNameImagesCase, DefFileManagerNameImagesShared, DefFileManagerNamePdfsCase, DefFileManagerNamePdfsShared]

    def calcManagerIdListPdf(self):
        return [DefFileManagerNamePdfsCase, DefFileManagerNamePdfsShared]

    def calcManagerIdListFont(self):
        return [DefFileManagerNameFontsShared]

    def calcManagerIdListSource(self):
        return [DefFileManagerNameSourceCase, DefFileManagerNameSourceShared]
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
    def getVariablesWithValue(self, val):
        # walk all visible variables and return a list of them that have the val
        varList = {}
        varListSaw = []

        # search all jumping up hierarchy, but only checking deepest var per name
        env = self
        while (env is not None):
            for k,v in env.envDict.items():
                if (k not in varListSaw):
                    valUnwrapped = v.getUnWrappedValue(None, None)
                    if (valUnwrapped == val):
                        varList[k]=v
                    varListSaw.append(k)
            env = env.parentEnv
        
        return varList
#---------------------------------------------------------------------------









class JrEnvVar:
    # holds a variable/constant that can be in the environment, and enforces constantness
    # note like most of Casebook runtime, this is a heavy weight object that keeps track of the source location where it was set from and its on parent env
    # in this way, a variable knows "where" in the source code its last value was asigned, etc.
    # so memory use is much higher than strictly needed, in order to support robust error reporting; this is ok for Casebook language tradeoff
    #
    # ON THE OTHER HAND: it seems like a lot of duplicity here, in that an EnvVar wraps as AtstVal which ALSO has env, sloc info; some of this seems very duplicative
    #
    def __init__(self, sloc, name, description, initialValue, isConstant):
        self.sloc = sloc
        self.name = name
        self.description = description
        self.value = None
        self.isConstant = False
        #
        self.setValue(sloc, None, initialValue, False)
        self.isConstant = isConstant



    def getStoredValue(self, sloc, partList):
        # if partList is empty, then we want our value, otherwise we want oject property
        if (partList is None):
            return self.value
        else:
            # we require a wrapped python OBJECT for dotted path resolution
            # ATTN: should we use passed sloc or getSloc of ourselves?
            val = self.value.getProperty(self.getSloc(), self.getName(), partList)
            return val

    def setValue(self, sloc, partList, val, flagCheckConst):
        # if partList is empty, then we want to set our value, otherwise we want oject property
        if (flagCheckConst and self.isConstant):
            msg = "Runtime error; variable {} is defined as constant with current value({}); cannot be set to new value ({})".format(self.name, self.getStoredValue(sloc, partList), val)
            raise self.makeEnvVarException(msg, sloc)
        #
        wrappedVal = wrapValIfNotAlreadyWrapped(None, None, val)

        # if partList is empty, then we want to set our value, otherwise we want oject property
        if (partList is None):
            self.value = wrappedVal
        else:
            # we require a wrapped python OBJECT for dotted path resolution
            return self.value.setProperty(sloc, self.getName(), partList, wrappedVal)








    def getWrappedValue(self, sloc, partList):
        val = self.getStoredValue(sloc, partList)
        return wrapValIfNotAlreadyWrapped(sloc, None, val)

    def getUnWrappedValue(self, sloc, partList):
        val = self.getStoredValue(sloc, partList)
        return unwrapIfWrappedVal(val)


    def getIsConstant(self):
        return self.isConstant

    def getSloc(self):
        return self.sloc
    def getName(self):
        return self.name

    def getIsFunction(self):
        from .jrastvals import AstValFunction
        if (isinstance(self.value, AstValFunction)):
            return True
        return False

    def makeEnvVarException(self, msg, sloc):
        # ATTN: TODO can we add source location info?
        return makeJriException(msg, [sloc, self.getSloc()])












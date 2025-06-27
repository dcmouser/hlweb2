# jrast
from .jrastfuncs import wrapValIfNotAlreadyWrapped, unwrapIfWrappedVal
from .jriexception import *
from .cbtask import DefRmodeRun, DefRmodeRender
from .jrastvals import AstValString

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint

# python modules
import difflib


# define kludge
DefArgDefaultValRequired = "__REQUIRED__"



class CbFunc:
    def __init__(self, name, description, paramList, returnType, targetsAccepted, customData, funcPointer, astloc=None):
        self.name = name
        self.description = description
        self.funcPointer = funcPointer
        self.paramList = paramList
        self.returnType = returnType
        self.targetsAccepted = targetsAccepted
        self.customData = customData
        # build param dict
        self.paramDict = self.buildParamDict(self.paramList, astloc)
    
    def getName(self):
        return self.name
    def getDescription(self):
        return self.description
    def getAllowedTargets(self):
        allowedTargets = self.targetsAccepted
        allowedTargets = unwrapIfWrappedVal(allowedTargets)
        return allowedTargets

    def buildParamDict(self, paramList, astloc):
        paramDict = {}
        for param in paramList:
            paramName = param.getName()
            if (paramName in paramDict):
                raise self.makeFunctionException("Bad function declaration; parameter '{}' was specified multiple times.".format(paramName), astloc)
            paramDict[paramName] = param
        return paramDict


    def buildFuncArgs(self, astloc, argList):
        # build a list of args that we can pass to a CbFunc; these are always named, taken from the positional and named lists and put into the list of cpparams the function declares
        # set defaults and resolve values, etc.

        positionalArgs = argList.getPositionArgs()
        namedArgs = argList.getNamedArgs()
        #
        parameterCount = len(self.paramList)
        args = {}

        # start by assigning positional args
        positionalArgNames = []
        for index,arg in enumerate(positionalArgs):
            if (index>=parameterCount):
                raise self.makeFunctionException("Too many parameters passed", astloc)
            param = self.paramList[index]
            paramName = param.getName()
            positionalArgNames.append(paramName)
            # assign it
            args[paramName] = arg

        
        # now named args, throwing error on duplicate
        for argName, arg in namedArgs.items():
            if (argName not in self.paramDict):
                 msg = "Unknown argument ({}) passed by name".format(argName)
                 # try to find case-insensitive intended arg name
                 guessedArgName = self.findDidYouMeanArg(argName)
                 if (guessedArgName is not None):
                     msg += " (did you mean '{}'?)".format(guessedArgName)
                 raise self.makeFunctionException(msg, astloc)
            if (argName in args):
                if (argName in positionalArgNames):
                    raise self.makeFunctionException("Argument ({}) passed by name was already passed previously positionally".format(argName), astloc)
                else:
                    raise self.makeFunctionException("Argument ({}) passed by name was already passed previously by name".format(argName), astloc)
            param = self.paramDict[argName]
            # assign it
            args[argName] = arg

        # lastly, complain about any REQUIRED args that are missing AND set any defaults
        defaultArgList = []
        for param in self.paramList:
            paramName = param.getName()
            if (paramName not in args):
                # param is missing; either it's require or it has a default
                if (param.getIsRequired()):
                    raise self.makeFunctionException("Missing required parameter ({})".format(paramName), astloc)
                # not required, set default
                defaultVal = param.getDefaultVal()
                # wrap default val if it needs to be wrapped
                # if we call the former we get always a COPY; the later will reuse it if its wrapped
                defaultValWrapped = wrapValIfNotAlreadyWrapped(astloc, None, defaultVal)
                args[paramName] = defaultValWrapped
                defaultArgList.append(paramName)

        return [args, defaultArgList]
    

    def findDidYouMeanArg(self, argName):
        # try to guess what they intended
        argNameLower = argName.lower()
        bestSimilarity = 0
        bestIdentifier = None
        for paramName, param in self.paramDict.items():
            paramNameLower = paramName.lower()
            if (argNameLower == paramNameLower):
                return paramName
            matcher = difflib.SequenceMatcher(None, paramNameLower, argNameLower)
            # Get the ratio of similarity
            similarity = matcher.ratio()
            if (similarity > bestSimilarity):
                bestSimilarity = similarity
                bestIdentifier = paramName

        if (bestIdentifier is not None):
            return paramName

        return None


    def resolveArgs(self, rmode, env, astloc, args, targets, entryp, leadp):
        # this is done at runtime
        resolvedArgs = {}
        # do in order of function params for nicer debug listing of args
        for paramName, param in self.paramDict.items():
            paramName = param.getName()
            arg = args[paramName]
            #
            flagResolveIdentifiers = param.getFlagResolveIdentifiers()
            # ATTN: TODO maybe force flagResolveIdentifiers to False when rmode == "render"?
            #
            resolvedArg = arg.resolve(env, flagResolveIdentifiers, entryp, leadp)
            # check if the arg is valid
            param.verifyValidValue(self, astloc, resolvedArg)
            resolvedArgs[paramName] = resolvedArg
        #
        return resolvedArgs


    def invoke(self, rmode, env, entryp, leadp, astloc, argList, targets):
        # invoke the function on the argDict
        # build named arg dict
        try:
            [args, defaultArgList] = self.buildFuncArgs(astloc, argList)
            # resolve args
            resolvedArgs = self.resolveArgs(rmode, env, astloc, args, targets, entryp, leadp)

            # add hidden internal args
            resolvedArgs["_functionName"] = self.getName()

            # verify correct number of targets was passed
            self.verifyTargetArity(env, astloc, targets)

            # invoke through function pointer
            return self.funcPointer(rmode, env, entryp, leadp, astloc, resolvedArgs, self.customData, self.name, targets)

        except Exception as e:
            # error running func
            # set msgExtra to tell the person how to use the function
            msgExtra = "NOTE: Here is some help for using function ${}(...):\n".format(self.getName()) + self.getErrorHelpInfoPlaintextCompact()
            # add location if an error is thrown without one
            e = makeModifyJriExceptionAddLocIfNeeded(e, astloc, msgExtra)
            interp = env.getInterp()
            if (interp.getFlagContinueOnException()):
                interp.displayException(e, True)
            else:
                raise e


    def makeFunctionException(self, msg, sloc):
        msg = msg + " for function {}(..), ".format(self.getName())
        msgExtra = "NOTE: Here is some help for using function ${}(...):\n".format(self.getName()) + self.getErrorHelpInfoPlaintextCompact()
        return makeJriException(msg, sloc, msgExtra)


    def verifyTargetArity(self, env, sloc, targets):
        targetCount = len(targets)
        allowedTargets = self.targetsAccepted
        allowedTargets = unwrapIfWrappedVal(allowedTargets)
        #
        if (allowedTargets == False) or (allowedTargets is None):
            if (targetCount!=0):
                raise self.makeFunctionException("Runtime error: Function does not operate on target brace blocks, but one or more ({}) provided".format(targetCount), sloc)
        elif (allowedTargets=="any"):
            return True
        elif (allowedTargets=="optional"):
            if (targetCount!=0) and (targetCount!=1):
                raise self.makeFunctionException("Runtime error: Too many target brace blocks ({}); should be 0 or 1".format(targetCount), sloc)
        elif (type(allowedTargets) is list):
            if (targetCount not in allowedTargets):
                raise self.makeFunctionException("Runtime error: Function was passed {} target brace blocks, but function requires from {}".format(targetCount, allowedTargets), sloc)
        else:
            try:
                allowedTargetsInt = int(allowedTargets)
            except Exception as e:
                raise self.makeFunctionException("Runtime error: Function declaration specification of targetsAccepted was not understood; should be list of ints or int ({})".format(allowedTargets), sloc)
            if (allowedTargetsInt!=targetCount):
                # wrong number of targets
                if (targetCount==0):
                    raise self.makeFunctionException("Runtime error: Function declaration specification states this function requires {} target brace group(s) to operate on, but none were provided".format(allowedTargetsInt), sloc)
                else:
                    raise self.makeFunctionException("Runtime error: Function declaration specification states this function requires {} target brace group(s) to operate on, but {} were provided".format(allowedTargetsInt, targetCount), sloc)
        # good
        return True








    def calcAnnotatedArgListStringForDebug(self, env, astloc, argList, targets, entryp, leadp):
        # helper function for debugging

        # catch any error and return it for display
        try:
            # convert positional args into named args, set defaults
            [args, defaultArgList] = self.buildFuncArgs(astloc, argList)
            rmode = DefRmodeRun
            resolvedArgs = self.resolveArgs(rmode, env, astloc, args, targets, entryp, leadp)
        except Exception as e:
            return repr(e)

        # ATTN: unfinished
        parts = []
        for paramName, param in self.paramDict.items():
            argVal = resolvedArgs[paramName]
            assignedValStr = argVal.asDebugStr()
            partVal = "{}={}".format(paramName, assignedValStr)
            if (paramName in defaultArgList):
                partVal += " (default)"
            parts.append(partVal)
        #
        argString = ", ".join(parts)
        return argString




    def getErrorHelpInfoPlaintextCompact(self):
        usageText = self.getUsageInfoSimple()
        usageText += "\nWHERE params are:\n" + self.getParameterInfoPlaintextCompact()
        return usageText

    def getUsageInfoSimple(self):
            paramTexts = []
            for param in self.paramList:
                name = param.getName()
                description = param.getDescription()
                defaultVal = param.getDefaultVal()
                isRequired = param.getIsRequired()
                paramStr = name
                if (defaultVal is None) and (not isRequired):
                    paramStr += "= NONE"
                elif (defaultVal is not None):
                    defaultVal = str(jrfuncs.quoteStringsForDisplay(defaultVal))
                    if (defaultVal=="True"):
                        defaultVal = "true"
                    elif (defaultVal=="False"):
                        defaultVal = "false"
                    paramStr += "=" + defaultVal
                paramTexts.append(paramStr)
            #
            paramTextAll = ", ".join(paramTexts)
            #
            html = self.getName() + "(" + paramTextAll + ")"
            #
            allowedTargets = self.getAllowedTargets()
            if (allowedTargets):
                html += ": {targetblock}"
            return html
    

    def getParameterInfoHtml(self):
            paramCount = len(self.paramList)
            if (paramCount==0):
                return ""
            #
            paramTexts = []
            for param in self.paramList:
                name = param.getName()
                description = param.getDescription()
                defaultVal = param.getDefaultVal()
                isRequired = param.getIsRequired()
                paramCheck = param.getParamCheck()
                #
                if (description is None) or (description==""):
                    description = "n/a"
                paramStr = name + ": " + jrfuncs.quoteStringsForDisplay(description)
                #
                if (paramCheck is not None):
                    paramStr += "; type=" + param.calcNiceParamCheckString()
                if (isRequired):
                    paramStr += "; required"
                if (defaultVal is not None):
                    paramStr += "; default="+jrfuncs.quoteStringsForDisplay(str(defaultVal))
                #
                paramStrLi = "<li>" + paramStr + "</li>\n"
                paramTexts.append(paramStrLi)
            #
            allowedTargets = self.getAllowedTargets()
            if (allowedTargets):
                paramStrLi = "<li>" + ":{targetblock} - a braced group of text to operate on" + "</li>\n"
                paramTexts.append(paramStrLi)
            #
            paramTextAll = "\n".join(paramTexts)
            html = "<ul>\n" + paramTextAll + "\n</ul>\n"
            return html



    def getParameterInfoPlaintextCompact(self):
            paramCount = len(self.paramList)
            if (paramCount==0):
                return "none"
            #
            paramTexts = []
            for param in self.paramList:
                name = param.getName()
                description = param.getDescription()
                defaultVal = param.getDefaultVal()
                isRequired = param.getIsRequired()
                paramCheck = param.getParamCheck()
                #
                if (description is None) or (description==""):
                    description = "n/a"
                paramStr = name + ": " + jrfuncs.quoteStringsForDisplay(description)
                #
                if (paramCheck is not None):
                    paramStr += "; type=" + param.calcNiceParamCheckString()
                if (isRequired):
                    paramStr += "; required"
                if (defaultVal is not None):
                    paramStr += "; default="+jrfuncs.quoteStringsForDisplay(str(defaultVal))
                #
                paramStrLi = paramStr
                paramTexts.append(" * " + paramStrLi)
            #
            allowedTargets = self.getAllowedTargets()
            if (allowedTargets):
                paramStrLi = " * :{targetblock} - a braced group of text to operate on"
                paramTexts.append(paramStrLi)
            #
            paramTextAll = "\n".join(paramTexts)
            return paramTextAll

















































class CbParam:
    def __init__(self, name, description, defaultVal, flagAllowNull, paramCheck, flagResolveIdentifiers):
        # the flagResolveIdentifiers parameter would normall be set to True, meaning that the expression passed in will be fully resolved and any referenced variables looked up
        # but you would set it to False if you wanted any IDENTIFIER to be left as the NAME of the identifier rather than for variables to be looked up in the environment
        # e.g. for the $set(varname, value) function, you see to set the first parameter to flagResolveIdentifiers=False, so that it passes in the NAME of the identifier rather than resolves it
        self.name = name
        self.description = description
        self.allowNull = flagAllowNull
        self.isRequired = (defaultVal is None) and (not flagAllowNull)
        self.flagResolveIdentifiers = flagResolveIdentifiers
        self.paramCheck = paramCheck
        self.defaultVal = defaultVal

    def getName(self):
        return self.name
    def getFlagResolveIdentifiers(self):
        return self.flagResolveIdentifiers
    def getIsRequired(self):
        return self.isRequired
    def getAllowNull(self):
        return self.allowNull
    def getDefaultVal(self):
        return self.defaultVal
    def getParamCheck(self):
        return self.paramCheck
    def getDescription(self):
        return self.description


    def calcNiceParamCheckString(self):
        # shorter class name if its a class
        if (isinstance(self.paramCheck, type)):
            text = self.paramCheck.__name__
        else:
            text = str(self.paramCheck)
        return text


    def verifyValidValue(self, cbfunc, astloc, value):
        isValid = self.verifyValidValueAgainstType(astloc, value, self.paramCheck)
        if (not isValid):
            functionName = cbfunc.getName()
            valueNiceString = value.asNiceString()
            paramCheckStr = self.calcNiceParamCheckString()
            msg = "Runtime error: In function call {}(..) the parameter '{}' was set to an illegal value '{}'; should be: {}".format(functionName, self.name, valueNiceString, paramCheckStr)
            msg += ": " + cbfunc.getErrorHelpInfoPlaintextCompact()
            raise makeJriException(msg, astloc)

    def verifyValidValueAgainstType(self, astloc, value, paramCheck):
        if (paramCheck is None):
            # no type, so it's fine
            return True
        
        if (isinstance(paramCheck, type)):
            # paramCheck is a CLASS
            # derived from AstVal? if so check if parameter is one of these
            valueType = value.getType()
            if (issubclass(valueType, paramCheck)):
                # yet its the expected type
                return True
            
        # raise exception if illegal value
        if (isinstance(paramCheck, list)):
            # its a list, so value just has to match ONE of these
            for subParamCheck in paramCheck:
                isValid = self.verifyValidValueAgainstType(astloc, value, subParamCheck)
                if (isValid):
                    return True
            # didn't match any
            return False

        # is paramType a primitive constant then the value must be equal to it to pass
        paramCheckType = type(paramCheck)
        wrappedValue = value.getWrapped()
        if (wrappedValue == paramCheck):
            return True

        # EVERYTHING is allowed to be null?
        if (wrappedValue is None) and (self.getAllowNull()):
            return True

        return False






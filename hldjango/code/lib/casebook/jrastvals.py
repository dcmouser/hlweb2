# jrast
from .jrastfuncs import calcNiceShortTypeStr
from .jrastfuncs import convertToSourceLocationObject, astPrintDebugLine
from .jrastfuncs import getObjectDictHierarchicalProperty, setObjectDictHierarchicalProperty
from .jriexception import *


# python
import re






# JrAst is base class for our Abstract Syntax Tree nodes
class JrAst:
    def __init__(self, sloc, parentp):
        # each node stores a reference to an object that records source location (taken originally from the lark parser), which is used (only) for error reporting
        # it can be passed to use as a lark node or another sloc object, and stores it as sloc lightweight object
        # often sloc and parentp will be identical but the idea is that sloc is an object used to identify the source code location (it may be JrSourceLocation obj, pnode, or JrAst)
        # wheras parentp is ALWAYS a hierarchy parent JrAst in the AST tree
        self.sloc = convertToSourceLocationObject(sloc)
        self.parentp = parentp

    def printDebug(self, env, depth, extraInfo = None):
        # nice hierarchical tabbed pretty print
        if (extraInfo is not None):
            extraInfoStr = " (" + extraInfo + ")"
        else:
            extraInfoStr = ""
        astPrintDebugLine(depth, "{}{} @ {}".format(self.asDebugStr(), extraInfoStr, self.sloc.debugString()))

    def asDebugStr(self):
        # default is just the type
        return self.getTypeStr()

    def getParentp(self):
        return self.parentp

    def getType(self):
        return type(self)

    def getTypeStr(self):
        # just last bit of type
        return self.__class__.__name__

    def getRootInterp(self):
        # climb hierarchy up until we find it
        if (hasattr(self, "interp")):
            return self.interp
        elif (self.parentp):
            return self.parentp.getRootInterp()
        else:
            return ({})

    def getRootRawHighlightedSourceLineDict(self, startPos, endPos):
        # climb hierarchy up until we find it
        if (hasattr(self, "interp")):
            interp = self.interp
            deepSource = interp.getDeepSource()
            locDict = deepSource.extractHighlightedSourceLineDictAtPos(startPos, endPos)
            return locDict
        elif (self.parentp):
            return self.parentp.getRootRawHighlightedSourceLineDict(startPos, endPos)
        else:
            return {}

    def getRootDeepSourceHighlightedLineDebugMessage(self, startPos, endPos):
        # climb hierarchy up until we find it
        if (hasattr(self, "interp")):
            interp = self.interp
            deepSource = interp.getDeepSource()
            msg = deepSource.extractHighlightedLineDebugMessageAtPos(startPos, endPos)
            return msg
        elif (self.parentp):
            return self.parentp.getRootDeepSourceHighlightedLineDebugMessage(startPos, endPos)
        else:
            return None




    def convertGenericPnodeContents(self, pnode):
        # helper function for just storing pnode contents in an ast node
        # this is only a stopgap, eventually the AST should not hold any info from pnodes
        return pnode


    # helpers for getting source loc
    def getSourceLoc(self):
        return self.sloc
    def getSourceStartPos(self):
        return self.sloc.getSourceStartPos()
    def getSourceEndPos(self):
        return self.sloc.getSourceEndPos()
    def getSourceLine(self):
        return self.sloc.getSourceLine()
    def getSourceColumn(self):
        return self.sloc.getSourceColumn()
    def getSourceEndLine(self):
        return self.sloc.getSourceEndLine()
    def getSourceEndColumn(self):
        return self.sloc.getSourceEndColumn()


    def makeAstException(self, msg, sloc = None):
        if (sloc is None):
            sloc = self
        return makeJriException(msg, sloc)   

    def calcHierarchicalMStyle(self):
        return None















# Base AstVal class; all other primitive types derive from this
# this is basically a wrapper around a string, number, identifier, etc.
class AstVal(JrAst):
    def __init__(self, sloc, parentp, val):
        super().__init__(sloc, parentp)
        self.setWrapped(val)



    def setWrapped(self, val):
        self.value = val
    def getWrapped(self):
        return self.value
    def getWrappedOrDefault(self, defaultVal):
        if (self.value is None):
            return defaultVal
        return self.value
    def getWrappedForDisplay(self):
        return str(self.getWrapped())

    def getWrappedExpect(self, expectedType):
        self.verifyType(expectedType)
        return self.getWrapped()

    def getUnWrappedExpect(self, expectedType):
        self.verifyType(expectedType)
        return self.value


    def copyFrom(self, val):
        self.value = val.value
        self.sloc.copyFrom(val.sloc)

    def verifyType(self, expectedType):
        if (isinstance(expectedType, list)):
            if (not self.getType() in expectedType):
                raise self.makeAvalExceptionWrongValueType(expectedType)
            return
        if (self.getType() is not expectedType):
            raise self.makeAvalExceptionWrongValueType(expectedType)
        return

    def asDebugStr(self):
        return self.getWrappedForDisplay()

    def asNiceString(self, flagShowType = True):
        value = str(self.getWrapped())
        # return string version
        if (flagShowType):
            typeStr = self.getTypeStr()
            return "{} (type={})".format(value, typeStr)
        return str(value)

    def resolve(self, env, flagResolveIdentifiers, entryp, leadp):
        # most value return themselves
        return self

    def getProperty(self, sloc, identifier, partList):
        # get hierarchical element
        partListStr = ".".join(partList)
        msg = "AstVal Identifier '{}' does not support dotted properties ({})".format(identifier, partListStr)
        raise self.makeAvalException(msg, sloc)

    def setProperty(self, sloc, identifier, partList, val):
        # set hierarchical element
        partListStr = ".".join(partList)
        msg = "AstVal Identifier '{}' does not support dotted properties ({})".format(identifier, partListStr)
        raise self.makeAvalException(msg, sloc)



    # exceptions

    def makeAvalException(self, msg, sloc = None):
        if (sloc is None):
            sloc = self
        return makeJriException(msg, sloc)   
    def makeAvalExceptionWrongValueType(self, expectedType):
        if (isinstance(expectedType, list)):
            return self.makeAvalException("AstValue of type {} was expected to be from {}".format(calcNiceShortTypeStr(self), str(expectedType)))
        else:
            return self.makeAvalException("AstValue of type {} was expected to be of {}".format(calcNiceShortTypeStr(self), calcNiceShortTypeStr(expectedType)))
    def makeAvalExceptionWrongWrappedValueType(self, env, expectedType, foundValueType):
        if (isinstance(expectedType, list)):
            return self.makeAvalException("Wrapped AstValue of type {} was expected to be from {}".format(calcNiceShortTypeStr(self), str(expectedType)))
        else:
            return self.makeAvalException("Wrapped AstValue of type {} was expected to be of {}".format(calcNiceShortTypeStr(self), calcNiceShortTypeStr(expectedType)))
























class AstValString(AstVal):
    def __init__(self, sloc, parentp, val):
        super().__init__(sloc, parentp, val)
    def getWrappedForDisplay(self):
        return '"{}"'.format(self.value)




class AstValNumber(AstVal):
    def __init__(self, sloc, parentp, val):
        # cast val from string if needed
        if (isinstance(val,str)):
            val = jrfuncs.intOrFloatFromStr(val)
        super().__init__(sloc, parentp, val)

class AstValBool(AstVal):
    def __init__(self, sloc, parentp, val):
        if (isinstance(val,str)):
            val = jrfuncs.boolFromStr(val)
        super().__init__(sloc, parentp, val)

class AstValIdentifier(AstVal):
    def __init__(self, sloc, parentp, val):
        super().__init__(sloc, parentp, val)

    def resolve(self, env, flagResolveIdentifiers, entryp, leadp):
        # most value return themselves but identifiers can resolve
        if (flagResolveIdentifiers):
            identifierName = self.value
            resolvedIdentifier = env.getEnvValue(self, identifierName, None)
            if (resolvedIdentifier is None):
                msg = "Unknown identifier: {}; make sure you did not intend to pass this as a quoted value".format(identifierName)
                raise self.makeAvalException(msg)
            return resolvedIdentifier
        # otherwise just return ourselves like base class
        return self





class AstValFunction(AstVal):
    def __init__(self, sloc, parentp, val):
        super().__init__(sloc, parentp, val)

    def getDescription(self):
        return self.value.getDescription()


class AstValNull(AstVal):
    def __init__(self, sloc, parentp):
        super().__init__(sloc, parentp, None)

    def asDebugStr(self):
        return "NULL"





class AstValLarkNode(AstVal):
    def __init__(self, sloc, parentp, val):
        super().__init__(sloc, parentp, val)







class AstValObject(AstVal):
    def __init__(self, sloc, parentp, val, flagReadOnly, flagCreateKeyOnSet):
        super().__init__(sloc, parentp, val)
        self.readOnly = flagReadOnly
        self.createKeyOnSet = flagCreateKeyOnSet

    def getProperty(self, sloc, identifier, partList):
        # return hierarchical element of OBJECT
        return getObjectDictHierarchicalProperty(sloc, identifier, self.value, partList)

    def setProperty(self, sloc, identifier, partList, val):
        # set hierarchical element
        if (self.readOnly):
            msg = "Runtime error; identifier object '{}' is set to read-only".format(identifier)
            raise self.makeAvalException(msg, sloc)
        return setObjectDictHierarchicalProperty(sloc, identifier, self.value, partList, val, self.createKeyOnSet)






class AstValList(AstVal):
    def __init__(self, sloc, parentp, val):
        super().__init__(sloc, parentp, val)

    def asDebugStr(self):
        # recurse into list to show nicer
        parts = []
        for val in self.value:
            parts.append(val.asDebugStr())
        partString = ", ".join(parts)
        listString = "[{}]".format(partString)
        return listString


class AstValDict(AstVal):
    def __init__(self, sloc, parentp, val, flagReadOnly, flagCreateKeyOnSet):
        super().__init__(sloc, parentp, val)
        self.readOnly = flagReadOnly
        self.createKeyOnSet = flagCreateKeyOnSet


    def asDebugStr(self):
        # recurse into dict to show nicer
        niceDict = {}
        parts = []
        for key,val in self.value.items():
            valstr = val.asDebugStr()
            niceDict[key]=valstr
            parts.append("{}={}".format(key,valstr))
        partString = ", ".join(parts)
        dictString = "{{ {} }}".format(partString)
        return dictString
        #return str(niceDict)


    def getProperty(self, sloc, identifier, partList):
        # return hierarchical element of OBJECT
        return getObjectDictHierarchicalProperty(sloc, identifier, self.value, partList)

    def setProperty(self, sloc, identifier, partList, val):
        # set hierarchical element
        if (self.readOnly):
            msg = "Runtime error; identifier dictionary '{}' is set to read-only".format(identifier)
            raise self.makeAvalException(msg, sloc)
        return setObjectDictHierarchicalProperty(sloc, identifier, self.value, partList, val, self.createKeyOnSet)




















def makeAstValNull():
    return AstValNull(None, None)

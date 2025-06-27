# lark
import lark

# pylatex for escaping
import pylatex

# ast
from .cblarkdefs import *
#
from .jriexception import *
from .casebookDefines import *

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
















# NON-CLASS HELPERS


def wrapDictForAstVal(sloc, val, flagReadOnly=False, flagCreateKeyOnSet=False):
    from .jrastvals import AstValDict
    return AstValDict(sloc, None, val, flagReadOnly, flagCreateKeyOnSet)

def wrapObjectForAstVal(sloc, val, flagReadOnly=False, flagCreateKeyOnSet=False):
    from .jrastvals import AstValObject
    return AstValObject(sloc, None, val, flagReadOnly, flagCreateKeyOnSet)


def wrapValIfNotAlreadyWrapped(sloc, parentp, value):
    # for creating wrapped value classes
    from .jrastvals import AstVal

    if (isinstance(value, AstVal)):
        # its already a wrapped value, so just return it
        return value
    return wrapValSmart(sloc, parentp, value)


def wrapValSmart(sloc, parentp, value):
    # for creating wrapped value classes
    from .jrastvals import AstVal, AstValNull, AstValString, AstValBool, AstValNumber, AstValList, AstValDict, AstValLarkNode, AstValObject

    valType = type(value)
    if (value is None):
        wrappedVal = AstValNull(sloc, parentp)
    elif (isinstance(value, AstVal)):
        wrappedVal = valType(sloc, parentp, None)
        wrappedVal.copyFrom(value)
    elif (valType is str):
        wrappedVal = AstValString(sloc, parentp, value)
    elif (valType is bool):
        wrappedVal = AstValBool(sloc, parentp, value)
    elif (valType is int) or (valType is float):
        wrappedVal = AstValNumber(sloc, parentp, value)
    elif (valType is list):
        wrappedVal = AstValList(sloc, parentp, value)
    elif (isinstance(value, lark.Token)):
        wrappedVal = AstValLarkNode(sloc, parentp, value)
    elif (valType is dict):
        flagReadOnly = False
        flagCreateKeyOnSet = True
        wrappedVal = AstValDict(sloc, parentp, value, flagReadOnly, flagCreateKeyOnSet)
    else:
        # generic object
        flagReadOnly = False
        flagCreateKeyOnSet = True
        wrappedVal = AstValObject(sloc, parentp, value, flagReadOnly, flagCreateKeyOnSet)
    #
    return wrappedVal



def unwrapIfWrappedVal(value):
    # for unwrapping wrapped values when we arent sure if they will be wrapped or primitive
    from .jrastvals import AstVal
    if (isinstance(value, AstVal)):
        return value.getWrapped()
    return value



def astPrintDebugLine(depth, str):
    # nice hierarchical tabbed pretty print
    spaceStr = " " * depth * 2
    jrprint(spaceStr + str)






# helper function to return value of parse tree node with a single child literal token
def getParseTreeChildLiteralToken(pnode, flagTrimWhitespace = True):
    literalChild = pnode.children[0]
    literalValue = literalChild.value
    if (flagTrimWhitespace):
        literalValue = literalValue.strip()
    return literalValue

# helper function to return value of parse tree node that is a string of some sort
def getParseTreeChildString(pnode):
    # we expect one child, which is a STRING type
    pchildStringNode = pnode.children[0]
    return getParseTreeString(pchildStringNode)


# helper function to return value of parse tree node that is a string or a new nonstringtextline (just remainder of line)
def getParseTreeChildStringOrTextLine(pnode):
    # we expect one child, which is a STRING type
    pchildNode = pnode.children[0]
    ruleValue = pchildNode.data.value
    if (ruleValue == JrCbLarkRule_nonstringtextline):
        pchildSubStringNode = pchildNode.children[0]
        val = getParseNodeTokenValue(pchildSubStringNode)
        return val
    else:
        return getParseTreeString(pchildNode)


# helper function to return value of parse tree node that is a string or a new nonstringtextline (just remainder of line)
def getParseTreeEntryLineLabel(pnode):
    # we expect one child, which is a STRING type
    pchildNode = pnode.children[0]
    val = getParseNodeTokenValue(pchildNode)
    return val




# helper function to return value of parse tree node with a single child literal token
def getParseTreeChildLiteralTokenOrString(pnode, flagTrimWhitespace = True):
    child = pnode.children[0]
    if (hasattr(child,"data")):
        return getParseTreeString(child)
    #
    literalValue = child.value
    flagTrimWhitespace = True
    if (flagTrimWhitespace):
        literalValue = literalValue.strip()
    return literalValue




def getParseTreeString(pnode):
    stringConst = pnode.data.value
    if (stringConst != JrCbLarkRule_string):
        raise makeJriException("Uncaught syntax error; expected string composite token '{}'.".format(JrCbLarkRule_string),  pnode)
    pchildSubStringNode = pnode.children[0]
    stringType = pchildSubStringNode.type
    stringValue = pchildSubStringNode.value
    if (stringType in [JrCbLarkRule_STRING_DOUBLE_QUOTE, JrCbLarkRule_STRING_SINGLE_QUOTE, JrCbLarkRule_UNICODE_STRING]):
        # remove outer double quotes
        literalValue = stringValue[1:len(stringValue)-1]
    elif (stringType == JrCbLarkRule_STRING_TRIPLE_SINGLE_QUOTE):
        # remove outer triple quotes
        literalValue = stringValue[3:len(stringValue)-3]
    else:
        raise makeJriException("Uncaught syntax error; expected string token of type {}.".format([JrCbLarkRule_STRING_DOUBLE_QUOTE, JrCbLarkRule_STRING_SINGLE_QUOTE, JrCbLarkRule_UNICODE_STRING]),  pchildSubStringNode)
    return literalValue

# just return the simple value of the pnode
def getParseNodeTokenValue(pnode):
    return pnode.value

def getParseNodeBool(pnode):
    rule = pnode.data
    if (rule == JrCbLarkRule_boolean_true):
        return True
    elif (rule == JrCbLarkRule_boolean_false):
        return False
    raise makeJriException("Internal error; expected boolean_true or boolean_false but got rule: {}.".format(rule), pnode)




def getParseNodeRuleName(pnode):
    rule = pnode.data
    if (type(rule) is str):
        return rule
    raise makeJriException("Expected string rule but found deeper token; see getParseNodeRuleNameSmart.", pnode)

def getParseNodeRuleDataName(pnode):
    rule = pnode.data
    if (type(rule) is str):
        raise makeJriException("Expected data embedded rule string but found string; see getParseNodeRuleNameSmart.", pnode)
    return rule.value




def getParseNodeRuleNameSmart(pnode):
    rule = pnode.data
    if (type(rule) is str):
        return rule
    return rule.value



def convertToSourceLocationObject(sloc):
    from .jrastutilclasses import JrSourceLocation
    if (sloc is None):
        # no source location available
        return JrSourceLocation()
    if (isinstance(sloc, JrSourceLocation)):
        # already a source location, just return it
        return sloc
    return JrSourceLocation(sloc)








def convertParseBraceGroupOrBlockSeq(pnode, parentp):
    # this is tricky because we send a bunch of different rules here
    # the only thing that doesnt go here is MULTI brace groups (used in function calls); so here we have EITHER a brace group, OR a block sequence (with possible newlines)
    from .jrast import JrAstBraceGroup, JrAstBlockSeq

    rule = getParseNodeRuleNameSmart(pnode)
    if (rule == JrCbLarkRule_brace_group):
        # brace group
        return JrAstBraceGroup(pnode, parentp)
    elif (rule in [JrCbLarkRule_BlockSeq1, JrCbLarkRule_BlockSeq2, JrCbLarkRule_BlockSeq3]):
        # block seq
        return JrAstBlockSeq(pnode, parentp)
    else:
        raise makeAstExceptionPNodeType("if consequence", pnode, [JrCbLarkRule_BlockSeq1, JrCbLarkRule_BlockSeq2, JrCbLarkRule_BlockSeq3, JrCbLarkRule_brace_group])


def convertParseMultiBraceGroupOrBlockSeq(pnode, parentp):
    # multiple brace groups or one block seq
    groups = []
    for childpnode in pnode.children:
        group = convertParseBraceGroupOrBlockSeq(childpnode, parentp)
        groups.append(group)
    return groups



def convertPositionalArgList(pnode, parentp):
    from .jrast import JrAstExpression

    argList = []
    # each child will be an expression
    for childpnode in pnode.children:
        expression = JrAstExpression(childpnode, parentp)
        argList.append(expression)
    return argList

def convertNamedArgList(pnode, parentp):
    from .jrast import JrAstExpression

    argDict = {}
    # each child will be an assignment expression
    for childpnode in pnode.children:
        keyNode = childpnode.children[0]
        expressionNode = childpnode.children[1]
        keyName = getParseNodeTokenValue(keyNode)
        if (keyName in argDict):
            raise makeJriException("Duplicate key in arg list ({}).".format(keyName), keyNode)
        argDict[keyName] = JrAstExpression(expressionNode, parentp)
    return argDict


def convertDictionary(pnode, parentp):
    from .jrast import JrAstExpression

    argDict = {}
    # each child will be an assignment expression
    for childpnode in pnode.children:
        keyNode = childpnode.children[0]
        expressionNode = childpnode.children[1]
        keyRule = getParseNodeRuleNameSmart(keyNode)
        if (keyRule == JrCbLarkRule_Atom_string):
            # string as dictionary left identifier
            keyName = getParseTreeString(keyNode)
            if (keyName in argDict):
                raise makeJriException("Duplicate key in dictionary ({}).".format(keyName), keyNode)
            argDict[keyName] = JrAstExpression(expressionNode, parentp)
        else:
            raise makeJriException("Expected string value for key name in dictionary.", keyNode)
    return argDict



def convertExpression(pnode, parentp):
    # the child is the rule (either an operation or an atom)
    childCount = len(pnode.children)
    if (childCount != 1):
        raise makeJriException("Expression parsing", pnode)
    child = pnode.children[0]
    return convertExpressionOperand(child, parentp)


def convertExpressionOperand(child, parentp):
    from .jrast import JrAstExpressionAtom, JrAstExpressionBinary, JrAstExpressionUnary, JrAstExpressionCollectionList, JrAstExpressionCollectionDict, JrAstFunctionCall

    rule = getParseNodeRuleNameSmart(child)
    if (rule in JrCbLarkRule_Operation_Binary_AllList):
        # binary node
        return JrAstExpressionBinary(rule, child, parentp)
    elif (rule in JrCbLarkRule_Operation_Unary_AllList):
        # binary node
        return JrAstExpressionUnary(rule, child, parentp)
    elif (rule in JrCbLarkRule_Atom_AllList):
        # atom node
        return JrAstExpressionAtom(rule, child, parentp)
    elif (rule == JrCbLarkRule_Collection_list):
        # collection node
        return JrAstExpressionCollectionList(child, parentp)
    elif (rule == JrCbLarkRule_Collection_dict):
        # collection node
        return JrAstExpressionCollectionDict(child, parentp)
    elif (rule == JrCbLarkRule_Block_FunctionCall):
        # function call
        return JrAstFunctionCall(child, parentp)
    elif (rule == JrCbLarkRule_Block_Expression):
        # nested expression recurse
        return convertExpression(child, parentp)
    else:
        raise makeJriException("Expression rule parsing", child)





def verifyPNodeType(pnode, errorHint, pnodeTypeList):
    nodeRule = getParseNodeRuleNameSmart(pnode)
    if (not nodeRule in pnodeTypeList):
        raise makeJriException("Uncaught syntax error; {} expected to be from {} (found '{}').".format(errorHint, pnodeTypeList, nodeRule), pnode)


def makeAstExceptionPNodeType(errorHint, pnode, pnodeTypeList):
    nodeRule = getParseNodeRuleNameSmart(pnode)
    if (not nodeRule in pnodeTypeList):
        return makeJriException("Uncaught syntax error; {} expected to be from {} (found '{}').".format(errorHint, pnodeTypeList, nodeRule), pnode)
    return makeJriException("Internal error; control branch hit with pnode type not from expected list during {} (found '{}').".format(errorHint, nodeRule), pnode)




def calcNiceShortTypeStr(obj):
    # shorter class name if its a class
    if (isinstance(obj, type)):
        text = obj.__name__
    else:
        objType = type(obj)
        text = objType.__name__
    return text
















# helper functions that will set values in dotted properites of OBJECTS or DICTS and report errors

def getObjectDictHierarchicalProperty(sloc, identifier, objdict, partList):
    # return hierarchical path of OBJECT OR DICT hierarchy

    # walk the partlist
    obj = objdict
    errored = False
    for index,p in enumerate(partList):
        partStringPartial = ".".join(partList[0:index+1])
        if isinstance(obj, dict):
            # its a dict, so we look for a key in dict
            if (p in obj):
                obj = obj[p]
            else:
                errored = True
                break
        else:
            # fall back to object
            if (hasattr(obj, p)):
                obj = getattr(obj,p)
            else:
                errored = True
                break
    #
    if (not errored):
        return obj
    # error
    msg = "Runtime error trying to get object dotted attribute; property {} does not exist on object {}".format(partStringPartial, identifier)
    raise makeJriException(msg, sloc)



def setObjectDictHierarchicalProperty(sloc, identifier, objdict, partList, val, flagCreateKeyOnSet):
    # set hierarchical path of OBJECT OR DICT hierarchy

    # walk the partlist
    obj = objdict
    errored = False
    lastIndex = len(partList) - 1
    for index,p in enumerate(partList):
        partStringPartial = ".".join(partList[0:index+1])
        if isinstance(obj, dict):
            # its a dict, so we look for a key in dict
            # ATTN: TODO - we might allow arbitrary dictionary values to be set (like python does) even if they do not exist
            if (flagCreateKeyOnSet) and (index == lastIndex):
                # SET IT AND DONE
                obj[p] = val
            elif (p in obj):
                if (index == lastIndex):
                    # SET IT AND DONE
                    obj[p] = val
                else:
                    # recurse
                    obj = obj[p]
            else:
                errored = True
                break
        else:
            # fall back to object
            if (hasattr(obj, p)):
                if (index == lastIndex):
                    # SET IT AND DONE
                    setattr(obj,p,val)
                else:
                    # recurse
                    obj = getattr(obj,p)
            else:
                errored = True
                break
    if (not errored):
        return obj
    # error
    msg = "Runtime error trying to set object dotted attribute; property {} does not exist on object {}".format(partStringPartial, identifier)
    raise makeJriException(msg, sloc)














def astOrNativeValueAsNiceString(val, flagShowType):
    from .jrastvals import AstVal
    if (isinstance(val, AstVal)):
        return val.asNiceString(flagShowType)
    return str(val)






































def getUnsafeDictValueAsString(env, obj, key, defaultVal = None):
    from .jrastvals import AstValString
    val = jrfuncs.getDictValueOrDefault(obj, key, defaultVal)
    if (val is None):
        valRet = defaultVal
    elif (isinstance(val,str)):
        valRet = val
    else:
        valRet = val.getUnWrappedExpect(AstValString)
    safeVal = convertEscapeUnsafePlainTextToLatex(valRet)
    return safeVal


def getUnsafeDictValueAsNumber(env, obj, key, defaultVal = None):
    from .jrastvals import AstValNumber
    val = jrfuncs.getDictValueOrDefault(obj, key, defaultVal)
    if (val is None):
        valRet = defaultVal
    elif (isinstance(val,  (int, float))):
        valRet = val
    else:
        valRet = val.getUnWrappedExpect(AstValNumber)
    return valRet


def convertEscapeVouchedOrUnsafePlainTextToLatex(text):
    if (isTextLatexVouched(text)):
        return removeLatexVouch(text)
    latexText = pylatex.utils.escape_latex(text)
    return latexText



def convertEscapeUnsafePlainTextToLatex(text):
    latexText = pylatex.utils.escape_latex(text)
    # see https://jeltef.github.io/PyLaTeX/current/pylatex/pylatex.utils.html#pylatex.utils.NoEscape
    latexText = str(latexText)
    return latexText




def convertEscapeUnsafePlainTextToLatexMorePermissive(text):
    # allow some stuff that is normally escaped

    # kludge protect
    text = text.replace("-","ALLOWEDLATEXHYPHEN")

    latexText = pylatex.utils.escape_latex(text)
    # see https://jeltef.github.io/PyLaTeX/current/pylatex/pylatex.utils.html#pylatex.utils.NoEscape
    latexText = str(latexText)

    # kludge undo
    latexText = latexText.replace("ALLOWEDLATEXHYPHEN","-")

    return latexText


def convertEscapePlainTextFilePathToLatex(text):
    # see https://stackoverflow.com/questions/57467173/include-figures-with-multiple-spaces-in-the-filename
    latexText = pylatex.utils.escape_latex(text)
    #latexText = latexText.replace(" ", r"\space")
    #latexText = '"' + latexText + '"'
    return latexText


def convertIdToSafeLatexId(text):
    # ATTN: this is not sufficient
    text = text.replace(" ", "spc")
    text = text.replace("_", "und")
    text = text.replace("%", "perc")
    text = text.replace("-", "dash")
    text = text.replace(".", "dot")
    text = text.replace("'", "sq")
    text = text.replace('"', "dq")
    text = text.replace("(", "lp")
    text = text.replace(")", "rp")
    text = text.replace("0", "zero")
    text = text.replace("1", "one")
    text = text.replace("2", "two")
    text = text.replace("3", "three")
    text = text.replace("4", "four")
    text = text.replace("5", "five")
    text = text.replace("6", "six")
    text = text.replace("7", "seven")
    text = text.replace("8", "eight")
    text = text.replace("9", "nine")

    latexText = pylatex.utils.escape_latex(text)
    return latexText

def makeLatexLabelFromRid(rid):
    ltext = r"\label{" + rid + "}" + "\n"
    return ltext



def makeLatexLinkToRid(rid, label, pageNumberStyle):
    if (label!="") and (label is not None):
        labelEscaped = convertEscapeVouchedOrUnsafePlainTextToLatex(label)
        ltext = labelEscaped
    else:
        ltext = ""

    if (pageNumberStyle=="onpage"):
        if (len(ltext)>0):
            ltext += " "
        ltext+= r"on p.\pageref*{" + rid + r"}"
    elif (pageNumberStyle=="page"):
        if (len(ltext)>0):
            ltext += " "
        ltext+= r"p.\pageref*{" + rid + r"}"
    elif (pageNumberStyle=="inparen"):
        if (len(ltext)>0):
            ltext += " "
        ltext+= r"(p.\pageref*{" + rid + r"})"


    # if no label, then hyperlink the page number
    ltext = r"\hyperref[{" + rid + r"}]{" + ltext + r"}"

    return ltext




def vouchForLatexString(text, flagEmbeddable):
    # ATTN: unfinished
    if (flagEmbeddable):
        return DefLatexVouchedEmbeddablePrefix + text
    return DefLatexVouchedPrefix + text


def isTextLatexVouched(text):
    return (text.startswith(DefLatexVouchedPrefix) or text.startswith(DefLatexVouchedEmbeddablePrefix))

def isTextLatexVouchedEmbeddable(text):
    return (text.startswith(DefLatexVouchedEmbeddablePrefix))


def removeLatexVouch(text):
    if (text.startswith(DefLatexVouchedEmbeddablePrefix)):
        return text[len(DefLatexVouchedEmbeddablePrefix):]
    if (text.startswith(DefLatexVouchedPrefix)):
        return text[len(DefLatexVouchedPrefix):]
    return text






def convertRenderBlockToSimpleText(block):
    # ast stuff
    from .jrast import AstValString

    if (block is None):
        text = ""
    elif (isinstance(block, str)):
        text = block
    elif (isinstance(block, AstValString)):
        text = block.getUnWrappedExpect(AstValString)
    else:
        # unknown format
        text = str(block)
    return text




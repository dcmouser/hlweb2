# core casebook functions


# jr ast helpers
from .jrcbfuncs import CbFunc, CbParam
from .jrast import AstValString, AstValNumber, AstValBool, AstValIdentifier, AstValList, AstValDict, AstValNull
from .cbtask import DefRmodeRun, DefRmodeRender
from .jriexception import *
from .jrastfuncs import getUnsafeDictValueAsString, makeLatexLinkToRid, vouchForLatexString, convertEscapeUnsafePlainTextToLatex, convertEscapePlainTextFilePathToLatex
from .jrast import JrAstResultList
#
from .cbdeferblock import CbDeferredBlockRefLead, CbDeferredBlockCaseStats, CbDeferredBlockFollowCase, CbDeferredBlockAbsorbFollowingNewline, CbDeferredBlockAbsorbPreviousNewline

# helpers for funcs
from .cbfuncs_core_support import calcInlineLeadLabel, parseTagListArg, buildLatexMarkCheckboxSentence, wrapTextInLatexBox, generateLatexBoxDict, generateLatexForSymbol, generateLatexForSeparator


# python modules
import re






#---------------------------------------------------------------------------
# To figure out:
# copyprev, copynext
#---------------------------------------------------------------------------









def buildFunctionList():
    # create the functions
    functionList = []

    # CbFunc takes: (name, description, paramList, returnType, targetsAccepted, customData, funcPointer, astloc=None)
    # CbParam takes: (name, description, defaultVal, flagAllowNull, paramCheck, flagResolveIdentifiers)

    #---------------------------------------------------------------------------
















    return functionList




































#---------------------------------------------------------------------------
# UNIMPLEMENTED FUNCTION STANDINS

def funcUnimplemented(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    if (rmode == DefRmodeRun):
        return "DEBUG: Unimplemented function output"
    else:
        return "DEBUG: Unimplemented function output (WARNING THIS FUNCTION IS NOT EXPECTED TO RUN IN '{}' mode)".format(rmode)
        raise makeJriException("In function funcUnimplemented but in rmode!= run; do not know what to do.", astloc)


def funcUnimplementedUnified(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    return "DEBUG: Unimplemented unified run/render function output"

#---------------------------------------------------------------------------

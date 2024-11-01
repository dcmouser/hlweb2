# ast modules
from . import jrast
from .jrastfuncs import wrapDictForAstVal, wrapObjectForAstVal
from .casebookDefines import *

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint



# derived class that adds output rendering

class JrAstRootCbr(jrast.JrAstRoot):
    def __init__(self, interp):
        super().__init__(interp)


    def setupBuiltInVars(self, env):
        # test
        info = {
            "name": None,
            "title": None,
            "subtitle": None,
            "authors": None,
            "version": None,
            "versionDate": None,
            "difficulty": None,
            "duration": None,
            "cautions": None,
            "summary": None,
            "extraCredits": None,
            "url": None,
            "keywords": None,
            "clockMode": DefCbGameDefault_clockMode,
        }

        leadDbData = {
            "version": None,
            "versionPrevious": None,
        }

        parserData = {
            #"balancedQuoteCheck": True,
        }

        rendererData = {
            "doubleSided": DefCbRenderDefault_doubleSided,
            "latexPaperSize": DefCbRenderDefault_latexPaperSize,
            "latexFontSize": DefCbRenderDefault_latexFontSize,
            "autoStyleQuotes": DefCbRenderDefault_autoStyleQuotes,
        }

        documentData = {
            "defaultLocation": DefCbDocumentDefault_defaultLocation,
            "printLocation": DefCbDocumentDefault_printLocation,
            "printStyle": DefCbDocumentDefault_printStyle,
        }




        # register these python objects with runtime environment
        env.declareEnvVar(None, "info", "information about the game", wrapDictForAstVal(None, info), False)
        env.declareEnvVar(None, "leadDbData", "highlow location data settings", wrapDictForAstVal(None, leadDbData), False)
        env.declareEnvVar(None, "parserData", "parser settings", wrapDictForAstVal(None, parserData), False)
        env.declareEnvVar(None, "rendererData", "renderer settings", wrapDictForAstVal(None, rendererData), False)
        env.declareEnvVar(None, "documentData", "document settings", wrapDictForAstVal(None, documentData), False)

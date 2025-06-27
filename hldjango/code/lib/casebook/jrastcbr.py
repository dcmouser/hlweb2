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
            "status": None,
            "difficulty": None,
            "duration": None,
            "cautions": None,
            "summary": None,
            "extraCredits": None,
            "url": None,
            "copyright": None,
            "keywords": None,
            "gameSystem": None,
            "gameDate": None,
            "campaignName": None,
            "campaignPosition": None,
            "clockMode": DefCbGameDefault_clockMode,
        }

        leadDbData = {
            "version": None,
            "versionPrevious": None,
            "seed": 0,
        }

        parserData = {
            #"balancedQuoteCheck": True,
        }

        rendererData = {
            "doubleSided": DefCbRenderDefault_doubleSided,
            "latexPaperSize": DefCbRenderDefault_latexPaperSize,
            "latexFontSize": DefCbRenderDefault_latexFontSize,
            "isNarrowPaperSize": False,
            "autoStyleQuotes": DefCbRenderDefault_autoStyleQuotes,
            "bypassErrorOnMissingImage": None,
            "timeStyle": DefCbRenderDefault_timeStyle,
            #"defaultTime": DefCbRenderDefault_defaultTime,
            "defaultTimeStyle": DefCbRenderDefault_defaultTimeStyle,
            "zeroTimeStyle": DefCbRenderDefault_zeroTimeStyle,
        }

        documentData = {
            "defaultLocation": DefCbDocumentDefault_defaultLocation,
            "printLocation": DefCbDocumentDefault_printLocation,
            "printStyle": DefCbDocumentDefault_printStyle,
        }

        tagData = {
            "alwaysNumber": DefCbRenderSettingDefault_Tag_alwaysNumber,
            "consistentNumber": DefCbRenderSettingDefault_Tag_consistentNumber,
            "mode": DefCbRenderSettingDefault_Tag_mode,
            "sortRequire": DefCbRenderSettingDefault_Tag_sortRequire,
        }

        localeData = {
            "language": DefCbLocaleDefault_language
        }



        # register these python objects with runtime environment
        env.declareEnvVar(None, "info", "information about the game", wrapDictForAstVal(None, info), False)
        env.declareEnvVar(None, "leadDbData", "nynoir or shcd database of locations", wrapDictForAstVal(None, leadDbData), False)
        env.declareEnvVar(None, "parserData", "parser settings", wrapDictForAstVal(None, parserData), False)
        env.declareEnvVar(None, "rendererData", "renderer settings", wrapDictForAstVal(None, rendererData), False)
        env.declareEnvVar(None, "documentData", "document settings", wrapDictForAstVal(None, documentData), False)
        env.declareEnvVar(None, "tagData", "tag settings", wrapDictForAstVal(None, tagData), False)
        env.declareEnvVar(None, "localeData", "locale (translation) settings", wrapDictForAstVal(None, localeData), False)

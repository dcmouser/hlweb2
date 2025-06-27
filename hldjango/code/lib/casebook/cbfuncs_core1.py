# core casebook functions


# jr ast helpers
from .jrcbfuncs import CbFunc, CbParam
from .jrast import AstValString, AstValNumber, AstValBool, AstValIdentifier, AstValList, AstValDict, AstValNull, convertTypeStringToAstType, JrAstResultList, DefCbDefine_IdBlank, DefCbDefine_IDEmpty
from .jrast import ResultAtomLatex, ResultAtomMarkdownString, ResultAtomPlainString, ResultAtomNote
from .jrastvals import AstValObject
from .cbtask import DefRmodeRun, DefRmodeRender
from .jriexception import *
from .jrastfuncs import getUnsafeDictValueAsString, makeLatexLinkToRid, vouchForLatexString, convertEscapeUnsafePlainTextToLatex, convertEscapePlainTextFilePathToLatex, convertEscapeUnsafePlainTextToLatexMorePermissive, convertIdToSafeLatexId, getUnsafeDictValueAsNumber
from .jrastfuncs import isTextLatexVouched, unwrapIfWrappedVal
from .jrastutilclasses import JrINote
from .jrast import JrAstResultList, JrAstEntry
#
from .cbdeferblock import CbDeferredBlockRefLead, CbDeferredBlockCaseStats, CbDeferredBlockFollowCase, CbDeferredBlockEndLinePeriod, CbDeferredBlockAbsorbFollowingNewline, CbDeferredBlockAbsorbPreviousNewline, CbDeferredBlockLeadTime, CbDeferredBlockLeadHeader

# helpers for funcs
from .cbfuncs_core_support import calcInlineLeadLabel, parseTagListArg, buildLatexMarkCheckboxSentence, wrapInLatexBox, wrapInLatexBoxJustStart, wrapInLatexBoxJustEnd, generateLatexForSymbol, generateLatexForDivider, generateLatexRuleThenLineBreak, generatelatexLineBreak2, convertHoursToNiceHourString, generateLatexBreak, generateImageEmbedLatex, generateLatexForPageStyle, generateLatexCalendar
from .cbfuncs_core_support import parseArgsGenericBoxOptions, isBoxRequested, addBoxToResultsIfAppropriateStart, addBoxToResultsIfAppropriateEnd, addTargetsToResults, addTargetsToResultsIntoCommand, exceptionIfNotRenderMode
from .cbfuncs_core_support import findDayByNumber, createStartEndLatexForFontSizeString, makeLatexSafeFilePath, parseFontSize, convertNumericWidthToFraction, convertStringToSafeLatexSize
from .cbfuncs_core_support import getTargetResultBlockAsTextIfAppropriate, convertTargetRetvToResultList
from .cbfuncs_core_support import generateFoundGainString, addGainTagTextLineToResults, addCheckTagTextLineToResults, blurbItemLatex
from .cbfuncs_core_support import makeMiniPageBlockLatexStart, makeMiniPageBlockLatexEnd, dropCapResults, resultTextOrFollowCase
from .cbfuncs_core_support import convertStringToSafeLatexSize, latexSideRulesAround, lookupLatexSymbol, preventWordWrapOnLeadIdHypenLatex
from .cbfuncs_core_support import newsLatexFormatHeadlineString, newsLatexFormatBylineString, safeLatexSizeFromUserString
from .cbfuncs_core_support import cipherMakeRandomSubstitutionKeyFromHash, cipherMakeSimpleSubstitutionKeyFromKeyword, cipherMakeUniqueKeywordAlphabet, cipherSpellDigits, cipherSegment, cipherStripChars, cipherMorseCode, cipherReplaceNonLettersReturnFixList, cipherReplaceFixList, cipherRemoveReplacePunctuation, cipherPlain
from .cbfuncs_core_support import formHelperListBuild, functionRunEffectOnImagePath, wrapInFigure
from .cbfuncs_core_support import makeMiniPageBlockLatexStart, makeMiniPageBlockLatexEnd, dropCapResults
from .cbfuncs_core_support import newsLatexFormatHeadlineString, newsLatexFormatBylineString, safeLatexSizeFromUserString
from .cbfuncs_core_support import JrDefUserFuncTargetsEnvVarId, buildFormElementTextLatex, generateFormTextLatex
#
from .cbdays import CbDayManager, CbDay
#
from .casebookDefines import *

# translation
from .cblocale import _

# python modules
import re
from datetime import datetime, timedelta
import string
import random

# cipher
import pycipher



# local defines
DEF_CustomLogicType_Arg = "_ARG_"



#---------------------------------------------------------------------------
# helper
def makeBoxParams(defaults={}):
    boxParams = [
        CbParam("box", "box style", jrfuncs.getDictValueOrDefault(defaults,"box", None), True, AstValString, True),
        CbParam("textColor", "color of Text", jrfuncs.getDictValueOrDefault(defaults,"textColor", None), True, AstValString, True),
        CbParam("symbol", "symbol", jrfuncs.getDictValueOrDefault(defaults,"symbol", None), True, AstValString, True),
        CbParam("symbolColor", "symbol color", jrfuncs.getDictValueOrDefault(defaults,"symbolColor", None), True, AstValString, True),
        CbParam("pos", "position alignment of enclosing box", jrfuncs.getDictValueOrDefault(defaults,"pos", None), True, AstValString, True),
        CbParam("width", "Width as a decimal percentage (0.1 to 1.0) or string ending in [in|cm]", jrfuncs.getDictValueOrDefault(defaults,"width", None), True, [AstValNumber, AstValString], True),
    ]
    return boxParams
#---------------------------------------------------------------------------







def buildFunctionList():
    # create the functions
    functionList = []


    # CbFunc takes: (name, description, paramList, returnType, targetsAccepted, customData, funcPointer, astloc=None)
    # CbParam takes: (name, description, defaultVal, flagAllowNull, paramCheck, flagResolveIdentifiers)





    #---------------------------------------------------------------------------
    # configureation of game
    # see casebookDefaults.py where some defaults are set for paramaeters, and jrastcbr.py for where defaults are set if these functions are not used

    functionList.append(CbFunc("configureGameInfo", "Configure game options", [
            CbParam("name", "Simple unique name of the case (used for filenames, etc.)", None, False, AstValString, True),
            CbParam("title", "Case title", None, False, AstValString, True),
            CbParam("subtitle", "Case subtitle", "", False, AstValString, True),
            CbParam("authors", "Authors of the case (name <email> separated by commas)", None, False, AstValString, True),
            CbParam("version", "Case version (dotted string like 1.0)", None, False, AstValString, True),
            CbParam("versionDate", "Date of this version (day/month/year)", None, False, AstValString, True),
            CbParam("status", "Status of the game (playable, inprogress, etc.)", "", False, AstValString, True),
            CbParam("difficulty", "From 1 to 5 (e.g. 3.5)", None, False, AstValNumber, True),
            CbParam("duration", "Estimated play time in hours", None, False, AstValNumber, True),
        ],
        "text", None, None,
        funcConfigureGameInfo
        ))

    functionList.append(CbFunc("configureGameSummary", "Configure game summary options", [
            CbParam("summary", "Summary to show in listing and on cover page", "", False, AstValString, True),
        ],
        "text", None, None,
        funcConfigureGameSummary
        ))

    functionList.append(CbFunc("configureGameInfoExtra", "Configure game options", [
            CbParam("gameSystem", "Game system (nyNoir, shcd)", "nyNoir", False, AstValString, True),
            CbParam("gameDate", "Date of the first day of the case in game time; as a string (mm/dd/yyyy)", "", False, AstValString, True),
            CbParam("cautions", "Any cautions to players (eg. adult language)", "", False, AstValString, True),
            CbParam("url", "Website url to learn more", "", False, AstValString, True),
            CbParam("copyright", "Copyright line", "", False, AstValString, True),
            CbParam("extraCredits", "Extra credits to show in listing and on cover page", "", False, AstValString, True),
            CbParam("keywords", "Keywords", "", False, AstValString, True),
        ],
        "text", None, None,
        funcConfigureGameInfoExtra
        ))

    functionList.append(CbFunc("configureCampaign", "Configure game campaign options", [
            CbParam("name", "Campaign name", None, True, AstValString, True),
            CbParam("position", "Position in campaign sequence", None, False, [AstValNumber, AstValString], True),
        ],
        "text", None, None,
        funcConfigureGameCampaign
        ))


    functionList.append(CbFunc("configureClock", "Configure game clock options", [
            CbParam("clockMode", "True means that players will track how much time passes as they visit leads", DefCbGameDefault_clockMode, False, AstValBool, True),
        ],
        "text", None, None,
        funcConfigureClock
        ))


    functionList.append(CbFunc("configureLeadDb", "Configure location data options (what database to use for looking up locations)", [
            CbParam("version", "Version of the location data", "v2", False, AstValString, True),
            CbParam("versionPrevious", "Version of the previous location data (used to help check for migration problems)", "", False, AstValString, True),
            CbParam("seed", "Random number generator seed used for randomizing unused leads", None, True, AstValString, True),
        ],
        "text", None, None,
        funcConfigureLeadDb
        ))


    functionList.append(CbFunc("configureParser", "Configure parser options", [
            #CbParam("balancedQuoteCheck", "Check and report any imbalance in double quotes", False, False, AstValBool, True),
        ],
        "text", None, None,
        funcConfigureParser
        ))


    functionList.append(CbFunc("configureRenderer", "Configure renderer options", [
            CbParam("doubleSided", "Lay out page numbers for double sided printing (alternating corners)", DefCbRenderDefault_doubleSided, False, AstValBool, True),
            CbParam("latexPaperSize", "Latex paper size", DefCbRenderDefault_latexPaperSize, False, DefCbRenderDefault_latexPaperSizesAllowed, True),
            CbParam("latexFontSize", "Latex font size", DefCbRenderDefault_latexFontSize, False, AstValNumber, True),
            CbParam("autoStyleQuotes", "Auto style unicode left and right quote markers for more subtle font look (can cause hard-to-diagnose latex compilation errors)", DefCbRenderDefault_autoStyleQuotes, False, AstValBool, True),
            CbParam("timeStyle", "How to display elapsed time in leads", DefCbRenderDefault_timeStyle, False, ["box", "header", "hide"], True),
            #CbParam("defaultTime", "Default time in minutes", DefCbRenderDefault_defaultTime, True, AstValNumber, True),
            CbParam("defaultTimeStyle", "Whether to hide or dim default times", DefCbRenderDefault_defaultTimeStyle, True, ["hide","normal","bold", "red"], True),
            CbParam("zeroTimeStyle", "Whether to say explicitly when leads have 0 time", DefCbRenderDefault_zeroTimeStyle, True, ["hide", "normal","bold", "red"], True),
        ],
        "text", None, None,
        funcConfigureRenderer
        ))


    functionList.append(CbFunc("configureTags", "Configure tag options", [
            CbParam("alwaysNumber", "Always use marker ids like A1,B1,...A2,B2 instead of A,B..A2,B2, even if < 26 markers; default true; note the caselog.pdf need to amtch)", DefCbRenderSettingDefault_Tag_alwaysNumber, False, AstValBool, True),
            CbParam("consistentNumber", "If alwaysNumber is false, you can set this to change A,B,... to A1,B1,... if and only if there are enough markers to reach A2, etc.", DefCbRenderSettingDefault_Tag_consistentNumber, False, AstValBool, True),
            CbParam("mode", "mode to use when generating obfuscated labels", DefCbRenderSettingDefault_Tag_mode, False, ["sequential", "random", "firstLetter"], True),
            CbParam("sortRequire", "When presenting list of required tags for the day, sort them by (obfuscated) tag label; default true; set this to false if you set sequential false and order of hint checking is important; if false, order in requirement list will match order that tags were declared", DefCbRenderSettingDefault_Tag_sortRequire, False, AstValBool, True),
        ],
        "text", None, None,
        funcConfigureTags
        ))


    functionList.append(CbFunc("configureLocale", "Configure locale options", [
            CbParam("language", "Language code [en|fr|es|...]", "en", False, AstValString, True),
        ],
        "text", None, None,
        funcConfigureLocale
        ))



    functionList.append(CbFunc("configureDivider", "Configure divider options", [
            CbParam("id", "Divider id", "lead", False, AstValString, True),
            CbParam("path", "Path to image (or specify 'none' for none or 'rule' for rule)", None, True, AstValString, True),
            CbParam("pgfornament", "PgfOrnament id", None, True, AstValNumber, True),
            CbParam("width", "Width as a decimal percentage (0.1 to 1.0) or string ending in [in|cm]", "3cm", True, [AstValNumber, AstValString], True),
            CbParam("rule", "put a side rule on either side of the image", False, False, AstValBool, True),
            CbParam("align", "Alignment", "center", False, ["left", "center", "right"], True), 
        ],
        "text", None, None,
        funcConfigureDivider
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    # Section Configuring
    #
    genericSectionConfigurationOptionsEarly = [
    ]
    #
    genericSectionConfigurationOptionsLate = [
        # IMPORTANT that these all allow None as missing fields, so that we can avoid setting values when none provided
            CbParam("autoLead", "Automatically assign a lead id", None, True, AstValBool, True),
            #
            CbParam("time", "Duration of lead (in minutes)", None, True, AstValNumber, True),
            CbParam("timePos", "Position to add time instruction", None, True, ["", "start", "end", "hide"], True),
            #
            CbParam("sectionColumns", "Number of columns in Section main text", None, True, AstValNumber, True),
            CbParam("leadColumns", "Number of columns in layout for child leads", None, True, AstValNumber, True),
            #
            CbParam("sectionBreak", "Break style for section", None, True, ["", "none", "before", "after", "solo", "beforeFacing", "afterFacing", "soloFacing", "soloAfterFacing"], True),
            CbParam("leadBreak", "Break style for child leads", None, True, ["", "none", "before", "after", "solo", "beforeFacing", "afterFacing", "soloFacing", "soloAfterFacing"], True),
            #
            CbParam("heading", "Heading text shown on page (blank for none)", None, True, AstValString, True),
            CbParam("toc", "Label for table of contents (blank to hide from table of contents)", None, True, AstValString, True),
            CbParam("childToc", "Label for table of contents for children (blank to hide from table of contents)", None, True, AstValString, True),
            #
            CbParam("childPlugins", "Name of the plugins to run on children", None, True, AstValString, True),
            #
            CbParam("dividers", "Should we show dividers between child entries", None, True, AstValBool, True),
            CbParam("address", "Address line under heading/label; set to 'auto' to auto grab from database or '' blank to mean none", None, True, AstValString, True),
            #
            CbParam("copy", "Entry id to copy contents from, or 'next' to copy from next lead", None, True, AstValString, True),
            #
            CbParam("render", "If set false this lead will not render", None, True, AstValBool, True),
            CbParam("blank", "If set true then we will not show the header or add this to toc", None, True, AstValBool, True),
            #
            CbParam("mStyle", "Set to a string keyword that informs mind map drawing", None, True, AstValString, True),
            #
            CbParam("continuedFrom", "Add label saying 'continued from this lead", None, True, AstValString, True),
            CbParam("headingStyle", "style for rendering heading", None, True, ["header", "footer", "alsoFooter", "huge"], True),
            CbParam("childHeadingStyle", "default style for child lead rendering heading", None, True, ["header", "footer", "alsoFooter", "huge"], True),
            CbParam("layout", "rendering layout styles", None, True, AstValString, True),
            #
            CbParam("label", "Label as parameter", None, True, AstValString, True),
            #
            CbParam("sortGroup", "sort group", None, True, [AstValString,AstValNumber], True),
            CbParam("sortKey", "sort key", None, True, AstValString, True),
            #
            CbParam("multiPage", "Should we show page N of M in header", None, True, [AstValString, AstValBool], True),
    ]

    # sections
    functionList.append(CbFunc("configureSection", "Configure an arbitrary section",
        [
        CbParam("id", "Section ID", None, False, AstValString, True),
        ] +
        genericSectionConfigurationOptionsEarly +
        [
        ]
        + genericSectionConfigurationOptionsLate,
        "text", None, None,
        funcConfigureSection
        ))

    functionList.append(CbFunc("configureLeads", "Configure leads options and leads section",
        genericSectionConfigurationOptionsEarly +
        [
        ]
        + genericSectionConfigurationOptionsLate,
        "text", None, None,
        funcConfigureLeads
        ))

    functionList.append(CbFunc("configureHints", "Configure hint options and hints section",
        genericSectionConfigurationOptionsEarly +
        [
        ]
        + genericSectionConfigurationOptionsLate,
        "text", None, None,
        funcConfigureHints
        ))

    functionList.append(CbFunc("configureFront", "Configure front section",
        genericSectionConfigurationOptionsEarly +
        [
        ]
        + genericSectionConfigurationOptionsLate,
        "text", None, None,
        funcConfigureFront
        ))

    functionList.append(CbFunc("configureEnd", "Configure end section",
        genericSectionConfigurationOptionsEarly +
        [
        ]
        + genericSectionConfigurationOptionsLate,
        "text", None, None,
        funcConfigureEnd
        ))

    functionList.append(CbFunc("configureReport", "Configure reports options and reports section",
        genericSectionConfigurationOptionsEarly +
        [
        ]
        + genericSectionConfigurationOptionsLate,
        "text", None, None,
        funcConfigureReport
        ))

    functionList.append(CbFunc("configureDocuments", "Configure document options and documents section",
        genericSectionConfigurationOptionsEarly +
        [
            CbParam("defaultLocation", "Default location of documents [back,custom text]", DefCbDocumentDefault_defaultLocation, False, AstValString, True),
            CbParam("printLocation", "Where to print documents [inline, end, pdf]", DefCbDocumentDefault_printLocation, False, ["inline", "end", "pdf"], True),
            CbParam("printStyle", "Style to print documents [simple, triFold]", DefCbDocumentDefault_printStyle, False, ["simple", "triFold"], True),
        ]
        + genericSectionConfigurationOptionsLate,
        "text", None, None,
        funcConfigureDocuments
        ))

    # new function for letting user configure days
    functionList.append(CbFunc("configureDay", "Configure a day",
        genericSectionConfigurationOptionsEarly +
        [
            CbParam("day", "Number of the day", None, False, AstValNumber, True),
            CbParam("type", "Day type", "normal", False, AstValString, True),
            CbParam("start", "24 hour clock hour or string", 9, False, [AstValNumber,AstValString], True),
            CbParam("end", "24 hour clock hour", 18, False, [AstValNumber,AstValString], True),
            CbParam("date", "Date in form mm/dd/yyyy", None, True, AstValString, True),
            # for hints
            CbParam("hintAlly", "is there an ally they can visit for more help", "", False, ["", "financialPrecinct"], True),
            CbParam("allyFreeStart", "start time where hint is free", -1, False, [AstValNumber,AstValString], True),
            CbParam("allyFreeEnd", "end time where hint is free", -1, False, [AstValNumber,AstValString], True),
        ]
        + genericSectionConfigurationOptionsLate,
        "text", None, None,
        funcConfigureDay
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    functionList.append(CbFunc("_entryApplyOptions", "Internal function for applying options to entry", [
            #CbParam("_entry", "Object pointer to entry whose options are being set", None, False, None, False),
            CbParam("id", "id as parameter for overiding", None, True, AstValString, True),
        ]
        + genericSectionConfigurationOptionsLate,
        None, None, None,
        funcApplyEntryOptions
        ))
    #---------------------------------------------------------------------------








    #---------------------------------------------------------------------------
    functionList.append(CbFunc("declareVar", "Declarts a variable", [
            CbParam("var", "The variable name to set", None, False, AstValIdentifier, False),
            CbParam("val", "Initial value for the variable", None, True, None, True),
            CbParam("desc", "Description", "", False, None, True),
        ],
        None, None, None,
        funcDeclareVar
        ))

    functionList.append(CbFunc("declareConst", "Declarts a variable", [
            CbParam("var", "The variable name to set", None, False, AstValIdentifier, False),
            CbParam("val", "Initial value for the variable", None, False, None, True),
            CbParam("desc", "Description", "", False, None, True),
        ],
        None, None, None,
        funcDeclareConst
        ))

    functionList.append(CbFunc("set", "Sets a variable to a value", [
            CbParam("var", "The variable name to set", None, False, AstValIdentifier, False),
            CbParam("val", "The new value for the variable", None, False, None, True),
        ],
        None, None, None,
        funcSet
        ))

    functionList.append(CbFunc("setDefault", "Sets a variable to a value IF its not already set", [
            CbParam("var", "The variable name to set", None, False, AstValIdentifier, False),
            CbParam("val", "The new value for the variable", None, False, None, True),
        ],
        None, None, None,
        funcSetDefault
        ))
    functionList.append(CbFunc("get", "Gets a variable if its set, or default val if not", [
            CbParam("var", "The variable name to set", None, False, AstValIdentifier, False),
            CbParam("val", "The default value if the variable is not set", None, False, None, True),
        ],
        None, None, None,
        funcGetDefault
        ))

    functionList.append(CbFunc("defineTag", "Defines a tag", [
            CbParam("tagId", "The dotted identifier used to refer to the tag", None, False, AstValString, True),
            CbParam("deadline", "Deadline label describing the tag", -1, False, AstValNumber, True),
            CbParam("label", "Longer label describing the tag", "", False, AstValString, True),
            CbParam("location", "Override default (document) location; use 'back' for back of book", None, True, AstValString, True),
            CbParam("obfuscatedLabel", "Override default (document) obfuscated label; set to 'label' to use the label", None, True, AstValString, True),
            CbParam("dependencies", "list of tags we are dependent on when giving hints", None, True, AstValString, True),
        ],
        None, None, None,
        funcDefineTag
        ))


    functionList.append(CbFunc("defineConcept", "Defines a tag", [
            CbParam("id", "The dotted identifier used to refer to the tag", None, False, AstValString, True),
            CbParam("label", "Longer label describing the tag", "", False, AstValString, True),
        ],
        None, None, None,
        funcDefineConcept
        ))


    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    functionList.append(CbFunc("toc", "Generate and insert table of contents", [
            CbParam("columns", "Number of columns for table of contents (leave blank for automatic based on page width)", None, True, AstValNumber, True),
        ],
        None, None, None,
        funcToc
        ))

    functionList.append(CbFunc("blurbCoverPage", "Creates a cover page blurb", [
        ],
        "text", 1, None,
        funcBlurbCoverPage
        ))

    functionList.append(CbFunc("image", "Insert an image", [
            CbParam("path", "Relative path to file image", None, False, AstValString, True),
            CbParam("style", "Choose from a preset style", None, True, ["frame", "plain", "bordered"], True), 
            CbParam("width", "Width (fraction where 0.5 is half page width) or string ending in [in|cm]", None, True, [AstValNumber, AstValString], True),
            CbParam("height", "Height (fraction where 0.5 is half page height; use 'remaining' to size to remaining space on page)", None, True, AstValString, True),
            CbParam("borderWidth", "border width (in points; 0 for none); default 0", None, True, AstValNumber, True),
            CbParam("padding", "padding width (in points; 0 for none); default 0", None, True, AstValNumber, True),
            CbParam("align", "Alignment", None, True, ["left", "center", "right"], True), 
            CbParam("caption", "caption to show under image", None, True, AstValString, True),
            CbParam("captionPos", "Position for caption'", "bottom", False, ["top", "bottom"], True),
            CbParam("captionSize", "Size of caption (default='normal')", None, True, AstValString, True),
            CbParam("rule", "put a side rule on either side of the image", False, False, AstValBool, True),
            CbParam("wrap", "Wrap subsequent text around image (must use align left)", False, False, [AstValBool,AstValNumber,AstValString], True),
        ],
        "text", None, None,
        funcImage
        ))

    functionList.append(CbFunc("embedFile", "Embed another pdf/text file in output", [
            CbParam("path", "Relative path to file to embed", None, False, AstValString, True),
            CbParam("pages", "Comma separated page list", "-", False, AstValString, True),
            CbParam("scale", "Scaled for embed", None, True, AstValNumber, True),
            CbParam("pageStyle", "Page style to use for the page (use 'empty' to hide footer)", "", False, AstValString, True),            
            CbParam("toc", "Table of contents label", None, True, AstValString, True),
        ],
        "text", None, None,
        funcEmbedFile
        ))


    functionList.append(CbFunc("pageBackground", "Set the current page background (useful for covers, etc.)", [
            CbParam("path", "Relative path to image OR pdf file to use as the background image", None, False, AstValString, True),
            CbParam("opacity", "Opacity of the background image", 1.0, False, AstValNumber, True),  
        ],
        "text", None, None,
        funcPageBackground
        ))

    #---------------------------------------------------------------------------





    #---------------------------------------------------------------------------
    # these all share the same work function (funcRefLead)

    refLeadParams = [
            CbParam("style", "style to show lead info", "default", False, ["default", "full", "nolabel", "plainid", "page", "pageparen", "pagenum"], True),
            CbParam("back", "tell them to come back after they visit lead", False, False, AstValBool, True),
        ]
    #
    functionList.append(CbFunc("referLead", "Add text to refer to lead", [
            CbParam("id", "ID of lead", None, False, AstValString, True),
            ]
            + refLeadParams,
        "text", None, {"pretext":"", "mindMapType": "refers"},
        funcRefLead
        ))
    functionList.append(CbFunc("goLead", "Add text to go to lead", [
            CbParam("id", "ID of lead", None, False, AstValString, True),
            ]
            + refLeadParams,
        "text", None, {"pretext":"go to ", "mindMapType": "go"},
        funcRefLead
        ))
    functionList.append(CbFunc("returnLead", "Add text to go to lead", [
            # note we allow a null id here
            CbParam("id", "ID of lead", None, True, AstValString, True),
            ]
            + refLeadParams,
        "text", None, {"pretext":"return to ", "mindMapType": "returns"},
        funcRefLead
        ))
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    functionList.append(CbFunc("reserveLead", "Reserve a lead from the unused list so it will not be used by the auto lead generator", [
            # note we allow a null id here
            CbParam("id", "ID of lead", None, True, AstValString, True),
            ],
        "text", None, None,
        funcReserveLead
        ))
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    functionList.append(CbFunc("embedLead", "Return inline", [
            CbParam("id", "Lead id", "", False, AstValString, True),
        ],
        "text", None, None,
        funcEmbedLead
        ))
    #---------------------------------------------------------------------------








    #---------------------------------------------------------------------------
    gainTagParams = [
            CbParam("id", "ID of tag (or list of ids)", None, False, AstValString, True),
            CbParam("box", "box style", None, True, AstValString, True),
        ]

    functionList.append(CbFunc("gainTag", "Mark a tag", [
        ] + gainTagParams,
        "text", None, {"action": "circle"},
        funcGainTag
        ))

    functionList.append(CbFunc("circleTag", "Mark a tag", [
        ] + gainTagParams,
        "text", None, {"action": "circle"},
        funcGainTag
        ))

    functionList.append(CbFunc("underlineTag", "Underline a tag", [
        ] + gainTagParams,
        "text", None, {"action": "underline"},
        funcGainTag
        ))

    functionList.append(CbFunc("strikeTag", "Strike through a tag", [
        ] + gainTagParams,
        "text", None, {"action": "strike"},
        funcGainTag
        ))


    if (True):
        # decoy tag support is fully written, BUT it breaks with the new post-process function that reassigns tag label, since that requires all tag to be defined AHEAD of time
        # that new code will generate an exception message explaining why decoyTag cannot be used
        functionList.append(CbFunc("gainDecoy", "Create and have the player gain a decoy red herring tag", [
                CbParam("id", "ID of tag (or list of ids)", "", False, AstValString, True),
                CbParam("box", "box style", None, True, AstValString, True),
                CbParam("deadline", "Deadline label describing the tag", -1, False, AstValNumber, True),
                CbParam("obfuscatedLabel", "Override default (document) obfuscated label; set to 'label' to use the label", None, True, AstValString, True),
            ],
            "text", None, {"action": "circle", "autoDeclarePrefix":"decoy"},
            funcGainTag
            ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    checkTagParams = [
            CbParam("id", "ID of tag", None, False, AstValString, True),
            CbParam("check", "check style for multiple tags", "all", False, ["", "any", "all"], True),
            CbParam("box", "box style", None, True, AstValString, True),
            CbParam("noif", "hide the preliminary if", False, False, AstValBool, True),
        ]
    
    functionList.append(CbFunc("requireTag", "Tell user they should leave if they dont have tag and come back when they do", [
        ] + checkTagParams,
        "text", None, {"testType": "require", "action": "circle"},
        funcCheckTag
        ))

    functionList.append(CbFunc("hasTag", "Check if user has tag", [
        ] + checkTagParams,
        "text", None, {"testType": "has", "action": "circle"},
        funcCheckTag
        ))

    functionList.append(CbFunc("missingTag", "Is player missing a tag", [
        ] + checkTagParams,
        "text", None, {"testType": "missing", "action": "circle"},
        funcCheckTag
        ))


    # new variations
    functionList.append(CbFunc("didCircleTag", "Check if user circled tag", [
        ] + checkTagParams,
        "text", None, {"testType": "has", "action": "circle"},
        funcCheckTag
        ))
    functionList.append(CbFunc("didGainTag", "Check if user gained tag", [
        ] + checkTagParams,
        "text", None, {"testType": "has", "action": "gain"},
        funcCheckTag
        ))
    functionList.append(CbFunc("didUnderlineTag", "Check if user underlined tag", [
        ] + checkTagParams,
        "text", None, {"testType": "has", "action": "underline"},
        funcCheckTag
        ))
    functionList.append(CbFunc("didStrikeTag", "Check if user underlined tag", [
        ] + checkTagParams,
        "text", None, {"testType": "has", "action": "strike"},
        funcCheckTag
        ))
    functionList.append(CbFunc("didMarkTag", "Check if user marked tag", [
        ] + checkTagParams,
        "text", None, {"testType": "has", "action": "mark"},
        funcCheckTag
        ))
    functionList.append(CbFunc("didUnderlineNotCircleTag", "Check if user marked tag", [
        ] + checkTagParams,
        "text", None, {"testType": "has", "action": "underlineNotCircle"},
        funcCheckTag
        ))
    
    #
    functionList.append(CbFunc("circleUnderlinedTag", "instruct user to circle an underlined tag and then extra", [
        ] + checkTagParams,
        "text", 1, {"testType": "has", "action": "underlineNotCircle", "gain": "circle"},
        funcInstructTag
        ))
    functionList.append(CbFunc("strikeCircledTag", "instruct user to strike a circled tag and then extra", [
        ] + checkTagParams,
        "text", 1, {"testType": "has", "action": "circleNotStrike", "gain": "strike"},
        funcInstructTag
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    functionList.append(CbFunc("referTag", "refer to tag(s) by its obfuscated label", [
            CbParam("id", "ID of tag", None, False, AstValString, True),
            CbParam("combine", "combine style [and,or] for multiple tags", "all", False, ["", "any", "all"], True),
        ],
        "text", None, "missing",
        funcReferTag
        ))


   
    functionList.append(CbFunc("mentionTags", "Just list some tags by their obfuscated ids (e.g. used when listing tags available for completionists)", [
            CbParam("tags", "list of tags", "", False, AstValString, True),
        ],
        "text", None, None,
        funcMentionTags
        ))



    functionList.append(CbFunc("autoHint", "generate an autohint", [
            CbParam("id", "ID of tag (or list of ids)", "", False, AstValString, True),
            CbParam("demerits", "Demerits to mark", 3, False, AstValNumber, True),
        ],
        None, None, None,
        funcAutoHint
        ))

    functionList.append(CbFunc("autoHintDependencies", "tell player about hint dependencies", [
            CbParam("id", "ID of tag (or list of ids)", "", False, AstValString, True),
        ],
        None, None, None,
        funcAutoHintDependencies
        ))

    #---------------------------------------------------------------------------






    #---------------------------------------------------------------------------
    functionList.append(CbFunc("mark", "Mark checkboxes", [
            CbParam("type", "type of mark to make", None, True, AstValString, True),
            CbParam("count", "How many to mark", 0, False, AstValNumber, True),
            #
            CbParam("demerits", "Demerits to mark", 0, False, AstValNumber, True),
            CbParam("culture", "Culture boxes to mark", 0, False, AstValNumber, True),
            CbParam("reputation", "Reputation boxes to mark", 0, False, AstValNumber, True),
            CbParam("extra", "Extra boxes to mark", 0, False, AstValNumber, True),
            CbParam("helpful", "Instruct to mark only if helpful", None, True, AstValBool, True),
            CbParam("why", "Label clarifying why", None, True, AstValString, True),
            CbParam("upto", "Say up to (max)", False, False, AstValBool, True),
        ],
        "text", None, None,
        funcMark
        ))
    #---------------------------------------------------------------------------











    #---------------------------------------------------------------------------
    # helper
    def makeInlineParams(defaults={}):
        params = [
            CbParam("link", "Text link", "", False, AstValString, True),
            CbParam("label", "Label for new lead", "", False, AstValString, True),
            CbParam("time", "Duration of lead (in minutes)", None, True, AstValNumber, True),
            CbParam("timePos", "Position to add time instruction", "", False, ["", "start","end"], True),
            CbParam("demerits", "Demerit checkboxes", jrfuncs.getDictValueOrDefault(defaults,"demerits",0), False, AstValNumber, True),
            CbParam("why", "why text (shown after demerit instruction)", "", False, AstValString, True),
            CbParam("back", "direct them to return after visiting inline lead?", False, False, AstValBool, True),
            CbParam("mLabel", "Label for mindmap link", "", False, AstValString, True),
        ]
        return params


    functionList.append(CbFunc("inline", "Create inline", [
        ] + makeInlineParams({"demerits": 0}),
        "text", 1, None,
        funcInline
        ))
    functionList.append(CbFunc("inlineHint", "Create inline", [
        ] + makeInlineParams({"demerits": 2}),
        "text", 1, {"helpful": "hint"},
        funcInline
        ))
    #---------------------------------------------------------------------------






    #---------------------------------------------------------------------------
    functionList.append(CbFunc("box", "Put contents in box",
        makeBoxParams({"box": "default"}) + [
        ],
        "text", 1, None,
        funcBox
        ))


    functionList.append(CbFunc("format", "Format text", [
            CbParam("style", "style for formatting", "font", False, ["", "font", "radio", "news", "handwriting", "typewriter", "choice", "warning", "culture", "dayTest", "quote", "tornYellow", "tornGray", "compact", "ttcompact"], True),
            CbParam("font", "font id previously set with defineFont()", None, True, AstValString, True),           
            CbParam("size", "size of font from ", None, True, [AstValNumber, AstValString], True), 
            CbParam("hyphenate", "set to false to avoid splitting end of line words", True, False, AstValBool, True),
        ] + makeBoxParams(),
        "text", 1, None,
        funcFormat
        ))


    functionList.append(CbFunc("quote", "Quote format text", [
            CbParam("cite", "citation credit (author); only used for quote type", "", False, AstValString, True),
            CbParam("style", "style variant", "default", False, AstValString, True),     
            CbParam("font", "font id previously set with defineFont()", None, True, AstValString, True),    
            CbParam("size", "size of font", None, True, [AstValNumber, AstValString], True), 

        ] + makeBoxParams(),
        "text", 1, None,
        funcQuote
        ))


    functionList.append(CbFunc("block", "Keep together as a block", [
            CbParam("align", "alignment of minipage block", "t", False, ["t", "b", "c"], True),
        ],
        "text", 1, None,
        funcBlock
        ))


    functionList.append(CbFunc("modifyText", "modify text", [
            CbParam("case", "force case to uppercase, titlecase, or sentence case? [upper|title|sentence]", None, True, ["lower", "upper", "title", "sentence"], True),
        ],
        "text", 1, None,
        funcModifyText
        ))
    #---------------------------------------------------------------------------











    #---------------------------------------------------------------------------
    functionList.append(CbFunc("symbol", "Insert symbol (unicode/icon) text", [
            CbParam("id", "Symbol id", None, False, AstValString, True),
            CbParam("color", "color", None, True, AstValString, True),
            CbParam("size", "size", None, True, AstValString, True),
        ],
        "text", None, None,
        funcSymbol
        ))


    functionList.append(CbFunc("divider", "divider insert", [
            CbParam("id", "Divider id", None, True, AstValString, True),
        ],
        "text", None, None,
        funcDivider
        ))
    #---------------------------------------------------------------------------









    #---------------------------------------------------------------------------
    functionList.append(CbFunc("otherwise", "Text saying otherwise", [
        ],
        "text", None, "otherwise",
        funcSimpleText
        ))

    functionList.append(CbFunc("leave", "Text saying to leave because there is nothing for you here", [
            CbParam("reason", "Reason player should leave", None, True, AstValString, True),
            CbParam("otherwise", "Show a divider and otherwise", True, True, AstValBool, True),
        ],
        "text", None, None,
        funcLeaveText
        ))
    #---------------------------------------------------------------------------






    #---------------------------------------------------------------------------
    functionList.append(CbFunc("print", "print value", [
            CbParam("expression", "Expression to print", None, False, None, True),
        ],
        "text", None, None,
        funcPrint
        ))

    functionList.append(CbFunc("debug", "debug print value", [
            CbParam("expression", "Expression to print in debug mode", None, False, None, True),
        ],
        "text", None, None,
        funcDebug
        ))

    functionList.append(CbFunc("break", "Add a page/column break", [
            CbParam("type", "Break type", "", False, ["column", "page"], True),
        ],
        "text", None, None,
        funcBreak
        ))
    #---------------------------------------------------------------------------






    #---------------------------------------------------------------------------
    functionList.append(CbFunc("advanceTime", "Instruct player to advance clock by some clicks", [
            CbParam("time", "Duration (in minutes)", 60, False, AstValNumber, True),
            CbParam("box", "Put this text in a standalone box", "default", True, [AstValString], True),
        ],
        "text", None, None,
        funcAdvanceTime
        ))

    functionList.append(CbFunc("timeHere", "Show lead time here (instead of normally at start or end)", [
        ],
        "text", None, None,
        funcTimeHere
        ))

    functionList.append(CbFunc("beforeDay", "Text saying if before day", [
            CbParam("day", "Day number", None, False, AstValNumber, True),
        ],
        "text", None, "before",
        funcDayTest
        ))
    # now blocking the use of afterDay as it is textually ambiguous, in favor of onAfter
    functionList.append(CbFunc("afterDay", "Text saying if after day", [
            CbParam("day", "Day number", None, False, AstValNumber, True),
        ],
        "text", None, "after",
        funcDayTest
        ))
    functionList.append(CbFunc("onAfterDay", "Text saying if on or after day", [
            CbParam("day", "Day number", None, False, AstValNumber, True),
        ],
        "text", None, "onAfter",
        funcDayTest
        ))
    functionList.append(CbFunc("onDay", "Text saying if on day", [
            CbParam("day", "Day number", None, False, AstValNumber, True),
        ],
        "text", None, "on",
        funcDayTest
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    # new function to generate text saying the start and end times of the day, and what markers are needed
    functionList.append(CbFunc("dayInstructions", "Generate instructions for the day", [
            CbParam("day", "Number of the day", None, False, AstValNumber, True),
            CbParam("when", "From [start|end]", None, False, ["start", "end"], True),
        ],
        "text", None, None,
        funcDayInstructions
        ))
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    # new function to generate text saying the start and end times of the day, and what markers are needed
    functionList.append(CbFunc("blurbStop", "Add some instructions to stop", [
            CbParam("type", "The stop blurb type", None, False, ["dayStart", "dayStartEvent", "dayEnd", "nextDay", "nightStart", "nightEnd", "conclusion", "questions", "questionPause", "resolvePause", "solution", "leads", "documents", "hints", "end", "begin", "noMore", "dayStartThenConclusion"], True),
            CbParam("day", "Number of the day", -1, False, AstValNumber, True),
            CbParam("rest", "Suggest player takes a rest?", None, True, AstValBool, True),
            CbParam("text", "Alternate text", None, True, AstValString, True),
            CbParam("goLead", "id of lead to go to", None, True, AstValString, True),
            #CbParam("breakBefore", "Page break before this entry", None, True, AstValBool, True),     
            #CbParam("breakAfter", "Page break after this entry", None, True, AstValBool, True),           
        ],
        "text", None, None,
        funcBlurbStop
        ))


    functionList.append(CbFunc("blurbDay", "Say some stuff about the day", [
            CbParam("day", "Number of the day", None, False, AstValNumber, True),
            CbParam("type", "What type of info to show", "", False, ["dayTimeStart", "dayDateStart", "dayDateNoYear", "calendar", "timeStart"], True),
        ] + makeBoxParams(),
        "text", None, None,
        funcBlurbDay
        ))


    functionList.append(CbFunc("blurb", "Add some text", [
            CbParam("type", "The blurb type", None, False, AstValString, True),
        ] + makeBoxParams(),
        "text", None, None,
        funcBlurb
        ))
    #---------------------------------------------------------------------------











    #---------------------------------------------------------------------------
    functionList.append(CbFunc("logicSuggests", "Add mindmap node", [
            CbParam("target", "Lead id", None, False, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "suggests", "direction": "ab"},
        funcLogic
        ))
    functionList.append(CbFunc("logicSuggestedBy", "Add mindmap node", [
            CbParam("source", "Lead id", None, False, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "suggests", "direction": "ba"},
        funcLogic
        ))
    functionList.append(CbFunc("logicImplies", "Add mindmap node", [
            CbParam("target", "Lead id", None, False, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "implies", "direction": "ab"},
        funcLogic
        ))
    functionList.append(CbFunc("logicImpliedBy", "Add mindmap node", [
            CbParam("source", "Lead id", None, False, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "implies", "direction": "ba"},
        funcLogic
        ))
    functionList.append(CbFunc("logicIrrelevant", "Add mindmap node", [
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "irrelevant", "direction": None},
        funcLogic
        ))
    functionList.append(CbFunc("logicFollows", "Add mindmap node", [
            CbParam("target", "Lead id", None, False, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "follows", "direction": "ab"},
        funcLogic
        ))
    functionList.append(CbFunc("logicFollowedBy", "Add mindmap node", [
            CbParam("source", "Lead id", None, False, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "follows", "direction": "ba"},
        funcLogic
        ))
    functionList.append(CbFunc("logic", "Add mindmap node", [
        # generic logic link
            CbParam("target", "target lead or concept", "", False, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "concept", "direction": "ab"},
        funcLogic
        ))
    functionList.append(CbFunc("logicConcept", "Add mindmap node", [
        # generic logic link
            CbParam("target", "target lead or concept", "", False, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "concept", "direction": "ab"},
        funcLogic
        ))

    functionList.append(CbFunc("logicProceed", "Add mindmap node", [
        # generic logic link
            CbParam("target", "target lead or concept", None, True, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "proceed", "direction": "ab"},
        funcLogic
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("authorNote", "An author note which is not shown in normal case book build only in author report", [
            CbParam("label", "label for note for author report", "", False, AstValString, True),
        ],
        "text", "any", None,
        funcAuthorNote
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("pageStyle", "set the current page style", [
            CbParam("style", "Page style to use for the page (use 'empty' to hide footer)", None, False, AstValString, True),
        ],
        "text", None, None,
        funcPageStyle
        ))
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    functionList.append(CbFunc("dropCaps", "Drop cap effect for some text (make first letter BIG)", [
            CbParam("style", "drop cap style", "letter", False, ["letter","word", "none", "bold"], True),
            CbParam("lines", "height in lines", DefCbRenderDefault_DropCapLineSize, False, AstValNumber, True),
            CbParam("multi", "how to handle multiple paragraphs", DefCbRenderDefault_DropCapProtectStyle, False, ["none", "wrap", "gap"], True),
            CbParam("fIndent", "findent", 0.25, True, AstValNumber, True),
            CbParam("nIndent", "nIndent", 0.75, True, AstValNumber, True),
            CbParam("lHang", "lHang", 0, True, AstValNumber, True),
        ],
        "text", 1, None,
        funcDropCaps
        ))


    functionList.append(CbFunc("effectUp", "text effect that makes first letter bold and bigger, and remaining words uppercase", [
            CbParam("text", "the text to operate one", None, False, AstValString, True),            
            CbParam("enabled", "set to false to disable", True, False, AstValBool, True),
            CbParam("style", "optional style (not supported yet)", None, True, AstValString, True),
        ],
        "text", None, None,
        funcEffectUp
        ))
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    functionList.append(CbFunc("lipsum", "Add some test text", [
            CbParam("start", "starting paragraph index", 1, False, AstValNumber, True),
            CbParam("end", "ending paragraph index", -1, False, AstValNumber, True),
            CbParam("length", "maxlimum length in characters (0 for no limit)", 0, False, AstValNumber, True),
        ],
        "text", None, None,
        funcLipsum
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("marginNote", "Add a short bit of text to the left or right margin; note that this doesn't seem to work right currently; left margins not showing?", [
            CbParam("pos", "position of note", "left", False, ["left","right"], True),
        ],
        "text", 1, None,
        funcMarginNote
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("designateFile", "Designate an uploaded file (local or shared) to be copied into certain builds", [
            CbParam("path", "Relative path to uploaded file", None, False, AstValString, True),
            CbParam("tag", "Tag which says how to use the file", "publish", False, ["debug", "publish"], True),
            CbParam("rename", "Rename copied version of file when it is moved to publish set, etc.", "", False, AstValString, True),
        ],
        "text", None, None,
        funcDesignateFile
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("headerHere", "Signify that the lead header should go HERE (instead of at top of lead)", [
        ],
        "text", None, None,
        funcHeaderHere
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("calendar", "Draw a calendar of one or more months", [
            CbParam("start", "Start date", None, False, AstValString, True),
            CbParam("end", "End date", None, False, AstValString, True),
            CbParam("style", "style of calendar (not supported yet, but eventually small and large)", "", False, AstValString, True),
            CbParam("strikeStart", "date strikes start", "", False, AstValString, True),
            CbParam("strikeEnd", "date strikes end", "", False, AstValString, True),
            CbParam("circle", "date to circle", "", False, AstValString, True),
        ] + makeBoxParams(),
        "text", None, None,
        funcCalendar
        ))
    
    
    functionList.append(CbFunc("date", "format a date into a nice string", [
            CbParam("date", "Date in form mm/dd/yyyy", None, False, AstValString, True),
            CbParam("year", "should show year?", True, False, AstValBool, True),
        ],
        "text", None, None,
        funcDate
        ))

    functionList.append(CbFunc("dayDate", "format a day's date into a nice string", [
            CbParam("day", "Day number", None, False, AstValNumber, True),
            CbParam("type", "What type of info to show", "dayDate", False, ["dayTimeStart", "dayDate", "dayDateNoYear", "mmddyyyy", "dayOfWeek", "timeStart"], True),
        ],
        "text", None, None,
        funcDayDate
        ))

    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    functionList.append(CbFunc("dither", "Return cached path to ditherized version of an image file, ditherizing it the first time", [
            CbParam("path", "Image file path", None, False, AstValString, True),
            CbParam("mode", "Ditherization mode", "bw", False, AstValString, True),
        ],
        "text", None, None,
        funcDither
        ))

    functionList.append(CbFunc("effect", "Build and cache (add to game file list) an effect version of image", [
            CbParam("path", "Image file path", None, False, AstValString, True),
            CbParam("effect", "Effect key", None, False, AstValString, True),
        ],
        "text", None, None,
        funcImageEffect
        ))


    functionList.append(CbFunc("flatAlpha", "Return cached path to alpha flattened (white background) version of an image file", [
            CbParam("path", "Image file path", None, False, AstValString, True),
        ],
        "text", None, None,
        funcFlatAlpha
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    # old form func
    functionList.append(CbFunc("form", "Form field insert", [
            CbParam("type", "Form field type", None, False, ["short", "mini", "score", "long", "multiline", "multipleChoice", "checkAll"], True),
            CbParam("size", "Size of field", None, True, AstValNumber, True),
            CbParam("choices", "List of choices, separated by | character", None, True, AstValString, True),
        ],
        "text", None, None,
        funcForm
        ))
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    # new form funcs
    functionList.append(CbFunc("formText", "Multi line text form field", [
            CbParam("lines", "Number of lines", 2, True, AstValNumber, True),
            CbParam("width", "Width of form line", None, True, [AstValNumber, AstValString], True),
            CbParam("pt", "Point thickness of line (default 0.5 for 0.5pt)", 0.5, False, AstValNumber, True),
        ],
        "text", None, None,
        funcFormText
        ))
    functionList.append(CbFunc("formLine", "Single line form field", [
            CbParam("margin", "Margin to subtract from remainder of length on current line", '1in', False, [AstValNumber, AstValString], True),
            CbParam("pt", "Point thickness of line (default 1 for 1pt)", 1, False, AstValNumber, True),
            CbParam("after", "Text to display at end of line", None, True, AstValString, True),
        ],
        "text", None, None,
        funcFormLine
        ))
    functionList.append(CbFunc("formShort", "Short line form field", [
            CbParam("width", "Width of short form", "2in", True, [AstValNumber, AstValString], True),
            CbParam("pt", "Point thickness of line (default 1 for 1pt)", 1, False, AstValNumber, True),
            CbParam("after", "Text to display at end of line", None, True, AstValString, True),
        ],
        "text", None, None,
        funcFormShort
        ))
    functionList.append(CbFunc("formCheckList", "Show choices in a list with checkboxes", [
            CbParam("choices", "Choices separated by | character", None, False, AstValString, True),
            CbParam("other", "Include an other option at end?", False, False, AstValBool, True),
        ],
        "text", None, None,
        funcFormCheckList
        ))
    functionList.append(CbFunc("formRadioList", "Show choices in a list with checkboxes", [
            CbParam("choices", "Choices separated by | character", None, False, AstValString, True),
            CbParam("other", "Include an other option at end?", False, False, AstValBool, True),
        ],
        "text", None, None,
        funcFormRadioList
        ))
    functionList.append(CbFunc("formNumber", "Short number line or box", [
            CbParam("width", "Width of box", "1cm", True, [AstValNumber, AstValString], True),
            CbParam("after", "Text to display at end of line", None, True, AstValString, True),
        ],
        "text", None, None,
        funcFormNumber
        ))
    #---------------------------------------------------------------------------






    #---------------------------------------------------------------------------
    functionList.append(CbFunc("newsPaper", "a newspaper page", [
					CbParam("style", "style variant", "nyTimes", False, AstValString, True),   
					CbParam("day", "day number", None, True, AstValNumber, True),  
					CbParam("date", "date as string", None, True, AstValString, True),  
					CbParam("dateString", "arbitrary date string", None, True, AstValString, True),  
					CbParam("dateStringExtra", "arbitrary date string to add to date", None, True, AstValString, True),
                    CbParam("columns", "number of columns", None, True, AstValNumber, True),  
					CbParam("raggedColumns", "disable column balancing?", None, True, AstValBool, True),
					CbParam("priceString", "price string (right hand margin)", None, True, AstValString, True),
					CbParam("issueString", "issue string (left hand margin)", None, True, AstValString, True),
					CbParam("bannerPath", "Relative path to file image", None, True, AstValString, True),
                    CbParam("bannerLines", "Put issue text etc inside banner lines below banner? If false they will be set above the banner bottom margin", True, False, AstValBool, True),
					CbParam("font", "font id", None, True, AstValString, True),  
					CbParam("fontSize", "size in points", None, True, AstValString, True),  
					CbParam("landscape", "display paper in landscape mode?", False, False, AstValBool, True),
                    CbParam("parSpaceHead", "Change paragraph spacing for headline", 0.4, False, AstValNumber, True), # used to be 0.4
                    CbParam("parSpaceBody", "Change paragraph spacing for body of article", 0.6, False, AstValNumber, True), # used to be 0.4
                    CbParam("lineSpace", "Change line spacing", 1.2, False, AstValNumber, True),
					CbParam("articleStyle", "article style variant", None, True, AstValString, True),   
					CbParam("headlineStyle", "headline style variant", None, True, AstValString, True), 
					CbParam("bylineStyle", "byline style variant", None, True, AstValString, True), 
                    CbParam("dropCaps", "Drop Caps style for articles", None, True, ["letter","word", "none", "bold"], True),
                    CbParam("dropCapsMulti", "how to handle multiple paragraphs", DefCbRenderDefault_DropCapProtectStyleNewspaper, False, ["none", "wrap", "gap"], True),
                    CbParam("indent", "indent paragraphs?", True, False, AstValBool, True),
                    CbParam("block", "require this all articles fit in a single (column) without splitting contents over a column", None, True, AstValBool, True),
                    CbParam("divider", "true to show divider at end of article, or specifiy divider id", None, True, [AstValBool, AstValString], True),
                    CbParam("effectsOn", "use in interior commands like effectUp", None, True, AstValBool, True),
        ],
        "text", 1, None,
        funcNewsPaper
        ))

    functionList.append(CbFunc("newsBannerBox", "banner bax for right hand margin", [
        ],
        "text", 1, None,
        funcNewsBannerBox
        ))

    functionList.append(CbFunc("newsGroup", "group of articles", [
					CbParam("columns", "number of columns", 3, False, AstValNumber, True),  
					CbParam("raggedColumns", "disable column balancing?", None, True, AstValBool, True),
        ],
        "text", 1, None,
        funcNewsGroup
        ))

    functionList.append(CbFunc("newsArticle", "an article", [
            CbParam("style", "style variant", None, True, AstValString, True),
            CbParam("block", "require this entire article to fit in a single block (column) together, dont split it", None, True, AstValBool, True),
            CbParam("dropCaps", "Drop Caps style", None, True, ["letter","word"], True),  
			CbParam("headline", "headline text", None, True, AstValString, True), 
			CbParam("byline", "byline text", None, True, AstValString, True),             
			CbParam("headlineStyle", "headline style variant", None, True, AstValString, True), 
			CbParam("bylineStyle", "byline style variant", None, True, AstValString, True), 
            CbParam("divider", "true to show divider at end of article, or specifiy divider id", None, True,  [AstValBool, AstValString], True),
            CbParam("effectsOn", "use in interior commands like effectUp", None, True, AstValBool, True),
            CbParam("size", "base font size", None, True, [AstValString,AstValNumber], True),
        ],
        "text", 1, None,
        funcNewsArticle
        ))


    functionList.append(CbFunc("newsHeadline", "headline for article", [
            CbParam("style", "style variant", "Large", False, AstValString, True),  
            CbParam("fit", "should force to fit on one line?", False, False, AstValBool, True),
            CbParam("bold", "bold text?", None, True, AstValBool, True),
            CbParam("underline", "underline text?", None, True, AstValBool, True),
            CbParam("italic", "italic text?", None, True, AstValBool, True),
            CbParam("case", "force case to uppercase, titlecase, or sentence case? [upper|title|sentence]", None, True, ["lower", "upper", "title", "sentence"], True),
        ],
        "text", 1, None,
        funcNewsHeadline
        ))

    functionList.append(CbFunc("newsByLine", "byline for article", [
            CbParam("style", "style variant", "script", False, AstValString, True),  
            CbParam("fit", "should force to fit on one line?", False, False, AstValBool, True),
            CbParam("bold", "bold text?", True, False, AstValBool, True),
        ],
        "text", 1, None,
        funcNewsByLine
        ))

    functionList.append(CbFunc("newsRule", "an image for an article", [
            CbParam("style", "style variant", "nytimes", False, AstValString, True),  
        ],
        "text", None, None,
        funcNewsRule
        ))

    functionList.append(CbFunc("newsEndLine", "helper to jsut say continued on Page X", [
            CbParam("text", "text string (e.g. Continued on Page Four)", None, True, AstValString, True),  
        ],
        "text", None, None,
        funcNewsEndLine
        ))
    #---------------------------------------------------------------------------





    #---------------------------------------------------------------------------
    # ATTN: we are deprecating use of fingerPrint() in favor of $image($fingerprintPath()..)
    functionList.append(CbFunc("fingerPrint", "insert a fingerprint image (DEPRECATED; instead use $image($fingerprintPath(..)))", [
					CbParam("id", "lead id", None, False, AstValString, True), 
					CbParam("finger", "finger id in form L# or R# where # is finger number from 1-5", None, False, AstValString, True), 
					CbParam("impression", "the impression id (1=rolled clean in book, 2=dirtyslightlydif)", "2", False, AstValString, True),   
					CbParam("style", "style variant", "", False, AstValString, True),   
                    CbParam("width", "Width (fraction where 0.5 is half page width) or string ending in [in|cm]", "1in", False, [AstValNumber, AstValString], True),
                    CbParam("align", "Alignment", None, True, ["left", "center", "right"], True), 
                    CbParam("showId", "show the person ID?", False, False, AstValBool, True),   
                    CbParam("caption", "Alternative caption when not showing id", None, True, AstValString, True),  
        ],
        "text", None, None,
        funcFingerprint
        ))

    functionList.append(CbFunc("fingerPrintSet", "insert a fingerprint image", [
					CbParam("id", "lead id", None, False, AstValString, True), 
					CbParam("style", "style variant", "", False, AstValString, True),   
                    CbParam("showId", "show the person ID?", False, False, AstValBool, True),  
                    CbParam("caption", "Alternative caption when not showing id", None, True, AstValString, True),  
        ],
        "text", None, None,
        funcFingerprintSet
        ))


    functionList.append(CbFunc("fingerPrintPath", "get the path to the image of a fingerprint, so it can be used in an $image() function call", [
					CbParam("id", "lead id", None, False, AstValString, True), 
					CbParam("finger", "finger id in form L# or R# where # is finger number from 1-5", None, False, AstValString, True), 
					CbParam("impression", "the impression id (1=rolled clean in book, 2=dirtyslightlydif)", "2", False, AstValString, True),   
        ],
        "text", None, None,
        funcFingerprintPath
        ))
    
    # ATTN: later add features to allow us to degrade the images more.
    #---------------------------------------------------------------------------





    #---------------------------------------------------------------------------
    # tracks in the case log
    functionList.append(CbFunc("setTrack", "set track value", [
					CbParam("id", "track id (A,B,C,D)", None, False, AstValString, True), 
					CbParam("val", "value to set", "", False, [AstValString,AstValNumber], True),   
					CbParam("min", "min value", None, True, AstValNumber, True),   
					CbParam("max", "max value", None, True, AstValNumber, True),   
        ],
        "text", None, "set",
        funcAdjustTrack
        ))


    functionList.append(CbFunc("adjustTrack", "adjust track value", [
					CbParam("id", "track id (A,B,C,D)", None, False, AstValString, True), 
					CbParam("val", "value to adust", "", False, AstValNumber, True),   
					CbParam("min", "min value", None, True, AstValNumber, True),   
					CbParam("max", "max value", None, True, AstValNumber, True),   
        ],
        "text", None, "modify",
        funcAdjustTrack
        ))
    #---------------------------------------------------------------------------






    #---------------------------------------------------------------------------
    # fonts


    functionList.append(CbFunc("defineFont", "Defines a font", [
            CbParam("id", "The id that will refer to the font", None, False, AstValString, True),
            CbParam("path", "Path to the font within the shared fonts dir", "", False, AstValString, True),
            #
            CbParam("size", "base font size (optional; prefer use of scale)", None, True, [AstValString,AstValNumber], True),
            CbParam("scale", "scale the font, use number from 0.1 to 10.0", None, True, AstValNumber, True),
            CbParam("color", "override default color with color name see https://www.latextemplates.com/svgnames-colors)", None, True, AstValString, True),
            CbParam("hyphenate", "set to true to let latex hyphenate and split long words at end of lines; defaults false)", False, False, AstValBool, True),
            CbParam("monoSpace", "set to true to force monospacing of font; defaults false)", False, False, AstValBool, True),
            CbParam("ignoreDupe", "if true this will be ignored if a font with this id already exists; otherwise an error will be thrown", False, False, AstValBool, True),
        ],
        None, None, None,
        funcDefineFont
        ))

    functionList.append(CbFunc("debugFonts", "do a test of all available fonts", [
            CbParam("size", "base font size", None, True, [AstValString,AstValNumber], True),
            CbParam("scale", "scale the font, use number from 0.1 to 10.0", None, True, AstValNumber, True),
            CbParam("color", "override default color with color name", None, True, AstValString, True),
            CbParam("hyphenate", "set to false to avoid splitting end of line words", True, False, AstValBool, True),
            CbParam("monoSpace", "set to true to force monospacing of font; defaults false)", False, False, AstValBool, True),
        ],
        "text", 1, "set",
        funcDebugFonts
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    functionList.append(CbFunc("imageBehind", "put an image behind text or other contents", [
            CbParam("path", "Relative path to file image", None, False, AstValString, True),
            CbParam("width", "Width (fraction where 0.5 is half page width) or string ending in [in|cm]", 1, False, [AstValNumber, AstValString], True),
            CbParam("opacity", "fraction (0 to 1)", 1.0, False, AstValNumber, True),
            CbParam("padding", "padding fraction (default 0.025)", 0.025, False, AstValNumber, True),
            CbParam("height", "Force height (fraction of page; leave blank to match text", None, True, AstValNumber, True),
            CbParam("scale", "Scaling mode ", "stretch", True, ["zoom", "stretch", "image"], True),
            CbParam("align", "Alignment", "center", False, ["center","left"], True),
            CbParam("shadow", "Add drop shadow to image background?", False, False, AstValBool, True),
            #
            CbParam("caption", "caption to show under image", None, True, AstValString, True),
            CbParam("captionPos", "Position for caption", "top", False, ["top", "bottom"], True),
            CbParam("captionSize", "Size of caption; default='normal'", None, True, AstValString, True),
        ],
        "text", 1, None,
        funcImageBehind
        ))


    functionList.append(CbFunc("imageMask", "mask text with an image pair; useful for things like a burned note effect", [
            CbParam("path", "Relative path to file image", None, False, AstValString, True),
            CbParam("width", "Width (fraction where 0.5 is half page width) or string ending in [in|cm]", 1, False, [AstValNumber, AstValString], True),
            CbParam("align", "Alignment", "center", False, ["center","left"], True),
            #
            CbParam("caption", "caption to show under image", None, True, AstValString, True),
            CbParam("captionPos", "Position for caption", "bottom", False, ["top", "bottom"], True),
            CbParam("captionSize", "Size of caption (default='normal')", None, True, AstValString, True),
        ],
        "text", 1, None,
        funcImageMask
        ))


    functionList.append(CbFunc("imageOverlay", "put an image in fromt of text or other contents", [
            CbParam("path", "Relative path to file image", None, False, AstValString, True),
            CbParam("width", "Width (fraction where 0.5 is half page width) or string ending in [in|cm]", 1, False, [AstValNumber, AstValString], True),
            CbParam("height", "Height (fraction of page or string ending in [in|cm]", None, False, [AstValNumber, AstValString], True),
            CbParam("opacity", "fraction (0 to 1)", 1.0, False, AstValNumber, True),

            CbParam("align", "Alignment", "center", False, ["center","left"], True),
            #
            CbParam("caption", "caption to show under image", None, True, AstValString, True),
            CbParam("captionPos", "Position for caption", "top", False, ["top", "bottom"], True),
            CbParam("captionSize", "Size of caption; default='normal'", None, True, AstValString, True),
        ],
        "text", 1, None,
        funcImageOverlay
        ))
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    functionList.append(CbFunc("cipher", "generate some cipher text", [
            CbParam("method", "Name of cipher method", None, False, AstValString, True),
            CbParam("key", "The cipher key to use", None, True, [AstValString, AstValNumber], True),
            CbParam("debug", "Debug by showing info about the cipher at top in plaintext.", False, False, AstValBool, True),  
            CbParam("removePunctuation", "Remove punctuation? (spells out periods as 'stop')", False, False, AstValBool, True),
            CbParam("spellDigits", "Change digits to spelled version", False, False, AstValBool, True),            
            CbParam("format", "Format the message nicely when appropriate", True, False, AstValBool, True),   
            CbParam("case", "convert to upper or lower case", None, True, ["lower", "upper", "title", "sentence"], True),   
        ],
        "text", 1, None,
        funcCipher
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    functionList.append(CbFunc("redact", "redact some text so it is unreadable", [
            CbParam("text", "Text to redact if you don't want to put it in a target block", None, True, AstValString, True),  
        ],
        "text", 1, None,
        funcRedact
        ))

    functionList.append(CbFunc("censor", "censors a small section of text so it is unreadable", [
            CbParam("text", "Text to redact if you don't want to put it in a target block", None, False, AstValString, True),  
        ],
        "text", None, None,
        funcCensor
        ))
    #---------------------------------------------------------------------------








    #---------------------------------------------------------------------------
    functionList.append(CbFunc("defineFunc", "define a new function", [
            CbParam("id", "Id name of the function", None, False, AstValIdentifier, False),
            CbParam("params", "List of parameters", None, True, AstValList, True),
            CbParam("description", "description of function", None, True, AstValString, True),
            CbParam("customData", "customData set during function definition", None, True, None, True),
        ],
        "text", 1, None,
        funcDefineFunc
        ))

    functionList.append(CbFunc("renderFunctionTargets", "render function targets at this location", [
        ],
        "text", None, None,
        funcRenderTargetsInUserFunction
        ))

    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("vspace", "add or remove vertical space", [
            CbParam("amount", "postive to add space, negative to remove; should be formatted as a number and then 'em' or 'pt' (eg. -5.5pt)", None, False, AstValString, False),
            CbParam("force", "force the space and dont allow latex to tweak", False, False, AstValBool, True),
        ],
        "text", None, None,
        funcVspace
        ))
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    functionList.append(CbFunc("formatList", "format a (numbered) list", [
            CbParam("indent", "Indent the paragraphs?", True, False, AstValBool, False),
            CbParam("divider", "Divider to use between items", None, True, AstValString, True),
        ],
        "text", 1, None,
        funcFormatList
        ))
    #---------------------------------------------------------------------------







    #---------------------------------------------------------------------------
    # and finally return the function list
    return functionList
    #---------------------------------------------------------------------------




















































# ---------------------------------------------------------------------------
# 
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def funcApplyEntryOptions(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # This is a "function" that gets called to configure entries; it is our one unusual function in that it is invoked like $() on an entry

    if (rmode != DefRmodeRun):
        raise makeJriException("In function ({}) but in rmode!= run; do not know what to do.".format(funcName), astloc)

    doFuncConfigureEntry(True, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets)
    return AstValNull(astloc, entryp)



def funcDeclareVar(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # declare a variable

    # args
    varName = args["var"].getWrapped()
    description = args["desc"].getWrapped()
    value = args["val"]
    #
    env.declareEnvVar(astloc, varName, description, value, False)



def funcDeclareConst(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # declare a constant

    # args
    varName = args["var"].getWrapped()
    description = args["desc"].getWrapped()
    value = args["val"]
    #
    env.declareEnvVar(astloc, varName, description, value, True)



def funcSet(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # set a variable

    # args
    varName = args["var"].getWrapped()
    value = args["val"]
    #
    env.setEnvValue(astloc, varName, value, True)




def funcSetDefault(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # set a variable
    # args
    varName = args["var"].getWrapped()
    value = args["val"]
    #
    curValue = env.getEnvValue(astloc, varName, None)
    if (curValue==None):
        # doesn't exist OR is None, so we set it to value
        env.setCreateEnvValue(astloc, varName, value, True)


def funcGetDefault(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # set a variable

    # args
    varName = args["var"].getWrapped()
    value = args["val"].getWrapped()
    #
    return env.getEnvValue(astloc, varName, value)





def funcDefineTag(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # declare a tag

    tagId = args["tagId"].getWrapped()
    tagDeadline = args["deadline"].getWrapped()
    tagLabel = args["label"].getWrapped()
    tagLocation = args["location"].getWrapped()
    tagObfuscatedLabel = args["obfuscatedLabel"].getWrapped()
    if (tagObfuscatedLabel=="label"):
        tagObfuscatedLabel = tagLabel
    tagDependencyString = args["dependencies"].getWrapped()

    tagManager = env.getTagManager()
    tagManager.declareTag(env, tagId, tagDeadline, tagLabel, tagLocation, tagObfuscatedLabel, tagDependencyString, True, astloc, "Defining tag", leadp, False)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def funcDefineConcept(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # declare a concept (like a tag)

    id = args["id"].getWrapped()
    label = args["label"].getWrapped()

    conceptManager = env.getConceptManager()
    conceptManager.declareConcept(env, id, label, True, astloc, "Defining concept", leadp)
# ---------------------------------------------------------------------------









# ---------------------------------------------------------------------------
def funcToc(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # generate table of contents

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    renderer = env.getRenderer()

    # args
    columns = args["columns"].getWrapped()
    if (columns is None):
        # auto columns
        reportMode = env.getReportMode()
        if (reportMode):
            columns = 1
        else:
            if (renderer.isNarrowPaperSize()):
                columns = 1
            else:
                columns = 2

    latex = ""

    # extra space below heading? NO
    if (False):
        latex += "~\n"

    if (columns is not None) and (columns>1):
        latex += "\\begin{multicols*}{" + str(columns) + "}\n"

    # wrap this in a "continued on next page" latex trick
    latex += renderer.breakWarnSecStart()
    #
    latex += '\n'
    latex += '\\addvspace{8pt}\n'
    latex += '\\tableofcontents\n'
    #
    latex += renderer.breakWarnSecEnd()
    
    if (columns is not None) and (columns>1):
        latex += "\\end{multicols*}\n"

    return vouchForLatexString(latex, False)



def funcBlurbCoverPage(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Create a nice cover page snippet which includes title and author from options, as well as any other user custom text/image

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    info = env.getEnvValueUnwrapped(None, "info", None)
    #
    namestr = getUnsafeDictValueAsString(env, info, "name", "n/a")
    titleStr = getUnsafeDictValueAsString(env,info, "title", "n/a")
    subtitleStr = getUnsafeDictValueAsString(env,info, "subtitle", "")
    authorsStr = getUnsafeDictValueAsString(env,info, "authors", "n/a")
    versionStr = getUnsafeDictValueAsString(env,info, "version", "n/a")
    dateStr =  getUnsafeDictValueAsString(env,info, "versionDate", "n/a")
    status =  getUnsafeDictValueAsString(env,info, "status", "n/a")
    #
    difficulty =  getUnsafeDictValueAsNumber(env,info, "difficulty", None)
    if (difficulty is None):
        difficultyStr = "n/a"
    else:
        difficultyStr = str(difficulty)+ " out of 5"
    duration =  getUnsafeDictValueAsNumber(env,info, "duration", None)
    if (duration is None):
        durationStr = "n/a"
    else:
        durationStr = str(duration)+ " " + jrfuncs.singularPlurals(duration,_("hour"), _("hours"), None)
    #
    cautionsStr =  getUnsafeDictValueAsString(env, info, "cautions", "")
    summaryStr =  getUnsafeDictValueAsString(env, info, "summary", "n/a")
    extraCreditsStr =  getUnsafeDictValueAsString(env, info, "extraCredits", "")
    urlStr =  getUnsafeDictValueAsString(env, info, "url", "")
    copyrightStr =  getUnsafeDictValueAsString(env, info, "copyright", "")
    keywordsStr =  getUnsafeDictValueAsString(env, info, "keywords", "")
    #
    gameSystemStr =  getUnsafeDictValueAsString(env, info, "gameSystem", "n/a")
    gameDateStr =  getUnsafeDictValueAsString(env, info, "gameDate", "")
    #
    campaignNameStr =  getUnsafeDictValueAsString(env, info, "campaignName", "")
    campaignPositionStr =  getUnsafeDictValueAsString(env, info, "campaignPosition", "")

    # derived args
    versionStrWithDate = "v{} - {}".format(versionStr, dateStr)
    authorsStrNoEmails = re.sub(r'\s*\<[^\<\>]*\>','', authorsStr)
    #
    buildStr = convertEscapeUnsafePlainTextToLatex(env.getBuildString())
    typesetStr = convertEscapeUnsafePlainTextToLatex(env.getTypesetString(True))
    currentDateStr = convertEscapeUnsafePlainTextToLatex(jrfuncs.getNiceCurrentDateTime())
    compiledStr = currentDateStr + " / " + buildStr

    #
    latex = "\\begin{titlepage}\n\\begin{center}\n"
    latex += r"\vspace*{0in} \begin{Huge}\bfseries \textbf{" + titleStr + r"} \par\end{Huge}" + "\n"
    if (subtitleStr != ""):
        latex += r"\vspace*{0in} \begin{Large}\bfseries \textbf{" + subtitleStr + r"} \par\end{Large}" + "\n"

    reportMode = env.getReportMode()
    if (reportMode):
        latexLine = r"\begin{center}\begin{Huge}\bfseries {\textbf{" + "DEBUG REPORT" + r"} }\par\end{Huge}\end{center}"
        boxOptions = {
            "box": "hLines",
            "pos": "center",
            "isTextSafe": True,
            "textColor": "red",
        }
        latex += wrapInLatexBox(boxOptions, latexLine)

    latex += r"\vspace*{0in} \bfseries by \textbf{" + authorsStrNoEmails + r"} \par" + "\n"
    latex += r"\vspace*{0in} \bfseries \textbf{" + versionStrWithDate + r"} \par \vspace{0.1in} \par" + "\n"
    #

    # assemble result
    results = JrAstResultList()

    # add text so far
    results.flatAdd(vouchForLatexString(latex, False))

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    # part 1
    latex = ""
    latex += "\n\\end{center}\n\n"
    # summary
    latex += r"\textbf{" + _("SUMMARY") + "}\n\n"
    latex += summaryStr + "\n"
    #
    latex += r"\begin{flushleft}" + "\n"
    latex += r"\begin{itemize} \setlength\itemsep{-0.5em}" + "\n"
    #
    latex += blurbItemLatex(_("Author"), authorsStr)
    latex += blurbItemLatex(_("Status"), status)
    #
    if (extraCreditsStr!=""):
        latex += blurbItemLatex(_("Additional credits"), extraCreditsStr)
    if (urlStr!=""):
        latex += blurbItemLatex(_("Web"), r"\path{" + urlStr.replace("{-}","-") + "}")
    if (keywordsStr!=""):
        latex += blurbItemLatex(_("Keywords"), keywordsStr)
    if (copyrightStr!=""):
        copyrightStr = copyrightStr.replace("@","\\textcopyright")
        latex += blurbItemLatex(_("Copyright"), copyrightStr)    
    #
    latex += blurbItemLatex(_("Game system"), gameSystemStr)
    #
    if (campaignNameStr!=""):
        if (campaignPositionStr!=""):
            campaignLineStr = campaignNameStr + " (part {})".format(campaignPositionStr)
        else:
            campaignLineStr = campaignNameStr
        #
        latex += blurbItemLatex(_("Campaign"), campaignLineStr)

    if (gameDateStr!=""):
        latex += blurbItemLatex(_("Case date"), gameDateStr)
    #
    latex += blurbItemLatex(_("Difficulty"), difficultyStr)
    latex += blurbItemLatex(_("Playtime"), durationStr)
    if (cautionsStr!=""):
        latex += blurbItemLatex(_("Cautions"), cautionsStr)
    #latex += blurbItemLatex(_("Build tool"), buildStr)
    latex += blurbItemLatex(_("Compiled"), compiledStr)
    latex += blurbItemLatex(_("Typesetting"), typesetStr)
    #
    results.flatAdd(vouchForLatexString(latex, False))

    # part 2
    # deferred stats line
    deferredResult = CbDeferredBlockCaseStats(astloc, entryp, leadp)
    results.flatAdd(deferredResult)

    # part 4
    latex = ""
    latex += r"\end{itemize}" + "\n"
    latex += r"\end{flushleft}" + "\n"

    # finally
    latex += r"\end{titlepage}"+"\n\n"

    results.flatAdd(vouchForLatexString(latex, False))

    # return results
    return results







def funcInline(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # major function that creates a new lead that is jumped to from within another lead (branching choice)

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    inlineLinkArg = args["link"].getWrapped()
    backArg = args["back"].getWrapped()
    time = args["time"].getWrapped()
    timePos = args["timePos"].getWrapped()
    demerits = args["demerits"].getWrapped()
    helpful = jrfuncs.getDictValueOrDefault(customData, "helpful", None)
    whyText = args["why"].getWrapped()

    # renderer
    renderer = env.getRenderer()

    # ATTN: this has lots of redundant code with funcEvent stuff; merge the two eventually

    # calc label for inline lead
    [inlineLeadLabel, inlineMindMapLabel] = calcInlineLeadLabel(entryp, leadp, inlineLinkArg)
    # create lead early, so we can pass it into the contents as they run
    inlineLead = renderer.addLeadInline(inlineLeadLabel, leadp, astloc)

    # there are two ways to have a custom label, either through inlineMindMapLabel parsing above (based on a custom LABEL of the inlined lead), or a custom mindmap link label (mLabel)
    # in the former case, the custom label goes to the lead NODE; in the latter it goes to the link label
    mLabel = args["mLabel"].getWrapped()
    if (mLabel==""):
        mLabel = None

    # mindmap
    inlineLead.setMindMapLabel(inlineMindMapLabel)
    if (False) and (funcName=="inlineHint"):
        inlineLead.setMStyle("hint")
    else:
        inlineLead.setMStyle("inline")


    # for INLINE leads, a time not specified does NOT get default time, and is treated as as 0 (no time taken for this lead)
    if (time is None):
        time = 0
    else:
        pass

    inlineLead.setTime(time)
    inlineLead.setTimePos(timePos)

    # generate contents of the new INLINE lead that will get its own entry
    inlineResults = JrAstResultList()
    # contents of inline lead

    # now contents
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, inlineLead)
        inlineResults.flatAdd(targetRetv)

    # AFTER contents add demerits instruction
    if (demerits>0):
        # after, tell them to mark demerits
        upto = False
        if (whyText is not None) and (whyText!=""):
            whyLatex = renderer.convertMarkdownToLatexDontVouch(whyText, False, True)
        else:
            whyLatex = None
        #
        msgString = buildLatexMarkCheckboxSentence("demerit", demerits, True, False, helpful, "red", whyLatex, upto)
        #inlineResults.flatAdd(vouchForLatexString(latex,False))
        checkboxManager = env.getCheckboxManager()
        checkboxManager.recordCheckMarks(env, astloc, inlineLead, "demerit", demerits)
        #
        # wrap it and add symbol
        boxOptions = {
            "box": "default",
            "symbol": "checkbox",
            "textColor": "red",
            "isTextSafe": True,
        }
        inlineResults.flatAdd(vouchForLatexString(wrapInLatexBox(boxOptions, msgString), False))

    if (backArg):
        # add instructions to return here

        # time
        if (timePos is None) or (timePos=="") or (timePos=="end"):
            # add it to inlineResults here?
            optionTimeStyle = renderer.getOptionTimeStyle()
            if (optionTimeStyle!="header") or (timePos=="end"):
                deferredResult = CbDeferredBlockLeadTime(astloc, entryp, inlineLead)
                inlineResults.flatAdd(deferredResult)
                inlineLead.setTimePos("hidden")

        # add instructions to return here
        referencedLeadIdText = convertEscapeUnsafePlainTextToLatex(leadp.getLabelIdPreferAutoId())
        referencedLeadIdText = preventWordWrapOnLeadIdHypenLatex(referencedLeadIdText)
        #
        referencedLeadRid = leadp.getRid()
        optionPage = True
        if (optionPage):
            referencedLeadIdText+= r" (p.\pageref*{" + referencedLeadRid + r"})"
        latex = r"\hyperref[{" + referencedLeadRid + r"}]{" + referencedLeadIdText + r"}"
        latex = "\n" + _("Return to") + " " + latex + "."
        inlineResults.flatAdd(vouchForLatexString(latex, True))


    # mindmapper
    mindMapper = env.getMindManager()
    if (backArg):
        mindMapper.addLinkBetweenNodes(env, "inlines", mLabel, leadp, inlineLead)
    else:
        mindMapper.addLinkBetweenNodes(env, "inlineb", mLabel, leadp, inlineLead)


    # set contents of inline lead
    inlineLead.setBlockList(inlineResults)

    # add link to newly created lead inside ourselves
    results = JrAstResultList()
    #
    useBulletIfEmptyLine = True
    deferredResult = CbDeferredBlockFollowCase(astloc, entryp, leadp, _("go to") + " ", useBulletIfEmptyLine, True, True)
    results.flatAdd(deferredResult)
    #
    inlineLeadId = inlineLead.getAutoId()
    inlineLeadRef = makeLatexLinkToRid(inlineLead.getRid(), inlineLeadId, "onpage")
    textLine = "{}".format(inlineLeadRef)
    if (backArg):
        textLine += ", " + _("and then return here")
    #
    results.flatAdd(vouchForLatexString(textLine, True))

    # add period automatically IFF at end of line
    deferredResult = CbDeferredBlockEndLinePeriod(astloc, entryp, leadp, True)
    results.flatAdd(deferredResult)

    return results



def funcImage(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Embed an image into a pdf

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    renderer = env.getRenderer()

    # args
    path = args["path"].getWrapped()
    style = args["style"].getWrapped()
    width = args["width"].getWrapped()
    heightStr = args["height"].getWrapped()
    borderWidth = args["borderWidth"].getWrapped()
    padding = args["padding"].getWrapped()
    align = args["align"].getWrapped()
    caption = args["caption"].getWrapped()
    captionPos = args["captionPos"].getWrapped()
    captionSize = args["captionSize"].getWrapped()
    rule = args["rule"].getWrapped()
    optionWrapText = args["wrap"].getWrapped()
    #
    optionAllowMissingFile = renderer.getBypassErrorOnMissingImage(env)

    # style defaults
    styleDict = {
        "plain": {}, # just a placeholder in case author WANTS to set a do-nothing style parameter
        "frame": {"width": 0.95, "padding":2, "borderWidth":1}, # simple bordering with some padding; note author can override any of these options like width
        "bordered": {"width": 0.98, "padding":0, "borderWidth":1}, # simple bordering with no padding; note author can override any of these options like width
    }
    if (style is not None):
        defaultOptions = styleDict[style]
    else:
        defaultOptions = {}
    
    # override options from style if we aren't passed an explicit value; or fallback to defaults if not specified
    width = jrfuncs.getOverrideWithDictValueIfBlank(defaultOptions, "width", width)
    borderWidth = jrfuncs.getOverrideWithDictValueIfBlank(defaultOptions, "borderWidth", borderWidth, 0)
    padding = jrfuncs.getOverrideWithDictValueIfBlank(defaultOptions, "padding", padding, 0)
    align = jrfuncs.getOverrideWithDictValueIfBlank(defaultOptions, "align", align, "center")

    # kludge fixup for full width plus padding/border
    if (borderWidth + padding > 0) and ((width==1) or (width=="1") or (width=="1.0")):
        width = 0.95

    # find the image
    [imageFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), path, "Embedded image", "embedImage", leadp, env, astloc, optionAllowMissingFile)

    if (imageFullPath is None):
        # exception would already be raised if warnOnMissingImage is false
        imageLatex = convertEscapeUnsafePlainTextToLatex(warningText)
    else:
        # build latex includegraphics command
        imageLatex = generateImageEmbedLatex(env, imageFullPath, width, heightStr, borderWidth, padding, align, None, caption, captionPos, captionSize, rule, optionWrapText)

    #
    return vouchForLatexString(imageLatex, False)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def funcRefLead(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Refer to another lead
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    id = args["id"].getWrapped()
    style = args["style"].getWrapped()
    back = args["back"].getWrapped()
    #
    # assemble result
    results = JrAstResultList()
    #
    pretext = customData["pretext"]
    if (pretext is not None) and (pretext !=""):
        useBulletIfEmptyLine = True
        deferredResult = CbDeferredBlockFollowCase(astloc, entryp, leadp, pretext, useBulletIfEmptyLine, True, True)
        results.flatAdd(deferredResult)

    # make DEFERRED link to entry lead
    result = CbDeferredBlockRefLead(astloc, entryp, leadp, id, style)
    results.flatAdd(result)

    if (back):
        text = ", " + _("and then return back here")
        results.flatAdd(text)

    # mindmapper
    mindMapTypeStr = customData["mindMapType"]
    mindMapper = env.getMindManager()
    mindMapper.addLinkBetweenNodes(env, mindMapTypeStr, None, leadp, id)

    return results
    # ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
def funcEmbedLead(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Reuse a lead in a new place
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    id = args["id"].getWrapped()
    #
    # find entry they want to insert
    insertedEntry = env.findEntryByIdPath(id, astloc)
    if (insertedEntry is None):
        raise makeJriException("Could not find entry to insert ({})".format(id), astloc)
    
    # now our RESULT is the result of renderRunning that entry (should we pass entryp or insertedEntry; i dont think its used so it doesn't matter
    results = insertedEntry.renderRun(rmode, env, entryp, leadp, True)

    # mindmapper
    mindMapper = env.getMindManager()
    mindMapper.addLinkBetweenNodes(env, "embeds", None, leadp, entryp)

    return results
    # ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
def funcEmbedFile(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Embed another pdf inside
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    path = args["path"].getWrapped()
    pages = args["pages"].getWrapped()
    scale = args["scale"].getWrapped()
    toc = args["toc"].getWrapped()
    #pagenum = args["pagenum"].getWrapped()
    pagenum = True
    pageStyle = args["pageStyle"].getWrapped()

    # get image import helper, and try to find image first in game-specicific list then fallback to shared
    [fileFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListPdf(), path, "Including pdf file", "embedPdf", leadp, env, astloc, False)

    #safeFileFullPath = convertEscapeUnsafePlainTextToLatexMorePermissive(fileFullPath)
    safeFileFullPath = makeLatexSafeFilePath(fileFullPath)

    extras = []
    if (pages != ""):
        # see https://texdoc.org/serve/pdfpages/0
        #validPageRegex = r"(\d+)(\s*[,\-]\s*\d+])*"
        pagesOut = []
        pagesList = pages.split(",")
        for pagei in pagesList:
            pagei = pagei.strip()
            if (pagei!=""):
                pagesOut.append(pagei)
            if (re.match(r"[\d]*", pagei) is not None):
                continue
            elif (re.match(r"[\d]+\-[\d]+", pagei) is not None):
                continue
            elif (pagei=="-"):
                continue
            else:
                raise makeJriException("In func {}, pages arg must be a comma separated list of numbers, or - or #-# or {} for blank; see https://texdoc.org/serve/pdfpages/0; got ({}).".format(funcName, pages), astloc)
        #validPagesRegex = r"(\d+)(\s*[,\-]\s*\d+])*"
        #matches = re.match(validPagesRegex, pages)
        #if (matches is None):
        #    raise makeJriException("In func {}, pages arg must be a comma separated list of numbers; got ({}).".format(funcName, pages), astloc)
        extras.append("pages=" + pages)

    if (scale is not None):
        extras.append("scale=" + convertEscapeUnsafePlainTextToLatex(scale))

    # add page numbers; this might only work when scale < 0.95 or so
    if (pageStyle!=""):
        pageStyleLatex = generateLatexForPageStyle(pageStyle, astloc)
        extras.append("pagecommand={" + pageStyleLatex + "}")
    elif (pagenum):
        extras.append("pagecommand={}")
    else:
        # hide pagenumbers
        pass

    renderer = env.getRenderer()

    latex = ""

    if (toc is not None) and (toc!=""):
        tocSafeLatex = renderer.convertMarkdownToLatexDontVouch(toc, False, True)
        tocLine = r"\phantomsection\addcontentsline{toc}{section}{~~" + tocSafeLatex + "}" + "\n"
        latex += tocLine

    if (len(extras)==0):
        latex += r"\includepdf{" + safeFileFullPath + "}" + "\n"
    else:
        extrasJoined = ",".join(extras)
        latex += r"\includepdf[" + extrasJoined + "]{" + safeFileFullPath + "}" + "\n"
    #

    return vouchForLatexString(latex, False)
    # ---------------------------------------------------------------------------




















# ---------------------------------------------------------------------------
def funcAutoHint(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # autohint text tells players where to find tags
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # get an explicit tag list, but fall back on ID OF THIS LEAD as default
    tagList = parseTagListArg(args["id"].getWrapped(), leadp.getId(), env, astloc, True)
    # optional demerits
    demerits = args["demerits"].getWrapped()

    if (len(tagList)==0):
        # error, no tag list
        raise Exception("In $autohint({}) but could not find any tags named; even after checking for ".format(tagList))

    # process tags
    leadList = []
    tagStringList = []
    for tag in tagList:
        tagStringList.append(tag.getId())
        tagLeadList = tag.getGainList(True)
        for tlead in tagLeadList:
            lead = tlead["lead"]
            leadList.append(lead)

    if (len(leadList)==0):
        # error, no tag list
        #raise Exception("In $autohint({}), found tags, but could not find any leads where tags were used.".format(tagStringList))
        msg = "In $autohint({}), found tags, but could not find any leads where tags were used.".format(tagStringList)
        return msg

    # create the autohint text
    if (demerits>0):
        flagAddCheckbox = True
        textColor = "red"
        optionHelpful = False
        whyLatex = None
        upto = False
        markExtra = buildLatexMarkCheckboxSentence("demerit", demerits, False, flagAddCheckbox, optionHelpful, textColor, whyLatex, upto) + ", " + ("then")
        checkboxManager = env.getCheckboxManager()
        checkboxManager.recordCheckMarks(env, astloc, leadp, "demerit", demerits)
    else:
        markExtra = ""

    latex = generateLatexRuleThenLineBreak() + _("If you still need help, as a last resort")
    if (markExtra!=""):
        latex += " " + markExtra
    latex += " "
    if (len(leadList)<=1):
        latex += _("visit the following lead where this item is obtained")
    else:
        latex += _("visit one or more of the following leads where this item is obtained")
    latex += ":\n"

    if (len(leadList)>0):
        latex += "\\begin{itemize}\n" 
        for tagLead in leadList:
            #tagLeadLabel = tagLead.getIdPreferAutoIdFallbackLabel()
            tagLeadLabel = tagLead.getLabelIdPreferAutoId()
            leadRefLatex = makeLatexLinkToRid(tagLead.getRid(), tagLeadLabel, "onpage")
            latex += "\\item " + leadRefLatex + "\n"
        latex += "\\end{itemize}\n"

    return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def funcAutoHintDependencies(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # autohint text tells players where to find tags
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # get an explicit tag list, but fall back on ID OF THIS LEAD as default
    tagList = parseTagListArg(args["id"].getWrapped(), leadp.getId(), env, astloc, True)
    if (len(tagList)==0):
        # error, no tag list
        raise Exception("In $autohint({}) but could not find any tags named; even after checking for ".format(tagList))

    # process tag(s) to build tagDependencyList
    tagManager = env.getTagManager()
    tagDependencyList = []
    for tag in tagList:
        optionRecurse = True
        aTagDependencyList = tagManager.getDependencyTagListFromTag(tag, optionRecurse, env, astloc)
        for dtag in aTagDependencyList:
            if (dtag not in tagDependencyList):
                tagDependencyList.append(dtag)

    if (len(tagDependencyList)==0):
        # no dependencies, just return null, nothing to say
        return AstValNull(astloc, entryp)

    # build results
    reportMode = env.getReportMode()
    results = JrAstResultList()

    # box start
    symbol = "markerGeneric"
    boxStyle = "default"
    check = "all"
    boxOptions = {
        "box":boxStyle,
        "symbol": symbol,
        "symbolColor": "red",
    }
    if (boxStyle!="none"):
        addBoxToResultsIfAppropriateStart(boxOptions, results)

    # text = _("Before you read the hints for *this* item, ensure that you have *first* located the following other items:")

    # add list of tags

    # tell the player about testing markers
    testType = "hintDependencyRequire"
    tagActionKeyword = "acquired"
    optionNoIf = False
    addCheckTagTextLineToResults(env, tagDependencyList, testType, check, tagActionKeyword, results, reportMode, astloc, entryp, leadp, optionNoIf)

    # box end
    if (boxStyle!="none"):
        addBoxToResultsIfAppropriateEnd(boxOptions, results)

    # wrap in box
    return results
# ---------------------------------------------------------------------------













#---------------------------------------------------------------------------
def funcMark(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # mark some checkboxes
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    typeStr = args["type"].getWrapped()
    count = args["count"].getWrapped()
    #
    demerits = args["demerits"].getWrapped()
    culture = args["culture"].getWrapped()
    reputation = args["reputation"].getWrapped()
    extra = args["extra"].getWrapped()
    helpful = args["helpful"].getWrapped()
    #
    why = args["why"].getWrapped()
    upto = args["upto"].getWrapped()
    
    checkboxManager = env.getCheckboxManager()

    renderer = env.getRenderer()

    # why
    if (why is not None):
        whyLatex = renderer.convertMarkdownToLatexDontVouch(why, False, True)
    else:
        whyLatex = None

    # build list
    msgList = []
    if (demerits>0):
        msgList.append(buildLatexMarkCheckboxSentence("demerit", demerits, True, False, helpful, None, whyLatex, upto))
        checkboxManager.recordCheckMarks(env, astloc, leadp, "demerit", demerits)
    if (culture>0):
        msgList.append(buildLatexMarkCheckboxSentence("culture", culture, True, False, helpful, None, whyLatex, upto))
        checkboxManager.recordCheckMarks(env, astloc, leadp, "culture", culture)
    if (reputation>0):
        msgList.append(buildLatexMarkCheckboxSentence("reputation", reputation, True, False, helpful, None, whyLatex, upto))
        checkboxManager.recordCheckMarks(env, astloc, leadp, "reputation", reputation)
    if (extra>0):
        msgList.append(buildLatexMarkCheckboxSentence("extra", extra, True, False, helpful, None, whyLatex, upto))
        checkboxManager.recordCheckMarks(env, astloc, leadp, "extra", culture)
    if (typeStr is not None):
        typeStrSafe = convertEscapeUnsafePlainTextToLatex(typeStr)
        msgList.append(buildLatexMarkCheckboxSentence(typeStrSafe, count, True, False, helpful, None, whyLatex, upto))
        checkboxManager.recordCheckMarks(env, astloc, leadp, typeStrSafe, count)
    #
    if (len(msgList)==0):
        raise Exception("Runtime Error: No non-zero boxes specified to mark.")

    # combine if more than one
    msgString = " ".join(msgList)


    # build results
    results = JrAstResultList()

    # wrap it and add symbol
    boxOptions = {
        "box": "default",
        "symbol": "checkbox",
        "textColor": "red",
        "isTextSafe": True,
    }
    results.flatAdd(vouchForLatexString(wrapInLatexBox(boxOptions, msgString), False))

    # absorb following newline
    if (False):
        deferredResult = CbDeferredBlockAbsorbFollowingNewline(astloc, entryp, leadp)
        results.flatAdd(deferredResult)

    # return results
    return results
#---------------------------------------------------------------------------










#---------------------------------------------------------------------------
def funcSymbol(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # insert a symbol graphic
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    symbolId = args["id"].getWrapped()
    color = args["color"].getWrapped()
    size = args["size"].getWrapped()

    latex = generateLatexForSymbol(symbolId, color, size)

    return vouchForLatexString(latex, True)
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcBox(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    boxOptions = parseArgsGenericBoxOptions(args, env, astloc, None)

    # assemble result
    results = JrAstResultList()
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    # box end
    addBoxToResultsIfAppropriateEnd(boxOptions, results)

    # results
    return results






def funcFormat(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # format a block of text with some effect
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    style = args["style"].getWrapped()
    font = args["font"].getWrapped()
    size = args["size"].getWrapped()
    hyphenate = args["hyphenate"].getWrapped()
    #
    boxOptions = parseArgsGenericBoxOptions(args, env, astloc, None)

    # non-box alignment
    pos = boxOptions["pos"]
    if (pos=="left") or (pos is None) or (pos==""):
        nonBoxTextAlignStart = r"\begin{flushleft}"
        nonBoxTextAlignEnd = r"\end{flushleft}"
    elif (pos=="center"):
        nonBoxTextAlignStart = r"\begin{center}"
        nonBoxTextAlignEnd = r"\end{center}"
    elif (pos=="center"):
        nonBoxTextAlignStart = r"\begin{flushright}"
        nonBoxTextAlignEnd = r"\end{flushright}"


    # overrides and other stuff
    optionsDict = {
        # ATTN: its important that we have newlines at start and end of enclosures so we dont confuse markdown
        # note if boxStyls is None, then we don't get a symbol; if you want a symbol, width, etc. and other things, use box "invisible"
        "": {"box": None, "symbol": None, "start": "", "end": ""},
        "font": {"box": None, "symbol": None, "start": "", "end": ""},
        "radio": {"box": "shadow", "symbol": "radio", "start": r"\ttfamily\bfseries\itshape ", "end": r""},
        "news": {"box": "shadow", "symbol": "news", "start": r"\large\bfseries\itshape \setlength{\parskip}{\baselineskip} \setlength{\parindent}{0pt} ", "end": r""},
        "culture": {"box": "shadow", "symbol": "culture", "start": r"", "end": r""},
        "handwriting": {"box": None, "start": nonBoxTextAlignStart + r"\Fontskrivan\LARGE ", "end": nonBoxTextAlignEnd},
        "typewriter": {"box": None, "start": nonBoxTextAlignStart + r"\ttfamily\Large ", "end": nonBoxTextAlignEnd},
        "choice": {"box": "default", "symbol": "choice", "start": "", "end": ""},
        "warning": {"box": "default", "symbol": "exclamation", "start": "", "end": ""},
        "dayTest": {"box": "default", "symbol": "calendar", "symbolColor":"red", "start": "", "end": ""},
        "quote": {"box": "shadow", "symbol": "radio", "start": r"\ttfamily\bfseries\itshape ", "end": r""},
        "tornYellow": {"box": None, "symbol": None, "symbolColor":None, "start": r"\begin{tornpage}{cbYellowPaperColor}", "end": r"\end{tornpage}"},
        "tornGray": {"box": None, "symbol": None, "symbolColor":None, "start": r"\begin{tornpage}{cbNewsPaperColorA}", "end": r"\end{tornpage}"},
        "compact": {"box": "compact", "symbol": None, "symbolColor":None, "start": r"\begin{mycompact}", "end": r"\end{mycompact}"},
        "ttcompact": {"box": "compact", "symbol": None, "symbolColor":None, "start": r"\begin{myttcompact}", "end": r"\end{myttcompact}"},
    }
    if (style not in optionsDict):
        raise makeJriException("Runtime Error: $format({}) should be from {}.", style, optionsDict.keys())
    # the style
    options = optionsDict[style]

    # font override
    # if they dont specify a font but so specify a size, then force default font size
    if (font is not None) or (size is not None):
        # add font
        renderer = env.getRenderer()
        latexFontCommandAdd = renderer.setFontWithSize(font, size, env, astloc) + " "
        options["start"] += "{" + latexFontCommandAdd
        options["end"] = "}" + options["end"]
    else:
        latexFontCommandAdd = ""

    if (not hyphenate):
        # this is also found in defineFont control
        options["start"] += "\\hyphenpenalty=10000\\exhyphenpenalty=10000 "

    # defaults and overrides
    jrfuncs.overideBlankOptions(boxOptions, options, True)

    # assemble result
    results = JrAstResultList()

    # box start
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    # wrap content start
    if ("startFunc" in options):
        latex = options["startFunc"]({})
    else:
        latex = options["start"]
    #
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    latex = r"\par "
    #
    # wrap content end
    if ("endFunc" in options):
        latex += options["endFunc"]({})
    else:
        latex += options["end"]      
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # box end
    addBoxToResultsIfAppropriateEnd(boxOptions, results)


    # results
    return results
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcModifyText(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # format a block of text with some effect
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    case = args["case"].getWrapped()

    # build results
    results = JrAstResultList()

    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, leadp)
        if (targetRetv is None):
            continue
        targetResultList = convertTargetRetvToResultList(targetRetv)
        contents = targetResultList.getContents()
        for targetBlock in contents:
            text = getTargetResultBlockAsTextIfAppropriate(targetBlock)
            if (text is not None):
                if (case is not None):
                    text = jrfuncs.applyCaseChange(text, case)
                results.flatAdd(text, False)
            else:
                # not a text block, add it as is
                results.flatAdd(targetBlock, False)

    return results
#---------------------------------------------------------------------------











#---------------------------------------------------------------------------
def funcDivider(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # insert a divider graphic
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    id = args["id"].getWrapped()
    # assemble result
    results = JrAstResultList()

    results.flatAdd(CbDeferredBlockAbsorbPreviousNewline(astloc, entryp, leadp))

    latex = " " + generateLatexForDivider(env, id, astloc)
    results.flatAdd(vouchForLatexString(latex, True))

    return results
#---------------------------------------------------------------------------







#---------------------------------------------------------------------------
def funcSimpleText(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display some text
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # function given simple text via customData
    text = customData

    return resultTextOrFollowCase(text, True, False, astloc, entryp, leadp)


def funcLeaveText(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display some text
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    reason = args["reason"].getWrapped()
    otherwise = args["otherwise"].getWrapped()

    #
    if (reason is None):
        reason = "I can't think of a reason for me to be here at this time"

    # text
    text = reason + ", so I leave [stop reading now; you may come back later]."

    # assemble result
    results = JrAstResultList()
    #
    optionUseBulletIfEmptyLine = False
    results.flatAdd(CbDeferredBlockFollowCase(astloc, entryp, leadp, text, optionUseBulletIfEmptyLine, True, True))

    # add separator
    if (otherwise is not False):
        separatorId = "otherwise"
        latex = " " + generateLatexForDivider(env, separatorId, astloc)
        results.flatAdd(vouchForLatexString(latex, True))

    return results
#---------------------------------------------------------------------------
























































































# ---------------------------------------------------------------------------
def funcPrint(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display an expression
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    expression = args["expression"].getWrapped()

    # expression as string
    text = str(expression)
    return text


def funcDebug(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display text in debug mode only
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # some text to ONLY display in debug mode
    # ATTN: TODO - ONLY DISPLAY IN DEBUG MODE
    if (env.getDebugMode()):
        expression = args["expression"].getWrapped()
        # expression as string
        text = "**DEBUG:** " + str(expression)
    else:
        # nothing to display
        text = ""

    return text



def funcBreak(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # various breaks
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    typeStr = args["type"].getWrapped()

    latex = generateLatexBreak(typeStr)

    return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
def funcAdvanceTime(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # advance time
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    time = args["time"].getWrapped()
    box = args["box"].getWrapped()

    # as nice string
    timeText = jrfuncs.minutesToTimeString(time)
    text = "advance time **{}**".format(timeText)

    # wrap in box with symbol
    if (box is not None) and (box!="none"):
        # markdown
        renderer = env.getRenderer()
        latex = renderer.convertMarkdownToLatexDontVouch(jrfuncs.uppercaseFirstLetter(text+"."), False, True)
        boxOptions = {
            "box": box,
            "isTextSafe": True,
            "symbol": "clock",
            "textColor": "red"
        }
        return vouchForLatexString(wrapInLatexBox(boxOptions, latex), False)

    # just return markdown
    return text



def funcTimeHere(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # show time here (instead of at bottom)
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    deferredResult = CbDeferredBlockLeadTime(astloc, entryp, leadp)
    leadp.setTimePos("hidden")
    return deferredResult


def funcHeaderHere(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # show header at this location (instead of at top)
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    
    deferredResult = CbDeferredBlockLeadHeader(astloc, entryp, leadp)
    # tell the lead to NOT auto render header
    leadp.setAutoHeaderRender(False)
    return deferredResult

# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def funcDayTest(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # text to test what day it is
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    dayNumber = args["day"].getWrapped()
    flagAllowTempCalculatedDay = False
    day = findDayByNumber(dayNumber, env, astloc, "day test", flagAllowTempCalculatedDay)
    dayOfWeek = day.getDayOfWeekShort()
    #    
    testType = customData

    # we are not blocking the use of afterDay because it is textually ambiguous, and force use of onafter
    testTypeDict = {
        "before": _("before") + " ",
        "after": _("after") + " ",
        "onAfter": _("on or after") + " ",
        "on": "",
    }

    # assemble result
    results = JrAstResultList()

    # starting if that matches case
    deferredResult = CbDeferredBlockFollowCase(astloc, entryp, leadp, _("If"), False, True, True)
    results.flatAdd(deferredResult)

    #text = _(" it is") + " **{} {} ({})**".format(testTypeDict[testType] + _("day"), dayNumber, dayOfWeek)
    dayDateStr = day.getDayNumberDateShortNoYear()
    text = _(" it is") + " **{}{}**".format(testTypeDict[testType], dayDateStr)

    results.flatAdd(text)

    return results
# ---------------------------------------------------------------------------















# ---------------------------------------------------------------------------
def funcDayInstructions(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # show instructions for a specified day, which includes a list of tags that must be found, and information about start and end times, etc.
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    dayNumber = args["day"].getWrapped()
    whenStr = args["when"].getWrapped()

    tagActionKeyword = "gain"
    #
    foundString = generateFoundGainString(tagActionKeyword)

    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # get day object
    dayManager = env.getDayManager()
    flagAllowTempCalculatedDay = False
    day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
    if (day is None):
        raise makeJriException("Unknown 'dayNumber' ({}) specified as argument to function {}; days must be defined in setup using $configureDay(...) but day {} has not been defined.".format(dayNumber, funcName, dayNumber), astloc)

    # get list of tags which must be found by end of the specified day
    tagManager = env.getTagManager()
    tagList = tagManager.findDeadlineTags(dayNumber)
    tagList = tagManager.sortByTypeAndObfuscatedLabel(tagList, env, False)
    itemCount = len(tagList)

    # when text
    if (whenStr=="start"):
        mustText1 = _("**must** be {} before you may end").format(foundString)
        mustText2 = _("You should note this in your case log in some way to avoid having to consult this list while playing")
        whenText = _("Record in your case log that")
    elif (whenStr=="end"):
        mustText1 = _("**must** have been {} before you ended").format(foundString)
        mustText2 = _("If you have missed {}, return to searching for leads until you find all of them (if stuck, consult the hints section)").format(jrfuncs.singularPlurals(itemCount,_("it"), _("one or more"), None))
        whenText = _("You should have noted in your case log that")
    else:
        raise makeJriException("Unknown 'when' argument ({}) to function {}.".format(whenStr, funcName), astloc)
    # 
    textEd = jrfuncs.alternateText(whenStr=="start","s","ed")

    # for markdown conversion
    renderer = env.getRenderer()

    # text for required items that must be found
    latex = ""
    if (itemCount==0):
        text = _("There are no items that must be {} before the end of **day {}**.").format(foundString, dayNumber) + "\n"
        symbolName = None
    else:
        text = _("The following {} {} **day {}**. {}").format(jrfuncs.singularPlurals(itemCount,_("item"), "**" + str(itemCount) +"** " + _("items"), None), mustText1, dayNumber, mustText2) + ":\n"
        # make a nice sorted list, documents followed by markers
        for tag in tagList:
            tagNameObfuscated = tag.getNiceObfuscatedLabelWithType(True, reportMode)
            text += "* {}\n".format(tagNameObfuscated)
        symbolName = "markerGeneric"
    #
    if (symbolName is not None):
        latex += generateLatexForSymbol(symbolName, None, None)
    latex += renderer.convertMarkdownToLatexDontVouch(text, False, False)

    # add info about time limits
    start = day.getStartTime()
    end = day.getEndTime()
    if (start>0) and (end>0):
        # tell them about deadline times
        startTimeStr = convertHoursToNiceHourString(start)
        endTimeStr = convertHoursToNiceHourString(end)

        text = _("THE CLOCK IS TICKING!") + " "

        text += whenText + " " + _("**day {}** start{} at **{}** and end{} at **{}**.").format(dayNumber, textEd, startTimeStr, textEd, endTimeStr)
        if (itemCount>0):
            if (itemCount==1):
                allItemText = _("the required item")
            else:
                allItemText = _("all of the required items")
            text += " " + _("If you have *not* {} {} listed above by **{}**, you enter **overtime**.  In overtime there is no limit to how many leads you may visit, time does not advance, and your day ends once you find {}.").format(foundString, allItemText, endTimeStr, allItemText)
        else:
            text += " " + _("Keep track of what time you visit each lead, until you reach (or pass) **{}**, after which your day ends.").format(endTimeStr)
        # build latex
        latex += "\n~\n\n" + generateLatexForSymbol("clock", None, None)
        latex += renderer.convertMarkdownToLatexDontVouch(text, False, False)

    # wrap these two sections above in a box
    boxOptions = {
        "box": "default",
        "isTextSafe": True,
    }
    latex = wrapInLatexBox(boxOptions, latex)
    latex += "\n"

    # now add hint info
    if (itemCount>0):
        if (whenStr == "start"):
            text = _("**Note**: There are specific hints available for each of the day's required items (see table of contents).")
            #
            hintAlly = day.getFreeAlly()
            freeAllyStartTime = day.getFreeAllyStartTime()
            freeAllyEndTime = day.getFreeAllyEndTime()
            if (hintAlly is not None) and (hintAlly!=""):
                # tell them about a specific ally who can help more
                text += " " + _("However, if you need guidance on where to focus your efforts on any given day") + ", "
                if (hintAlly=="financialPrecinct"):
                    text += _("you can drop by your old police precinct in the Financial District for some advice")
                    allyDetailText = _("you can catch the chief on his break and get his advice without penalty")
                else:
                    raise makeJriException("Unknown hintAlly ({}) in dayConfigure.".format(hintAlly))
                freeAllyStartTimeStr = convertHoursToNiceHourString(freeAllyStartTime)
                freeAllyEndTimeStr = convertHoursToNiceHourString(freeAllyEndTime)
                ifYouArriveText = _("if you arrive")
                if (freeAllyStartTime>-1) and (freeAllyEndTime>-1):
                    text += " (" + ifYouArriveText + " " + _("between") + " **" + freeAllyStartTimeStr + " " + _("and") + " " + freeAllyEndTimeStr + "** " + allyDetailText + ")."
                elif (freeAllyStartTime>-1):
                    text += " (" + ifYouArriveText + " " + _("after") + " **" + freeAllyStartTimeStr + "** " + allyDetailText + ")."
                elif (freeAllyEndTime>-1):
                    text += " (" + ifYouArriveText + " " + _("before") + " **" + freeAllyEndTimeStr + "**" + allyDetailText + ")."
                else:
                    text += "."
            text += "\n"
        else:
            text = ""

        if (text!=""):
            # add latex symbol, etc.
            latex += generateLatexForSymbol("hand", None, None)
            latex += renderer.convertMarkdownToLatexDontVouch(text, False, False)
    
    # vouch for entire text
    return vouchForLatexString(latex, False)



def funcBlurbStop(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display a "STOP" warning message
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    typeStr = args["type"].getWrapped()
    dayNumber = args["day"].getWrapped()
    rest = args["rest"].getWrapped()
    text = args["text"].getWrapped()
    goLead = args["goLead"].getWrapped()


    if (dayNumber!=-1):
        # get day object
        dayManager = env.getDayManager()
        flagAllowTempCalculatedDay = False
        day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
        if (day is None):
            raise makeJriException("Unknown 'dayNumber' ({}) specific argument to function {}; days must be defined in setup using $configureDay(...).".format(dayNumber, funcName), astloc)
        # get list of tags which must be found by end of the specified day
        tagManager = env.getTagManager()
        tagList = tagManager.findDeadlineTags(dayNumber)
        itemCount = len(tagList)
    else:
        itemCount = 0

    curDayText = ("**day {}**".format(dayNumber)) if (dayNumber !=-1) else "the current day"
    nextDayText = ("**day {}**".format(dayNumber)) if (dayNumber !=-1) else "the next day"

    blurbDict = {
        # these are actually used
        "dayStart": {"txt": _("Stop reading this case book now, and begin searching for leads in the directories.\n\nContinue to the next page only when you are ready to end") + " " + curDayText + ".",},
        "dayStartEvent": {"txt": _("Stop reading this case book now, and begin searching for leads in the directories.\n\nDo not turn the page. You should have set an event which will trigger at the end of") + " " + curDayText + ", " + _("which will instruct you on what to do when the day ends.")},
        "nextDay": {"txt": _("Turn the page when you are ready to begin") + " " + nextDayText + ".", "rest": True},
        "dayEnd": {"txt": _("Proceed only after you have completed searching for leads on") + " " + curDayText + (_(", and found the day's required **{} item{}**.").format(itemCount, jrfuncs.plurals(itemCount,"s")) if (itemCount>=1) else "."),},
        "conclusion": {"txt": _("The case is nearing an end. You will have another chance to search for leads, but in the meantime, turn to") + ": ", "rest": True,},
        "questions": {"txt": _("Proceed only when you are ready to answer questions.")},
        "questionPause": {"txt": _("Once you have answered all questions on the previous page(s) you may continue to the next page."),},
        "leads": {"txt": _("WARNING! Do **not** read through the rest of this document like a book from beginning to end. Lead entries are meant to be read individually only when you look up a lead by its number.\n\nClose this book now and follow rulebook instructions for looking up leads."),},
        "documents": {"txt": _("Do **not** access the documents section unless directed to retrieve a specific document."),},
        "hints": {"txt": _("Do **not** access the hints section except when looking up a specific hint from the table of contents at the start of this case book."),},
        "briefingEnd": {"txt": _("Proceed only after you are ready to continue."),},
        "dayStartThenConclusion": {"txt": _("Stop reading this case book now, and begin searching for leads in the directories.  When your day is over, turn to: \n\n"),},

        # i dont think we actually use these, they are hypothetically useful
        "nightStart": {"txt": _("Turn the page when you are ready to proceed to **Late Night** activities."),},
        "nightEnd": {"txt": _("Proceed only after you have finished resolving any special **Late Night** actions described on the previous pages."),},
        "resolvePause": {"txt": _("Once you have resolved the previous page you may continue to the next page."),},
        "solution": {"txt": _("Once you have answered all questions on the previous page(s) you may turn the page for the **conclusion to the case**."),},
        "end": {"txt": _("Do **not** turn the page until you are ready to begin wrapping up your case."),},
        "noMore": {"txt": _("Your case has ended, there is nothing more to read."),},
        "begin": {"txt": _("Stop reading this case book now, and begin searching for leads in the directories."),},
    }

    if (typeStr in blurbDict):
        blurb = blurbDict[typeStr]
    else:
        raise makeJriException("Unknown blurb type ({}).".format(typeStr), astloc)
    
    # build reply
    renderer = env.getRenderer()
    if (text is None):
        text = blurb["txt"]
    else:
        # use passed in text
        text = text.replace("\\n","\n")

    # assemble result
    results = JrAstResultList()
    latex = ""

    #
    latex += r"\begin{Huge}\bfseries \textbf{" + _("STOP!") + r"}\par\end{Huge}" + "\n\n~\n\n"
    symbolName = "stop"
    if (symbolName is not None):
        latex += generateLatexForSymbol(symbolName, "red", None) + "  "
    latex += renderer.convertMarkdownToLatexDontVouch(text, False, False)

    # special stuff
    if (typeStr=="conclusion") or (typeStr=="dayStartThenConclusion"):
        # intermediate add, then deferred link to conclusion
        results.flatAdd(vouchForLatexString(latex,False))
        # make DEFERRED link to entry lead
        leadId = goLead if (goLead is not None) else "Conclusion"
        style = "full"
        result = CbDeferredBlockRefLead(astloc, entryp, leadp, leadId, style)
        results.flatAdd(result)
        latex = ".\n"

    # rest?
    if (rest is None) and ("rest" in blurb):
        rest = blurb["rest"]
    if (rest):
        latex += "\n\n~\n\n" + r"\textit{" + _("NOTE: If you’ve been playing for a couple of hours, now might be a good time to take a break before continuing...") + "}" +"\n"

    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    return results
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def funcBlurb(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display a "STOP" warning message
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    typeStr = args["type"].getWrapped()
    #

    blurbDict = {
        # these are actually used
        "continue": {"markdown": "**_[" + _("Continue to next entry") + "...]_**",},
        "remindEveningEvent": {"markdown": "**Important**: You should have been explicitly directed to this entry after triggering the mandatory end-of-day event.  If not, turn back to the day's introduction and trigger it now.", "boxDefaults": {"box":"default", "symbol": "warning", "textColor": "red", "symbolColor":"red"}}
    }

    if (typeStr in blurbDict):
        blurb = blurbDict[typeStr]
    else:
        raise makeJriException("Unknown blurb type ({}).".format(typeStr), astloc)

    boxDefaults = blurb["boxDefaults"] if ("boxDefaults" in blurb) else None
    boxOptions = parseArgsGenericBoxOptions(args, env, astloc, boxDefaults)

    # assemble result
    results = JrAstResultList()
    # box start
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    if ("markdown" in blurb):
        results.flatAdd(blurb["markdown"])
    else:
        results.flatAdd(vouchForLatexString(blurb["latex"], True))

    # box end
    addBoxToResultsIfAppropriateEnd(boxOptions, results)
    return results
# ---------------------------------------------------------------------------











# ---------------------------------------------------------------------------
def funcLogic(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # add a logic relationship
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    if (leadp is None):
        # this is not a real rendering lead so we do not record logic entry for it
        return AstValNull(astloc, entryp)

    label = args["label"].getWrapped()
    typeStr = customData["type"]
    direction = customData["direction"]

    if (typeStr == DEF_CustomLogicType_Arg):
        # get type from key
        typeStr = args["type"].getWrapped()
        target = args["target"].getWrapped()
        if (target==""):
            direction = None
        else:
            direction = "ab"

    # renderer
    renderer = env.getRenderer()

    # target and source
    target = args["target"].getWrapped() if ("target" in args) else None
    source = args["source"].getWrapped() if ("source" in args) else None

    # allow logic to mention next and prev
    if (typeStr == "proceed"):
        target = "next"


    if (target is not None):
        source = leadp
        possibleTagId = target
    elif (source is not None):
        target = leadp
        possibleTagId = source
    else:
        source = leadp
        target = None
        possibleTagId = None


    # convert source or target string to tag
    if (isinstance(source,str)):
        sourceTag = env.findTagOrConcept(source, False)
        if (sourceTag is not None):
            source = sourceTag
    if (isinstance(target,str)):
        targetTag = env.findTagOrConcept(target, False)
        if (targetTag is not None):
            target = targetTag


    # kludge for when lead id is a document, we dont actually render document LEAD nodes, just document TAGS, so we want the mindmap link to point to the TAG not the lead
    if (source == leadp):
        # source is a lead pointer, but is it ALSO a tag? we check by ID
        tag = env.findTagOrConcept(leadp.getId(), False)
        if (tag is not None) and (tag.getIsTagTypeDoc()):
            source = tag
            possibleTagId = None
            tag.recordLogic(env, typeStr, label, astloc, target)
    if (target == leadp):
        tag = env.findTagOrConcept(leadp.getId(), False)
        if (tag is not None) and (tag.getIsTagTypeDoc()):
            target = tag
            possibleTagId = None
            tag.recordLogic(env, typeStr, label, astloc, source)
    
    # we could still get here with source or target being string tag if
    # ATTN: this is not an error, its a deferred lookup
    if (isinstance(source,str)):
        # ATTN: this should now be considered an error??
        if (False):
            raise makeJriException("Failed to find source '{}' for logic link.".format(source), astloc)
    if (isinstance(target,str)):
        # ATTN: this should now be considered an error??
        if (False):
            raise makeJriException("Failed to find target '{}' for logic link.".format(target), astloc)

    # mindmapper
    mindMapper = env.getMindManager()
    if (source is not None) and (target is not None):
        mindMapper.addLinkBetweenNodes(env, typeStr, label, source, target)
    else:
        mindMapper.addLinkAtributeOnNode(env, typeStr, label, source)

    # record a logic use, IF the target or source is a TAG
    if (possibleTagId is not None):
        tag = env.findTagOrConcept(possibleTagId, False)
        if (tag is not None):
            tag.recordLogic(env, typeStr, label, astloc, leadp)

    # just return blank
    return AstValNull(astloc, entryp)
# ---------------------------------------------------------------------------


















#---------------------------------------------------------------------------
def funcAuthorNote(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # marks a target block to ONLY be shown in author debug output
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    
    label = args["label"].getWrapped()

    # only show in report mode
    if (not env.getReportMode()):
        return AstValNull(astloc, entryp)

    # assemble result
    results = JrAstResultList()

    # box start
    boxOptions = {
        "box": "report",
        "symbol": "report",
        "symbolColor": "red"
    }
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    # add note for debug report
    if (label==""):
        msg = "Author note"
    else:
        msg = "Author Note ({})".format(label)
    note = JrINote("authorNote", leadp, msg, None, None)
    env.addNote(note)
    # use this note as start of text box contents
    results.flatAdd(msg+"\n\n")

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    # box end
    addBoxToResultsIfAppropriateEnd(boxOptions, results)

    # results
    return results
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcMarginNote(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display some text in the margin
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    
    position = args["pos"].getWrapped()

    extraLatex = r"\sffamily\scriptsize "

    # assemble result
    results = JrAstResultList()

    if (position=="left"):
        latextStart = r"\marginnote["
        latextEnd = r"]{} "
    else:
        latextStart = r"\marginnote[]{"
        latextEnd = r"} "
    
    # start of note
    if (extraLatex!=""):
        latextStart+=extraLatex
    results.flatAdd(vouchForLatexString(latextStart, False))

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    # end of note
    results.flatAdd(vouchForLatexString(latextEnd, False))

    # results
    return results
#---------------------------------------------------------------------------

















#---------------------------------------------------------------------------
# configuration helpers

def funcConfigureGameInfo(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    info = env.getEnvValueUnwrapped(None, "info", None)
    info["name"] = args["name"].getWrapped()
    info["title"] = args["title"].getWrapped()
    info["subtitle"] = args["subtitle"].getWrapped()
    info["authors"] = args["authors"].getWrapped()
    info["version"] = args["version"].getWrapped()
    info["versionDate"] = args["versionDate"].getWrapped()
    info["status"] = args["status"].getWrapped()
    info["difficulty"] = args["difficulty"].getWrapped()
    info["duration"] = args["duration"].getWrapped()

    # empty text reply (does not add text)
    return AstValNull(astloc, entryp)


def funcConfigureGameSummary(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    info = env.getEnvValueUnwrapped(None, "info", None)
    info["summary"] = args["summary"].getWrapped()

    # empty text reply (does not add text)
    return AstValNull(astloc, entryp)


def funcConfigureGameInfoExtra(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "info", None)
    data["cautions"] = args["cautions"].getWrapped()
    data["url"] = args["url"].getWrapped()
    data["copyright"] = args["copyright"].getWrapped()
    data["extraCredits"] = args["extraCredits"].getWrapped()
    data["keywords"] = args["keywords"].getWrapped()
    data["gameSystem"] = args["gameSystem"].getWrapped()
    data["gameDate"] = args["gameDate"].getWrapped()

    # empty text reply (does not add text)
    return AstValNull(astloc, entryp)


def funcConfigureGameCampaign(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "info", None)
    data["campaignName"] = args["name"].getWrapped()
    data["campaignPosition"] = str(args["position"].getWrapped())

    # empty text reply (does not add text)
    return AstValNull(astloc, entryp)

        


def funcConfigureClock(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "info", None)
    data["clockMode"] = args["clockMode"].getWrapped()

    # empty text reply (does not add text)
    return AstValNull(astloc, entryp)


def funcConfigureLeadDb(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "leadDbData", None)
    data["version"] = args["version"].getWrapped()
    data["versionPrevious"] = args["versionPrevious"].getWrapped()
    seed = args["seed"].getWrapped()

    if (seed is None):
        # auto seed based on game name
        info = env.getEnvValueUnwrapped(None, "info", None)
        gameName = jrfuncs.getDictValueOrDefault(info, "name", "")
        seed = hash(gameName)
    #
    data["seed"] = seed

    # empty text reply (does not add text)
    return AstValNull(astloc, entryp)


def funcConfigureParser(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "parserData", None)
    #data["balancedQuoteCheck"] = args["balancedQuoteCheck"].getWrapped()

    # empty text reply (does not add text)
    return AstValNull(astloc, entryp)


def funcConfigureRenderer(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "rendererData", None)
    data["doubleSided"] = args["doubleSided"].getWrapped()
    data["latexPaperSize"] = args["latexPaperSize"].getWrapped()
    data["latexFontSize"] = args["latexFontSize"].getWrapped()
    data["autoStyleQuotes"] = args["autoStyleQuotes"].getWrapped()
    data["timeStyle"] = args["timeStyle"].getWrapped()
    #data["defaultTime"] = args["defaultTime"].getWrapped()
    data["defaultTimeStyle"] = args["defaultTimeStyle"].getWrapped()
    data["zeroTimeStyle"] = args["zeroTimeStyle"].getWrapped()


    # empty text reply (does not add text)
    return AstValNull(astloc, entryp)


def funcConfigureTags(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "tagData", None)
    data["alwaysNumber"] = args["alwaysNumber"].getWrapped()
    data["consistentNumber"] = args["consistentNumber"].getWrapped()
    data["mode"] = args["mode"].getWrapped()
    data["sortRequire"] = args["sortRequire"].getWrapped()

    # empty text reply (does not add text)
    return AstValNull(astloc, entryp)


 
#---------------------------------------------------------------------------





#---------------------------------------------------------------------------
def funcPageStyle(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    style = args["style"].getWrapped()
    if (style!=""):
        latex = generateLatexForPageStyle(style, astloc)
    return vouchForLatexString(latex, True)
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcPageBackground(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # show a packground pic that covers whole page
    # see https://tex.stackexchange.com/questions/167719/how-to-use-background-image-in-latex
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    path = args["path"].getWrapped()
    opacity = args["opacity"].getWrapped()

    # get image import helper, and try to find image first in game-specicific list then fallback to shared
    [imageFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImageOrPdf(), path, "Image page background", "embedImage", leadp, env, astloc, False)

    # generate latex
    latexPath = makeLatexSafeFilePath(imageFullPath)
    latex = "\\imageFullPage{" + latexPath + "}" + "{" + str(opacity) + "}"

    #
    return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------

















#---------------------------------------------------------------------------
def funcDropCaps(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # drop cap effect has big first letter of sentence
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    
    # options
    optionStyle = args["style"].getWrapped()
    optionLines = args["lines"].getWrapped()
    optionFindent = args["fIndent"].getWrapped()
    optionNindent = args["nIndent"].getWrapped()
    optionLhang = args["lHang"].getWrapped()   
    optionFindent = str(optionFindent)+ "em"
    optionNindent = str(optionNindent)+ "em"
    optionLhang = str(optionLhang)
    optionProtectStyle = args["multi"].getWrapped()

    # assemble result
    optionPreferAfterNoteType = None
    flagStripEndingNewlines = False
    results = dropCapResults(optionStyle, optionPreferAfterNoteType, targets, rmode, env, entryp, leadp, astloc, optionLines, optionFindent, optionNindent, optionLhang, optionProtectStyle, flagStripEndingNewlines)
    return results
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcEffectUp(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # drop cap effect has big first letter of sentence
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    
    # options
    text = args["text"].getWrapped()
    enabled = args["enabled"].getWrapped()
    style = args["style"].getWrapped()

    if (enabled is not None) and (not enabled):
        return text

    [firstChar, upperCaseText, remainderText] = jrfuncs.smartSplitTextForDropCaps(text, "bold")
    #
    renderer = env.getRenderer()
    markdownTextRemainder = (upperCaseText+remainderText).upper()
    remainderLatexed = renderer.convertMarkdownToLatexDontVouch(markdownTextRemainder, True, False)
    #
    latex = r"\noindent{\Large\bfseries " + firstChar + r"}{\bfseries " + (remainderLatexed) + "}"

    return vouchForLatexString(latex, True)
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcLipsum(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # insert filler text for testing
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    start = args["start"].getWrapped()
    end = args["end"].getWrapped()
    if (end==-1):
        end = start
    length = args["length"].getWrapped()

    # usinig built in latex
    if (False):
        latex = "\\lipsum[{}-{}]".format(start,end)
        return vouchForLatexString(latex, False)

    # new using inhouse text generator
    renderer = env.getRenderer()
    jrLorum = renderer.getLorem()
    text = jrLorum.getParagraphs(start, end, length)

    # add as one block of text?
    if (False):
        # yes; this may not properly paragraph break
        return text + "\n"
    else:
        # assemble result
        results = JrAstResultList()
        textLines = text.split("\n")
        for i, line in enumerate(textLines):
            results.flatAdd(line + "\n")
        return results   
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcDesignateFile(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # ATTN: unfinished
    path = args["path"].getWrapped()
    tag = args["tag"].getWrapped()
    rename = args["rename"].getWrapped()

    # find the file mentioned
    [fileFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImageOrPdf(), path, "Designated file with tag", "designateFile", leadp, env, astloc, False)
    renderer = env.getRenderer()
    renderer.designateFile(fileFullPath, tag, rename)

    return AstValNull(astloc, entryp)
#---------------------------------------------------------------------------


















#---------------------------------------------------------------------------
def funcQuote(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # insert a nice looking big quote
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    style = args["style"].getWrapped()
    cite= args["cite"].getWrapped()
    font = args["font"].getWrapped()
    size = args["size"].getWrapped()
    #
    boxOptions = parseArgsGenericBoxOptions(args, env, astloc, None)

    # select group of options
    optionStyles = {
        "default": {"box": "hLines"},
    }
    if (style not in optionStyles):
        raise makeJriException("Runtime Error: $quote({}) should be from {}.", style, optionStyles.keys())
    # the style
    options = optionStyles[style]

    # defaults and overrides
    jrfuncs.overideBlankOptions(boxOptions, options, True)

    # programmatically override
    options = {}
    options["start"] = r" \begin{cb_quoteenv} \setstretch{1} "
    #quoteOptions["start"] += r"\huge "
    options["start"] += r"\textit{"
    options["end"] = r" \end{cb_quoteenv}"

    # citation alignment based on box alignment
    pos = boxOptions["pos"]
    citeAlign = r"flushright"
    if (pos in ["right","topRight"]):
        citeAlign = r"flushright"
    elif (pos in ["left", "topLeft"]):
        citeAlign = r"flushleft"

    # assemble result
    results = JrAstResultList()

    # box start
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    # custom font?
    if (font is not None) or (size is not None):
        # add font
        renderer = env.getRenderer()
        latexFontCommandAdd = renderer.setFontWithSize(font, size, env, astloc) + " "
        options["start"] += "{" + latexFontCommandAdd
        options["end"] = "}" + options["end"]
    else:
        latexFontCommandAdd = ""

    # add citation
    if (cite!=""):
        options["end"] = r"} \begin{" + citeAlign + r"} \vspace{0.5em} " + latexFontCommandAdd + r"\textbf{ - " + convertEscapeUnsafePlainTextToLatex(cite) + r"} \end{" + citeAlign + r"} " +  options["end"]


    # wrap content start
    if ("startFunc" in options):
        latex = options["startFunc"]({})
    else:
        latex = options["start"]
    #
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    # wrap content end
    if ("endFunc" in options):
        latex = options["endFunc"]({})
    else:
        latex = options["end"]      
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # box end
    addBoxToResultsIfAppropriateEnd(boxOptions, results)

    if (pos in ["topRight", "topLeft"]):
        # be nice and auto add a deferred header afterwords to make sure header of lead comes after
        deferredResult = CbDeferredBlockLeadHeader(astloc, entryp, leadp)
        # tell the lead to NOT auto render header
        if (leadp is not None):
            leadp.setAutoHeaderRender(False)
        results.flatAdd(deferredResult)

    # results
    return results
#---------------------------------------------------------------------------





#---------------------------------------------------------------------------
def funcBlock(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # insert a nice looking big quote
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    align = args["align"].getWrapped()

     # assemble result
    results = JrAstResultList()

    results.flatAdd(makeMiniPageBlockLatexStart(True, align), False)

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    results.flatAdd(makeMiniPageBlockLatexEnd(True), False)

    # results
    return results
#---------------------------------------------------------------------------






#---------------------------------------------------------------------------
def funcCalendar(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    start = args["start"].getWrapped()
    end = args["end"].getWrapped()
    strikeStart = args["strikeStart"].getWrapped()
    strikeEnd = args["strikeEnd"].getWrapped()
    circle = args["circle"].getWrapped()
    #
    boxOptions = parseArgsGenericBoxOptions(args, env, astloc, None)

    # assemble result
    results = JrAstResultList()
    # box start
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    dateStartString = convertEscapeUnsafePlainTextToLatexMorePermissive(start)
    dateEndString = convertEscapeUnsafePlainTextToLatexMorePermissive(end)
    strikeStartString = convertEscapeUnsafePlainTextToLatexMorePermissive(strikeStart)
    strikeEndString = convertEscapeUnsafePlainTextToLatexMorePermissive(strikeEnd)
    circleString = convertEscapeUnsafePlainTextToLatexMorePermissive(circle)
    #
    latex = generateLatexCalendar(dateStartString, dateEndString, strikeStartString, strikeEndString, circleString)
    results.flatAdd(vouchForLatexString(latex, False))

    # box end
    addBoxToResultsIfAppropriateEnd(boxOptions, results)

    return results
#---------------------------------------------------------------------------

















































#---------------------------------------------------------------------------
def funcConfigureSection(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    sectionId = args["id"].getWrapped()
    # generic section stuff
    return doFuncConfigureSectionWithId(sectionId, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets, True)

def funcConfigureLeads(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    sectionId = "LEADS"
    return doFuncConfigureSectionWithId(sectionId, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets, True)


def funcConfigureHints(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    sectionId = "HINTS"
    return doFuncConfigureSectionWithId(sectionId, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets, True)

def funcConfigureReport(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    sectionId = "REPORT"
    return doFuncConfigureSectionWithId(sectionId, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets, True)

def funcConfigureFront(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    sectionId = "FRONT"
    return doFuncConfigureSectionWithId(sectionId, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets, True)

def funcConfigureEnd(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    sectionId = "END"
    return doFuncConfigureSectionWithId(sectionId, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets, True)
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def doFuncConfigureSectionWithId(sectionId, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets, flagErrorIfNotFound):
    # create the entry for the section, and then run entry configure on it

    # this is MOSTLY just an alternative way of creating a section ahead of time with an ID as you might otherwise do with a # TOPLEVEL SECTION that we can call from a configure
    # BUT there is one MAJOR difference
    # The major difference is that these run AFTER the entry section definitions, and the options set should NOT modify any manually set values from when the entries were defined
    # so the options here only apply when the option is not already set

    sectionEntryp = env.findEntryByIdPath(sectionId, astloc)
    if (sectionEntryp is None):
        # ATTN: I thought we would encounter this early, but actually these run AFTER the entries are parsed
        # we are going to try something different, by only using the $configure() functions to operate on existing sections, and skip if not found
        if (False):
            # create top level entry
            sectionEntryp = JrAstEntry(astloc, None, 1)
            rootp = entryp.getParentEntry()
            rootp.entries.addChild(env, sectionEntryp, astloc)
        else:
            # ??
            if (flagErrorIfNotFound):
                raise makeJriException("Could not configure section '{}' since it could not be found.".format(sectionId), astloc)
            else:
                return AstValNull(astloc, entryp)

    # run it
    doFuncConfigureEntry(False, rmode, env, sectionEntryp, leadp, astloc, args, customData, funcName, targets)
    return AstValNull(astloc, entryp)




def doFuncConfigureEntry(flagDoneOverride, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # ATTN: it's important now that all of these allow None as a missing field so we can AVOID setting/overwriting it
    # args
    jrfuncs.callSetIfValNotNone(entryp.setLeadColumns, args["leadColumns"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setSectionColumns, args["sectionColumns"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setLeadBreak, args["leadBreak"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setSectionBreak, args["sectionBreak"].getWrapped())
    toc = args["toc"].getWrapped()
    jrfuncs.callSetIfValNotNone(entryp.setChildToc, args["childToc"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setHeading, args["heading"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setChildPlugins, args["childPlugins"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setIsAutoLead, args["autoLead"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setCopyFrom, args["copy"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setShouldRender, args["render"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setContinuedFromLead, args["continuedFrom"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setMStyle, args["mStyle"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setAddress, args["address"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setHeadingStyle, args["headingStyle"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setChildHeadingStyle, args["childHeadingStyle"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setLayout, args["layout"].getWrapped())
    #
    jrfuncs.callSetIfValNotNone(entryp.setSortGroup, args["sortGroup"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setSortKey, args["sortKey"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setMultiPage, args["multiPage"].getWrapped())
    
    #
    labelOverride = args["label"].getWrapped()
    idOverride = args["id"].getWrapped() if ("id" in args) else None

    # evil kludge
    if (labelOverride is not None) and (toc is None):
        # a custom label means toc gets set to default label if its not set; author can set toc if they want it to be different
        toc = entryp.getLabel()
        if (toc=="") or (toc is None):
            # but only set it if not autolead
            if (not args["autoLead"].getWrapped()):
                toc = entryp.getId()
            #toc = entryp.getIdPreferAutoId()

    # set toc
    jrfuncs.callSetIfValNotNone(entryp.setToc, toc)

    # blank header means dont show the id/title, etc.
    blank = args["blank"].getWrapped()
    # ATTN: 1/18/25 do not auto mark entries as supposedly blank just because they dont have an id set (if they habe a label)
    if (flagDoneOverride) and (blank is None):
        entryId = entryp.getId()
        # new we check for blank entry id or if entryid AND label are blank
        if (entryId in [DefCbDefine_IdBlank]) or ((entryId in [DefCbDefine_IDEmpty]) and (entryp.getLabel() in ["", None])):
            # blank id means it should be officially "blank"
            blank = True

    if (blank is not None):
        entryp.setBlankHead(blank)

    if (labelOverride is not None):
        entryp.setLabel(labelOverride)

    if (idOverride is not None):
        #entryp.setId(idOverride)
        entryp.setAutoId(idOverride)

    # time
    jrfuncs.callSetIfValNotNone(entryp.setTime, args["time"].getWrapped())
    jrfuncs.callSetIfValNotNone(entryp.setTimePos, args["timePos"].getWrapped())

    # dividers
    jrfuncs.callSetIfValNotNone(entryp.setDividers, args["dividers"].getWrapped())
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcConfigureDocuments(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "documentData", None)
    data["defaultLocation"] = args["defaultLocation"].getWrapped()
    data["printLocation"] = args["printLocation"].getWrapped()
    data["printStyle"] = args["printStyle"].getWrapped()

    # generic section stuff
    sectionId = "DOCUMENTS"
    return doFuncConfigureSectionWithId(sectionId, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets, True)

#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcConfigureDay(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure a specific day

    dayNumber = args["day"].getWrapped()
    typeStr = args["type"].getWrapped()
    start = args["start"].getWrapped()
    end = args["end"].getWrapped()
    dayDate = args["date"].getWrapped()
    #
    hintAlly = args["hintAlly"].getWrapped()
    allyFreeStart = args["allyFreeStart"].getWrapped()
    allyFreeEnd = args["allyFreeEnd"].getWrapped()

    # create day object
    day = CbDay(dayNumber, typeStr, dayDate, start, end, hintAlly, allyFreeStart, allyFreeEnd)
    dayManager = env.getDayManager()
    dayManager.addDay(day)

    # generic section stuff
    sectionId = "D" + str(dayNumber)
    return doFuncConfigureSectionWithId(sectionId, rmode, env, entryp, leadp, astloc, args, customData, funcName, targets, False)
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcBlurbDay(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display some information about a day
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    dayNumber = args["day"].getWrapped()
    typeStr = args["type"].getWrapped()
    #
    boxOptions = parseArgsGenericBoxOptions(args, env, astloc, None)

    # get day object
    dayManager = env.getDayManager()
    flagAllowTempCalculatedDay = False
    day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
    if (day is None):
        raise makeJriException("Unknown 'dayNumber' ({}) specific argument to function {}; days must be defined in setup using $configureDay(...).".format(dayNumber, funcName), astloc)

    # build reply
    renderer = env.getRenderer()

    # assemble result
    results = JrAstResultList()
    # box start
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    if (typeStr in ["dayTimeStart", "dayDateStart", "calendar", "timeStart"]):
        # show the date, time, day of week
        dayDate = day.getDate()
        if (dayDate is None):
            raise makeJriException("Day {} has no date; needs to be set with $configureDay().".format(dayNumber, funcName), astloc)
        dayDate = jrfuncs.replaceFractionalHourTime(dayDate, day.getStartTime())

    if (typeStr=="calendar"):
        # create a calendate for the given day, striking out previous days
        # first get day 1 starting month and year
        flagAllowTempCalculatedDay = True
        firstDay = dayManager.findDayByNumber(1, flagAllowTempCalculatedDay)
        firstDayDate = firstDay.getDate()
        firstDayMonth = firstDayDate.month
        firstDayYear = firstDayDate.year
        firstDayDay = firstDayDate.day
        thisDayMonth = dayDate.month
        thisDayYear = dayDate.year
        thisDayDay = dayDate.day
        yearDif = thisDayYear-firstDayYear
        #
        strikeStartString = ""
        strikeEndString = ""
        dateEndString = "{}-{}-{}".format(thisDayYear,thisDayMonth,"last")
        circleString = "{}-{}-{}".format(thisDayYear,thisDayMonth,thisDayDay)
        #
        if (yearDif>=0) and (yearDif<=1):
            # gap is small enough for a calendar
            dateStartString = "{}-{}-{}".format(firstDayYear,firstDayMonth,1)
            if ((firstDayYear!=thisDayYear) or (firstDayMonth!=thisDayMonth) or (firstDayDay!=thisDayDay)):
                # we can strike through 
                dayBefore = dayDate - timedelta(days=1)
                strikeStartString = "{}-{}-{}".format(firstDayYear, firstDayMonth, firstDayDay)
                strikeEndString = "{}-{}-{}".format(dayBefore.year, dayBefore.month, dayBefore.day)
        else:
            # too big a gap, just start at first of month
            dateStartString = "{}-{}-{}".format(thisDayYear,thisDayMonth,1)

        latex = generateLatexCalendar(dateStartString, dateEndString, strikeStartString, strikeEndString, circleString)
        results.flatAdd(vouchForLatexString(latex, False))

    elif (typeStr == "dayTimeStart"):
        text = jrfuncs.niceDayDateTimeStr(dayDate, True, True)
        text = "**" + text + "**\n"
        results.flatAdd(text)

    elif (typeStr == "dayDateStart"):
        text = jrfuncs.niceDayDateStr(dayDate, True, True)
        text = "**" + text + "**\n"
        results.flatAdd(text)

    elif (typeStr == "timeStart"):
        text = jrfuncs.niceTimeDayStr(dayDate)
        text = "**" + text + "**\n"
        results.flatAdd(text)

    # box start
    addBoxToResultsIfAppropriateEnd(boxOptions, results)

    return results
#---------------------------------------------------------------------------






#---------------------------------------------------------------------------
def funcDate(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # convert a mm/dd/yyyy date to a string like "Tuesday, June 10th, 1915"
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    dateStr = args["date"].getWrapped()
    flagYear = args["year"].getWrapped()

    dayDate = jrfuncs.makeDateTimeFromString(dateStr, DefCbDefine_ParseDayConfigureDate)
    text = jrfuncs.niceDayDateStr(dayDate, flagYear, True)

    return text
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcDayDate(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):

    dayNumber = args["day"].getWrapped()
    typeStr = args["type"].getWrapped()

    # get day object
    dayManager = env.getDayManager()
    flagAllowTempCalculatedDay = True
    day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
    if (day is None):
        raise makeJriException("Unknown 'dayNumber' ({}) specific argument to function {}; days must be defined in setup using $configureDay(...).".format(dayNumber, funcName), astloc)

    # build reply
    renderer = env.getRenderer()

    # date of the day
    dayDate = day.getDate()
    if (dayDate is None):
        raise makeJriException("Day {} has no date; needs to be set with $configureDay().".format(dayNumber, funcName), astloc)

    if (typeStr in ["dayTimeStart", "dayDate"]):
        # show the date, time, day of week
        dayDate = jrfuncs.replaceFractionalHourTime(dayDate, day.getStartTime())

    if (typeStr == "dayTimeStart"):
        text = jrfuncs.niceDayDateTimeStr(dayDate, True, True)
    elif (typeStr == "timeStart"):
        text = jrfuncs.niceTimeDayStr(dayDate)
    elif (typeStr == "dayDate"):
        text = jrfuncs.niceDayDateStr(dayDate, True, True)
    elif (typeStr == "dayDateNoYear"):
        text = jrfuncs.niceDayDateStr(dayDate, False, True)
    elif (typeStr == "mmddyyyy"):
        text = dayDate.strftime("%m/%d/%Y")
    elif (typeStr == "dayOfWeek"):
        text = dayDate.strftime("%A")
    else:
        raise makeJriException("Unknown 'type' value {} for function '{}'.".format(typeStr, funcName), astloc)

    return text
#---------------------------------------------------------------------------












































#---------------------------------------------------------------------------
def funcMentionTags(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # mention a list of tags
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    tagList = parseTagListArg(args["tags"].getWrapped(), "", env, astloc, True)

    # record tag use
    for tag in tagList:
        tag.recordCheck(env, "mentions", astloc, leadp)

    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # process tags
    tagStringList = []
    for tag in tagList:
        tagString = tag.getNiceObfuscatedLabelWithType(True, reportMode)
        tagStringList.append(tagString)

    tagStringText = jrfuncs.makeNiceCommaAndOrList(tagStringList, "and")

    return tagStringText





def funcReferTag(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # check if play has tag
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    tagList = parseTagListArg(args["id"].getWrapped(), "", env, astloc, True)
    check = args["combine"].getWrapped()
    #
    testType = customData

    # record tag use
    for tag in tagList:
        tag.recordCheck(env, testType, astloc, leadp)

    # in report mode we show the real tag label
    reportMode = env.getReportMode()


    # we want to SAY that the tags have been gained
    if (len(tagList)==1):
        tagNameObfuscated = tagList[0].getNiceObfuscatedLabelWithType(True, reportMode)
        text = "{}".format(tagNameObfuscated)
    else:
        if (check=="all"):
            combineText = "and"
        elif (check=="any"):
            combineText = "or"
        else:
            raise Exception("check parameter '{}' to requiretag should be from [any,all]".format(check))
        #
        tagLabelList = []
        for tag in tagList:
            tagLabelList.append(tag.getNiceObfuscatedLabelWithType(True, reportMode))
        tagListString = jrfuncs.makeNiceCommaAndOrList(tagLabelList, combineText)
        #
        text = "{}".format(tagListString)

    return text
#---------------------------------------------------------------------------













# ---------------------------------------------------------------------------
def funcGainTag(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # player gains one or more tags
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    id = args["id"].getWrapped()
    tagActionKeyword = customData["action"]
    autoDeclarePrefix = jrfuncs.getDictValueOrDefault(customData,"autoDeclarePrefix",None)

    if (autoDeclarePrefix is not None):
        # we are letting them autodeclare a marker tag to be gained
        tagManager = env.getTagManager()
        #
        deadline = args["deadline"].getWrapped()
        label = autoDeclarePrefix + " auto label"
        tagLocation = None
        tagObfuscatedLabel = args["obfuscatedLabel"].getWrapped()
        tagDependencyString = None
        autoDeclaredTag = tagManager.autoDeclareTag(id, autoDeclarePrefix, deadline, label, tagLocation, tagObfuscatedLabel, tagDependencyString, env, astloc, leadp)
        #
        tagList = [autoDeclaredTag]
    else:
        tagList = parseTagListArg(id, "", env, astloc, True)

    #
    boxStyle = args["box"].getWrappedOrDefault("default")

    # record tag use
    for tag in tagList:
        tag.recordGain(env, tagActionKeyword, astloc, leadp)

    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # build results
    results = JrAstResultList()

    # symbol
    if (len(tagList)==1):
        symbol = tagList[0].getSymbol()
    else:
        multiSymbols = []
        for tag in tagList:
            symbol = tag.getSymbol()
            if (symbol not in multiSymbols):
                multiSymbols.append(symbol)
        # all the same kind of symbol tag
        if (len(multiSymbols)>1):
            symbol = "markerGeneric"
        else:
            symbol = multiSymbols[0]

    # box start
    useBox = (boxStyle!="none")
    boxOptions = {
        "box":boxStyle,
        "symbol": symbol,
        "symbolColor": "red",
    }
    if useBox:
        addBoxToResultsIfAppropriateStart(boxOptions, results)

    # we want to tell the player that the tags have been gained
    for tag in tagList:
        addGainTagTextLineToResults(tag, tagActionKeyword, results, reportMode, astloc, entryp, leadp, (not useBox), None)

    # box end
    if useBox:
        addBoxToResultsIfAppropriateEnd(boxOptions, results)

    return results
# ---------------------------------------------------------------------------









# ---------------------------------------------------------------------------
def funcCheckTag(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # check if play has tag
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    boxStyle = args["box"].getWrappedOrDefault("none")
    tagList = parseTagListArg(args["id"].getWrapped(), "", env, astloc, True)
    check = args["check"].getWrapped()
    noif = args["noif"].getWrapped()
    # passed custom test type
    testType = customData["testType"]
    tagActionKeyword = customData["action"]
    #


    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # record tag use
    for tag in tagList:
        tag.recordCheck(env, testType+"_"+tagActionKeyword, astloc, leadp)

    # build results
    results = JrAstResultList()

    # box start
    symbol = "markerGeneric"
    boxOptions = {
        "box":boxStyle,
        "symbol": symbol,
        "symbolColor": "red",
    }
    if (boxStyle!="none"):
        addBoxToResultsIfAppropriateStart(boxOptions, results)

    # tell the player about testing markers
    addCheckTagTextLineToResults(env, tagList, testType, check, tagActionKeyword, results, reportMode, astloc, entryp, leadp, noif)

    # box end
    if (boxStyle!="none"):
        addBoxToResultsIfAppropriateEnd(boxOptions, results)

    return results
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def funcInstructTag(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    boxStyle = args["box"].getWrappedOrDefault("default")
    tagList = parseTagListArg(args["id"].getWrapped(), "", env, astloc, True)
    check = args["check"].getWrapped()
    # passed custom test type
    testType = customData["testType"]
    tagActionKeyword = customData["action"]
    gainKeyword = customData["gain"]

    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # record tag use
    for tag in tagList:
        tag.recordCheck(env, testType+"_"+tagActionKeyword, astloc, leadp)
        tag.recordGain(env, gainKeyword, astloc, leadp)

    # build results
    results = JrAstResultList()

    # box start
    symbol = "markerGeneric"
    boxOptions = {
        "box":boxStyle,
        "symbol": symbol,
        "symbolColor": "red",
    }
    if (boxStyle!="none"):
        addBoxToResultsIfAppropriateStart(boxOptions, results)

    # first the check
    optionNoIf = False
    addCheckTagTextLineToResults(env, tagList, testType, check, tagActionKeyword, results, reportMode, astloc, entryp, leadp, optionNoIf)

    results.flatAdd(", then ")

    # now the action
    addGainTagTextLineToResults(tagList[0], gainKeyword, results, reportMode, astloc, entryp, leadp, False, None)

    # additional
    results.flatAdd(", and ")
    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)    

    # box end
    if (boxStyle!="none"):
        addBoxToResultsIfAppropriateEnd(boxOptions, results)

    return results

# ---------------------------------------------------------------------------









# ---------------------------------------------------------------------------
def funcReserveLead(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    id = args["id"].getWrapped()

    renderer = env.getRenderer()
    hlApi = renderer.getHlApi()
    hlApi.reserveLead(id)
    return AstValNull(astloc, entryp)
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
def funcConfigureLocale(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    language = args["language"].getWrapped()

    data = env.getEnvValueUnwrapped(None, "localeData", None)
    data["language"] = language

    return AstValNull(astloc, entryp)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def funcConfigureDivider(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    id = args["id"].getWrapped()
    path = args["path"].getWrapped()
    pgfornament = args["pgfornament"].getWrapped()
    width = args["width"].getWrapped()
    rule = args["rule"].getWrapped()
    align = args["align"].getWrapped()

    # path to image?
    specialDivider = False
    symbol = None
    imageFullPath = None
    if (path is not None):
        if (path in ["rule","none"]):
            # special paths
            imageFullPath = None
            specialDivider = True
        else:
            symbol = lookupLatexSymbol(path)
            if (symbol is not None):
                path = None
            else:
                [imageFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), path, "Divider image", "embedImage", leadp, env, astloc, False)

    
    if (pgfornament is not None):
        pgfornament = int(pgfornament)

    if (pgfornament is None) and (path is None) and (symbol is None):
        raise makeJriException("You must pass a value for 'path' or 'pgfornament' or 'symbol'.", astloc, None)

    renderer = env.getRenderer()

    id = convertEscapeUnsafePlainTextToLatex(id)
    commandName = "cbDivider" + id

    alignDict = {
        "left": "flushleft",
        "right": "flushright",
        "center": "center",
    }
    alignCommand = alignDict[align]

    #
    safeWidthStr = convertStringToSafeLatexSize(width, r"\columnwidth", r"\columnwidth", r"\columnwidth", 1.0)

    # ok add custom latex
    latexStart = "\\providecommand{\\" + commandName + "}{}" + "\n"
    latexStart += "\\renewcommand{\\" + commandName + "}{" + "\n"

    latexMain = ""
    if (not rule) and (not specialDivider):
        latexMain += "\\begin{" + alignCommand + "}"
    #
    if (pgfornament is not None):
        latexMain += "{\\pgfornament[anchor=center,ydelta=0pt,width=" + safeWidthStr + "]{" + str(pgfornament) + "}}"
    elif (path=="rule"):
        # just a simple rule
        latexMain += r"\rule{0.95\columnwidth}{0.5pt}"
    elif (path=="none"):
        # nothing
        pass
    elif (symbol is not None):
        latexMain += "\\footnotesize\\" + symbol
    else:
        # use an image
        extra = ""
        extra += "width={}".format(safeWidthStr)
        if (extra != ""):
            extra = "[" + extra + "]"
        latexMain += "\\includegraphics{}{{{}}} ".format(extra, imageFullPath)
    #
    if (not rule) and (not specialDivider):
        latexMain += "\\end{" + alignCommand + "}" + "\n"
        if (symbol is None):
            latexMain += "\\vspace*{-1em}" + "\n"

    # side rule wrap
    if (rule):
        latexMain = latexSideRulesAround(latexMain, safeWidthStr)

    # extra spacing
    latexMain = "\\vspace{1em}"+ latexMain + "\\vspace{1em}"

    #
    latexEnd = "}" + "\n"

    renderer.addToPreambleLatex(latexStart + latexMain + latexEnd)

    renderer.setDividerCommand(id, commandName)

    return AstValNull(astloc, entryp)
# ---------------------------------------------------------------------------






#---------------------------------------------------------------------------
# newspaper helpers
def funcNewsPaper(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    style = args["style"].getWrapped()
    articleStyle = args["articleStyle"].getWrapped()
    headlineStyle = args["headlineStyle"].getWrapped()
    bylineStyle = args["bylineStyle"].getWrapped()
    dateAsStr = args["date"].getWrapped()
    dateString = args["dateString"].getWrapped()
    dateStringExtra = args["dateStringExtra"].getWrapped()
    dayNumber = args["day"].getWrapped()
    columns = args["columns"].getWrapped()
    raggedColumns = args["raggedColumns"].getWrapped()
    bannerPath = args["bannerPath"].getWrapped()
    bannerLines = args["bannerLines"].getWrapped()
    priceString = args["priceString"].getWrapped()
    issueString = args["issueString"].getWrapped()
    font = args["font"].getWrapped()
    fontSize = args["fontSize"].getWrapped()
    landscape = args["landscape"].getWrapped()
    parSpaceHead = args["parSpaceHead"].getWrapped()
    parSpaceBody = args["parSpaceBody"].getWrapped()
    lineSpace = args["lineSpace"].getWrapped()
    indent = args["indent"].getWrapped()
    block = args["block"].getWrapped()
    divider = args["divider"].getWrapped()
    effectsOn = args["effectsOn"].getWrapped()
    dropCaps = args["dropCaps"].getWrapped()
    dropCapsMulti = args["dropCapsMulti"].getWrapped()

    # defaults based on style
    paperDict = {
        "nyTimes": {"banner": "newspaper/nyTimesBanner.png"},
        "dailyNews": {"banner": "newspaper/dailyNewsBanner.png"},
        "nyHerald": {"banner": "newspaper/nyHeraldBanner.png"},
        "nyPost": {"banner": "newspaper/nyPostBanner.png"},
        "villager": {"banner": "newspaper/villagerBanner.png", "underBannerFunc": "npUnderBannerAbove"},
        "wsj": {"banner": "newspaper/wsjBanner.jpg"},
        "londonTimes": {"banner": "newspaper/london/londonTimesBanner.jpg"},
        "londonPallMall": {"banner": "newspaper/london/pallMallBanner.jpg"},
        "londonPoliceNews": {"banner": "newspaper/london/policeNewsBanner.jpg"},
        "londonGazette": {"banner": "newspaper/london/gazetteNewsBanner.png"},
        "arkhamAdvertiser": {"banner": "newspaper/other/arkhamAdvertiser.png"},
        "": {"banner": None},
        "blank": {"banner": None},
        "excerpt": {"banner": None},
    }


    # banner (and any related options)
    # ATTN: TODO -- add other default options to make style distinguised
    if (style in paperDict):
        npPaperOptions = paperDict[style]
        imagePath = npPaperOptions["banner"]
        if (bannerLines == False):
            # force
            underBannerFunc = "npUnderBannerAbove"
        else:
            underBannerFunc = jrfuncs.getDictValueOrDefault(npPaperOptions, "underBannerFunc", "npUnderBanner")
    else:
        raise makeJriException("Unknown style for newspaper: '{}'".format(style), astloc)




    # scaling line and paragraph spacing
    parSpaceStr = str(parSpaceHead)+ "em"
    lineSpaceStr = str(lineSpace)


    # assemble result
    results = JrAstResultList()

    renderer = env.getRenderer()

    # latex start
    latex = ""
    latex += r"\npNewsPaperBegin" + "{" + parSpaceStr + "}{" + lineSpaceStr + "}" + "\n"

    # landscape
    if (style=="excerpt"):
         if (priceString is None):
             priceString=""
    elif (landscape):
        latex += r"\npWeatherBoxSetupLandscape" + "\n"
        latex += r"\begin{landscape}" + "\n"
    else:
        pass

    # tweak weatherbox size pased on paper size

    if (renderer.isNarrowPaperSize()) and (not landscape):
        latex += r"\npWeatherBoxSetupPortraitNarrow" + "\n"
    else:
        latex += r"\npWeatherBoxSetupPortrait" + "\n"



    # font
    if (font is not None):
        latexFontCommandAdd = renderer.setFontWithSize(font, None, env, astloc) + " "
        latex += latexFontCommandAdd
    else:
        latexFontCommandAdd = ""

    # font size
    fontSizeParts = parseFontSize(env, fontSize, 8, 7)
    if (fontSizeParts["base"] is not None):
        latex += r"\fontsize{" + str(fontSizeParts["base"]) + "}{" + str(fontSizeParts["spacing"]) + r"}\selectfont" + "\n"


    # add latex so far
    results.flatAdd(vouchForLatexString(latex, False))



    # banner image (overrides style based thing above)
    if (bannerPath is not None) and (bannerPath!=""):
        imagePath = bannerPath

    # banner latex
    if (imagePath is not None):
        [imageFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), imagePath, "Newspaper banner image", "embedImage", leadp, env, astloc, False)
        safeLatexPath = makeLatexSafeFilePath(imageFullPath)
        latex = r"\npBanner{" + safeLatexPath + "}" + "\n"
        results.flatAdd(vouchForLatexString(latex, False))
    else:
        latex = r"\npBannerNone" + "\n"
        results.flatAdd(vouchForLatexString(latex, False))

    # under banner

    # smart date
    if (dateString is not None):
        # use dateStr directly, ignore the rest
        dateStringSafe = convertEscapeUnsafePlainTextToLatex(dateString)
        dayDate = None
    elif (dayNumber is not None):
        # try to use day
        flagAllowTempCalculatedDay = True
        day = findDayByNumber(dayNumber, env, astloc, "newspaper day lookup", flagAllowTempCalculatedDay)
        dayDate = day.getDate()
        dateStr = jrfuncs.niceDayDateStr(dayDate, True, False)
        dateStr = dateStr.upper()
        dateStringSafe = convertEscapeUnsafePlainTextToLatex(dateStr)
    elif (dateAsStr is not None):
        # user gave us a date as DD/MM/YY
        try:
            dayDate = jrfuncs.makeDateTimeFromString(dateAsStr, DefCbDefine_ParseDayConfigureDate)
            dateStr = jrfuncs.niceDayDateStr(dayDate, True, False)
            dateStr = dateStr.upper()
            dateStringSafe = convertEscapeUnsafePlainTextToLatex(dateStr)
        except Exception as e:
            raise makeJriException("Error processing newspaper date: {}".format(str(e)), astloc)
    else:
        raise makeJriException("You need to provide a date/day/datestr in newspaper call", astloc)

    issueStrSafe = None
    priceStrSafe = None

    if (dayDate is not None):
        # try to guess price and volume algorithmically
        year = dayDate.year
        if (priceString is None):
            # new york times yearly costs
            yearlyPriceData = [(1800,1), (1900, 1), (1920, 2), (1940, 3), (1950, 4), (1960, 5), (1980,25), (2000,75)]
            price = str(jrfuncs.estimateCostInYear(year, yearlyPriceData))
            priceStrSafe = convertEscapeUnsafePlainTextToLatex(str(price)) + " cents"
        #
        if (issueString is None):
            # try to guess isse number
            firstDate = datetime(1880, 1, 1)
            firstNumber = 8833
            firstVolume = 29
            [issueNumber, roman_volume] = jrfuncs.estimateIssueAndVolume(dayDate, firstDate, firstNumber, firstVolume)
            issueStr = "VOL. " + roman_volume + "... No. " + f"{issueNumber:,}" + "."
            issueStrSafe = convertEscapeUnsafePlainTextToLatex(issueStr)

    if (issueStrSafe is None):
        if (issueString is None):
            issueStrSafe = ""
        else:
            issueStrSafe = convertEscapeUnsafePlainTextToLatex(issueString)

    if (priceStrSafe is None):
        if (priceString is None) or (priceString==""):
            priceStrSafe = ""
        else:
            priceStrSafe = convertEscapeUnsafePlainTextToLatex(priceString)

    # extra text to add to date info
    if (dateStringExtra is not None):
        dateStringExtraSafe = convertEscapeUnsafePlainTextToLatex(dateStringExtra)
        # add to datestring
        dateStringSafe += " " + dateStringExtraSafe

    #
    latex = "\\" + underBannerFunc + "{" + issueStrSafe + "}"
    latex += r"{" + dateStringSafe + "}"
    latex += r"{" + priceStrSafe + "}" + "\n"
    results.flatAdd(vouchForLatexString(latex, False))



    # ATTN: new attempt to pass newspaper options in hierarchy that news articles can get
    parentNewsPaperState = {
        "style": style,
        "articleStyle": articleStyle,
        "headlineStyle": headlineStyle,
        "bylineStyle": bylineStyle,
        "dropCaps": dropCaps,
        "dropCapsMulti": dropCapsMulti,
        "indent": indent,
        "block": block,
        "divider": divider,
        "parSpaceHead": parSpaceHead,
        "parSpaceBody": parSpaceBody,
        "effectsOn": effectsOn,
        "raggedColumns": raggedColumns,
    }
    henv = env.makeChildEnv()
    henv.createEnvVar(astloc, "newspaperState", "newspaper state variable", parentNewsPaperState, True)
    henv.createEnvVar(astloc, "effectsOn", "newspaper effectsOn", effectsOn, True)


    # columns in base newspaper
    columnsBaseCommand = ""
    if (columns is not None) and (columns>1):
        columnsBaseCommand = r"\npArticleGroup"
        if (raggedColumns):
            columnsBaseCommand += "Star"
        # columns start
        latex = columnsBaseCommand + "Begin{" + str(columns) +"}"
        latex += "\n"
        results.flatAdd(vouchForLatexString(latex, False))


    # contents of targets
    # note that we pass 'henv' as the environment state so that hierarchical children can get our state
    addTargetsToResults(results, targets, rmode, henv, entryp, leadp, False, False)


    # end columns
    if (columns is not None) and (columns>1):
        # columns end
        results.flatAdd(vouchForLatexString(columnsBaseCommand + "End"+"\n", False))


    # landscape end
    if (landscape):
        results.flatAdd(vouchForLatexString(r"\end{landscape}" + "\n", False))

    # latex end
    results.flatAdd(vouchForLatexString(r"\npNewsPaperEnd"+"\n", False))

    # results
    return results




def funcNewsBannerBox(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):

    # assemble result
    results = JrAstResultList()

    # latex start
    results.flatAdd(vouchForLatexString(r"\npBannerBox{", False))

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    # latex end
    results.flatAdd(vouchForLatexString(r"}"+"\n", False))

    # results
    return results



def funcNewsGroup(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    columns = args["columns"].getWrapped()
    raggedColumns = args["raggedColumns"].getWrapped()

    # parent newspaper object values if blank
    newspaperState = env.getEnvValueUnwrapped(astloc, "newspaperState", None)
    #
    raggedColumns = jrfuncs.getOverrideWithDictValueIfBlank(newspaperState, "raggedColumns", raggedColumns)

    # assemble result
    results = JrAstResultList()

    if (columns>1):
        baseCommand = r"\npArticleGroup"
        if (raggedColumns):
            columnsBaseCommand += "Star"
    else:
        baseCommand = r"\npArticleGroupOneCol"

    # latex start

    # columns start
    latex = baseCommand + "Begin{" + str(columns) +"}"
    latex += "\n"
    results.flatAdd(vouchForLatexString(latex, False))

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    # latex end
    results.flatAdd(vouchForLatexString(baseCommand + "End"+"\n", False))

    # results
    return results



def funcNewsArticle(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    style = args["style"].getWrapped()
    block = args["block"].getWrapped()
    dropCaps = args["dropCaps"].getWrapped()
    headline = args["headline"].getWrapped()
    byline = args["byline"].getWrapped()
    headlineStyle = args["headlineStyle"].getWrapped()
    bylineStyle = args["bylineStyle"].getWrapped()
    divider = args["divider"].getWrapped()
    effectsOn = args["effectsOn"].getWrapped()
    size = args["size"].getWrapped()
    font = None

    # parent newspaper object values if blank
    newspaperState = env.getEnvValueUnwrapped(astloc, "newspaperState", None)
    #
    dropCaps = jrfuncs.getOverrideWithDictValueIfBlank(newspaperState, "dropCaps", dropCaps)
    dropCapsMulti = jrfuncs.getDictValueOrDefault(newspaperState, "dropCapsMulti", None)
    block = jrfuncs.getOverrideWithDictValueIfBlank(newspaperState, "block", block)
    headlineStyle = jrfuncs.mergeOveridePipeFeatureStringFromDict(newspaperState, "headlineStyle", headlineStyle)
    bylineStyle = jrfuncs.mergeOveridePipeFeatureStringFromDict(newspaperState, "bylineStyle", bylineStyle)
    indent = jrfuncs.getDictValueOrDefault(newspaperState, "indent", True)
    divider = jrfuncs.getOverrideWithDictValueIfBlank(newspaperState, "divider", divider)
    effectsOn = jrfuncs.getOverrideWithDictValueIfBlank(newspaperState, "effectsOn", effectsOn)
    # parSpace is not adjustible per article but is per newspaper
    parSpaceHead = jrfuncs.getDictValueOrDefault(newspaperState, "parSpaceHead", None)
    parSpaceBody = jrfuncs.getDictValueOrDefault(newspaperState, "parSpaceBody", None)


    renderer = env.getRenderer()

    # newline and other expansions
    if (True):
        # we need to do this early before any case changes, etc.
        headline = jrfuncs.expandUserEscapeChars(headline)
        byline = jrfuncs.expandUserEscapeChars(byline)

    # assemble result
    results = JrAstResultList()

    if (block):
        results.flatAdd(makeMiniPageBlockLatexStart(True, "t"), False)


    # article start
    latex = r"\npArticleBegin" + "\n"

    # different parspace for headline and body
    # add space between paragraphs beyond what newspaper is set to by default
    latex += r"\setlength{\parskip}{" + str(parSpaceHead) + "em}" + "\n"
    #
    results.flatAdd(vouchForLatexString(latex, False))

    #
    startLatex = None
    endLatex = None
    if (style=="box"):
        # start box
        boxOptions = {"box": "npArticle", "padding": "5", "borderWidth": "1" }
        startLatex = wrapInLatexBoxJustStart(boxOptions)
        startLatex += r"\vspace{1em} "
        endLatex = wrapInLatexBoxJustEnd(boxOptions)
        endLatex += r"\vspace{1em} "

    #
    if (startLatex is not None):
        results.flatAdd(vouchForLatexString(startLatex, False))


    # optional headline
    if (headline is not None):
        #latex = newsLatexFormatHeadlineString(env, headline, headlineStyle, {"bold": True, "size": "large", "linespace": "1.5"})
        latex = newsLatexFormatHeadlineString(env, headline, headlineStyle, "bold=true|size=large|lineSpace=1.2")
        results.flatAdd(vouchForLatexString(latex, False))

    # optional byline
    if (byline is not None):
        #latex = newsLatexFormatBylineString(env, byline, bylineStyle, {"italic": True})
        latex = newsLatexFormatBylineString(env, byline, bylineStyle, "italic=true")
        results.flatAdd(vouchForLatexString(latex, False))


    # par spacing for body
    latex = ""
    if (indent):
        # indent paragraphs
        latex += r"\setlength{\parindent}{0.2cm}" + "\n"
        if (True):
            #parSpaceBody -= 0.15
            latex += r"\setlength{\parskip}{" + str(parSpaceBody) + "em}" + "\n"
    else:
        # add space between paragraphs beyond what newspaper is set to by default
        latex += r"\setlength{\parskip}{" + str(parSpaceBody) + "em}" + "\n"
    results.flatAdd(vouchForLatexString(latex, False))

    # set a child env so we can set a temp value in it
    henv = env.makeChildEnv()
    henv.createEnvVar(astloc, "effectsOn", "newspaper effectsOn", effectsOn, True)

    # font override
    # if they dont specify a font but so specify a size, then force default font size
    if (font is not None) or (size is not None):
        # add font
        latexFontCommandAdd = renderer.setFontWithSize(font, size, env, astloc) + " "
        results.flatAdd(vouchForLatexString(latexFontCommandAdd,True))


    # contents of targets
    if (dropCaps is not None) and (dropCaps!="none"):
        # options
        optionLines = 2
        optionFindent = "0.25em"
        optionNindent = "0em"
        optionLhang = "0"
        optionProtectStyle = dropCapsMulti
        # assemble result
        optionPreferAfterNoteType = DefCbResultNoteTypePreArticleBodyEnd
        flagStripEndingNewlines = True
        dropCapResultRetv = dropCapResults(dropCaps, optionPreferAfterNoteType, targets, rmode, henv, entryp, leadp, astloc, optionLines, optionFindent, optionNindent, optionLhang, optionProtectStyle, flagStripEndingNewlines)

        results.flatAdd(dropCapResultRetv, False)
    else:
        # normal results
        addTargetsToResults(results, targets, rmode, henv, entryp, leadp, False, False)

    if (endLatex is not None):
        results.flatAdd(vouchForLatexString(endLatex, False))

    # article end
    results.flatAdd(vouchForLatexString(r"\npArticleEnd"+"\n", False))

    # divider
    if (divider=="none"):
        # no divider
        latex = ""
    elif (divider is None) or (divider == True):
        # defaults on, to standard full rule
        latex = "\\npDividerFull" + "\n"
    elif (isinstance(divider, str)):
        latex = renderer.generateLatexForDivider(divider, astloc)
    else:
        # no divider, needs space
        latex = "\\vspace*{1.5em}"
    results.flatAdd(vouchForLatexString(latex, False), False)

    if (block):
        # hmm why do we need this?
        latex = "\\vspace*{1.5em}"
        results.flatAdd(vouchForLatexString(latex, False), False)
        #
        results.flatAdd(makeMiniPageBlockLatexEnd(True), False)

    # results
    return results



# Move to just use normal $image func
def funcNewsImage_OLDUNUSED(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    path = args["path"].getWrapped()
    style = args["style"].getWrapped()
    caption = args["caption"].getWrapped()
    width = args["width"].getWrapped()

    # assemble result
    results = JrAstResultList()

    # scale with from 10 to 100
    width = convertNumericWidthToFraction(width)

    # image
    [imageFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), path, "Newspaper image", "embedImage", leadp, env, astloc, False)
    safeImagePath = makeLatexSafeFilePath(imageFullPath)
    if (style=="bordered"):
        latexCommand = r"\npImageBordered"
        # make it slightly smaller for bordered images
        width -= 0.05
    elif (style in ["", "unbordered"]):
        latexCommand = r"\npImage"
    else:
        raise makeJriException("Unknown newspaper image style '{}' shouild be [bordered|unbordered].".format(style), astloc)

    # latex command to bring in image
    latex = latexCommand + "{" + safeImagePath +"}" + "{" + caption +"}" + "{" + str(width) + "}" + "\n"
    results.flatAdd(vouchForLatexString(latex, False))

    # experimental attempt to avoid double linebreak afterwards
    if (True):
        deferredResult = CbDeferredBlockAbsorbFollowingNewline(astloc, entryp, leadp)
        results.flatAdd(deferredResult)

    # results
    return results



def funcNewsHeadline(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    style = args["style"].getWrapped()
    fit = args["fit"].getWrapped()
    bold = args["bold"].getWrapped()
    underline = args["underline"].getWrapped()
    italic = args["italic"].getWrapped()
    case = args["case"].getWrapped()

    # parent newspaper object
    newspaperState = env.getEnvValueUnwrapped(astloc, "newspaperState", None)
    # use parent settings if blank
    if ("headlineStyle" in newspaperState):
        headlineStyle = newspaperState["headlineStyle"]
        if (headlineStyle is not None):
            if (underline is None) and ("underline" in headlineStyle):
                underline = True
            if (italic is None) and ("italic" in headlineStyle):
                italic = True
            if (bold is None) and ("bold" in headlineStyle):
                bold = True
            if (case is None) and ("upper" in headlineStyle):
                case = "upper"
            if (case is None) and ("title" in headlineStyle):
                case = "title"
            if (fit is None) and ("fit" in headlineStyle):
                fit = True


    # default is bold
    if (bold is None):
        bold = True

    # assemble result
    results = JrAstResultList()
    
    # headline latex start group
    results.flatAdd(vouchForLatexString(r"\npHeadline{", False))

    # extra latex
    formattingDict = createStartEndLatexForFontSizeString(style)

    # fit and bold
    if (fit is not None) and (fit):
        formattingDict["start"] += r"\resizebox{\columnwidth}{!}{"
        formattingDict["end"] += r"}"
    if (bold is not None) and (bold):
        formattingDict["start"] += r"\textbf{"
        formattingDict["end"] += r"}"
    if (underline is not None) and (underline):
        formattingDict["start"] += r"\underline{"
        formattingDict["end"] += r"}"
    if (italic is not None) and (italic):
        formattingDict["start"] += r"\textit{"
        formattingDict["end"] += r"}"


    # style start
    results.flatAdd(vouchForLatexString(formattingDict["start"], False))

    # contents of targets (with changeBlankLinestoNewlines=True)
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, True, False)

    # style end
    results.flatAdd(vouchForLatexString(formattingDict["end"], False))

    # headline latex end group
    results.flatAdd(vouchForLatexString(r"}", False))

    # add a non-rendering note that we can look for (this is used in newspaperArticle function to skip over headlines when doing things like dropcaps, etc.)
    results.flatAdd(ResultAtomNote({"type": DefCbResultNoteTypePreArticleBodyEnd}))

    results.flatAdd(CbDeferredBlockAbsorbFollowingNewline(astloc, entryp, leadp))

    # results
    return results




def funcNewsByLine(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    style = args["style"].getWrapped()
    fit = args["fit"].getWrapped()
    bold = args["bold"].getWrapped()
    emph = True

    # assemble result
    results = JrAstResultList()
    
    # headline latex start group
    results.flatAdd(vouchForLatexString(r"\npByLine{", False))

    # extra latex
    formattingDict = createStartEndLatexForFontSizeString(style)

    # fit and bold
    if (fit):
        formattingDict["start"] += r"\resizebox{\columnwidth}{!}{"
        formattingDict["end"] += r"}"
    if (bold):
        formattingDict["start"] += r"\textbf{"
        formattingDict["end"] += r"}"
    if (emph):
        formattingDict["start"] += r"\emph{"
        formattingDict["end"] += r"}"

    # style start
    results.flatAdd(vouchForLatexString(formattingDict["start"], False))

    # contents of targets (with changeBlankLinestoNewlines=True)
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, True, False)

    # style end
    results.flatAdd(vouchForLatexString(formattingDict["end"], False))

    # headline latex end group
    results.flatAdd(vouchForLatexString(r"}", False))

    # add a non-rendering note that we can look for (this is used in newspaperArticle function to skip over headlines when doing things like dropcaps, etc.)
    results.flatAdd(ResultAtomNote({"type": DefCbResultNoteTypePreArticleBodyEnd}))

    results.flatAdd(CbDeferredBlockAbsorbFollowingNewline(astloc, entryp, leadp))

    # results
    return results



def funcNewsRule(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # divider rule
    style = args["style"].getWrapped()

    # assemble result
    results = JrAstResultList()

    penaltyLatex = "" #r"\penalty-1"
    if (style=="full"):
        latex = penaltyLatex + "\n" + r"\npDividerFull"
    elif (style=="half"):
        latex = penaltyLatex + "\n" + r"\npDividerHalf"
    else:
        raise makeJriException("In function ({}) unknown divider style '{}'.".format(funcName, style), astloc)
    #
    results.flatAdd(vouchForLatexString(latex, False))

    results.flatAdd(CbDeferredBlockAbsorbFollowingNewline(astloc, entryp, leadp))

    # results
    return results


def funcNewsEndLine(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # divider rule
    text = args["text"].getWrapped()

    # assemble result
    results = JrAstResultList()

    textSafe = convertEscapeUnsafePlainTextToLatex(text)
    results.flatAdd(vouchForLatexString(r"\npEndLine{" + textSafe + "}", False))

    results.flatAdd(CbDeferredBlockAbsorbFollowingNewline(astloc, entryp, leadp))

    # results
    return results
#---------------------------------------------------------------------------





#---------------------------------------------------------------------------
def funcFingerprint(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # ATTN: should we deprecate this in favor of standard image and $fingerprintPath()
    id = args["id"].getWrapped()
    fingerId = args["finger"].getWrapped()
    impression = args["impression"].getWrapped()
    style = args["style"].getWrapped()
    width = args["width"].getWrapped()
    align = args["align"].getWrapped()
    showId = args["showId"].getWrapped()
    caption = args["caption"].getWrapped()

    if (align is None):
        align="left"

    # ok ask the hlapi to go find the fingerprint for us
    renderer = env.getRenderer()
    hlApi = renderer.getHlApi()
    try:
        [relativePath, imageFullPath, fingerCaption] = hlApi.lookupFingerprintImagePath(id, fingerId, impression)
    except Exception as e:
        raise makeJriException(str(e), astloc)

    # assemble result
    results = JrAstResultList()

    # build latex includegraphics command
    heightStr = ""
    # caption
    if (caption is None):
        caption = fingerCaption if (showId) else None
    else:
        if showId:
            caption = "{} ({})".format(caption, fingerCaption)
    if (caption is not None):
        caption = renderer.convertMarkdownToLatexDontVouch(caption, True, True)
    #
    borderWidth = 0
    padding = 2
    captionPos = None
    optionWrapText = False
    imageLatex = generateImageEmbedLatex(env, imageFullPath, width, heightStr, borderWidth, padding, align, None, caption, captionPos, None, False, optionWrapText)

    # add it
    results.flatAdd(vouchForLatexString(imageLatex, False))

    # add note for debug report
    notePath = "fingerprints" + "/" + relativePath
    msg = 'Embedded fingerprint image: "{}"'.format(notePath)
    msgLatex = 'Embedded fingerprint image: "\\path{' + notePath + '}"'
    extras = {"filePath": imageFullPath, "caption": caption, "fpLead":id, "fpFinger": fingerId, "set": False}
    note = JrINote("fingerPrint", leadp, msg, msgLatex, extras)
    env.addNote(note)

    # results
    return results
#---------------------------------------------------------------------------










#---------------------------------------------------------------------------
def funcFingerprintSet(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # divider rule
    id = args["id"].getWrapped()
    style = args["style"].getWrapped()
    showId = args["showId"].getWrapped()
    caption = args["caption"].getWrapped()

    renderer = env.getRenderer()
    hlApi = renderer.getHlApi()
    try:
        person = hlApi.lookupFingerprintPerson(id)
    except Exception as e:
        raise makeJriException(str(e), astloc)

    # caption
    niceCaption = person.getPlayerCaption()
    if (caption is None):
        caption = niceCaption if (showId) else None
    else:
        if showId:
            caption = "{} ({})".format(caption, niceCaption)
    if (caption is not None):
        caption = renderer.convertMarkdownToLatexDontVouch(caption, True, True)

    # ok ask the hlapi to go find the fingerprint for us

    hlApi = renderer.getHlApi()
    latex = ""
    try:
        columnCountL = leadp.calcLeadColumns()
        flagCompact = (columnCountL>1)
        latex = hlApi.generateFingerprintSetLatexByLeadId(id, caption, flagCompact)
    except Exception as e:
        raise makeJriException(str(e), astloc)

    # assemble result
    results = JrAstResultList()

    # add it
    results.flatAdd(vouchForLatexString(latex, False))

    # ok ask the hlapi to go find the fingerprint for us
    try:
        fingerId = "L1"
        impression = "2"
        [relativePath, imageFullPath, fingerCaption] = hlApi.lookupFingerprintImagePath(id, fingerId, impression)
    except Exception as e:
        raise makeJriException(str(e), astloc)

    # add note for debug report
    msg = 'Embedded fingerprint set: "{}"'.format(id)
    msgLatex = msg
    extras = {"filePath": imageFullPath, "caption": caption, "fpLead":id, "fpFinger": fingerId, "set": True}
    note = JrINote("fingerPrintSet", leadp, msg, msgLatex, extras)
    env.addNote(note)

    # results
    return results
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcFingerprintPath(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # divider rule
    id = args["id"].getWrapped()
    fingerId = args["finger"].getWrapped()
    impression = args["impression"].getWrapped()

    # ok ask the hlapi to go find the fingerprint for us
    renderer = env.getRenderer()
    hlApi = renderer.getHlApi()
    try:
        [relativePath, imageFullPath, fingerCaption] = hlApi.lookupFingerprintImagePath(id, fingerId, impression)
    except Exception as e:
        raise makeJriException(str(e), astloc)

    # add note for debug report
    notePath = "fingerprints" + "/" + relativePath
    msg = 'Embedded fingerprint image path: "{}"'.format(notePath)
    msgLatex = 'Embedded fingerprint image path: "\\path{' + notePath + '}"'
    extras = {"filePath": imageFullPath, "caption": fingerCaption, "fpLead":id, "fpFinger": fingerId, "set": False}
    note = JrINote("fingerPrint", leadp, msg, msgLatex, extras)
    env.addNote(note)

    return relativePath
#---------------------------------------------------------------------------















#---------------------------------------------------------------------------
def funcAdjustTrack(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # divider rule
    id = args["id"].getWrapped()
    val = args["val"].getWrapped()
    min = args["min"].getWrapped()
    max = args["max"].getWrapped()
    modType = customData

    trackSafe = convertEscapeUnsafePlainTextToLatex(id)

    # build results
    results = JrAstResultList()

    if (modType=="set"):
        if (type(val) is str):
            val = '"' + val + '"'
        valSafe = convertEscapeUnsafePlainTextToLatex(val)
        text = _("In your case log, record that the current value of **track {}** is: **{}**.").format(trackSafe, valSafe)
    else:
        if (val<0):
            valSafe = convertEscapeUnsafePlainTextToLatex(str(val*-1))
            text = _("In your case log, **reduce** the current value of **track {}** by **{}**").format(trackSafe, valSafe)
            if (min is not None):
                text += ", but not less than " + convertEscapeUnsafePlainTextToLatex(min)
        else:
            valSafe = convertEscapeUnsafePlainTextToLatex(str(val))
            text = _("In your case log, **increase** the current value of **track {}** by **+{}**").format(trackSafe, valSafe)
            if (max is not None):
                text += _(", but not greater than ") + convertEscapeUnsafePlainTextToLatex(max)
        text += "."

    # box start
    symbol = "track"
    boxOptions = {
        "box": "default",
        "symbol": symbol,
        "symbolColor": "red",
    }
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    # add text
    results.flatAdd(text)

    # box end
    addBoxToResultsIfAppropriateEnd(boxOptions, results)

    # results
    return results
#---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def funcDefineFont(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    id = args["id"].getWrapped()
    path = args["path"].getWrapped()
    size = args["size"].getWrapped()
    scale = args["scale"].getWrapped()
    color = args["color"].getWrapped()
    hyphenate = args["hyphenate"].getWrapped()
    monoSpace = args["monoSpace"].getWrapped()
    ignoreDupe = args["ignoreDupe"].getWrapped()
    # this defines a font that will be available when creating the document
    # but requires some commands be added to the preamble

    # it's all handled through renderer
    # later when we want to USE this font, we will ask the renderer for it

    renderer = env.getRenderer()
    renderer.defineFont(id, path, size, scale, color, hyphenate, monoSpace, ignoreDupe, env, astloc)

    # just return blank
    return AstValNull(astloc, entryp)
# ---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcDebugFonts(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # debug all fonts

    size = args["size"].getWrapped()
    scale = args["scale"].getWrapped()
    color = args["color"].getWrapped()
    hyphenate = args["hyphenate"].getWrapped()
    monoSpace = args["monoSpace"].getWrapped()
    ignoreDupe = False

    # build results
    results = JrAstResultList()

    # to show
    modSizes = [None]
    #
    sampleText =  "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "\n"
    sampleText += "abcdefghijklmnopqrstuvwxyz" + "\n"
    sampleText += "0123456789.\"-,'" + "\n"
    sampleTextLatex = convertEscapeUnsafePlainTextToLatex(sampleText)

    # iterate known fonts, define each one
    renderer = env.getRenderer()
    fontHelper = env.getFileManagerFontsShared()
    fontFiles = fontHelper.getFileDict()
    for k, v in fontFiles.items():
        fullPath = v[0]
        path = k
        dirPath, baseFilename = jrfuncs.splitFilePathToPathAndFile(fullPath)
        #baseFilenameNoExtension, extension  = jrfuncs.splitFileNameToExtension(baseFilename)
        id = convertIdToSafeLatexId(baseFilename)
        renderer.defineFont(id, path, size, scale, color, hyphenate, monoSpace, ignoreDupe, env, astloc)
        #
        # use font in a sample
        for modSize in modSizes:
            if (modSize is not None):
                text = "FONT PATH: {} ({})\n".format(path, modSize)
            else:
                text = "FONT PATH: {}\n".format(path)
            #
            results.flatAdd(text)
            # start
            latex = "{" + renderer.setFontWithSize(id, modSize, env, astloc) + " "
            results.flatAdd(vouchForLatexString(latex, False))
            # contents of targets
            if (targets is not None) and (len(targets)>0):
                addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)
                results.flatAdd("\n")
            # and now sample text
            latex =  " " + sampleTextLatex
            results.flatAdd(vouchForLatexString(latex, False))
            # end
            latex =  "}" + "\n\n"
            results.flatAdd(vouchForLatexString(latex, False))

    return results
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcImageBehind(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Embed an image into a pdf

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    renderer = env.getRenderer()

    # args
    path = args["path"].getWrapped()
    width = args["width"].getWrapped()
    opacity = args["opacity"].getWrapped()
    padding = args["padding"].getWrapped()
    height = args["height"].getWrapped()
    scale = args["scale"].getWrapped()
    align = args["align"].getWrapped()
    shadow = args["shadow"].getWrapped()
    caption = args["caption"].getWrapped()
    captionPos = args["captionPos"].getWrapped()
    captionSize = args["captionSize"].getWrapped()

    fixedSmallPaddingWidth = 0.025

    # ATTN: we use two different techniques here, depending on whether we want the background image to size automatically to the text
    # or whether we want it at full width/height and preserved aspect ratio with text in the center

    # find image, raise exception if not found
    [imageFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), path, "Image behind Text", "embedImage", leadp, env, astloc, False)
    # exception would already be raised if warnOnMissingImage is false
    # build latex includegraphics command
    pathLatex = makeLatexSafeFilePath(imageFullPath)

    # other options
    if (align=="center"):
        valign = "center"
    else:
        valign = "top"
    #
    extraParamList = []
    if (height is not None):
        extraParamList.append("{}={}\\textheight".format("height", height))

    # user watermark style image?
    if (scale!="image"):
        # add option to show watermark graphcis in tcolorbox
        extraParamList.append("watermark graphics=" + pathLatex)
    else:
        # we will show graphics in tikz image
        extraParamList.append("top=-1em, bottom=-1em")

    if (False):
        extraParamList.append("boxrule=1pt, borderline={0.5mm}{0mm}{blue, dashed}")

    if (scale=="zoom"):
        # keep aspect ratio doesn't work currently, we dont know how to force it
        extraParamList.append("watermark overzoom=1.0")
    elif (scale=="stretch"):
        extraParamList.append("watermark stretch=1.0")
    if (shadow):
        #extraParamList.append("drop shadow={black!50!white,opacity=0.5,xshift=2mm,yshift=-2mm}")
        extraParamList.append("drop shadow")

    #
    extraParams = ", ".join(extraParamList)

    
    # build results
    results = JrAstResultList()

    # FIRST save contents
    preCommand = ""
    postCommand = ""
    # new code to handle scale image
    twidth = "\\textwidth"
    if (scale=="image"):
        # wrap text in tikz node with image overlay
        twidth = str (1.0 - (padding*2)) + "\\linewidth"
        preCommand += "% TikZ picture environment to overlay text on the image\n"
        preCommand += "\\begin{tikzpicture}\n"
        preCommand += "\\node[anchor=south west, inner sep=0, opacity=" + str(opacity) + "] (image) at (0,0) {\\includegraphics[width=1\\linewidth]{" + pathLatex + "}};\n"
        preCommand += "% Ensure the node text is on top of the image\n"
        textNodeBaseOptions = "inner sep=0pt "
        #textNodeBaseOptions = "inner sep=" + str(padding)+ "\\linewidth, text width=" + str (1.0 - (paddingWidth*2)) + "\\linewidth"

        if (padding>0):
            xyshift = "[xshift={}\\linewidth,yshift=-{}\\linewidth]".format(padding,padding)
        else:
            xyshift = ""

        if (align=="center"):
            # align to center
            preCommand += "\\node[" + textNodeBaseOptions + "] at (" + xyshift + "image.center) {\n"
        else:
            # align to top
            preCommand += "\\node[" + textNodeBaseOptions + ", anchor=north west] at (" + xyshift + "image.north west) {\n"
    #
    #preCommand += "\\begin{minipage}{\\textwidth}\n"
    preCommand += "\\begin{minipage}[t]{" + twidth + "}\n"
    #
    if (align=="center"):
        preCommand += "\\centering\n"
    #
    postCommand += "\\end{minipage} "
    #
    if (scale=="image"):
        postCommand += "};\n" + "\\end{tikzpicture}"

    textCommand = "\\cbImageBehindTempText"
    addTargetsToResultsIntoCommand(textCommand, preCommand, postCommand, results, targets, rmode, env, entryp, leadp, False, False)

    # now the command which will use this text
    widthStr = convertStringToSafeLatexSize(width, r"\columnwidth", r"\columnwidth", r"\columnwidth", 1.0)
    latex = "\\imageBehindFull{"+widthStr+"}" + "{"+str(fixedSmallPaddingWidth)+"}" + "{"+str(opacity)+"}" + "{"+valign+"}" + "{"+ extraParams + "}" + "{" + textCommand + "}"


    if (True):
        flagTightCaption = True
        flagWrapInMiniPage = False
        flagUnboxable = True
        optionWrapText = False
        latex = wrapInFigure(env, latex, caption, align, captionPos, captionSize, flagTightCaption, False, flagWrapInMiniPage, flagUnboxable, optionWrapText)

    results.flatAdd(vouchForLatexString(latex, False))
    return results
#---------------------------------------------------------------------------





#---------------------------------------------------------------------------
def funcImageMask(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Embed an image into a pdf

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    renderer = env.getRenderer()

    # args
    path = args["path"].getWrapped()
    width = args["width"].getWrapped()
    align = args["align"].getWrapped()
    caption = args["caption"].getWrapped()
    captionPos = args["captionPos"].getWrapped()
    captionSize = args["captionSize"].getWrapped()

    # we need to get this image in two versions, by adding a suffics 

    # find image(s), raise exception if not found
    pathForeground = jrfuncs.addSuffixToPath(path, "Foreground")
    pathBackground = jrfuncs.addSuffixToPath(path, "Background")
    [imageFullPathForeground, warningText1] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), pathForeground, "Masked image (foreground)", "embedImage", leadp, env, astloc, False)
    [imageFullPathBackground, warningText2] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), pathBackground, "Masked image (background)", "embedImage", leadp, env, astloc, False)
    # exception would already be raised if warnOnMissingImage is false
    # build latex includegraphics command
    pathLatexForeground = makeLatexSafeFilePath(imageFullPathForeground)
    pathLatexBackground = makeLatexSafeFilePath(imageFullPathBackground)

    #
    extraParams = ""

    
    # build results
    results = JrAstResultList()

    # FIRST save contents
    preCommand = ""
    postCommand = ""

    widthStr = convertStringToSafeLatexSize(width, r"\columnwidth", r"\columnwidth", r"\columnwidth", 1.0)

    # wrap text in tikz node with image overlay
    preCommand += "% TikZ picture environment to overlay text on the image\n"
    if (align=="center"):
        preCommand += r"\begin{center}" + "\n"
    preCommand += "\\begin{tikzpicture}\n"
    preCommand += r"\node[anchor=west, inner sep=0pt, remember picture] (image) at (0,0) {\phantom{\includegraphics[width=" + widthStr + r"]{" + pathLatexForeground + "}}};" + "\n"
    preCommand += r"\node[anchor=west, inner sep=0pt, opacity=1.0] at (0,0) {\includegraphics[width=" + widthStr + r"]{" + pathLatexForeground + "}};" + "\n"
    preCommand += r"% Begin scope for clipping" + "\n"
    preCommand += r"\begin{scope}" + "\n"
    preCommand += r"% Clip to the bounding box of the 'image' node" + "\n"
    preCommand += r"\clip (image.south west) rectangle (image.north east);" + "\n"
    preCommand += r"\node[anchor=west, inner sep=0pt] (text) at (0,0) {" + "\n"
    #
    preCommand += "\\begin{minipage}{" + widthStr + "}\n"
    if (align=="center"):
        preCommand += "\\begin{center}\n"
    #
    #if (align=="center"):
    #    preCommand += "\\centering\n"
    #
    # NOW POSTCOMMAND AFTER THE TEXT
    if (align=="center"):
        postCommand += "\\end{center}\n"
    #
    postCommand += "\\end{minipage} "
    #
    postCommand += "};\n"
    postCommand += r"\end{scope}" + "\n"
    postCommand += r"% Overlay the semi-transparent image" + "\n"
    postCommand += r"\node[anchor=west, inner sep=0pt, opacity=1.0] at (0,0) {\includegraphics[width=" + widthStr + r"]{" + pathLatexBackground + "}};" + "\n"
    postCommand += r"\end{tikzpicture}" + "\n"
    if (align=="center"):
        postCommand += r"\end{center}" + "\n"

    textCommand = "\\cbImageBehindTempText"
    addTargetsToResultsIntoCommand(textCommand, preCommand, postCommand, results, targets, rmode, env, entryp, leadp, False, False)

    latex = textCommand

    if (True):
        flagTightCaption = True
        flagWrapInMiniPage = False
        flagUnboxable = True
        optionWrapText = False
        latex = wrapInFigure(env, latex, caption, align, captionPos, captionSize, flagTightCaption, False, flagWrapInMiniPage, flagUnboxable, optionWrapText)

    results.flatAdd(vouchForLatexString(latex, False))
    return results
#---------------------------------------------------------------------------


























#---------------------------------------------------------------------------
def funcCipher(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Embed an image into a pdf

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    method = args["method"].getWrapped()
    key = args["key"].getWrapped()
    removePunctuation = args["removePunctuation"].getWrapped()
    spellDigits = args["spellDigits"].getWrapped()
    format = args["format"].getWrapped()
    debug = args["debug"].getWrapped()
    case = args["case"].getWrapped()

    # create the cipher using pycipher library
    # see https://pycipher.readthedocs.io/en/master/#the-ciphers
    debugString = ""
    cipher = None
    blockSize = None
    stripSpaces = False
    replaceDict = None
    optionRemoveReplaceNonLetters = False
    puntuationArg = False
    preReplaceDict = None
    outputCharSize = 1
    spaceReplaceChar = '*'
    padToEvenLengthPlaintext = False
    #
    if (method=="caesar"):
        cipher = pycipher.Caesar(key=int(key))
        puntuationArg = True
    elif (method=="substitution"):
        cipher = pycipher.SimpleSubstitution(key=cipherMakeRandomSubstitutionKeyFromHash(key))
        puntuationArg = True
    elif (method=="plain"):
        cipher = cipherPlain()
        puntuationArg = True
    elif (method=="keyword"):
        cipher = pycipher.SimpleSubstitution(key=cipherMakeSimpleSubstitutionKeyFromKeyword(key))
        puntuationArg = True
    elif (method=="atbash"):
        cipher = pycipher.Atbash()
        puntuationArg = True
    elif (method=="vigenere"):
        cipher = pycipher.pycipher.Vigenere(key)
        optionRemoveReplaceNonLetters = True
        spaceReplaceChar = ' '
    elif False and (method=="railfence"):
        # DISABLED BECAUSE IT DOESNT FORMAT WELL
        cipher = pycipher.Railfence(key=int(key))
        stripSpaces = True
        blockSize = int(key)
    elif False and (method=="playfair"):
        # DISABLED BECAUSE IT DOESNT FORMAT WELL
        cipher = pycipher.Playfair(key=cipherMakeUniqueKeywordAlphabet(key,25))
        preReplaceDict = {'J':'I'}
        optionRemoveReplaceNonLetters = True
        spaceReplaceChar = ' '
        padToEvenLengthPlaintext = True
    elif (method=="polybius"):
        cipher = pycipher.PolybiusSquare(key=cipherMakeUniqueKeywordAlphabet(key,25), size=5, chars="12345")
        preReplaceDict = {'J':'I'}
        blockSize = 2
        optionRemoveReplaceNonLetters = True
        spaceReplaceChar = '*'
        outputCharSize = 2
    elif (method=="morse"):
        cipher = cipherMorseCode()
        #optionRemoveReplaceNonLetters = True
        #outputCharSize = 1
        #if True and (format):
        #    replaceDict = {" ": " ~"}
    #
    if (cipher is None):
        raise makeJriException("Unknown cipher method '{}'.".format(method), astloc)

    # build results
    results = JrAstResultList()

    # debug string
    debugString = "DEBUG NOTE: Applying cipher '{}' with key '{}' (spellDigits={}, removePunctuation={}, format={}):".format(method, key, spellDigits, removePunctuation, format)


    if (removePunctuation) and puntuationArg:
        # we want to remove punctuation AND this cipher has an explicit option for it
        # we need something to break it up
        if (not format):
            format = True
        if (blockSize is None):
            blockSize = 5

    # we need to walk through our target blocks and convert all text entries
    fixes = None
    flagChangeBlankLinesToLatexNewlines = False
    if (debug):
        results.flatAdd(debugString + "\n", False)
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, leadp)
        if (targetRetv is None):
            continue
        targetResultList = convertTargetRetvToResultList(targetRetv)
        contents = targetResultList.getContents()
        for targetBlock in contents:
            text = getTargetResultBlockAsTextIfAppropriate(targetBlock)
            if (text is not None):
                if (spellDigits):
                    text = cipherSpellDigits(text)
                if (stripSpaces):
                    text = cipherStripChars(text, " ")
                if (removePunctuation):
                    text = cipherRemoveReplacePunctuation(text)
                if (optionRemoveReplaceNonLetters):
                    [text, fixes] = cipherReplaceNonLettersReturnFixList(text, spaceReplaceChar, padToEvenLengthPlaintext)
                if (case is not None):
                    text = jrfuncs.applyCaseChange(text, case)
                #
                if (preReplaceDict is not None):
                    # substitue I for j, etc.
                    text = text.upper()
                    text = jrfuncs.replaceStrings(text, preReplaceDict)
                #
                if (puntuationArg):
                    textCiphered = cipher.encipher(text, not removePunctuation)
                else:
                    textCiphered = cipher.encipher(text)
                #
                if (fixes is not None) and (not removePunctuation):
                    # put back punctuation, spaces, etc.
                    textCiphered = cipherReplaceFixList(textCiphered, fixes, outputCharSize)
                #
                if (format):
                    if (blockSize is not None):
                        # segment
                        textCiphered = cipherSegment(textCiphered, blockSize, "X")
                if (replaceDict is not None):
                    textCiphered = jrfuncs.replaceStrings(textCiphered, replaceDict)
                #

                # change case again
                if (case is not None):
                    textCiphered = jrfuncs.applyCaseChange(textCiphered, case)

                results.flatAdd(textCiphered, flagChangeBlankLinesToLatexNewlines)
            else:
                # not a text block, add it as is
                # ATTN: jesse fixing this 5/29/25 based not on a problem but what seems a clear mistake
                #results.flatAdd(targetRetv, flagChangeBlankLinesToLatexNewlines)
                results.flatAdd(targetBlock, flagChangeBlankLinesToLatexNewlines)

    return results
#---------------------------------------------------------------------------






#---------------------------------------------------------------------------
def funcRedact(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Embed an image into a pdf

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    text = args["text"].getWrapped()

    # build results
    results = JrAstResultList()

    if (len(targets)>0) or (text is not None):
        # start redaction
        latex = "\\blackout{"
        results.flatAdd(vouchForLatexString(latex, False))

        #  plaintext will be converted via markdown, etc.
        if (text is not None):
            results.flatAdd(text)

        # contents of targets
        addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)
        
        # end
        latex = "} "
        results.flatAdd(vouchForLatexString(latex, False))

    return results



def funcCensor(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Embed an image into a pdf

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    text = args["text"].getWrapped()

    #censorCommand = "censor"
    censorCommand = "blackout"

    latex = "\\" + censorCommand + "{" + convertEscapeUnsafePlainTextToLatex(text) + "} "
    return vouchForLatexString(latex, True)
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcDefineFunc(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Define a new user function

    # args
    id = args["id"].getWrapped()
    params = args["params"].getWrapped()
    description = args["description"].getWrapped()
    customData = args["customData"].getWrapped()

    # now we are goint to convert the arg list to a CParam list and then create a new proper wrapped function
    cParamList = []
    if (params is not None):
        for paramAst in params:
            # each param in the params list should be a dictionaryu with a name, type, default
            param = paramAst.getWrapped()
            name = unwrapIfWrappedVal(param["name"])
            description = unwrapIfWrappedVal(jrfuncs.getDictValueOrDefault(param, "description", None))
            defaultVal = unwrapIfWrappedVal(jrfuncs.getDictValueOrDefault(param, "defaultVal", None))
            flagAllowNull = unwrapIfWrappedVal(jrfuncs.getDictValueOrDefault(param, "flagAllowNull", False))
            paramTypeString = unwrapIfWrappedVal(jrfuncs.getDictValueOrDefault(param, "type", "any"))
            paramCheck = unwrapIfWrappedVal(convertTypeStringToAstType(paramTypeString))
            flagResolveIdentifiers = False
            cparam = CbParam(name, description, defaultVal, flagAllowNull, paramCheck, flagResolveIdentifiers)
            #
            cParamList.append(cparam)

    wrappedCustomData = {
        "customDataInner": customData,
        "functionContents": targets,
    }

    # dynamically create a new function
    targetBlockCount = "any"
    wrappedFunction = CbFunc(id, description, cParamList,
        "text", targetBlockCount, wrappedCustomData,
        funcRunUserFunction
        )
    # register the wrapped function
    env.loadFuncsFromList(astloc, [wrappedFunction])

    return AstValNull(astloc, entryp)



def funcRunUserFunction(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # this function will be called when user CALLS a user defined function

    # ok now we get any customData set when function we defined
    customDataInner = customData["customDataInner"]

    # and the actual function contents/code
    functionContents = customData["functionContents"]

    # ok create a new child environment
    childEnv = env.makeChildEnv()

    # now set args in the ENVIRONMENT
    for k,v in args.items():
        # attn we could try to get a better description from funcParamList
        description = "user func arg"
        childEnv.createEnvVar(astloc, k, description, v, True)
    # set custom data
    childEnv.createEnvVar(astloc, "customData", description, customDataInner, True)

    # targets
    targetVal = AstValObject(astloc, astloc, targets, True, True)
    childEnv.createEnvVar(astloc, JrDefUserFuncTargetsEnvVarId, "passed targets list", targetVal, True)

    # assemble result
    results = JrAstResultList()

    # now "invoke" the user defined function by asking it to "render" the function contents into our results, using our CHILDENV
    addTargetsToResults(results, functionContents, rmode, childEnv, entryp, leadp, False, False)

    return results




def funcRenderTargetsInUserFunction(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # this function will be called when user CALLS a user defined function

    # now "invoke" the user defined function by asking it to "render" the function contents into our results, using our CHILDENV
    functionTargetVal = env.getEnvValue(astloc, JrDefUserFuncTargetsEnvVarId, None)
    functionTargets = functionTargetVal.getWrapped()
    if (functionTargets is not None):
        # assemble result
        results = JrAstResultList()
        addTargetsToResults(results, functionTargets, rmode, env, entryp, leadp, False, False)
        return results

    # nothing
    return AstValNull(astloc, entryp)
#---------------------------------------------------------------------------

























# ---------------------------------------------------------------------------
def funcForm(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display form field
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    typeStr = args["type"].getWrapped()
    sizeVal = args["size"].getWrapped()
    choices = args["choices"].getWrapped()

    [text, latex] = buildFormElementTextLatex(typeStr, sizeVal, choices)


    if (latex is None):
        # return MARKDOWN text
        return text
    else:
        # return latex
        return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------





















# ---------------------------------------------------------------------------
def funcFormText(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display form field
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    lines = args["lines"].getWrapped()
    widthStr = args["width"].getWrapped()
    pt = args["pt"].getWrapped()
    latex = generateFormTextLatex(lines, widthStr, pt)
    return vouchForLatexString(latex, False)




def funcFormLine(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display form field
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    marginStr = args["margin"].getWrapped()
    pt = args["pt"].getWrapped()
    safeMarginStr = convertStringToSafeLatexSize(marginStr, r"\columnwidth", r"\columnwidth", r"0.95\columnwidth", 1.0)
    after = args["after"].getWrapped()

    renderer = env.getRenderer()

    latex = "\\nopagebreak"
    #latex += "\\cbFormIndent\\cbFormRemainderLine{" + safeMarginStr + "}" + "{" + str(pt) + "pt}"
    latex += "\\cbFormRemainderLine{" + safeMarginStr + "}" + "{" + str(pt) + "pt}"
    if (after is not None):
        latex += " " + renderer.convertMarkdownToLatexDontVouch(after, True, True)
    latex += generatelatexLineBreak2()

    return vouchForLatexString(latex, False)



def funcFormShort(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display form field
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    widthStr = args["width"].getWrapped()
    pt = args["pt"].getWrapped()
    #
    safeWidthStr = convertStringToSafeLatexSize(widthStr, r"\columnwidth", r"\columnwidth", r"0.95\columnwidth", 1.0)
    after = args["after"].getWrapped()

    renderer = env.getRenderer()

    latex = "\\cbFormLine{" + safeWidthStr + "}" + "{" + str(pt) + "pt}"
    if (after is not None):
        latex += " " + renderer.convertMarkdownToLatexDontVouch(after, True, True)
    latex += "\n"

    return vouchForLatexString(latex, True)



def funcFormNumber(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display form field
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    widthStr = args["width"].getWrapped()
    pt = 1
    #
    safeWidthStr = convertStringToSafeLatexSize(widthStr, r"\columnwidth", r"\columnwidth", r"0.95\columnwidth", 1.0)
    after = args["after"].getWrapped()

    renderer = env.getRenderer()

    latex = "\\cbFormLine{" + safeWidthStr + "}" + "{" + str(pt) + "pt}"
    if (after is not None):
        latex += " " + renderer.convertMarkdownToLatexDontVouch(after, True, True)
    latex += "\n"

    return vouchForLatexString(latex, True)




def funcFormCheckList(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display form field
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    choices = args["choices"].getWrapped()
    other = args["other"].getWrapped()
    #
    latex = "\\nopagebreak"
    latex += formHelperListBuild(env, "Check", choices, other)

    latex += generatelatexLineBreak2()
    return vouchForLatexString(latex, False)



def funcFormRadioList(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display form field
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    choices = args["choices"].getWrapped()
    other = args["other"].getWrapped()
    #
    latex = "\\nopagebreak"
    latex += formHelperListBuild(env, "Radio", choices, other)

    latex += generatelatexLineBreak2()
    return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------











# ---------------------------------------------------------------------------
def funcDither(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Return cached path to ditherized version of an image file, ditherizing it the first time
    path = args["path"].getWrapped()
    mode = args["mode"].getWrapped()
    #

    # process
    # 1. Convert the imagePath to add the dithered file path suffix
    # 2. Lookup this image path, if it exists, return it; done.
    # 3. Otherwise, look up main image path in LOCAL game dir only
    # 4. If it doesn't exist, return it, which will lead to an error
    # 5. Otherwise, run affect convert
    # 6. Then add it to the game model
    # 7. Then add it to the local game file manager
    # 8. Then return it

    modeDict = {
            "bw": "bwDither6",
            "bw4": "bwDither4",
            "bw6": "bwDither6",
            "bw8": "bwDither8",
            "color": "colorwDither6",
            "color4": "colorDither6",
            "color6": "colorDither6",
            "color8": "colorDither8",
    }
    # ok first step, convert mode to effect name to pass to game model
    if (mode not in modeDict):
        raise makeJriException("Unknown ditherize mode: '{}'.".format(mode), astloc)
    effectKey = modeDict[mode]

    funcCallText = funcName + "({},{})".format(path, mode)
    return functionRunEffectOnImagePath(env, entryp, leadp, astloc, path, effectKey, funcCallText)


def funcFlatAlpha(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Return cached path to flattened version of an image file, flattening it the first time
    path = args["path"].getWrapped()
    #
    effectKey = "flatAlpha"
    funcCallText = funcName + "({})".format(path)
    return functionRunEffectOnImagePath(env, entryp, leadp, astloc, path, effectKey, funcCallText)




def funcImageEffect(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Return cached path to ditherized version of an image file, ditherizing it the first time
    path = args["path"].getWrapped()
    effect = args["effect"].getWrapped()

    funcCallText = funcName + "({},{})".format(path, effect)
    return functionRunEffectOnImagePath(env, entryp, leadp, astloc, path, effect, funcCallText)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def funcVspace(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Return cached path to ditherized version of an image file, ditherizing it the first time
    amount = args["amount"].getWrapped()
    force = args["force"].getWrapped()

    sizeStr = safeLatexSizeFromUserString(amount, astloc)
    if (force):
        latex = "\\vspace*{" + sizeStr + "}"
    else:
        latex = "\\vspace{" + sizeStr + "}"

    return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def funcFormatList(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Return cached path to ditherized version of an image file, ditherizing it the first time
    indent = args["indent"].getWrapped()
    divider = args["divider"].getWrapped()

    # assemble result
    results = JrAstResultList()

    # start of list
    latex = "\\begin{cbNumberedItemList}"+"\n"
    results.flatAdd(vouchForLatexString(latex, False))

    # ok we need to MODIFY our contents
    # ATTN: UNFINISHED

    # end of list
    latex = "\\end{cbNumberedItemList}"+"\n"
    results.flatAdd(vouchForLatexString(latex, False))

    return results
# ---------------------------------------------------------------------------














#---------------------------------------------------------------------------
def funcImageOverlay(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Embed an image into a pdf

    exceptionIfNotRenderMode(rmode, funcName, env, astloc)
    renderer = env.getRenderer()

    # args
    path = args["path"].getWrapped()
    width = args["width"].getWrapped()
    height = args["height"].getWrapped()
    align = args["align"].getWrapped()
    caption = args["caption"].getWrapped()
    captionPos = args["captionPos"].getWrapped()
    captionSize = args["captionSize"].getWrapped()
    opacity = args["opacity"].getWrapped()

    padding = 0
    valign = "center"
    extraParams = ""

    # ATTN: we use two different techniques here, depending on whether we want the background image to size automatically to the text
    # or whether we want it at full width/height and preserved aspect ratio with text in the center

    widthStr = convertStringToSafeLatexSize(width, r"\columnwidth", r"\columnwidth", r"\columnwidth", 1.0)
    heightStr = convertStringToSafeLatexSize(height, r"\textheight", r"\textheight", r"\textheight", 1.0)

    # find image, raise exception if not found
    [imageFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), path, "Image in front of Text", "embedImage", leadp, env, astloc, False)
    # exception would already be raised if warnOnMissingImage is false
    # build latex includegraphics command
    pathLatex = makeLatexSafeFilePath(imageFullPath)

    
    # build results
    results = JrAstResultList()

    # FIRST save contents
    preCommand = ""
    postCommand = ""
    # new code to handle scale image
    if (True):
        # wrap text in tikz node with image overlay
        preCommand += "% TikZ picture environment to overlay text on the image\n"
        preCommand += "\\begin{tikzpicture}\n"
        textNodeBaseOptions = "inner sep=0, text width=" + widthStr
        if (align=="center"):
            # align to center
            preCommand += "\\node[" + textNodeBaseOptions + "] (text) at (0,0) {\n"
        else:
            # align to top
            preCommand += "\\node[" + textNodeBaseOptions + ", anchor=north] (text) at (0,0) {\n"
    #
    preCommand += "\\begin{minipage}[c][" + heightStr + "][c]{" + widthStr + "}\n"
    #
    if (align=="center"):
        preCommand += "\\centering\n"
    #
    postCommand += "\\end{minipage} "
    postCommand += "};\n"

    postCommand += "\\node[inner sep=0, opacity=" + str(opacity) + "] at (text.center) {\\includegraphics[width=" + widthStr + ", height= " + heightStr + ", keepaspectratio=false]{" + pathLatex + "}};\n"

    #
    if (True):
        postCommand += "\\end{tikzpicture}"

    textCommand = "\\cbImageBehindTempText"
    addTargetsToResultsIntoCommand(textCommand, preCommand, postCommand, results, targets, rmode, env, entryp, leadp, False, False)

    # now the command which will use this text
    widthStr = convertStringToSafeLatexSize(width, r"\columnwidth", r"\columnwidth", r"\columnwidth", 1.0)
    latex = "\\imageBehindFull{"+widthStr+"}" + "{"+str(padding)+"}" + "{"+str(opacity)+"}" + "{"+valign+"}" + "{"+ extraParams + "}" + "{" + textCommand + "}"

    if (caption is not None):
        flagTightCaption = True
        flagWrapInMiniPage = False
        flagUnboxable = True
        optionWrapText = False
        latex = wrapInFigure(env, latex, caption, align, captionPos, captionSize, flagTightCaption, False, flagWrapInMiniPage, flagUnboxable, optionWrapText)

    results.flatAdd(vouchForLatexString(latex, False))
    return results
#---------------------------------------------------------------------------

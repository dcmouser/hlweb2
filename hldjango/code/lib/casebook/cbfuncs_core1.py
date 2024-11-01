# core casebook functions


# jr ast helpers
from .jrcbfuncs import CbFunc, CbParam
from .jrast import AstValString, AstValNumber, AstValBool, AstValIdentifier, AstValList, AstValDict, AstValNull
from .cbtask import DefRmodeRun, DefRmodeRender
from .jriexception import *
from .jrastfuncs import getUnsafeDictValueAsString, getUnsafeDictValueAsNumber, makeLatexLinkToRid, vouchForLatexString, convertEscapeUnsafePlainTextToLatex, convertEscapeUnsafePlainTextToLatexMorePermissive, convertEscapePlainTextFilePathToLatex
from .jrastutilclasses import JrINote
from .jrast import JrAstResultList
from .jrastfuncs import isTextLatexVouched
#
from .cbdeferblock import CbDeferredBlockRefLead, CbDeferredBlockCaseStats, CbDeferredBlockFollowCase, CbDeferredBlockEndLinePeriod, CbDeferredBlockAbsorbFollowingNewline, CbDeferredBlockAbsorbPreviousNewline, CbDeferredBlockLeadTime, CbDeferredBlockLeadHeader

# helpers for funcs
from .cbfuncs_core_support import calcInlineLeadLabel, parseTagListArg, buildLatexMarkCheckboxSentence, wrapTextInLatexBox, generateLatexBoxDict, generateLatexForSymbol, generateLatexForSeparator, generateLatexLineBreak, convertHoursToNiceHourString, generateLatexBreak, generateImageEmbedLatex, generateLatexForPageStyle
#
from .cbdays import CbDayManager, CbDay
#
from .casebookDefines import *


# python modules
import re




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
            CbParam("cautions", "Any cautions to players (eg. adult language)", "", False, AstValString, True),
            CbParam("url", "Optional website url to learn more", "", False, AstValString, True),
            CbParam("extraCredits", "Optional extra credits to show in listing and on cover page", "", False, AstValString, True),
            CbParam("keywords", "Optional keywords", "", False, AstValString, True),
        ],
        "text", None, None,
        funcConfigureGameInfoExtra
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
        ],
        "text", None, None,
        funcConfigureRenderer
        ))


    functionList.append(CbFunc("configureDocuments", "Configure document options", [
            CbParam("defaultLocation", "Default location of documents [back,custom text]", DefCbDocumentDefault_defaultLocation, False, AstValString, True),
            CbParam("printLocation", "Where to print documents [inline, end, pdf]", DefCbDocumentDefault_printLocation, False, ["inline", "end", "pdf"], True),
            CbParam("printStyle", "Style to print documents [simple, triFold]", DefCbDocumentDefault_printStyle, False, ["simple", "triFold"], True),
        ],
        "text", None, None,
        funcConfigureDocuments
        ))
    #---------------------------------------------------------------------------








    #---------------------------------------------------------------------------
    functionList.append(CbFunc("_entryApplyOptions", "Internal function for applying options to entry", [
            CbParam("_entry", "Object pointer to entry whose options are being set", None, False, None, False),
            CbParam("autoLead", "Automatically assign a lead id", False, False, AstValBool, True),
            #
            CbParam("time", "Duration of lead (in minutes)", None, True, AstValNumber, True),
            CbParam("timePos", "Position to add time instruction", "", False, ["", "start", "end", "hide"], True),
            #
            CbParam("sectionColumns", "Number of columns in Section main text", None, True, AstValNumber, True),
            CbParam("leadColumns", "Number of columns in layout for child leads", None, True, AstValNumber, True),
            #
            CbParam("sectionBreak", "Break style for section", None, True, ["", "none", "before", "after", "solo", "beforeFacing", "afterFacing", "soloFacing", "soloAfterFacing"], True),
            CbParam("leadBreak", "Break style for child leads", None, True, ["", "none", "before", "after", "solo", "beforeFacing", "afterFacing", "soloFacing", "soloAfterFacing"], True),
            #
            CbParam("heading", "Heading text shown on page (blank for none)", None, True, AstValString, True),
            CbParam("toc", "Label for table of contents (blank to hide from table of contents)", None, True, AstValString, True),
            #
            CbParam("childPlugins", "Name of the plugins to run on children (optional)", None, True, AstValString, True),
            #
            CbParam("tombstones", "Should we show tombstombs between child entries", None, True, AstValBool, True),
            CbParam("address", "Address line under heading/label (optional); set to 'auto' to auto grab from database or '' blank to mean none", None, True, AstValString, True),
            #
            CbParam("copy", "Entry id to copy contents from, or 'next' to copy from next lead", None, True, AstValString, True),
            #
            CbParam("render", "If set false this lead will not render", True, False, AstValBool, True),
            CbParam("blank", "If set true then we will not show the header or add this to toc", False, False, AstValBool, True),
            #
            CbParam("mStyle", "Set to a string keyword that informs mind map drawing (optional)", None, True, AstValString, True),
            #
            # not used YET
            CbParam("sortIndex", "Sort index", -1, False, AstValNumber, True),
            CbParam("continuedFrom", "Add label saying 'continued from this lead", None, True, AstValString, True),

            CbParam("deadline", "Deadline day for a check", -1, False, AstValNumber, True),
        ],
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

    functionList.append(CbFunc("defineTag", "Defines a tag", [
            CbParam("tagId", "The dotted identifier used to refer to the tag", None, False, AstValString, True),
            CbParam("deadline", "Deadline label describing the tag", -1, False, AstValNumber, True),
            CbParam("label", "Longer label describing the tag", "", False, AstValString, True),
            CbParam("location", "Override default (document) location; use 'back' for back of book", None, True, AstValString, True),
            CbParam("obfuscatedLabel", "Override default (document) obfuscated label", None, True, AstValString, True),
        ],
        None, None, None,
        funcDefineTag
        ))


    
    functionList.append(CbFunc("mentiontags", "Just list some tags by their obfuscated ids (e.g. used when listing tags available for completionists)", [
            CbParam("tags", "list of tags", "", False, AstValString, True),
        ],
        "text", None, None,
        funcMentionTags
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    functionList.append(CbFunc("toc", "Generate and insert table of contents", [
            CbParam("columns", "Number of columns for table of contents", None, True, AstValNumber, True),
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
            CbParam("width", "Width (e.g. 3in)", "", False, AstValString, True),
            CbParam("height", "Height (e.g. 3in)", "", False, AstValString, True),
            CbParam("borderWidth", "border width (in points; 0 for none)", 0, False, AstValNumber, True),
            CbParam("padding", "padding width (in points; 0 for none)", 0, False, AstValNumber, True),
        ],
        "text", None, None,
        funcImage
        ))

    functionList.append(CbFunc("embedFile", "Embed another pdf/text file in output", [
            CbParam("path", "Relative path to file to embed", None, False, AstValString, True),
            CbParam("pages", "Comma separated page list", None, True, AstValString, True),
            CbParam("scale", "Scaled for embed", None, True, AstValNumber, True),
            #CbParam("pagenum", "Show page number? Usually requires scale<0.90 or so", False, False, AstValBool, True),
            CbParam("pageStyle", "Page style to use for the page (use 'empty' to hide footer)", "", False, AstValString, True),            
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

    functionList.append(CbFunc("reflead", "Add text to refer to lead", [
            CbParam("id", "ID of lead", None, False, AstValString, True),
            CbParam("page", "Show page number?", True, False, AstValBool, True),
            CbParam("href", "Hyperlink clickable", True, False, AstValBool, True),
            CbParam("showLabel", "Show label", False, False, AstValBool, True),
            CbParam("back", "tell them to come back after they visit lead", False, False, AstValBool, True),
        ],
        "text", None, {"pretext":"", "mindMapType": "refers"},
        funcRefLead
        ))

    functionList.append(CbFunc("golead", "Add text to go to lead", [
            CbParam("id", "ID of lead", None, False, AstValString, True),
            CbParam("page", "Show page number?", True, False, AstValBool, True),
            CbParam("href", "Hyperlink clickable", True, False, AstValBool, True),
            CbParam("showLabel", "Show label", False, False, AstValBool, True),
            CbParam("back", "tell them to come back after they visit lead", False, False, AstValBool, True),
        ],
        "text", None, {"pretext":"go to ", "mindMapType": "go"},
        funcRefLead
        ))
    functionList.append(CbFunc("returnlead", "Add text to go to lead", [
            # note we allow a null id here
            CbParam("id", "ID of lead", None, True, AstValString, True),
            CbParam("page", "Show page number?", True, False, AstValBool, True),
            CbParam("href", "Hyperlink clickable", True, False, AstValBool, True),
            CbParam("showLabel", "Show label", False, False, AstValBool, True),
            CbParam("back", "tell them to come back after they visit lead", False, False, AstValBool, True),
        ],
        "text", None, {"pretext":"return to ", "mindMapType": "returns"},
        funcRefLead
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
    functionList.append(CbFunc("gaintag", "Mark a tag", [
            CbParam("id", "ID of tag (or list of ids)", None, False, AstValString, True),
            #CbParam("define", "Should the tag be defined if it doesn't exist?", False, False, AstValBool, True),
        ],
        "text", None, None,
        funcGainTag
        ))
    

    functionList.append(CbFunc("autohint", "generate an autohint", [
            CbParam("id", "ID of tag (or list of ids)", "", False, AstValString, True),
            CbParam("demerits", "Demerits to mark", 3, False, AstValNumber, True),
        ],
        None, None, None,
        funcAutoHint
        ))
    #---------------------------------------------------------------------------





    #---------------------------------------------------------------------------
    functionList.append(CbFunc("requiretag", "Tell user they should leave if they dont have tag and come back when they do", [
            CbParam("id", "ID of tag", None, False, AstValString, True),
            CbParam("check", "check style [and,or] for multiple tags", "all", False, ["", "any", "all"], True),
        ],
        "text", None, None,
        funcRequireTag
        ))


    functionList.append(CbFunc("hastag", "Check if user has tag", [
            CbParam("id", "ID of tag", None, False, AstValString, True),
            CbParam("check", "check style [and,or] for multiple tags", "all", False, ["", "any", "all"], True),
        ],
        "text", None, "has",
        funcCheckTag
        ))



    functionList.append(CbFunc("missingtag", "Is player missing a tag", [
            CbParam("id", "ID of tag", None, False, AstValString, True),
            CbParam("check", "check style [and,or] for multiple tags", "all", False, ["", "any", "all"], True),
        ],
        "text", None, "missing",
        funcCheckTag
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("mark", "Mark checkboxes", [
            CbParam("demerits", "Demerits to mark", 0, False, AstValNumber, True),
            CbParam("culture", "Culture boxes to mark", 0, False, AstValNumber, True),
            CbParam("extra", "Extra boxes to mark", 0, False, AstValNumber, True),
            CbParam("type", "Mark type", None, True, AstValString, True),
            CbParam("count", "How many to mark", 0, False, AstValNumber, True),
        ],
        "text", None, None,
        funcMark
        ))
    #---------------------------------------------------------------------------











    #---------------------------------------------------------------------------
    functionList.append(CbFunc("inline", "Create inline", [
            CbParam("link", "Text link", "", False, AstValString, True),
            CbParam("label", "Label for new lead", "", False, AstValString, True),
            CbParam("time", "Duration of lead (in minutes)", None, True, AstValNumber, True),
            CbParam("timePos", "Position to add time instruction", "", False, ["", "start","end"], True),
            CbParam("demerits", "Demerit checkboxes", 0, False, AstValNumber, True),
            CbParam("unless", "Unless text", "", False, AstValString, True),
            CbParam("back", "direct them to return after visiting inline lead?", False, False, AstValBool, True),
            CbParam("mLabel", "Label for mindmap link", "", False, AstValString, True),
        ],
        "text", 1, None,
        funcInline
        ))
    functionList.append(CbFunc("inlineHint", "Create inline", [
            CbParam("link", "Text link", "", False, AstValString, True),
            CbParam("label", "Label for new lead", "", False, AstValString, True),
            CbParam("time", "Duration of lead (in minutes)", None, True, AstValNumber, True),
            CbParam("timePos", "Position to add time instruction", "", False, ["", "start","end"], True),
            CbParam("demerits", "Demerit checkboxes", 2, False, AstValNumber, True),
            CbParam("back", "direct them to return after visiting inline lead?", False, False, AstValBool, True),
            CbParam("mLabel", "Label for mindmap link", "", False, AstValString, True),
        ],
        "text", 1, None,
        funcInline
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


    functionList.append(CbFunc("format", "Format text", [
            CbParam("style", "style for formatting", None, False, ["", "radio", "handwriting", "typewriter", "choice", "warning", "culture", "dayTest", "quote"], True),
            CbParam("substyle", "style variant", "", True, AstValString, True),           
            CbParam("box", "[true, false, stylename]", None, True, [AstValBool, AstValString], True),
            CbParam("symbol", "symbol", None, True, AstValString, True),
        ],
        "text", 1, None,
        funcFormat
        ))


    functionList.append(CbFunc("quote", "Quote format text", [
            CbParam("pos", "position of quote variant", "right", False, ["right", "left", "center", "topRight", "topLeft"], True),  
            CbParam("cite", "citation credit (author); only used for quote type", "", False, AstValString, True),
            CbParam("style", "style variant", "default", False, AstValString, True),     
            CbParam("box", "[true, false, stylename]", None, True, [AstValBool, AstValString], True),
            CbParam("symbol", "symbol", None, True, AstValString, True),
        ],
        "text", 1, None,
        funcQuote
        ))


    functionList.append(CbFunc("separator", "separator insert", [
            CbParam("style", "Separator style", None, True, AstValString, True),
        ],
        "text", None, None,
        funcSeparator
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    functionList.append(CbFunc("otherwise", "Text saying otherwise", [
        ],
        "text", None, "otherwise",
        funcSimpleText
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
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
            CbParam("time", "Duration (in minutes)", 1, False, AstValNumber, True),
            CbParam("box", "Put this text in a standalone box", True, False, AstValBool, True),
        ],
        "text", None, None,
        funcAdvanceTime
        ))

    functionList.append(CbFunc("timeHere", "Show lead time here (instead of normally at start or end)", [
        ],
        "text", None, None,
        funcTimeHere
        ))

    functionList.append(CbFunc("beforeday", "Text saying if before day", [
            CbParam("day", "Day number", None, False, AstValNumber, True),
        ],
        "text", None, "before",
        funcDayTest
        ))
    functionList.append(CbFunc("afterday", "Text saying if after day", [
            CbParam("day", "Day number", None, False, AstValNumber, True),
        ],
        "text", None, "after",
        funcDayTest
        ))
    functionList.append(CbFunc("onday", "Text saying if on day", [
            CbParam("day", "Day number", None, False, AstValNumber, True),
        ],
        "text", None, "on",
        funcDayTest
        ))
    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    # new function for letting user configure days
    functionList.append(CbFunc("configureDay", "Configure a day", [
            CbParam("day", "Number of the day", None, False, AstValNumber, True),
            CbParam("type", "Day type", "normal", False, AstValString, True),
            CbParam("start", "24 hour clock hour", 9, False, AstValNumber, True),
            CbParam("end", "24 hour clock hour", 18, False, AstValNumber, True),
            # for hints
            CbParam("hintAlly", "is there an ally they can visit for more help", "financialPrecinct", False, ["", "financialPrecinct"], True),
            CbParam("allyFreeStart", "tell the user this period is free", -1, False, AstValNumber, True),
            CbParam("allyFreeEnd", "tell the user this period is free", -1, False, AstValNumber, True),
        ],
        "text", None, None,
        funcConfigureDay
        ))

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
            CbParam("type", "The stop blurb type", None, False, ["dayStart", "dayEnd", "nextDay", "nightStart", "nightEnd", "conclusion", "questions", "questionPause", "resolvePause", "solution", "leads", "documents", "hints", "end", "begin", "noMore"], True),
            CbParam("day", "Number of the day", -1, False, AstValNumber, True),
            CbParam("rest", "Suggest player takes a rest?", None, True, AstValBool, True),
            #CbParam("breakBefore", "Page break before this entry", None, True, AstValBool, True),     
            #CbParam("breakAfter", "Page break after this entry", None, True, AstValBool, True),           
        ],
        "text", None, None,
        funcBlurbStop
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
            CbParam("target", "Lead id", None, False, AstValString, True),
            CbParam("label", "Link label", "", False, AstValString, True),
        ],
        "text", None, {"type": "follows", "direction": "ba"},
        funcLogic
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("authorNote", "An author note which is not shown in normal case book build only in author report", [
            CbParam("label", "label for note for author report", "", False, AstValString, True),
        ],
        "text", 1, None,
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
    functionList.append(CbFunc("dropcaps", "Drop cap effect for some text (make first letter BIG)", [
            CbParam("style", "drop cap style", "", False, AstValString, True),
            CbParam("lines", "height in lines", DefCbRenderDefault_DropCapLineSize, False, AstValNumber, True),
            CbParam("multi", "how to handle multiple paragraphs [none, wrap, gap]", "wrap", False, AstValString, True),
        ],
        "text", 1, None,
        funcDropCaps
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    functionList.append(CbFunc("lipsum", "Add some test text", [
            CbParam("start", "starting paragraph index", 1, False, AstValNumber, True),
            CbParam("end", "ending paragraph index", -1, False, AstValNumber, True),
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
        ],
        "text", None, None,
        funcCalendar
        ))
    #---------------------------------------------------------------------------



    return functionList

















































# ---------------------------------------------------------------------------
# IMPLEMENTED
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def funcApplyEntryOptions(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # This is a "function" that gets called to configure entries; it is our one unusual function in that it is invoked like $() on an entry

    if (rmode != DefRmodeRun):
        raise makeJriException("In function ({}) but in rmode!= run; do not know what to do.".format(funcName), astloc)

    # args
    entryp.setLeadColumns(args["leadColumns"].getWrappedExpect([AstValNumber, AstValNull]))
    entryp.setSectionColumns(args["sectionColumns"].getWrappedExpect([AstValNumber, AstValNull]))
    entryp.setLeadBreak(args["leadBreak"].getWrappedExpect([AstValString, AstValNull]))
    entryp.setSectionBreak(args["sectionBreak"].getWrappedExpect([AstValString, AstValNull]))
    entryp.setToc(args["toc"].getWrappedExpect([AstValString, AstValNull]))
    entryp.setHeading(args["heading"].getWrappedExpect([AstValString, AstValNull]))
    entryp.setChildPlugins(args["childPlugins"].getWrappedExpect([AstValString, AstValNull]))
    entryp.setIsAutoLead(args["autoLead"].getWrappedExpect(AstValBool))
    entryp.setCopyFrom(args["copy"].getWrappedExpect([AstValString, AstValNull]))
    entryp.setShouldRender(args["render"].getWrappedExpect(AstValBool))
    entryp.setContinuedFromLead(args["continuedFrom"].getWrappedExpect([AstValString, AstValNull]))
    entryp.setMStyle(args["mStyle"].getWrappedExpect([AstValString, AstValNull]))
    entryp.setAddress(args["address"].getWrappedExpect([AstValString, AstValNull]))

    # blankness
    blank = args["blank"].getWrappedExpect(AstValBool)
    if (not blank) and (entryp.getId()=="BLANK"):
        blank = True
    entryp.setBlankHead(blank)

    # time
    time = args["time"].getWrappedExpect([AstValNumber, AstValNull])
    timePos = args["timePos"].getWrappedExpect(AstValString)
    entryp.setTime(time)
    entryp.setTimePos(timePos)

    # tombstones
    tombstones = args["tombstones"].getWrappedExpect([AstValBool, AstValNull])
    if (tombstones is None) and (entryp.getLevel()==1):
        # top level sections default to tombstones = true
        tombstones = True
    entryp.setTombstones(tombstones)



def funcDeclareVar(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # declare a variable

    # args
    varName = args["var"].getWrappedExpect(AstValIdentifier)
    description = args["desc"].getWrappedExpect(AstValString)
    value = args["val"]
    #
    env.declareEnvVar(astloc, varName, description, value, False)



def funcDeclareConst(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # declare a constant

    # args
    varName = args["var"].getWrappedExpect(AstValIdentifier)
    description = args["desc"].getWrappedExpect(AstValString)
    value = args["val"]
    #
    env.declareEnvVar(astloc, varName, description, value, True)



def funcSet(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # set a variable

    # args
    varName = args["var"].getWrappedExpect(AstValIdentifier)
    value = args["val"]
    #
    env.setEnvValue(astloc, varName, value, True)



def funcDefineTag(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # declare a tag

    tagId = args["tagId"].getWrapped()
    tagDeadline = args["deadline"].getWrapped()
    tagLabel = args["label"].getWrapped()
    tagLocation = args["location"].getWrapped()
    tagObfuscatedLabel = args["obfuscatedLabel"].getWrapped()

    tagManager = env.getTagManager()
    tagManager.declareTag(env, tagId, tagDeadline, tagLabel, tagLocation, tagObfuscatedLabel, True, astloc, "Defining tag", leadp)
# ---------------------------------------------------------------------------









# ---------------------------------------------------------------------------
def funcToc(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # generate table of contents

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # args
    columns = args["columns"].getWrappedExpect([AstValNumber, AstValNull])

    # get renderer to help us
    text = "~\n"

    if (columns is not None) and (columns>1):
        text += "\\begin{multicols*}{" + str(columns) + "}\n"

    # wrap this in a "continued on next page" latex trick
    renderer = env.getRenderer()
    text += renderer.breakWarnSecStart()
    #
    text += '\n\\tableofcontents\n'
    #
    text += renderer.breakWarnSecEnd()
    
    if (columns is not None) and (columns>1):
        text += "\\end{multicols*}\n"

    vouchedText = vouchForLatexString(text, False)
    return vouchedText



def funcBlurbCoverPage(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Create a nice cover page snippet which includes title and author from options, as well as any other user custom text/image

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # args
    info = env.getEnvValueUnwrapped(None, "info", None)
    #
    namestr = getUnsafeDictValueAsString(env, info, "name", "n/a")
    titleStr = getUnsafeDictValueAsString(env,info, "title", "n/a")
    subtitleStr = getUnsafeDictValueAsString(env,info, "subtitle", "")
    authorsStr = getUnsafeDictValueAsString(env,info, "authors", "n/a")
    versionStr = getUnsafeDictValueAsString(env,info, "version", "n/a")
    dateStr =  getUnsafeDictValueAsString(env,info, "versionDate", "n/a")
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
        durationStr = str(duration)+ " hours"
    #
    cautionsStr =  getUnsafeDictValueAsString(env,info, "cautions", "")
    summaryStr =  getUnsafeDictValueAsString(env,info, "summary", "n/a")
    extraCreditsStr =  getUnsafeDictValueAsString(env,info, "extraCredits", "")
    urlStr =  getUnsafeDictValueAsString(env,info, "url", "")
    keywordsStr =  getUnsafeDictValueAsString(env,info, "keywords", "")
    # derived args
    versionStrWithDate = "v{} - {}".format(versionStr, dateStr)
    authorsStrNoEmails = re.sub(r'\s*\<[^\<\>]*\>','', authorsStr)
    #
    buildStr = env.getBuildString()
    #
    currentDateStr = jrfuncs.getNiceCurrentDateTime()

    #
    text = "\\begin{titlepage}\n\\begin{center}\n"
    text += r"\vspace*{0in} \begin{Huge}\bfseries \textbf{" + titleStr + r"} \par\end{Huge}" + "\n"
    if (subtitleStr != ""):
        text += r"\vspace*{0in} \begin{Large}\bfseries \textbf{" + subtitleStr + r"} \par\end{Large}" + "\n"

    reportMode = env.getReportMode()
    if (reportMode):
        latexLine = r"\begin{Huge}\bfseries {\textbf{" + "DEBUG REPORT" + r"} }\par\end{Huge}"
        boxStyle = "hLinesCenter"
        text += wrapTextInLatexBox(boxStyle, latexLine, False, symbolName=None, latexFontColor="red", extras=None)
        #text += r"\vspace*{0in} \begin{Huge}\bfseries {\color{red} \textbf{" + "DEBUG REPORT" + r"} }\par\end{Huge} \vspace*{.20in}" + "\n"

    text += r"\vspace*{0in} \bfseries by \textbf{" + authorsStrNoEmails + r"} \par" + "\n"
    text += r"\vspace*{0in} \bfseries \textbf{" + versionStrWithDate + r"} \par \vspace{0.1in} \par" + "\n"
    #

    # assemble result
    results = JrAstResultList()

    # add text so far
    results.flatAdd(vouchForLatexString(text, False))

    # allow user to add arbitrary text/image between title and details using target blocks
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, leadp)
        results.flatAdd(targetRetv)

    # part 1
    text = ""
    text += "\n\\end{center}\n"
    # summary
    text += "\n" + r"\textbf{SUMMARY}%:" + "\n\n" + summaryStr + "\n"
    text += r"\begin{flushleft}" + "\n"
    text += r"\begin{itemize} \setlength\itemsep{-0.5em}" + "\n"
    text += r"\item \textbf{Author}: " + authorsStr + "\n"
    #
    if (extraCreditsStr!=""):
        text += r"\item \textbf{Additional credits}: " + extraCreditsStr + "\n"
    if (urlStr!=""):
        text += r"\item \textbf{Web}: \path{" + urlStr.replace("{-}","-") + "}\n"
    if (keywordsStr!=""):
        text += r"\item \textbf{Keywords}: " + keywordsStr + "\n"
    #
    text += r"\item \textbf{Difficulty}: " + difficultyStr + "\n"
    text += r"\item \textbf{Playtime}: " + durationStr + "\n"
    if (cautionsStr!=""):
        text += r"\item \textbf{Cautions}: " + cautionsStr + "\n"
    text += r"\item \textbf{Build tool}: " + buildStr + "\n"
    text += r"\item \textbf{Compiled}: " + currentDateStr + "\n"
    results.flatAdd(vouchForLatexString(text, False))

    # part 2
    # deferred stats line
    deferredResult = CbDeferredBlockCaseStats(astloc, entryp, leadp)
    results.flatAdd(deferredResult)

    # part 4
    text = ""
    text += r"\end{itemize}" + "\n"
    text += r"\end{flushleft}" + "\n"

    # finally
    text += r"\end{titlepage}"+"\n\n"

    results.flatAdd(vouchForLatexString(text, False))

    # return results
    return results



def funcInline(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # major function that creates a new lead that is jumped to from within another lead (branching choice)

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # args
    inlineLinkArg = args["link"].getWrappedExpect(AstValString)
    backArg = args["back"].getWrappedExpect(AstValBool)

    # renderer
    renderer = env.getRenderer()

    # calc label for inline lead
    [inlineLeadLabel, inlineMindMapLabel] = calcInlineLeadLabel(entryp, leadp, inlineLinkArg)
    # create lead early, so we can pass it into the contents as they run
    inlineLead = renderer.addLeadInline(inlineLeadLabel, leadp, astloc)

    # there are two ways to have a custom label, either through inlineMindMapLabel parsing above (based on a custom LABEL of the inlined lead), or a custom mindmap link label (mLabel)
    # in the former case, the custom label goes to the lead NODE; in the latter it goes to the link label
    mLabel = args["mLabel"].getWrappedExpect(AstValString)
    if (mLabel==""):
        mLabel = None

    # mindmap
    inlineLead.setMindMapLabel(inlineMindMapLabel)
    if (False) and (funcName=="inlineHint"):
        inlineLead.setMStyle("hint")
    else:
        inlineLead.setMStyle("inline")

    # time
    time = args["time"].getWrappedExpect([AstValNumber, AstValNull])
    timePos = args["timePos"].getWrappedExpect(AstValString)

    # for INLINE leads, a time not specified does NOT get default time, and is treated as as 0 (no time taken for this lead)
    if (time is None):
        time = 0
    else:
        pass

    inlineLead.setTime(time)
    inlineLead.setTimePos(timePos)

    # generate contents of it
    inlineResults = JrAstResultList()
    # contents of inline lead
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, inlineLead)
        inlineResults.flatAdd(targetRetv)

    if (backArg):
        # add instructions to return here

        # BUT FIRST - a KLUDGE -- we add an end position time for the inline lead HERE before the return text
        # ATTN: THIS FAILS BECAUSE THE LEADS SECTION MAY NOT ALWAYS EXIST YET -- I THINK WE NEED TO USE A DEFFERRED THING HERE
        if (timePos is None) or (timePos=="") or (timePos=="end"):
            # add it to inlineResults here
            #deferredResult = CbDeferredBlockLeadTime(astloc, entryp, leadp)
            deferredResult = CbDeferredBlockLeadTime(astloc, entryp, inlineLead)
            inlineResults.flatAdd(deferredResult)
            inlineLead.setTimePos("hidden")

        # add instructions to return here
        referencedLeadIdText = convertEscapeUnsafePlainTextToLatex(leadp.getLabelIdPreferAutoId())
        referencedLeadRid = leadp.getRid()
        optionPage = True
        if (optionPage):
            referencedLeadIdText+= r" (p.\pageref*{" + referencedLeadRid + r"})"
        latex = r"\hyperref[{" + referencedLeadRid + r"}]{" + referencedLeadIdText + r"}"
        latex = "\nReturn to " + latex + "."
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
    deferredResult = CbDeferredBlockFollowCase(astloc, entryp, leadp, "go to ", useBulletIfEmptyLine)
    results.flatAdd(deferredResult)
    #
    inlineLeadId = inlineLead.getAutoId()
    inlineLeadRef = makeLatexLinkToRid(inlineLead.getRid(), inlineLeadId, "onpage")
    textLine = "{}".format(inlineLeadRef)
    if (backArg):
        textLine += ", and then return here"
    #
    results.flatAdd(vouchForLatexString(textLine, True))

    # add period automatically IFF at end of line
    deferredResult = CbDeferredBlockEndLinePeriod(astloc, entryp, leadp, True)
    results.flatAdd(deferredResult)

    return results



def funcImage(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Embed an image into a pdf

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # args
    path = args["path"].getWrappedExpect(AstValString)
    widthStr = args["width"].getWrappedExpect(AstValString)
    heightStr = args["height"].getWrappedExpect(AstValString)
    borderWidth = int(args["borderWidth"].getWrapped())
    padding = int(args["padding"].getWrapped())
    flagCenter = True

    # get image import helper, and try to find image first in game-specicific list then fallback to shared
    imageHelper = env.getFileManagerImagesCase()
    imageFullPath = imageHelper.findFullPath(path, True)
    if (imageFullPath is None):
        imageHelper = env.getFileManagerImagesShared()
        imageFullPath = imageHelper.findFullPath(path, True)
        locationClass = "shared"
    else:
        locationClass = "local"

    #
    if (imageFullPath is None):
        raise makeJriException("Image file not found ({}).".format(path), astloc)

    # build latex includegraphics command
    imageLatex = generateImageEmbedLatex(imageFullPath, widthStr, heightStr, borderWidth, padding, flagCenter, None)

    # add note for debug report
    notePath = locationClass + "/" + path
    msg = 'Embedded image: "{}"'.format(notePath)
    msgLatex = 'Embedded image: "\\path{' + notePath + '}"'
    extras = {"img": imageFullPath}
    note = JrINote("embedImage", leadp, msg, msgLatex, extras)
    env.addNote(note)
    #
    return vouchForLatexString(imageLatex, False)
    # ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def funcRefLead(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Refer to another lead
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # args
    id = args["id"].getWrappedExpect([AstValString, AstValNull])
    page = args["page"].getWrappedExpect(AstValBool)
    href = args["href"].getWrappedExpect(AstValBool)
    showLabel = args["showLabel"].getWrappedExpect(AstValBool)
    back = args["back"].getWrappedExpect(AstValBool)
    showId = True
    #
    # assemble result
    results = JrAstResultList()
    #
    pretext = customData["pretext"]
    if (pretext is not None) and (pretext !=""):
        useBulletIfEmptyLine = True
        deferredResult = CbDeferredBlockFollowCase(astloc, entryp, leadp, pretext, useBulletIfEmptyLine)
        results.flatAdd(deferredResult)

    # make DEFERRED link to entry lead
    result = CbDeferredBlockRefLead(astloc, entryp, leadp, id, page, href, showLabel, showId)
    results.flatAdd(result)

    if (back):
        text = ", and then return back here"
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
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # args
    id = args["id"].getWrappedExpect([AstValString, AstValNull])
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

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # args
    path = args["path"].getWrappedExpect(AstValString)
    pages = args["pages"].getWrappedExpect([AstValString, AstValNull])
    scale = args["scale"].getWrappedExpect([AstValNumber, AstValNull])
    #pagenum = args["pagenum"].getWrappedExpect(AstValBool)
    pagenum = True
    pageStyle = args["pageStyle"].getWrapped()

    # get image import helper, and try to find image first in game-specicific list then fallback to shared
    fileManager = env.getFileManagerPdfsCase()
    fileFullPath = fileManager.findFullPath(path, True)
    if (fileFullPath is None):
        fileManager = env.getFileManagerPdfsShared()
        fileFullPath = fileManager.findFullPath(path, True)
    #
    if (fileFullPath is None):
        raise makeJriException("In func {}, file not found ({}).".format(funcName, path), astloc)

    fileFullPathE = convertEscapePlainTextFilePathToLatex(fileFullPath)

    extras = []
    if (pages is not None):
        validPagesRegex = r"(\d+)(\s*[,\-]\s*\d+])*"
        matches = re.match(validPagesRegex, pages)
        if (matches is None):
            raise makeJriException("In func {}, pages arg must be a comma separated list of numbers; got ({}).".format(funcName, pages), astloc)
        extras.append("pages=" + pages)

    if (scale is not None):
        extras.append("scale=" + str(scale))

    # add page numbers; this might only work when scale < 0.95 or so
    if (pageStyle!=""):
        pageStyleLatex = generateLatexForPageStyle(pageStyle, astloc)
        extras.append("pagecommand={" + pageStyleLatex + "}")
    elif (pagenum):
        extras.append("pagecommand={}")
    else:
        # hide pagenumbers
        pass

    latex = ""
    if (len(extras)==0):
        latex += r"\includepdf{" + fileFullPathE + "}" + "\n"
    else:
        extrasJoined = ",".join(extras)
        latex += r"\includepdf[" + extrasJoined + "]{" + fileFullPathE + "}" + "\n"
    #

    # add note for debug report
    msg = 'Including pdf file: "{}"'.format(fileFullPathE)
    msgLatex = 'Including pdf file: "\\path{' + fileFullPathE + '}"'
    note = JrINote("embedPdf", leadp, msg, msgLatex, None)
    env.addNote(note)

    return vouchForLatexString(latex, False)
    # ---------------------------------------------------------------------------



















# ---------------------------------------------------------------------------
def funcGainTag(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # player gains one or more tags
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    tagList = parseTagListArg(args["id"].getWrappedExpect(AstValString), "", env, astloc, leadp)

    # record tag use
    for tag in tagList:
        tag.recordGain(env, "gain", astloc, leadp)

    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # we want to SAY that the tags have been gained
    if (len(tagList)==1):
        tagNameObfuscated = tagList[0].getNiceGainedObfuscatedLabelWithType(True, reportMode, True)

        instructionText = tagList[0].getInstructionText()
        whereText = tagList[0].getWhereText()
        text = "You have {}{} ({}).\n".format(tagNameObfuscated, whereText, instructionText)
        symbol = tagList[0].getSymbol()
    else:
        multiSymbols = []
        #instructionText = "(please note these in your case log unless you have previously acquired them)"
        instructionText = "please note these in your case log"
        text = "You have gained the following items ({}):\n".format(instructionText)
        for tag in tagList:
            tagNameObfuscated = tag.getNiceObfuscatedLabelWithType(True, reportMode)
            text += "* {}\n".format(tagNameObfuscated)
            symbol = tag.getSymbol()
            if (symbol not in multiSymbols):
                multiSymbols.append(symbol)
        # all the same kind of symbol tag
        if (len(multiSymbols)>1):
            symbol = "markerGeneric"
        else:
            symbol = multiSymbols[0]

    # markdown
    renderer = env.getRenderer()
    latex = renderer.convertMarkdownToLatexDontVouch(text)

    # wrap in box with symbol
    latex = wrapTextInLatexBox(True, latex, False, symbol, "red", None)

    return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def funcAutoHint(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # autohint text tells players where to find tags
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # get an explicit tag list, but fall back on ID OF THIS LEAD as default
    tagList = parseTagListArg(args["id"].getWrappedExpect(AstValString), leadp.getId(), env, astloc, leadp)
    # optional demerits
    demerits = args["demerits"].getWrappedExpect(AstValNumber)

    if (len(tagList)==0):
        # error, no tag list
        raise Exception("In $autohint({}) but could not find any tags named; even after checking for ".format(tagList))

    # process tags
    leadList = []
    tagStringList = []
    for tag in tagList:
        tagStringList.append(tag.getId())
        tagLeadList = tag.getGainList()
        for lead in tagLeadList:
            leadList.append(lead)

    if (len(leadList)==0):
        # error, no tag list
        raise Exception("In $autohint({}), found tags, but could not find any leads where tags were used.".format(tagStringList))

    # create the autohint text

    if (demerits>0):
        flagAddCheckbox = True
        latexFontColor = "red"
        markExtra = buildLatexMarkCheckboxSentence("demerit", demerits, False, flagAddCheckbox, latexFontColor) + ", then "
        checkboxManager = env.getCheckboxManager()
        checkboxManager.recordCheckMarks(env, astloc, leadp, "demerit", demerits)
    else:
        markExtra = ""

    if (len(leadList)<=1):
        latex = generateLatexLineBreak() + "If you still need help, as a last resort {}visit the following lead where this item is obtained:\n".format(markExtra)
    else:
        latex = generateLatexLineBreak() + "If you still need help, as a last resort {}visit one or more of the following leads where this item is obtained:\n".format(markExtra)

    if (len(leadList)>0):
        latex += "\\begin{itemize}\n" 
        for tagLead in leadList:
            tagLeadLabel = tagLead.getIdPreferAutoId()
            leadRefLatex = makeLatexLinkToRid(tagLead.getRid(), tagLeadLabel, "onpage")
            latex += "\\item " + leadRefLatex + "\n"
        latex += "\\end{itemize}\n"

    return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------







#---------------------------------------------------------------------------
def funcMark(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    demerits = args["demerits"].getWrappedExpect(AstValNumber)
    culture = args["culture"].getWrappedExpect(AstValNumber)
    extra = args["extra"].getWrappedExpect(AstValNumber)
    typeStr = args["type"].getWrappedExpect([AstValString, AstValNull])
    count = args["count"].getWrappedExpect(AstValNumber)

    checkboxManager = env.getCheckboxManager()

    # build list
    msgList = []
    if (demerits>0):
        msgList.append(buildLatexMarkCheckboxSentence("demerit", demerits, True))
        checkboxManager.recordCheckMarks(env, astloc, leadp, "demerit", demerits)
    if (culture>0):
        msgList.append(buildLatexMarkCheckboxSentence("culture", culture, True))
        checkboxManager.recordCheckMarks(env, astloc, leadp, "culture", culture)
    if (extra>0):
        msgList.append(buildLatexMarkCheckboxSentence("extra", extra, True))
        checkboxManager.recordCheckMarks(env, astloc, leadp, "extra", culture)
    if (typeStr is not None):
        typeStrSafe = convertEscapeUnsafePlainTextToLatex(typeStr)
        msgList.append(buildLatexMarkCheckboxSentence(typeStrSafe, count, True))
        checkboxManager.recordCheckMarks(env, astloc, leadp, typeStrSafe, culture)
    #
    if (len(msgList)==0):
        raise Exception("Runtime Error: No non-zero boxes specified to mark.")

    # combine if more than one
    msgString = " ".join(msgList)

    # font color
    latexFontColor = "red"

    # wrap it and add symbol
    boxStyle = "default"
    latex = wrapTextInLatexBox(boxStyle, msgString, False, "checkbox", latexFontColor, None)

    # build results
    results = JrAstResultList()
    results.flatAdd(vouchForLatexString(latex, False))

    # absorb following newline
    if (False):
        deferredResult = CbDeferredBlockAbsorbFollowingNewline(astloc, entryp, leadp)
        results.flatAdd(deferredResult)

    # return results
    return results
#---------------------------------------------------------------------------










#---------------------------------------------------------------------------
def funcSymbol(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    symbolId = args["id"].getWrappedExpect(AstValString)
    color = args["color"].getWrappedExpect([AstValString, AstValNull])
    size = args["size"].getWrappedExpect([AstValString, AstValNull])

    latex = generateLatexForSymbol(symbolId, color, size)

    return vouchForLatexString(latex, True)



def funcFormat(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    style = args["style"].getWrappedExpect(AstValString)
    substyle = args["substyle"].getWrappedExpect(AstValString)
    boxStyle = args["box"].getWrappedExpect([AstValBool, AstValNull])
    symbol = args["symbol"].getWrappedExpect([AstValString, AstValNull])

    symbolColor = None

    optionsDict = {
        # ATTN: its important that we have newlines at start and end of enclosures so we dont confuse markdown
        "radio": {"boxStyle": False, "symbol": "radio", "start": r"\setlength{\fboxsep}{2em} \begin{center}\shadowbox{\begin{minipage}[c]{.80\columnwidth}\ttfamily\bfseries\itshape ", "end": r"\end{minipage}}\end{center}"},
        "culture": {"boxStyle": "shadow", "symbol": "culture", "start": r"", "end": r""},
        "handwriting": {"boxStyle": False, "start": r"{\Fontskrivan\LARGE\raggedright ", "end": "}"},
        "typewriter": {"boxStyle": False, "start": r"{\ttfamily\Large\raggedright ", "end": "}"},
        "choice": {"boxStyle": True, "symbol": "choice", "start": "", "end": ""},
        "warning": {"boxStyle": True, "symbol": "exclamation", "start": "", "end": ""},
        "dayTest": {"boxStyle": True, "symbol": "calendar", "symbolColor":"red", "start": "", "end": ""},
    }

    if (style not in optionsDict):
        raise makeJriException("Runtime Error: $format({}) should be from {}.", style, optionsDict.keys())
    # the style
    options = optionsDict[style]


    # defaults and overrides
    if (symbol is None) and ("symbol" in options):
        symbol = options["symbol"]
    if (boxStyle is None) and ("boxStyle" in options):
        boxStyle = options["boxStyle"]

    # assemble result
    results = JrAstResultList()

    # box start
    if (boxStyle):
        latexBoxDict = generateLatexBoxDict(boxStyle, None)
        latex = latexBoxDict["start"]
        results.flatAdd(vouchForLatexString(latex, False))

    # wrap content start
    if ("startFunc" in options):
        latex = options["startFunc"]({})
    else:
        latex = options["start"]
    #
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # symbol
    if (symbol is not None):
        if (symbolColor is None) and ("symbolColor" in options):
            symbolColor = options["symbolColor"]
        latex = generateLatexForSymbol(options["symbol"], symbolColor, None)
        results.flatAdd(vouchForLatexString(latex, False))

    # contents of targets
    # allow user to add arbitrary text/image between title and details using target blocks
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, leadp)
        results.flatAdd(targetRetv)

    # wrap content end
    if ("endFunc" in options):
        latex = options["endFunc"]({})
    else:
        latex = options["end"]      
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # box end
    if (boxStyle):
        latex = latexBoxDict["end"]
        results.flatAdd(vouchForLatexString(latex, False))

    # results
    return results

























def funcSeparator(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    style = args["style"].getWrappedExpect([AstValString, AstValNull])

    # assemble result
    results = JrAstResultList()

    results.flatAdd(CbDeferredBlockAbsorbPreviousNewline(astloc, entryp, leadp))

    latex = " " + generateLatexForSeparator(style)
    results.flatAdd(vouchForLatexString(latex, True))

    return results
#---------------------------------------------------------------------------






#---------------------------------------------------------------------------
def funcMentionTags(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # mention a list of tags
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    tagList = parseTagListArg(args["tags"].getWrappedExpect(AstValString), "", env, astloc, leadp)

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
#---------------------------------------------------------------------------





#---------------------------------------------------------------------------
def funcSimpleText(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display some text

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # function given simple text via customData
    simpleText = customData

    # assemble result
    results = JrAstResultList()
    #
    optionUseBulletIfEmptyLine = True
    results.flatAdd(CbDeferredBlockFollowCase(astloc, entryp, leadp, simpleText, optionUseBulletIfEmptyLine))

    return results
#---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def funcRequireTag(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # require a player have a tag
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    tagList = parseTagListArg(args["id"].getWrappedExpect(AstValString), "", env, astloc, leadp)
    check = args["check"].getWrappedExpect(AstValString)

    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # record tag use
    for tag in tagList:
        tag.recordCheck(env, "require", astloc, leadp)

    # we want to SAY that the tags have been gained
    stopText = ", stop reading now, and return here after you have"
    if (len(tagList)==1):
        tagNameObfuscated = tagList[0].getNiceGainedObfuscatedLabelWithType(True, reportMode, False)
        text = "* If you have *not* {}{}.\n".format(tagNameObfuscated, stopText)
    else:
        if (check=="all"):
            if (len(tagList)==2):
                checkText = "**both**"
            else:
                checkText = "**all**" 
        elif (check=="any"):
            checkText = "*any*"
        else:
            raise Exception("check parameter '{}' to requiretag should be from [any,all]".format(check))
        #
        text = "If you have *not* previously acquired {} of the following {} items{}:\n".format(checkText, len(tagList), stopText)
        for tag in tagList:
            tagNameObfuscated = tag.getNiceObfuscatedLabelWithType(True, reportMode)
            text += "* {}\n".format(tagNameObfuscated)

    return text



def funcCheckTag(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # check if play has tag
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    tagList = parseTagListArg(args["id"].getWrappedExpect(AstValString), "", env, astloc, leadp)
    check = args["check"].getWrappedExpect(AstValString)
    #
    testType = customData

    # record tag use
    for tag in tagList:
        tag.recordCheck(env, testType, astloc, leadp)

    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # text to use
    if (testType == "has"):
        checkTypeText = "have"
    elif (testType == "missing"):
        checkTypeText = "are missing"

    # we want to SAY that the tags have been gained
    if (len(tagList)==1):
        tagNameObfuscated = tagList[0].getNiceGainedObfuscatedLabelWithType(True, reportMode, False)
        text = "If you {} {}".format(checkTypeText, tagNameObfuscated)
    else:
        if (check=="all"):
            if (len(tagList)==2):
                checkText = "**both**"
            else:
                checkText = "**all**" 
            combineText = "and"
        elif (check=="any"):
            checkText = "*any*"
            combineText = "or"
        else:
            raise Exception("check parameter '{}' to requiretag should be from [any,all]".format(check))
        #
        tagLabelList = []
        for tag in tagList:
            tagLabelList.append(tag.getNiceObfuscatedLabelWithType(True, reportMode))
        tagListString = jrfuncs.makeNiceCommaAndOrList(tagLabelList, combineText)
        #
        text = "If you {} {} of the the following {} items ({})".format(checkTypeText, checkText, len(tagList), tagListString)

    return text
# ---------------------------------------------------------------------------





































# ---------------------------------------------------------------------------
def funcForm(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display form field
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    typeStr = args["type"].getWrappedExpect(AstValString)
    sizeVal = args["size"].getWrappedExpect([AstValNumber,AstValNull])
    choices = args["choices"].getWrappedExpect([AstValString,AstValNull])

    latex = None
    if (typeStr == "short"):
        oneLine = ">`____________________________`"
        text = oneLine
    elif (typeStr in ["mini", "score"]):
        text = "_____"
    elif (typeStr == "long"):
        oneLine = ">`____________________________`"
        text = oneLine
    elif (typeStr == "multiline"):
        oneLine = ">`__________________________________________________`\n"
        if (sizeVal is None):
            sizeVal = 6
        text = oneLine * sizeVal
    elif (typeStr == "multipleChoice"):
        choiceList = choices.split("|")
        latex = ""
        latex = r"\begin{flushleft}" + "\n"
        latex += r"\begin{nobulletlist} \setlength\itemsep{-0.5em}" + "\n"
        itemLatex = r""
        for index,choiceVal in enumerate(choiceList):
            choiceVal = choiceVal.strip()
            latex += "\\item {}\\textbf{{{}}}) {}\n".format(itemLatex, chr(65+index), choiceVal)
        latex += r"\end{nobulletlist}" + "\n"
        latex += r"\end{flushleft}" + "\n"
    elif (typeStr == "checkAll"):
        choiceList = choices.split("|")
        latex = r"\begin{flushleft}" + "\n"
        latex += r"\begin{todolist} \setlength\itemsep{-0.5em}" + "\n"
        #itemLatex = r"{\square} "
        #itemLatex = r"{\faSquareO} "
        #itemLatex = r"{$\square$} "
        itemLatex = r""
        for index,choiceVal in enumerate(choiceList):
            choiceVal = choiceVal.strip()
            latex += "\\item {}\\textbf{{{}}}) {}\n".format(itemLatex, chr(65+index), choiceVal)
        latex += r"\end{todolist}" + "\n"
        latex += r"\end{flushleft}" + "\n"
    else:
        raise Exception("form({}) type not understood".format(typeStr))

    if (latex is None):
        # return MARKDOWN text
        return text
    else:
        # return latex
        return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
def funcPrint(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display an expression
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    expression = args["expression"].getWrapped()

    # expression as string
    text = str(expression)
    return text


def funcDebug(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display text in debug mode only
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

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
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    typeStr = args["type"].getWrappedExpect(AstValString)

    latex = generateLatexBreak(typeStr)

    return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
def funcAdvanceTime(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # advance time
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    time = args["time"].getWrappedExpect(AstValNumber)
    box = args["box"].getWrappedExpect(AstValBool)

    # as nice string
    timeText = jrfuncs.minutesToTimeString(time)
    text = "advance time **{}**".format(timeText)

    # wrap in box with symbol
    if (box):
        # markdown
        renderer = env.getRenderer()
        latex = renderer.convertMarkdownToLatexDontVouch(jrfuncs.uppercaseFirstLetter(text+"."))
        latex = wrapTextInLatexBox(True, latex, False, "clock", "red", None)
        return vouchForLatexString(latex, False)

    # just return markdown
    return text



def funcTimeHere(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # advance time
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)
    deferredResult = CbDeferredBlockLeadTime(astloc, entryp, leadp)
    leadp.setTimePos("hidden")
    return deferredResult


def funcHeaderHere(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # advance time
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)
    deferredResult = CbDeferredBlockLeadHeader(astloc, entryp, leadp)
    # tell the lead to NOT auto render header
    leadp.setAutoHeaderRender(False)
    return deferredResult

# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
def funcDayTest(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # text to test what day it is

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    dayNumber = args["day"].getWrappedExpect(AstValNumber)
    #
    dayManager = env.getDayManager()
    day = dayManager.findDayByNumber(dayNumber)
    if (day is None):
        raise makeJriException("Unknown day ({}) in day test; days must be defined using $configureDay()".format(dayNumber), astloc)
    #    
    testType = customData

    testTypeDict = {
        "before": "**before day**",
        "after": "**after day**",
        "on": "**day**",
    }
    #
    text = "If it is {} **{}**".format(testTypeDict[testType], dayNumber)

    # mindmapper
    mindMapper = env.getMindManager()
    mindMapper.addLinkBetweenNodes(env, testType, None, leadp, day)

    # just return markdown
    return text
# ---------------------------------------------------------------------------















# ---------------------------------------------------------------------------
def funcConfigureDay(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure a specific day

    #if (rmode != DefRmodeRender):
    #    return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    dayNumber = args["day"].getWrappedExpect(AstValNumber)
    typeStr = args["type"].getWrappedExpect(AstValString)
    start = args["start"].getWrappedExpect(AstValNumber)
    end = args["end"].getWrappedExpect(AstValNumber)
    #
    hintAlly = args["hintAlly"].getWrappedExpect(AstValString)
    allyFreeStart = args["allyFreeStart"].getWrappedExpect(AstValNumber)
    allyFreeEnd = args["allyFreeEnd"].getWrappedExpect(AstValNumber)

    # create day object
    day = CbDay(dayNumber, typeStr, start, end, hintAlly, allyFreeStart, allyFreeEnd)
    dayManager = env.getDayManager()
    dayManager.addDay(day)

    # empty text reply (does not add text)
    text = ""

    # just return markdown
    return text





def funcDayInstructions(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # show instructions for a specified day, which includes a list of tags that must be found, and information about start and end times, etc.

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    dayNumber = args["day"].getWrappedExpect(AstValNumber)
    whenStr = args["when"].getWrappedExpect(AstValString)

    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # get day object
    dayManager = env.getDayManager()
    day = dayManager.findDayByNumber(dayNumber)
    if (day is None):
        raise makeJriException("Unknown 'dayNumber' ({}) specific argument to function {}; days must be defined in setup using $configureDay(...).".format(dayNumber, funcName), astloc)

    # get list of tags which must be found by end of the specified day
    tagManager = env.getTagManager()
    tagList = tagManager.findDeadlineTags(dayNumber)
    tagList = tagManager.sortByTypeAndObfuscatedLabel(tagList)
    itemCount = len(tagList)

    # when text
    if (whenStr=="start"):
        mustText1 = "**must** be found before you may end"
        mustText2 = "You should note this in your case log in some way to avoid having to consult this list while playing"
        whenText = "Record in your case log that"
    elif (whenStr=="end"):
        mustText1 = "**must** have been found before you ended"
        mustText2 = "If you have missed {}, return to searching for leads until you find all of them (if stuck, consult the hints section)".format(jrfuncs.singularPlurals(itemCount,"it", "one or more"))
        whenText = "You should have noted in your case log that"
    else:
        raise makeJriException("Unknown 'when' argument ({}) to function {}.".format(whenStr, funcName), astloc)
    # 
    textEd = jrfuncs.alternateText(whenStr=="start","s","ed")

    # for markdown conversion
    renderer = env.getRenderer()

    # text for required items that must be found
    latex = ""
    if (itemCount==0):
        text = "There are no items that must be found before the end of **day {}**.\n".format(dayNumber)
        symbolName = None
    else:
        text = "The following {} {} **day {}**. {}:\n".format(jrfuncs.singularPlurals(itemCount,"item", "**" + str(itemCount) +"** items"), mustText1, dayNumber, mustText2)
        # make a nice sorted list, documents followed by markers
        for tag in tagList:
            tagNameObfuscated = tag.getNiceObfuscatedLabelWithType(True, reportMode)
            text += "* {}\n".format(tagNameObfuscated)
        symbolName = "markerGeneric"
    #
    if (symbolName is not None):
        latex += generateLatexForSymbol(symbolName, None, None)
    latex += renderer.convertMarkdownToLatexDontVouch(text)

    # add info about time limits
    start = day.getStartTime()
    end = day.getEndTime()
    if (start>0) and (end>0):
        # tell them about deadline times
        startTimeStr = convertHoursToNiceHourString(start)
        endTimeStr = convertHoursToNiceHourString(end)

        text = "THE CLOCK IS TICKING! "

        text += whenText + " **day {}** start{} at **{}** and end{} at **{}**.".format(dayNumber, textEd, startTimeStr, textEd, endTimeStr)
        if (itemCount>0):
            if (itemCount==1):
                allItemText1 = "the required item"
            else:
                allItemText = "all of the required items"
            text += " If you have *not* found {} listed above by **{}**, you enter **overtime**.  In overtime there is no limit to how many leads you may visit, time does not advance, and your day ends once you find {}.".format(allItemText, endTimeStr, allItemText)
        else:
            text += "Keep track of what time you visit each lead, until you reach (or pass) **{}**, after which your day ends.".format(endTimeStr)
        # build latex
        latex += "\n~\n\n" + generateLatexForSymbol("clock", None, None)
        latex += renderer.convertMarkdownToLatexDontVouch(text)

    # wrap these two sections above in a box
    latex = wrapTextInLatexBox("default", latex, False, None, None, None)
    latex += "\n"

    # now add hint info
    if (itemCount>0):
        if (whenStr == "start"):
            text = "**Note**: There are specific hints available for each of the the day's required items (see index)."
            #
            hintAlly = day.getFreeAlly()
            freeAllyStartTime = day.getFreeAllyStartTime()
            freeAllyEndTime = day.getFreeAllyEndTime()
            if (hintAlly is not None) and (hintAlly!=""):
                # tell them about a specific ally who can help more
                text += " However, if you need guidance on where to focus your efforts on any given day, "
                if (hintAlly=="financialPrecinct"):
                    text += "you can drop by your old police precinct in the Financial District for some advice"
                    allyDetailText = "you can catch the chief on his break and get his advice without penalty"
                else:
                    raise makeJriException("Unknown hintAlly ({}) in dayConfigure.".format(hintAlly))
                freeAllyStartTimeStr = convertHoursToNiceHourString(freeAllyStartTime)
                freeAllyEndTimeStr = convertHoursToNiceHourString(freeAllyEndTime)
                if (freeAllyStartTime>-1) and (freeAllyEndTime>-1):
                    text += " (if you arrive between **{} and {}** {}).".format(freeAllyStartTimeStr, freeAllyEndTimeStr, allyDetailText)
                elif (freeAllyStartTime>-1):
                    text += " (if you arrive after **{} {}).".format(freeAllyStartTimeStr, allyDetailText)
                elif (freeAllyEndTime>-1):
                    text += " (if you arrive before **{} {}).".format(freeAllyEndTimeStr, allyDetailText)
                else:
                    text += "."
            text += "\n"
        else:
            text = ""
        if (text!=""):
            # add latex symbol, etc.
            latex += generateLatexForSymbol("hand", None, None)
            latex += renderer.convertMarkdownToLatexDontVouch(text)
    
    # vouch for entire text
    return vouchForLatexString(latex, False)



def funcBlurbStop(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # display a "STOP" warning message
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    typeStr = args["type"].getWrappedExpect(AstValString)
    dayNumber = args["day"].getWrappedExpect(AstValNumber)
    rest = args["rest"].getWrappedExpect([AstValBool,AstValNull])


    if (dayNumber!=-1):
    # get day object
        dayManager = env.getDayManager()
        day = dayManager.findDayByNumber(dayNumber)
        if (day is None):
            raise makeJriException("Unknown 'dayNumber' ({}) specific argument to function {}; days must be defined in setup using $configureDay(...).".format(dayNumber, funcName), astloc)
        # get list of tags which must be found by end of the specified day
        tagManager = env.getTagManager()
        tagList = tagManager.findDeadlineTags(dayNumber)
        itemCount = len(tagList)
    else:
        itemCount = 0

    blurbDict = {
        # these are actually used
        "dayStart": {"txt": "Stop reading this case book now, and begin searching for leads in the directories.\n\nContinue to the next page only when you are ready to " + (" end **day {}**.".format(dayNumber)) if (dayNumber !=-1) and (itemCount>=1) else "end the current day.",},
        "nextDay": {"txt": "Proceed only when you are ready to begin " + "**day {}**.".format(dayNumber) if (dayNumber !=-1) else "the next day.", "rest": True},
        "conclusion": {"txt": "The case is nearing an end. You will have another chance to search for leads, but in the meantime, turn to: ", "rest": True,},
        "questions": {"txt": "Proceed only when you are ready to answer questions."},
        "questionPause": {"txt": "Once you have answered all questions on the previous page(s) you may continue to the next page.",},
        "leads": {"txt": "WARNING! Do **not** read through the rest of this document like a book from beginning to end. Lead entries are meant to be read individually only when you look up a lead by its number.\n\nClose this book now and follow rulebook instructions for looking up leads.",},
        "documents": {"txt": "Do **not** access the documents section unless directed to retrieve a specific document.",},
        "hints": {"txt": "Do **not** access the hints section except when looking up a specific hint from the table of contents at the start of this case book.",},

        # i dont think we actually use these, they are hypothetically useful
        "dayEnd": {"txt": "Proceed only after you have completed searching for leads on " + ("**day {}**, and found the day's required **{} item{}**.".format(dayNumber, itemCount, jrfuncs.plurals(itemCount,"s"))) if (dayNumber !=-1) and (itemCount>=1) else "the current day.",},
        "nightEnd": {"txt": "Proceed only after you have finished resolving any special **Late Night** actions described on the previous pages.",},
        "resolvePause": {"txt": "Once you have resolved the previous page you may continue to the next page.",},
        "solution": {"txt": "Once you have answered all questions on the previous page(s) you may turn the page for the **conclusion to the case**."},
        "end": {"txt": "Do **not** turn the page until you are ready to begin wrapping up your case.",},
        "noMore": {"txt": "Your case has ended, there is nothing more to read.",},
        "begin": {"txt": "Stop reading this case book now, and begin searching for leads in the directories.",},
    }

    if (typeStr in blurbDict):
        blurb = blurbDict[typeStr]
    else:
        raise makeJriException("Unknown blurb type ({}).".format(typeStr))
    
    # build reply
    renderer = env.getRenderer()
    text = blurb["txt"]

    # assemble result
    results = JrAstResultList()
    latex = ""

    #
    latex += r"\begin{Huge}\bfseries \textbf{" + "STOP!" + r"}\par\end{Huge}" + "\n\n~\n\n"
    symbolName = "stop"
    if (symbolName is not None):
        latex += generateLatexForSymbol(symbolName, "red", None) + "  "
    latex += renderer.convertMarkdownToLatexDontVouch(text)

    # special stuff
    if (typeStr=="conclusion"):
        # intermediate add, then deferred link to conclusion
        results.flatAdd(vouchForLatexString(latex,False))
        # make DEFERRED link to entry lead
        page = True
        href = True
        showLabel = True
        showId = True
        id = "Conclusion"
        result = CbDeferredBlockRefLead(astloc, entryp, leadp, id, page, href, showLabel, showId)
        results.flatAdd(result)
        latex = ".\n"

    # rest?
    if (rest is None) and ("rest" in blurb):
        rest = blurb["rest"]
    if (rest):
        latex += "\n\n~\n\n" + r"\textit{NOTE: If you’ve been playing for a couple of hours, now might be a good time to take a break before continuing...}" +"\n"

    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    return results
# ---------------------------------------------------------------------------














# ---------------------------------------------------------------------------
def funcLogic(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure a specific day

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    label = args["label"].getWrappedExpect(AstValString)
    typeStr = customData["type"]
    direction = customData["direction"]

    # renderer
    renderer = env.getRenderer()

    # target and source
    if (direction=="ab"):
        source = leadp
        target = args["target"].getWrappedExpect(AstValString)
    elif (direction=="ba"):
        target = leadp
        source = args["source"].getWrappedExpect(AstValString)
    else:
        source = leadp
        target = None

    # mindmapper
    mindMapper = env.getMindManager()
    if (source is not None) and (target is not None):
        mindMapper.addLinkBetweenNodes(env, typeStr, label, source, target)
    else:
        mindMapper.addLinkAtributeOnNode(env, typeStr, label, source)

    # just return blank
    return ""
# ---------------------------------------------------------------------------


















#---------------------------------------------------------------------------
def funcAuthorNote(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # marks a target block to ONLY be shown in author debug output
    # this looks a lot like the $format() function but does not display if not building author report mode

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)
    
    label = args["label"].getWrappedExpect(AstValString)

    # only show in report mode
    reportMode = env.getReportMode()
    if (not reportMode):
        return ""

    # the style
    astyle = {"boxStyle": "report", "symbol": "report", "symbolColor":"red", "start": "", "end": ""}
    boxStyle = astyle["boxStyle"]
    symbol = astyle["symbol"]
    symbolColor = astyle["symbolColor"]

    # assemble result
    results = JrAstResultList()

    # box start
    latexBoxDict = generateLatexBoxDict(boxStyle, None)
    latex = latexBoxDict["start"]
    results.flatAdd(vouchForLatexString(latex, False))

    # wrap content start
    latex = astyle["start"]
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # symbol
    latex = generateLatexForSymbol(symbol, symbolColor, None)
    results.flatAdd(vouchForLatexString(latex, False))

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
    # allow user to add arbitrary text/image between title and details using target blocks
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, leadp)
        results.flatAdd(targetRetv)

    # wrap content end
    latex = astyle["end"]      
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # box end
    if (boxStyle):
        latex = latexBoxDict["end"]
        results.flatAdd(vouchForLatexString(latex, False))



    # results
    return results
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcMarginNote(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # marks a target block to ONLY be shown in author debug output
    # this looks a lot like the $format() function but does not display if not building author report mode

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)
    
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
    # allow user to add arbitrary text/image between title and details using target blocks
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, leadp)
        results.flatAdd(targetRetv)

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
    info["difficulty"] = args["difficulty"].getWrapped()
    info["duration"] = args["duration"].getWrapped()

    # empty text reply (does not add text)
    return ""


def funcConfigureGameSummary(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    info = env.getEnvValueUnwrapped(None, "info", None)
    info["summary"] = args["summary"].getWrapped()

    # empty text reply (does not add text)
    return ""


def funcConfigureGameInfoExtra(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "info", None)
    data["cautions"] = args["cautions"].getWrapped()
    data["url"] = args["url"].getWrapped()
    data["extraCredits"] = args["extraCredits"].getWrapped()
    data["keywords"] = args["keywords"].getWrapped()

    # empty text reply (does not add text)
    return ""


def funcConfigureClock(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "info", None)
    data["clockMode"] = args["clockMode"].getWrapped()

    # empty text reply (does not add text)
    return ""


def funcConfigureLeadDb(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "leadDbData", None)
    data["version"] = args["version"].getWrapped()
    data["versionPrevious"] = args["versionPrevious"].getWrapped()

    # empty text reply (does not add text)
    return ""


def funcConfigureParser(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "parserData", None)
    #data["balancedQuoteCheck"] = args["balancedQuoteCheck"].getWrapped()

    # empty text reply (does not add text)
    return ""


def funcConfigureRenderer(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "rendererData", None)
    data["doubleSided"] = args["doubleSided"].getWrapped()
    data["latexPaperSize"] = args["latexPaperSize"].getWrapped()
    data["latexFontSize"] = args["latexFontSize"].getWrapped()
    data["autoStyleQuotes"] = args["autoStyleQuotes"].getWrapped()

    # empty text reply (does not add text)
    return ""


def funcConfigureDocuments(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # configure
    data = env.getEnvValueUnwrapped(None, "documentData", None)
    data["defaultLocation"] = args["defaultLocation"].getWrapped()
    data["printLocation"] = args["printLocation"].getWrapped()
    data["printStyle"] = args["printStyle"].getWrapped()
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
    # Embed an image into a pdf
    # see https://tex.stackexchange.com/questions/167719/how-to-use-background-image-in-latex

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    # args
    path = args["path"].getWrappedExpect(AstValString)
    opacity = args["opacity"].getWrappedExpect(AstValNumber)

    # get image import helper, and try to find image first in game-specicific list then fallback to shared
    [imageFullPath, foundFileManagerLabel] = env.findFullPathImageOrPdf(path, True)
    if (imageFullPath is None):
        raise makeJriException("Image file not found ({}).".format(path), astloc)

    # build latex includegraphics command
    includeGraphicsLatexLine =r"\includegraphics[width=\paperwidth,height=\paperheight]{" + imageFullPath + "}"
    if (opacity<1.0):
        nodeLine = r"\node[opacity=" + str(opacity) + "] at (current page.center) {"
    else:
        nodeLine = r"\node at (current page.center) {"
    #
    latex = r"""
\AddToHookNext{shipout/background}{
  \begin{tikzpicture}[remember picture,overlay]
  """ + nodeLine + "\n   " + includeGraphicsLatexLine + r"""
  };
  \end{tikzpicture}
}
"""


    # add note for debug report
    notePath = foundFileManagerLabel + "({})".format(path)
    msg = 'Set page background: "{}"'.format(notePath)
    msgLatex = 'Set page background: "\\path{' + notePath + '}"'
    extras = {"img": imageFullPath}
    note = JrINote("embedImage", leadp, msg, msgLatex, extras)
    env.addNote(note)
    #
    return vouchForLatexString(latex, False)
# ---------------------------------------------------------------------------

















#---------------------------------------------------------------------------
def funcDropCaps(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # marks a target block to ONLY be shown in author debug output
    # this looks a lot like the $format() function but does not display if not building author report mode

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)
    
    style = args["style"].getWrapped()

    # options
    optionLines = args["lines"].getWrapped()
    optionFindent = "0.25em"
    optionNindent = "0.75em"
    optionProtectStyle = args["multi"].getWrapped()
    lettrineOptions = "[lines={},findent={},nindent={},lhang=0.2]".format(optionLines, optionFindent, optionNindent)

    # to help us with markdown
    renderer = env.getRenderer()

    # assemble result
    results = JrAstResultList()

    # contents of targets
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, leadp)
        results.flatAdd(targetRetv)
    
    # now we want to find the first textual line

    didWork = False
    afterIndex = -1
    for index, block in enumerate(results.getContents()):
        if (isinstance(block,str)):
            text = block
        elif (isinstance(block,AstValString)):
            text = block.getUnWrappedExpect(AstValString)
        else:
            continue
        if (text=="\n") or (text==""):
            continue
        if (isTextLatexVouched(text)):
            continue
        # ok we have some pure text
        [firstChar, upperCaseText, remainderText] = jrfuncs.smartSplitTextForDropCaps(text)
        if (firstChar is not None):
            firstChar = text[0]
            latexLettrine = r"\lettrine" + lettrineOptions + "{" + firstChar + "}"
            if (upperCaseText!=""):
                latexLettrine += "{" + renderer.convertMarkdownToLatexDontVouch(upperCaseText) + "}"
            # build new results to insert at this point
            resultsIn = JrAstResultList()
            resultsIn.flatAdd(vouchForLatexString(latexLettrine, True))
            resultsIn.flatAdd(remainderText)
            # insert it
            results.removeByIndex(index)
            results.flatInsertAtIndex(resultsIn, index)

            # kludgey way to replace parargraphs so that dropcase lettrine indents all paragraphs in this text target block
            if (optionProtectStyle=="none"):
                results.flatAdd("\n")
            elif (optionProtectStyle=="wrap"):
                afterIndex = index+1
                sequentialNewlines = 0
                latexFpar = vouchForLatexString(r"\fakepar" + "\n", False)
                for index2 in range(afterIndex, len(results.getContents())):
                    block2 = results.contents[index2]
                    if (block2=="\n"):
                        sequentialNewlines += 1
                        if (sequentialNewlines==1):
                            # change "\n" newline paragraph to fpar
                            results.removeByIndex(index2)
                            results.flatInsertAtIndex(latexFpar, index2)
                            sequentialNewlines = 0
                    else:
                        sequentialNewlines = 0
            elif (optionProtectStyle=="gap"):
                # try to force the drop cap to force following paragraphs down
                #latexAdd = r"\ifnum\prevgraf<" + str(optionProtectLines) + r" \vspace{\baselineskip}\vspace{" + optionProtectExtraVspace + r"}\fi "
                latexAdd = r"\ifnum\prevgraf<" + str(optionLines) + " " + r"\vspace{" + str(optionLines) + r"\baselineskip} \vspace{-\dimexpr \prevgraf\baselineskip} "
                # last line kludge
                lastBlock = results.contents[len(results.contents)-1]
                if (lastBlock!="\n"):
                    latexAdd = "\n" + latexAdd
                results.flatAdd(vouchForLatexString(latexAdd, True))
                # KLUDGE since we have added a paragraph above in order to check prevgrad, we eat the next newline in source
                results.flatAdd(CbDeferredBlockAbsorbFollowingNewline(astloc, entryp, leadp))
            else:
                raise makeJriException("Unknown multi option '{}' for $dropcase()".format(optionProtectStyle), astloc)
        didWork = True
        break

    # results
    return results
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def funcLipsum(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):

    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    start = args["start"].getWrapped()
    end = args["end"].getWrapped()
    if (end==-1):
        end = start
    latex = "\\lipsum[{}-{}]".format(start,end)
    return vouchForLatexString(latex, False)
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcDesignateFile(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # ATTN: unfinished
    path = args["path"].getWrapped()
    tag = args["tag"].getWrapped()
    rename = args["rename"].getWrapped()

    # find the file mentioned
    [fileFullPath, foundFileManagerLabel] = env.findFullPathImageOrPdf(path, True)
    if (fileFullPath is None):
        raise makeJriException("Image file not found ({}).".format(path), astloc)

    # add note for debug report
    notePath = foundFileManagerLabel + "({})".format(path)
    msg = 'Designated file with tag: "{}"'.format(notePath)
    msgLatex = 'Designated file with tag: "\\path{' + notePath + '}"'
    extras = {"filePath": fileFullPath}
    note = JrINote("designateFile", leadp, msg, msgLatex, extras)
    env.addNote(note)

    renderer = env.getRenderer()
    renderer.designateFile(fileFullPath, tag, rename)

    return ""
#---------------------------------------------------------------------------


















#---------------------------------------------------------------------------
def funcQuote(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    if (rmode != DefRmodeRender):
        return "DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName)

    style = args["style"].getWrapped()
    boxStyle = args["box"].getWrapped()
    symbol = args["symbol"].getWrapped()
    cite= args["cite"].getWrapped()
    position = args["pos"].getWrapped()
    #
    symbolColor = None
    boxExtras = {}

    # select group of options
    optionsDict = {
        "default": {"boxStyle": "hLines"},
    }

    if (style not in optionsDict):
        raise makeJriException("Runtime Error: $quote({}) should be from {}.", style, optionsDict.keys())
    # the style
    options = optionsDict[style]

    # programmatically override
    options["start"] = r" \begin{cb_quoteenv} \setstretch{1} \huge \textit{"
    #
    options["end"] = r" \end{cb_quoteenv}"

    # alignment
    boxExtras["alignment"] = "none"
    citeAlign = r"flushright"
    if (position in ["right","topRight"]):
        boxExtras["alignment"] = "right"
        citeAlign = r"flushright"
    elif (position in ["left", "topLeft"]):
        citeAlign = r"flushleft"

    # add citation
    if (cite!=""):
        options["end"] = r"} \begin{" + citeAlign + r"} \vspace{0.5em} \textbf{ - " + convertEscapeUnsafePlainTextToLatex(cite) + r"} \end{" + citeAlign + r"} " +  options["end"]


    # defaults and overrides
    if (symbol is None) and ("symbol" in options):
        symbol = options["symbol"]
    if (boxStyle is None) and ("boxStyle" in options):
        boxStyle = options["boxStyle"]

    # assemble result
    results = JrAstResultList()

    # box start
    if (boxStyle):
        latexBoxDict = generateLatexBoxDict(boxStyle, boxExtras)
        latex = latexBoxDict["start"]
        results.flatAdd(vouchForLatexString(latex, False))

    # wrap content start
    if ("startFunc" in options):
        latex = options["startFunc"]({})
    else:
        latex = options["start"]
    #
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # symbol
    if (symbol is not None):
        if (symbolColor is None) and ("symbolColor" in options):
            symbolColor = options["symbolColor"]
        latex = generateLatexForSymbol(options["symbol"], symbolColor, None)
        results.flatAdd(vouchForLatexString(latex, False))

    # contents of targets
    # allow user to add arbitrary text/image between title and details using target blocks
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, leadp)
        results.flatAdd(targetRetv)

    # wrap content end
    if ("endFunc" in options):
        latex = options["endFunc"]({})
    else:
        latex = options["end"]      
    if (latex!=""):
        results.flatAdd(vouchForLatexString(latex, False))

    # box end
    if (boxStyle):
        latex = latexBoxDict["end"]
        results.flatAdd(vouchForLatexString(latex, False))

    if (position in ["topRight", "topLeft"]):
        # be nice and auto add a deferred header afterwords to make sure header of lead comes after
        deferredResult = CbDeferredBlockLeadHeader(astloc, entryp, leadp)
        # tell the lead to NOT auto render header
        leadp.setAutoHeaderRender(False)
        results.flatAdd(deferredResult)

    # results
    return results
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcCalendar(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # ATTN: unfinished
    start = args["start"].getWrapped()
    end = args["end"].getWrapped()
    strikeStart = args["strikeStart"].getWrapped()
    strikeEnd = args["strikeEnd"].getWrapped()
    circle = args["circle"].getWrapped()

    dateStartString = convertEscapeUnsafePlainTextToLatexMorePermissive(start)
    dateEndString = convertEscapeUnsafePlainTextToLatexMorePermissive(end)
    strikeStartString = convertEscapeUnsafePlainTextToLatexMorePermissive(strikeStart)
    strikeEndString = convertEscapeUnsafePlainTextToLatexMorePermissive(strikeEnd)
    circleString = convertEscapeUnsafePlainTextToLatexMorePermissive(circle)

    latex = r"""
    \tikz[every day/.style={anchor=mid}]\calendar[dates=""" + dateStartString + " to " + dateEndString + r""",
        week list,
        month label above centered,
        day xshift = 0.8cm,
        day headings=orange,
        day letter headings,
        month text=\textit{\%mt \%y0}
    ]
"""
    if (strikeStartString != ""):
        latex += r"if (between=" + strikeStartString + r" and " + strikeEndString + r") [nodes={strike out,draw}]" + "\n"
    if (circleString != ""):
        latex += r"if (equals=" + circleString + r") { \draw (0,0) circle (8pt);}" + "\n;\n"

    return vouchForLatexString(latex, False)
#---------------------------------------------------------------------------

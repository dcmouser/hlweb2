# core casebook functions


# jr ast helpers
from .jrcbfuncs import CbFunc, CbParam
from .jrast import AstValString, AstValNumber, AstValBool, AstValIdentifier, AstValList, AstValDict, AstValNull, convertTypeStringToAstType, JrAstResultList, DefCbDefine_IdBlank, DefCbDefine_IDEmpty
from .jrast import ResultAtomLatex, ResultAtomMarkdownString, ResultAtomPlainString, ResultAtomNote
from .jrastvals import AstValObject
from .cbtask import DefRmodeRun, DefRmodeRender
from .jriexception import *
from .jrastfuncs import getUnsafeDictValueAsString, makeLatexLinkToRid, vouchForLatexString, convertEscapeUnsafePlainTextToLatex, convertEscapePlainTextFilePathToLatex, convertEscapeUnsafePlainTextToLatexMorePermissive, convertIdToSafeLatexId
from .jrastfuncs import isTextLatexVouched, unwrapIfWrappedVal
from .jrastutilclasses import JrINote

#
from .cbdeferblock import CbDeferredBlockRefLead, CbDeferredBlockCaseStats, CbDeferredBlockFollowCase, CbDeferredBlockAbsorbFollowingNewline, CbDeferredBlockAbsorbPreviousNewline
# helpers for funcs
from .cbfuncs_core_support import calcInlineLeadLabel, parseTagListArg, buildLatexMarkCheckboxSentence, wrapInLatexBox, wrapInLatexBoxJustStart, wrapInLatexBoxJustEnd, generateLatexForSymbol, generateLatexForDivider, generateLatexRuleThenLineBreak, convertHoursToNiceHourString, generateLatexBreak, generateImageEmbedLatex, generateLatexForPageStyle, generateLatexCalendar
from .cbfuncs_core_support import parseArgsGenericBoxOptions, isBoxRequested, addBoxToResultsIfAppropriateStart, addBoxToResultsIfAppropriateEnd, addTargetsToResults, addTargetsToResultsIntoCommand, exceptionIfNotRenderMode, addResultsToResults
from .cbfuncs_core_support import findDayByNumber, createStartEndLatexForFontSizeString, makeLatexSafeFilePath, parseFontSize, convertNumericWidthToFraction, convertStringToSafeLatexSize
from .cbfuncs_core_support import getTargetResultBlockAsTextIfAppropriate, convertTargetRetvToResultList
from .cbfuncs_core_support import cipherMakeRandomSubstitutionKeyFromHash, cipherMakeSimpleSubstitutionKeyFromKeyword, cipherMakeUniqueKeywordAlphabet, cipherSpellDigits, cipherSegment, cipherStripChars, cipherMorseCode, cipherReplaceNonLettersReturnFixList, cipherReplaceFixList, cipherRemoveReplacePunctuation
from .cbfuncs_core_support import formHelperListBuild, functionRunEffectOnImagePath, wrapInFigureCaption
from .cbfuncs_core_support import makeMiniPageBlockLatexStart, makeMiniPageBlockLatexEnd, dropCapResults
from .cbfuncs_core_support import newsLatexFormatHeadlineString, newsLatexFormatBylineString, safeLatexSizeFromUserString
from .cbfuncs_core_support import irpWhenText, addGainTagTextLineToResults, wrapLatexInColorStart, wrapLatexInColorEnd, buildFormElementTextLatex, generateFormTextLatex
#
from .casebookDefines import *

# translation
from .cblocale import _


# python modules
import re
from datetime import datetime














def buildFunctionList():
    # create the functions
    functionList = []

    # CbFunc takes: (name, description, paramList, returnType, targetsAccepted, customData, funcPointer, astloc=None)
    # CbParam takes: (name, description, defaultVal, flagAllowNull, paramCheck, flagResolveIdentifiers)

    #---------------------------------------------------------------------------




    #---------------------------------------------------------------------------
    functionList.append(CbFunc("instructionsEvening", "Display boilerplate instructions about how an evening event works", [
            CbParam("day", "Day number", None, False, AstValNumber, False),
            CbParam("next", "Next lead to go to after they finish", None, False, AstValString, False),
            CbParam("reputationBonus", "Instruct them about reputation bonuses", True, False, AstValBool, False),
            CbParam("final", "Final evening", False, False, AstValBool, False),
            
        ],
        "text", None, None,
        funcInstructionsEvening
        ))



    functionList.append(CbFunc("instructionsStartDay", "Tell the player some brief instructions of how to play using new event system", [
            CbParam("day", "Day number", None, False, AstValNumber, False),
            CbParam("box", "Box style", "default", True, [AstValString,AstValBool], False),
            #
            CbParam("bonus", "Is this a bonus day?", False, False, AstValBool, False),
            CbParam("bonusReputation", "reputation for skipping bonus day", 0, False, AstValNumber, False),
            CbParam("bonusTag", "tag to make them mark if they choose to skip bonus day", None, True, AstValString, True),

        ],
        "text", None, None,
        funcInstructionsStartDay
        ))


    functionList.append(CbFunc("instructionsEndLastDay", "Display boilerplate instructions to wrap up your case", [
            CbParam("day", "Day number", None, False, AstValNumber, False),
            CbParam("overtime", "Allow player to go into overtime", False, True, AstValBool, False),
            CbParam("demerits", "Demerits for going into overtime", None, True, AstValNumber, False),
            CbParam("goLead", "id of lead to go to to end case", None, True, AstValString, True),
        ],
        "text", None, None,
        funcInstructionsEndLastDay
        ))


    functionList.append(CbFunc("instructionsPostQuestionsResume", "Display boilerplate instructions to let player go back and read leads again", [
            CbParam("day", "Day number", None, False, AstValNumber, False),
            CbParam("demerits", "Demerits for going into overtime", 0, False, AstValNumber, False),
            CbParam("tag", "tagid to make them mark if they choose to skip bonus day", None, True, AstValString, True),
            CbParam("halve", "Tell them to halve their score if they change", True, True, AstValBool, False),
        ],
        "text", None, None,
        funcInstructionsPostQuestionsResume
        ))
    #---------------------------------------------------------------------------






    #---------------------------------------------------------------------------
    functionList.append(CbFunc("instructionsIrps", "Display boilerplate instructions about irps", [
            CbParam("start", "Tell player they are starting with this number of IRPs", None, True, AstValNumber, False),
            CbParam("gain", "Tell player they are gaining this number of IRPs", None, True, AstValNumber, False),
            CbParam("use", "Tell player to use them now", False, True, AstValBool, False),
            CbParam("lastUse", "Is it players last chance to use irps", False, True, AstValBool, False),            
            CbParam("max", "Max irps player may spend now", None, True, AstValNumber, False),
            CbParam("when", "When they can read/visit the leads? (blank for no comment)", None, True, [AstValNumber, AstValString], False),
        ],
        "text", None, None,
        funcInstructionsIrps
        ))

    functionList.append(CbFunc("instructionsScheduledEvent", "Display boilerplate instructions not to read entry unless triggering an event", [
        ],
        "text", None, None,
        funcInstructionsScheduledEvent
        ))
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    functionList.append(CbFunc("event", "Boilerplate language to schedule an event", [
            CbParam("lead", "What lead player should read at schedule time", None, True, AstValString, False),
            CbParam("day", "Day number when", None, True, AstValNumber, False),
            CbParam("time", "Time when", None, True, AstValString, False),
            CbParam("when", "When they can read/visit the lead", None, True, AstValString, False),
            CbParam("mandatory", "is it mandatory", None, True, AstValBool, False),
            CbParam("label", "Label of the event", None, True, AstValString, False),
            CbParam("duration", "Duration of an inline lead", None, True, AstValString, False),
        ],
        "text", "optional", None,
        funcEvent
        ))


    functionList.append(CbFunc("scheduleIrp", "Boilerplate language to schedule an irp expenditure to read a lead", [
            CbParam("lead", "What lead player should read at schedule time", None, False, AstValString, False),
            CbParam("cost", "Cost in IRP", 1, False, AstValNumber, False),
            CbParam("when", "When they can read/visit the lead", None, True, [AstValNumber, AstValString], False),
        ],
        "text", None, None,
        funcScheduleIrp
        ))
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    functionList.append(CbFunc("referDb", "Lookup a lead by NAME and display a link to it", [
            CbParam("id", "search string to look for", None, True, AstValString, False),
            CbParam("style", "style to show lead info", "default", False, ["default", "full", "nolabel", "plainid", "page", "pageparen", "pagenum"], True),
        ],
        "text", None, None,
        funcReferDb
        ))
    #---------------------------------------------------------------------------



    #---------------------------------------------------------------------------
    # ATTN: THIS CURRENTLY HAS NO USE CASE
    if (False):
        functionList.append(CbFunc("formatAfterImage", "format some text after a left aligned image", [
            ],
            "text", 1, None,
            funcFormatAfterImage
            ))
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    functionList.append(CbFunc("defineQuestion", "Create a question", [
            CbParam("id", "Id of the question (like Q1)", None, True, AstValString, False),
            CbParam("summary", "Summary of question for repeating in answer", None, True, AstValString, False),
            CbParam("points", "Max points the question is worse", None, True, [AstValString, AstValNumber], False),
            CbParam("type", "Question type", None, True, AstValString, False),
            CbParam("size", "How much size for answer space", None, True, AstValNumber, False),
            CbParam("lines", "How many lines for answer spaces", None, True, AstValNumber, False),
            CbParam("choices", "List of choices, separated by | character", None, True, AstValString, True),
        ],
        "text", "optional", None,
        funcDefineQuestion
        ))


    functionList.append(CbFunc("questionAnswer", "Display answer to a question", [
            CbParam("id", "Id of the question (like Q1)", None, True, AstValString, False),
            CbParam("summary", "Override summary", None, True, AstValString, False),
        ],
        "text", 1, None,
        funcQuestionAnswer
        ))

    functionList.append(CbFunc("questionTotal", "Display a line for them to record their total score from questions", [
        ],
        "text", None, None,
        funcQuestionTotal
        ))

    functionList.append(CbFunc("pointsLine", "Display a line with form after leder", [
            CbParam("text", "Text for left side", None, False, AstValString, False),
        ],
        "text", None, None,
        funcPointsLine
        ))
    functionList.append(CbFunc("lederLine", "Display right-aligned element", [
            CbParam("leftText", "Text for left side", None, False, AstValString, False),
            CbParam("rightText", "Text for right side", None, False, AstValString, False),
        ],
        "text", None, None,
        funcLederLine
        ))
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






















#---------------------------------------------------------------------------
def funcInstructionsStartDay(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    dayNumber = args["day"].getWrapped()
    bonusReputation = args["bonusReputation"].getWrapped()
    bonusTagId = args["bonusTag"].getWrapped()

    # get day object
    dayManager = env.getDayManager()
    flagAllowTempCalculatedDay = False
    day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
    if (day is None):
        raise makeJriException("Unknown 'dayNumber' ({}) specified as argument to function {}; days must be defined in setup using $configureDay(...) but day {} has not been defined.".format(dayNumber, funcName, dayNumber), astloc)
    dayDate = day.getDate()
    dayStartTime = day.getStartTime()
    dayEndTime = day.getEndTime()
    endTimeStr = convertHoursToNiceHourString(dayEndTime)
    startTimeStr = convertHoursToNiceHourString(dayStartTime)
    dayDateShort = jrfuncs.shortDayDateStr(dayDate, False)

    # tag
    if (bonusTagId is not None):
        bonusTag = env.findTagOrConcept(bonusTagId, True)
    else:
        bonusTag = None

    # helpers
    renderer = env.getRenderer()
    reportMode = env.getReportMode()

    # assemble result
    results = JrAstResultList()


    # wrap it and add symbol
    useBox = True
    boxOptions = {
        "box": "default",
        "symbol": "clock",
        #"symbol": "warning",
        #"textColor": "red",
        "isTextSafe": True,
    }
    if (bonusReputation>0) or (bonusTag is not None):
        #boxOptions["symbol"] = "warning"
        boxOptions["symbolColor"] = "red"
    if useBox:
        addBoxToResultsIfAppropriateStart(boxOptions, results)

    tagManager = env.getTagManager()
    tagList = tagManager.findDeadlineTags(dayNumber)
    
    # build output
    if (bonusReputation>0) or (bonusTag is not None):
        # bonus day info
        if (len(tagList)>0):
            text = _("This is your last day.  You **may** already know everything you need to know to wrap up the case.  If you think you do, you can simply advance the clock now (or at any time during the day) to trigger the end of day event above.\n")
        else:
             text = _("This is your last day.  There are **no** items that you are required to find today, and you may already know everything you need to know to wrap up the case. You may wish to simply advance the clock now (or at any time during the day) to trigger the end of day event above.\n")
           
        results.flatAdd(text)
        results.flatAdd("~\n")

        # bonus important line
        textColor = "red"
        if (textColor is not None):
            results.flatAdd(vouchForLatexString(wrapLatexInColorStart(textColor), True))

        if (bonusReputation>0):
            # after, tell them to mark demerits
            results.flatAdd("\n")
            upto = False
            whyText = _("if you choose to advance the clock now to **{}** and trigger the above end of day event immediately").format(endTimeStr)
            whyLatex = renderer.convertMarkdownToLatexDontVouch(whyText, False, False)
            markLatex = buildLatexMarkCheckboxSentence("reputation", bonusReputation, True, True, False, "red", whyLatex, upto)
            results.flatAdd(vouchForLatexString(markLatex, False)+"\n")
            checkboxManager = env.getCheckboxManager()
            checkboxManager.recordCheckMarks(env, astloc, leadp, "reputation", bonusReputation)
        if (bonusTag is not None):
            # tell them they should mark tag if they skip
            tagActionKeyword = "circle"
            results.flatAdd("\n")
            whyText = _("If you choose to advance the clock now to **{}** and trigger the above end of day event immediately, ").format(endTimeStr)
            results.flatAdd(whyText)
            addGainTagTextLineToResults(bonusTag, tagActionKeyword, results, reportMode, astloc, entryp, leadp, False, None)
            #
            bonusTag.recordGain(env, tagActionKeyword, astloc, leadp)

        # end bonus important line
        results.flatAdd(vouchForLatexString(wrapLatexInColorEnd(), True))
        results.flatAdd("\n~\n")
        mainInstructionTextStart = _("Otherwise, you are now ready to start your day.")
    else:
        mainInstructionTextStart = _("You are now ready to start your day.")

    # standard instructions
    text = mainInstructionTextStart
    text += _(" On a blank case log sheet record that it is Day **{}** (**{}**) and that the current time is **{}**.").format(dayNumber, dayDateShort, startTimeStr)
    text += " " + _("Then close this case book and begin searching for leads in the directories.  Don't forget to keep an eye on your schedule for the **{}** event above that will trigger and lead to the conclusion of your work day.").format(endTimeStr) + "\n"
    results.flatAdd(text)

    # end
    if useBox:
        addBoxToResultsIfAppropriateEnd(boxOptions, results)

    return results
#---------------------------------------------------------------------------



















#---------------------------------------------------------------------------
def funcInstructionsEvening(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    dayNumber = args["day"].getWrapped()
    nextLeadId = args["next"].getWrapped()
    reputationBonus = args["reputationBonus"].getWrapped()
    final = args["final"].getWrapped()

    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # get day object
    dayManager = env.getDayManager()
    flagAllowTempCalculatedDay = False
    day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
    if (day is None):
        raise makeJriException("Unknown 'dayNumber' ({}) specified as argument to function {}; days must be defined in setup using $configureDay(...) but day {} has not been defined.".format(dayNumber, funcName, dayNumber), astloc)
    dayDate = day.getDate()
    dayDateNice = jrfuncs.niceDayDateStr(dayDate, False, False)
    dayDateShort = jrfuncs.shortDayDateStr(dayDate, False)
    dayDateLong = jrfuncs.niceDayDateStr(dayDate, True, True)
    dayEndTime = day.getEndTime()
    endTimeStr = convertHoursToNiceHourString(dayEndTime)

    # get list of tags which must be found by end of the specified day
    tagManager = env.getTagManager()
    tagList = tagManager.findDeadlineTags(dayNumber)
    tagList = tagManager.sortByTypeAndObfuscatedLabel(tagList, env, False)
    itemCount = len(tagList)


    # for markdown conversion
    renderer = env.getRenderer()

    # assemble result
    results = JrAstResultList()

    # create nextLeadResult
    nextProceedResult = CbDeferredBlockRefLead(astloc, entryp, leadp, nextLeadId, "full")

    if (final):
        dayEndExtra = ", " + _("the final day of your case") + ", "
    else:
        dayEndExtra = ""

    #text = _("It's time to wrap up day {}, **{} at {}**.").format(dayNumber, dayDateShort, endTimeStr) + "\n"
    text = _("It's **{}** on **{}**, and day #**{}**{} is ending.").format(endTimeStr, dayDateLong, dayNumber, dayEndExtra) + "\n"
    #text = _("It's time to wrap up day {}, **{}**.").format(dayNumber, dayDateShort) + "\n"
    results.flatAdd(text)


    # box start
    boxOptions = {
        "box": "default",
        "symbol": "markerGeneric",
        # "symbolColor": "red"
    }
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    # text for required items that must be found
    latex = ""

    if (itemCount==0):
        text = _("Because are no specific items that you are required to find before the end of day {}, you must now proceed immediately to ").format(dayNumber)
        results.flatAdd(text)
        # make DEFERRED link to entry lead
        results.flatAdd(nextProceedResult)
        results.flatAdd(".\n")
        # end box
        addBoxToResultsIfAppropriateEnd(boxOptions, results)
    else:
        text = _("The following {} must be found before you may move on:").format(jrfuncs.singularPlurals(itemCount,_("item"), "**" + str(itemCount) +"** " + _("items"), None)) + "\n"
        # make a nice sorted list, documents followed by markers
        for tag in tagList:
            tagNameObfuscated = tag.getNiceObfuscatedLabelWithType(True, reportMode)
            text += "* {}\n".format(tagNameObfuscated)
        #latex = renderer.convertMarkdownToLatexDontVouch(text, False, False)
        #results.flatAdd(vouchForLatexString(latex, False))
        results.flatAdd(text)

        # end box
        addBoxToResultsIfAppropriateEnd(boxOptions, results)

        #
        itemsText = jrfuncs.singularPlurals(itemCount,_("this item"), _("all") + " **" + str(itemCount) +"** " + _("items"), " **" + _("both") + "** " + _("items"))

        #
        if (reputationBonus):
            #results.flatAddBlankLine()
            if (len(tagList)==1):
                text = _("Record +1 reputation in your case log if you have already found this item.") + "\n"
            else:
                text = _("Record +1 reputation in your case log for each of these items that you have already found, and an additional +{} reputation in your case log if you have already found {}.").format(len(tagList), itemsText) + "\n"
        #
            results.flatAdd(text)
        #
        text = _("If you have not yet found {}, resume searching for leads now until you have (using hints if needed), and consider yourself in **\"overtime\"** for the rest of the day; in overtime, time does not advance past **{}**.").format(itemsText, endTimeStr)
        results.flatAdd(text)
        results.flatAdd("\n")
        text = _("As soon as you have found {}, you must proceed to: ").format(itemsText)
        results.flatAdd(text)   
        # make DEFERRED link to entry lead
        results.flatAdd(nextProceedResult)
        results.flatAdd(".\n")

    return results
#---------------------------------------------------------------------------







#---------------------------------------------------------------------------
def funcInstructionsEndLastDay(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    dayNumber = args["day"].getWrapped()
    overtime = args["overtime"].getWrapped()
    demerits = args["demerits"].getWrapped()
    goLead = args["goLead"].getWrapped()

    # get day object
    dayManager = env.getDayManager()
    flagAllowTempCalculatedDay = False
    day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
    if (day is None):
        raise makeJriException("Unknown 'dayNumber' ({}) specified as argument to function {}; days must be defined in setup using $configureDay(...) but day {} has not been defined.".format(dayNumber, funcName, dayNumber), astloc)
    dayDate = day.getDate()
    dayStartTime = day.getStartTime()
    dayEndTime = day.getEndTime()
    endTimeStr = convertHoursToNiceHourString(dayEndTime)
    dayDateNice = jrfuncs.niceDayDateStr(dayDate, False, False)
    dayDateShort = jrfuncs.shortDayDateStr(dayDate, False)
    dayDateLong = jrfuncs.niceDayDateStr(dayDate, True, True)

    # assemble result
    results = JrAstResultList()
    renderer = env.getRenderer()

    # build output
    text = _("It's **{}** on **{}** (day #**{}**), and your case is coming to an end.").format(endTimeStr, dayDateLong, dayNumber) + "\n"
    results.flatAdd(text)

    if (overtime):
        # show a box with overtime options
        text = _("If there are still leads you wish to visit before ending the case, you may visit those leads now.\n")
        latex = renderer.convertMarkdownToLatexDontVouch(text, False, False)
        if (demerits>0):
            # after, tell them to mark demerits
            upto = False
            whyLatex = "if you choose to do so"
            markLatex = buildLatexMarkCheckboxSentence("demerit", demerits, True, True, False, "red", whyLatex, upto)
            latex += "\n\n~\n\n" + markLatex + "\n\n~\n\n"
            #inlineResults.flatAdd(vouchForLatexString(latex,False))
            checkboxManager = env.getCheckboxManager()
            checkboxManager.recordCheckMarks(env, astloc, leadp, "demerit", demerits)

        text = _("Consider yourself in overtime. In overtime there is no limit to how many leads you may visit, and time does not advance past **{}** (ignore any instructions to do so).\n").format(endTimeStr)
        latex += renderer.convertMarkdownToLatexDontVouch(text, False, False)

        # wrap it and add symbol
        boxOptions = {
            "box": "default",
            #"symbol": "checkbox",
            #"textColor": "red",
            "isTextSafe": True,
        }
        latex = wrapInLatexBox(boxOptions, latex)
        # add instructions
        results.flatAdd(vouchForLatexString(latex, False))


    # end stuff
    text = _("When you are ready to conclude the case and answer questions, proceed to ")
    results.flatAdd(text)

    # make DEFERRED link to entry lead
    leadId = goLead if (goLead is not None) else "Conclusion"
    style = "full"
    result = CbDeferredBlockRefLead(astloc, entryp, leadp, leadId, style)
    results.flatAdd(result)
    results.flatAdd(".\n")

    return results
#---------------------------------------------------------------------------








#---------------------------------------------------------------------------
def funcInstructionsPostQuestionsResume(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    dayNumber = args["day"].getWrapped()
    demerits = args["demerits"].getWrapped()
    tagId = args["tag"].getWrapped()
    halve = args["halve"].getWrapped()

    # get day object
    dayManager = env.getDayManager()
    flagAllowTempCalculatedDay = False
    day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
    if (day is None):
        raise makeJriException("Unknown 'dayNumber' ({}) specified as argument to function {}; days must be defined in setup using $configureDay(...) but day {} has not been defined.".format(dayNumber, funcName, dayNumber), astloc)
    dayDate = day.getDate()
    dayStartTime = day.getStartTime()
    dayEndTime = day.getEndTime()
    endTimeStr = convertHoursToNiceHourString(dayEndTime)
    dayDateNice = jrfuncs.niceDayDateStr(dayDate, False, False)
    dayDateShort = jrfuncs.shortDayDateStr(dayDate, False)

    # tag
    if (tagId is not None):
        tag = env.findTagOrConcept(tagId, True)
    else:
        tag = None

    # assemble result
    results = JrAstResultList()
    renderer = env.getRenderer()
    # in report mode we show the real tag label
    reportMode = env.getReportMode()

    # wrap it and add symbol
    useBox = True
    boxOptions = {
        "box": "default",
        "symbol": "warning",
        #"textColor": "red",
        "isTextSafe": True,
        "symbolColor": "red",
    }
    if useBox:
        addBoxToResultsIfAppropriateStart(boxOptions, results)

    # build output
    text = _("*After* you finish answering the questions above, you may, for the very last time, resume searching for new leads in an attempt to improve your answers.\n")
    results.flatAdd(text)
    results.flatAdd("~\n")


    if (demerits>0):
        # after, tell them to mark demerits
        results.flatAdd("\n")
        upto = False
        whyText = _("if you choose resume visiting leads at this point")
        whyLatex = renderer.convertMarkdownToLatexDontVouch(whyText, False, False)
        markLatex = buildLatexMarkCheckboxSentence("demerit", demerits, True, True, False, "red", whyLatex, upto)
        results.flatAdd(vouchForLatexString(markLatex, False)+"\n")
        checkboxManager = env.getCheckboxManager()
        checkboxManager.recordCheckMarks(env, astloc, leadp, "demerit", demerits)
        results.flatAdd("\n")
        results.flatAdd("~\n")
    if (tag is not None):
        # tell them they should mark tag if they skip
        tagActionKeyword = "circle"
        results.flatAdd("\n")

        textColor = "red"
        if (textColor is not None):
            results.flatAdd(vouchForLatexString(wrapLatexInColorStart(textColor), True))
        whyText = _("If you you choose resume visiting leads at this point, ")
        results.flatAdd(whyText)
        addGainTagTextLineToResults(tag, tagActionKeyword, results, reportMode, astloc, entryp, leadp, False, None)
        if (textColor is not None):
            results.flatAdd(vouchForLatexString(wrapLatexInColorEnd(), True))
        #
        tag.recordGain(env, tagActionKeyword, astloc, leadp)
        results.flatAdd("\n")
        results.flatAdd("~\n")

    text = _("Then consider yourself on **overtime** at **{}** on day **{}** (**{}**).").format(endTimeStr, dayNumber, dayDateShort) + "\n"
    results.flatAdd(text)
    results.flatAdd("~\n")
    text = _("Afterward, return here to *revise* any of your answers above")
   #
    if (halve):
        text += _(", scoring the **average** score of your original and revised answer.")
    results.flatAdd(text)

    if useBox:
        addBoxToResultsIfAppropriateEnd(boxOptions, results)

    return results

#---------------------------------------------------------------------------











#---------------------------------------------------------------------------
def funcInstructionsIrps(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    start = args["start"].getWrapped()
    gain = args["gain"].getWrapped()
    use = args["use"].getWrapped()
    max = args["max"].getWrapped()
    lastUse = args["lastUse"].getWrapped()
    when = args["when"].getWrapped()

    # assemble result
    results = JrAstResultList()


    # text
    text = ""
    irpStringBase = "Investigative Resource Point{} (IRP{})"
    if (start is not None):
        optionalS = "s" if (start>1) else ""
        irpString = irpStringBase.format(optionalS, optionalS)
        text = _("Record that you are starting out the case with **{}** {}.").format(start, irpString)
        text += " " + _("You may receive additional IRPs during the course of your investigation, and any unspent IRP will positively impact your end game score and reputation.")
    elif (gain is not None):
        optionalS = "s" if (gain>1) else ""
        irpString = irpStringBase.format(optionalS, optionalS)
        text += _("Record that you have gained **{}** additional {}.").format(gain, irpString)
    if (use) or (lastUse):
        if (max is not None):
            maxAmountExtra = _("a maximum of {} ").format(max)
            maxAmountExtras = "s" if (max>1) else ""
        else:
            maxAmountExtra = ""
            maxAmountExtras = ""
        if (text!=""):
            text += "\n~\n"
        if (lastUse):
            if maxAmountExtra!="":
                maxAmountExtraFinal = "(" + maxAmountExtra.strip() +") "
            else:
                maxAmountExtraFinal = ""
            text += _("This is your **last** opportunity to spend IRPs {}to schedule one or more of the following actions.").format(maxAmountExtraFinal)
        else:
            text += _("You may, if you wish, spend {}IRP{} now to schedule one or more of the following actions.").format(maxAmountExtra, maxAmountExtras)

    # when
    [whenText1, whenText2] = irpWhenText(when)
    if (whenText1 is not None):
        if (text!=""):
            text += " "
        text += _("Record chosen leads in your schedule as events that trigger **{}**, and read those leads {}.").format(whenText1, whenText2)
    else:
        #text += _("Schedule events as shown for each choice.")
        pass
     
    if (start is None):
        if (text!=""):
            text += " "
        text += _("Remember that at the end of your case any unspent IRP will positively impact your end game score and reputation.")


    # box
    boxOptions = {
        "box": "default",
        "isTextSafe": True,
        "symbol": "irp",
    }

    latex = wrapInLatexBoxJustStart(boxOptions)
    results.flatAdd(vouchForLatexString(latex, False))
    results.flatAdd(text)
    latex = wrapInLatexBoxJustEnd(boxOptions)
    results.flatAdd(vouchForLatexString(latex, False))

    return results
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def funcInstructionsScheduledEvent(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # for markdown conversion
    renderer = env.getRenderer()

    # assemble result
    results = JrAstResultList()

    text = _("You should only read this entry **when a scheduled event has triggered**.")
    latex = renderer.convertMarkdownToLatexDontVouch(text, False, False)

    boxOptions = {
        "box": "default",
        "isTextSafe": "True",
        "symbol": "warning",
        "textColor": "red"
    }
    latex = wrapInLatexBox(boxOptions, latex)

    results.flatAdd(vouchForLatexString(latex, False))

    return results
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcScheduleIrp(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    leadid = args["lead"].getWrapped()
    cost = args["cost"].getWrapped()
    when = args["when"].getWrapped()

    # assemble result
    results = JrAstResultList()

    results.flatAdd("[ ")
    #
    # what
    if (when != 0):
        text = _("Schedule")
    else:
        text = _("Visit")
    results.flatAdd(text + " ")
    #
    # make DEFERRED link to entry lead
    style = "default" # "default", "full", "nolabel", "plainid", "page", "pageparen", "pagenum"
    result = CbDeferredBlockRefLead(astloc, entryp, leadp, leadid, style)
    results.flatAdd(result)
    #
    # when
    [whenText1, whenText2] = irpWhenText(when)
    if (whenText1 is not None):
        results.flatAdd(" " + whenText1)

    # cost
    if (cost>0):
        text = _("for {} IRP").format(cost)
    else:
        text = _("at no IRP cost").format(cost)
    results.flatAdd(" " + text)

    results.flatAdd(" ]")


    # mindmapper
    mindMapTypeStr = "irp"
    mindMapper = env.getMindManager()
    mindMapper.addLinkBetweenNodes(env, mindMapTypeStr, None, leadp, leadid)

    return results
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def funcEvent(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    leadid = args["lead"].getWrapped()
    dayNumber = args["day"].getWrapped()
    time = args["time"].getWrapped()
    when = args["when"].getWrapped()
    mandatory = args["mandatory"].getWrapped()
    label = args["label"].getWrapped()
    duration = args["duration"].getWrapped()

    # special evening type event has its own defaults
    if (when=="evening"):
        if (mandatory is None):
            mandatory = True
        if (duration is None):
            duration = 0

    # get day object
    if (dayNumber is not None):
        dayManager = env.getDayManager()
        flagAllowTempCalculatedDay = False
        day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
        if (day is None):
            raise makeJriException("Unknown 'dayNumber' ({}) specified as argument to function {}; days must be defined in setup using $configureDay(...) but day {} has not been defined.".format(dayNumber, funcName, dayNumber), astloc)
        dayDate = day.getDate()
        if (dayDate is None):
            raise makeJriException("Day '{} has no assigned date ({}) specified as argument to function {}; days must be defined in setup using $configureDay(...) but day {} has not been defined.".format(dayNumber, funcName, dayNumber), astloc)
        
        dayDateShort = jrfuncs.shortDayDateStr(dayDate, False)
        dayDateLong = jrfuncs.niceDayDateStr(dayDate, True, True)


    # for markdown conversion
    renderer = env.getRenderer()
    mindMapper = env.getMindManager()
    mLabel = "event"
    
    # assemble result
    results = JrAstResultList()

    if (len(targets)>0):
        # this event uses an inline lead

        # first create a new inline lead that we will reference
        # ATTN: this has lots of redundant code with funcInline; merge the two eventually

        # calc label for inline lead
        inlineLinkArg = "Evening Event for day {}".format(dayNumber)
        [inlineLeadLabel, inlineMindMapLabel] = calcInlineLeadLabel(entryp, leadp, inlineLinkArg)
        # create lead early, so we can pass it into the contents as they run
        inlineLead = renderer.addLeadInline(inlineLeadLabel, leadp, astloc)

        # mindmap

        inlineLead.setMindMapLabel(inlineMindMapLabel)
        inlineLead.setMStyle("inline")

        if (duration is not None):
            inlineLead.setTime(duration)

        # try to break it into its own column because its long?
        inlineLead.setLeadBreak("column")

        # generate contents of the new INLINE lead that will get its own entry
        inlineResults = JrAstResultList()

        # now contents
        for target in targets:
            targetRetv = target.renderRun(rmode, env, entryp, inlineLead)
            inlineResults.flatAdd(targetRetv)

        # set contents of inline lead
        inlineLead.setBlockList(inlineResults)
        leadid = inlineLead.getAutoId()

        # mindmapper
        mlinkType = "eventInline"

    else:
        # leadid passed to us
        if (leadid is None):
            raise makeJriException("You must provide a lead id or an inline target.", astloc)
        # mindmapper
        mlinkType = "event"

    # mindmap
    mindMapper.addLinkBetweenNodes(env, mlinkType, mLabel, leadp, leadid)


    # box start
    boxOptions = {
        "box": "default",
        "symbol": "markerEvent",
        "symbolColor": "red"
    }
    addBoxToResultsIfAppropriateStart(boxOptions, results)

    if (mandatory):
        eventTypeStr=_("**mandatory** event")
    else:
        eventTypeStr=_("(*optional*) event")
    #
    text = _("Record the following {} in your schedule:").format(eventTypeStr) + "\n"
    results.flatAdd(text)
    if (label is not None):
        text = "* " + _("**What**: ") + label + "\n"
        results.flatAdd(text) 

    if (when=="evening"):
        # special when
        dayEndTime = day.getEndTime()
        endTimeStr = convertHoursToNiceHourString(dayEndTime)
        #
        text = "* " + _("**When**: ") + _("Today, day #**{}** ({}).").format(dayNumber, dayDateLong) + "\n"
        results.flatAdd(text)
        text = "* " + _("**Time**: ") + "{}".format(endTimeStr) + "\n"
        results.flatAdd(text)
    else:
        if (dayNumber is not None):
            if (time is None):
                raise makeJriException("You must provide a when string or a day number and time.", astloc)
            #
            text = "* " + _("**When**: ") + _("Day #**{}** ({})").format(dayNumber, dayDateLong) + "\n"
            results.flatAdd(text)
            text = "* " + _("**Time**: ") + "{}".format(time) + "\n"
            results.flatAdd(text)
        else:
            if (when is None):
                raise makeJriException("You must provide a when string or a day number and time.", astloc)
            text = "* " + _("**When**: ") + "{}".format(when) + "\n"
            results.flatAdd(text) 
            if (time is not None):
                text = "* " + _("**Time**: ") + "{}".format(time) + "\n"
                results.flatAdd(text)
    #
    text = "* " + _("**Where**: ")
    results.flatAdd(text)

    # make DEFERRED link to entry lead
    style = "default" # "default", "full", "nolabel", "plainid", "page", "pageparen", "pagenum"
    result = CbDeferredBlockRefLead(astloc, entryp, leadp, leadid, style)
    results.flatAdd(result)
    results.flatAddBlankLine()

    #
    mandatoryYesNo = _("YES") if (mandatory) else _("No")
    text = "* " + _("**Mandatory**: {}.").format(mandatoryYesNo) + "\n"
    results.flatAdd(text)
    results.flatAddBlankLine()
    if (mandatory):
        text = _("When you reach this time (or finish an action that causes you to surpass it) you are **required** to go to the specified lead above, which will instruct you on how to conclude your day.") + "\n"
    else:
        text = _("Note that this is **not** a mandatory event, so you are **not** required to visit this lead.") + "\n"
    results.flatAdd(text)

    # end box
    addBoxToResultsIfAppropriateEnd(boxOptions, results)

    return results
#---------------------------------------------------------------------------












# ---------------------------------------------------------------------------
def funcReferDb(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Refer to another lead
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    id = args["id"].getWrapped()
    style = args["style"].getWrapped()
    #
    # assemble result
    results = JrAstResultList()

    renderer = env.getRenderer()
    hlApi = renderer.getHlApi()

    # lookup the row by its "id" which may be a dName, a lead #, or a flexible string
    # parse it into a LABEL and an ID
    [textOut, addCount] = hlApi.flexiblyAddLeadNumbersToText(id, "markdownCb")
    results.flatAdd(textOut)

    return results
# ---------------------------------------------------------------------------











# ---------------------------------------------------------------------------
# ATTN: THIS CURRENTLY HAS NO USE CASE
def funcFormatAfterImage(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    # Refer to another lead
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # assemble result
    results = JrAstResultList()

    #latex = r"\hspace{1em}\parbox[b][][t]{\dimexpr\linewidth-\wd\myfigbox-1em}{"
    #results.flatAdd(vouchForLatexString(latex, False))

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    #latex = "}"
    #results.flatAdd(vouchForLatexString(latex, False))

    latex = "\n" + r"\par\hfill\null" + "\n"
    results.flatAdd(vouchForLatexString(latex, False))

    return results
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
def funcDefineQuestion(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    id = args["id"].getWrapped()
    summary = args["summary"].getWrapped()
    points = args["points"].getWrapped()
    typeStr = args["type"].getWrapped()
    lines = args["lines"].getWrapped()
    sizeVal = args["size"].getWrapped()
    choices = args["choices"].getWrapped()

    # assemble result, contents of question
    results = JrAstResultList()
    tresults = JrAstResultList()

    # contents of targets
    addTargetsToResults(tresults, targets, rmode, env, entryp, leadp, False, False)

    # build question
    questionManager = env.getQuestionManager()
    question = questionManager.defineQuestion(id, summary, points, typeStr, lines, sizeVal, choices, tresults)

    # now present question
    question.addToResultsAsQuestion(env, results)

    return results




def funcQuestionAnswer(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    # args
    id = args["id"].getWrapped()
    summary = args["summary"].getWrapped()

    #
    questionManager = env.getQuestionManager()
    question = questionManager.findQuestionById(id)
    #
    # assemble result
    results = JrAstResultList()

    # present question repeat before telling player answer
    question.addToResultsAsAnswer(env, results, summary)

    # contents of target, which is the answer
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, False)

    return results
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
def funcQuestionTotal(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    renderer = env.getRenderer()

    # sum max score
    questionManager = env.getQuestionManager()
    totalScore = questionManager.calcTotalPoints()

    # assemble result
    results = JrAstResultList()
    #

    # left half of total score
    text = "**Total score from questions** (max. {}): ".format(totalScore)
    latexPartA = renderer.convertMarkdownToLatexDontVouch(text, False, False)

    # line for user to put total
    safeWidthStr = "0.5in"
    pt = 1
    latexPartB = "\\cbFormLine{" + safeWidthStr + "}" + "{" + str(pt) + "pt}"


    latex = r"\jrledline{" + latexPartA + "}{" + latexPartB + "}\n"
    results.flatAdd(vouchForLatexString(latex, True))

    return results
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
def funcPointsLine(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    renderer = env.getRenderer()

    text = args["text"].getWrapped()

    # assemble result
    results = JrAstResultList()

    # left half of total score
    latexPartA = renderer.convertMarkdownToLatexDontVouch(text, False, False)

    # line for user to put total
    safeWidthStr = "0.5in"
    pt = 1
    latexPartB = "\\cbFormLine{" + safeWidthStr + "}" + "{" + str(pt) + "pt}"

    # combine
    latex = r"\jrledline{" + latexPartA + "}{" + latexPartB + "}\n"

    results.flatAdd(vouchForLatexString(latex, True))

    return results


def funcLederLine(rmode, env, entryp, leadp, astloc, args, customData, funcName, targets):
    exceptionIfNotRenderMode(rmode, funcName, env, astloc)

    renderer = env.getRenderer()
    
    leftText = args["leftText"].getWrapped()
    rightText = args["rightText"].getWrapped()

    # assemble result
    results = JrAstResultList()

    # left half of total score
    latexPartA = renderer.convertMarkdownToLatexDontVouch(leftText, False, False)
    latexPartB = renderer.convertMarkdownToLatexDontVouch(rightText, False, False)

    # combine
    latex = r"\jrledline{" + latexPartA + "}{" + latexPartB + "}\n"

    results.flatAdd(vouchForLatexString(latex, True))

    return results
# ---------------------------------------------------------------------------

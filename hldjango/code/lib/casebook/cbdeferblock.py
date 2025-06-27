# this is an "advanced" functionality; there are times when functions being run/rendered need to make use of information that is not available on a "first pass"
# the solution in casebook is to create a result "object" that is not text, as normal, but rather a deferred renderable object that can be resolved AFTER all leads have been generated
# this could be needed for example if we want to go from one lead to another

from .jrastfuncs import vouchForLatexString, convertEscapeUnsafePlainTextToLatex, convertEscapeVouchedOrUnsafePlainTextToLatex, convertRenderBlockToSimpleText
from .jriexception import *
from lib.jr import jrfuncs



# defines
CbDef_SkipNextNewline = "__CbDef_SkipNextNewline__"






class CbDeferredBlock:
    def __init__(self, astloc, entryp, leadp):
        self.astloc = astloc
        self.entryp = entryp
        self.leadp = leadp
        pass





class CbDeferredBlockRefLead(CbDeferredBlock):
    def __init__(self, astloc, entryp, leadp, targetLeadId, optionStyle):
        super().__init__(astloc, entryp, leadp)
        #
        self.targetLeadId = targetLeadId
        self.optionStyle = optionStyle

    def renderToLatexString(self, env, renderDoc, lead, parentSection, priorMarkdownText, nextBlock):
        # build the latex for this reference
        from .cbfuncs_core_support import makeLatexReferenceToLeadById
        latex = makeLatexReferenceToLeadById(self.astloc, self.entryp, lead, renderDoc, self.targetLeadId, self.optionStyle, True)
        return [latex, None, None]



class CbDeferredBlockCaseStats(CbDeferredBlock):
    def __init__(self, astloc, entryp, leadp):
        super().__init__(astloc, entryp, leadp)

    def renderToLatexString(self, env, renderDoc, lead, parentSection, priorMarkdownText, nextBlock):
        # build the latex for this reference
        # deferred stats line
        latex = r"\item \textbf{Stats}: "
        latex += renderDoc.calcLeadStatsString(env)
        latex += "\n"
        return [vouchForLatexString(latex, False), None, None]




class CbDeferredBlockFollowCase(CbDeferredBlock):
    def __init__(self, astloc, entryp, leadp, text, useBulletIfEmptyLine, flagShiftUp, flagShiftDown):
        super().__init__(astloc, entryp, leadp)
        self.text = text
        self.useBulletIfEmptyLine = useBulletIfEmptyLine
        self.flagShiftUp = flagShiftUp
        self.flagShiftDown = flagShiftDown

    def renderToLatexString(self, env, renderDoc, lead, parentSection, priorMarkdownText, nextBlock):
        # here we have some text, and we want to change the first letter's case depending if we are following in the middle of a sentence or starting a new one, etc.
        text = self.text
        priorTextPosStyle = jrfuncs.calcTextPositionStyle(priorMarkdownText)
        if (self.useBulletIfEmptyLine):
            optionLineStartPrefix = " * "
        else:
            optionLineStartPrefix = ""
        optionPeriodIfStandalone = False
        #
        text = jrfuncs.modifyTextToSuitTextPositionStyle(text, priorTextPosStyle, optionLineStartPrefix, optionPeriodIfStandalone, self.flagShiftUp, self.flagShiftDown)
        return [text, None, None]


class CbDeferredBlockEndLinePeriod(CbDeferredBlock):
    def __init__(self, astloc, entryp, leadp, optionAggressive):
        super().__init__(astloc, entryp, leadp)
        self.optionAggressive = optionAggressive

    def renderToLatexString(self, env, renderDoc, lead, parentSection, priorMarkdownText, nextBlock):
        # we want to add a period IFF we are followed by a newline
        nextBlockText = convertRenderBlockToSimpleText(nextBlock)
        if (nextBlockText=="") or (nextBlockText.startswith("\n")) or (nextBlockText.startswith("~")):
            text = "."
        elif (self.optionAggressive and (nextBlockText[0] not in ".;, ")):
            text = "."
        else:
            text = ""
        return [text, None, None]



class CbDeferredBlockAbsorbPreviousNewline(CbDeferredBlock):
    def __init__(self, astloc, entryp, leadp):
        super().__init__(astloc, entryp, leadp)

    def renderToLatexString(self, env, renderDoc, lead, parentSection, priorMarkdownText, nextBlock):
        # we want to add a period IFF we are followed by a newline

        # ATTN: we don't currently use this and solved it in grammar
        if (True):
            if (priorMarkdownText.endswith("\n")):
                newPriorMarkdownText = priorMarkdownText[0:len(priorMarkdownText)-1]
                return ["", newPriorMarkdownText, None]

        # do nothing
        return ["", None, None]
    


class CbDeferredBlockAbsorbFollowingNewline(CbDeferredBlock):
    def __init__(self, astloc, entryp, leadp):
        super().__init__(astloc, entryp, leadp)

    def renderToLatexString(self, env, renderDoc, lead, parentSection, priorMarkdownText, nextBlock):
        # we want to add a period IFF we are followed by a newline

        # ATTN: we don't currently use this and solved it in grammar
        if (True):
            # if next block is a plain text newline (rendered as double newline in latex, remove it)
            nextBlockText = convertRenderBlockToSimpleText(nextBlock)
            if (nextBlockText == "\n"):
                # return new block as pure newline in latex (rather than a double markdown newline)
                return ["", None, vouchForLatexString("\n", False)]

        # do nothing
        return ["", None, None]
            





class CbDeferredBlockLeadTime(CbDeferredBlock):
    def __init__(self, astloc, entryp, leadp):
        super().__init__(astloc, entryp, leadp)

    def renderToLatexString(self, env, renderDoc, lead, parentSection, priorMarkdownText, nextBlock):
        #inlineSection = renderDoc.getInlineSection()
        #timeLatex = renderDoc.calculateItemTimeLatexBoxStyle(env, self.leadp, inlineSection)
        timeLatex = renderDoc.calculateItemTimeLatexBoxStyle(env, self.leadp, parentSection)
        if (timeLatex is not None):
            # return the time string
            return [vouchForLatexString(timeLatex, False), None, None]

        # do nothing
        return ["", None, None]
    


class CbDeferredBlockLeadHeader(CbDeferredBlock):
    def __init__(self, astloc, entryp, leadp):
        super().__init__(astloc, entryp, leadp)

    def renderToLatexString(self, env, renderDoc, lead, parentSection, priorMarkdownText, nextBlock):
        # just the deferred header text
        latex = renderDoc.calcHeaderLatexForLead(env, lead, parentSection, True)
        return [vouchForLatexString(latex, False), None, None]




class CbDeferredBlockPotentialEndLeadTime(CbDeferredBlock):
    def __init__(self, astloc, entryp, leadp):
        super().__init__(astloc, entryp, leadp)

    def renderToLatexString(self, env, renderDoc, lead, parentSection, priorMarkdownText, nextBlock):
        itemTimePos = lead.getTimePos()
        optionTimeStyle = renderDoc.getOptionTimeStyle()
        if (itemTimePos=="end") or (optionTimeStyle!="header") and ((itemTimePos is None) or (itemTimePos=="")):
            timeLatex = renderDoc.calculateItemTimeLatexBoxStyle(env, lead, parentSection)
            if (timeLatex is not None):
                # return the time string
                return [vouchForLatexString(timeLatex, False), None, None]

        # do nothing
        return ["", None, None]






# jr ast helpers
from .jrastfuncs import getUnsafeDictValueAsString, makeLatexLinkToRid, vouchForLatexString, DefContdStr, DefInlineLeadPlaceHolder, convertEscapeUnsafePlainTextToLatex, convertEscapeUnsafePlainTextToLatexMorePermissive
from .jriexception import *
from .jrastutilclasses import JrINote
from .jrastvals import AstValString, AstValNull
from .jrast import JrAstResultList
from .jrast import ResultAtomLatex, ResultAtomMarkdownString, ResultAtomPlainString, ResultAtomNote
from .jrastfuncs import isTextLatexVouched

from .cbtask import DefRmodeRun, DefRmodeRender

from .cbdeferblock import CbDeferredBlockRefLead, CbDeferredBlockCaseStats, CbDeferredBlockFollowCase, CbDeferredBlockEndLinePeriod, CbDeferredBlockAbsorbFollowingNewline, CbDeferredBlockAbsorbPreviousNewline, CbDeferredBlockLeadTime, CbDeferredBlockLeadHeader

from .casebookDefines import *

# translation
from .cblocale import _

from lib.jreffects.jreffect import JrImageEffects


# python modules
import re
import random
import string



# other functions use this; we map font size keyword to a latex font size command, and this also defines numerical scale
latexFontSizeMap = {
    "tiny": "\\tiny",
    "script": "\\scriptsize",
    "footnote": "\\footnotesize",
    "small": "\\small",
    "normal": "\\normalsize",
    "large": "\\large",
    "Large": "\\Large",
    "LARGE": "\\LARGE",
    "huge": "\\huge",
    "Huge": "\\Huge",
    # custom ones here
}


DefHelpulIfText = _("If this information is helpful")
DefHintIfText = _("If this hadn't already occurred to you")

JrDefUserFuncTargetsEnvVarId = "_targets"






def calcInlineLeadLabel(entryp, leadp, inlineLinkArg):
    # calculate the label for an inline lead
    # we use a placeholder here (DefInlineLeadPlaceHolder) which will be replaced at render time with latex that will link to the parent lead we are inlined from
    inlineMindMapLabel = None

    if (leadp is None):
        inlineLabel = entryp.calcDisplayTitle()
    else:
        inlineLabel = leadp.calcDisplayTitlePreferSubheading()

    # remove any ADDITIONAL (see previous lead text if its a recursive inline)
    inlineLabel = inlineLabel.replace(DefInlineLeadPlaceHolder + " " + DefContdStr, "")
    inlineLabel = inlineLabel.replace(DefInlineLeadPlaceHolder, "")
    inlineLabel = inlineLabel.strip()

    # add inlineLinkArg
    if (inlineLinkArg!=""):
        if (inlineLabel == ""):
            inlineLabel = DefInlineLeadPlaceHolder + " " + inlineLinkArg
            inlineMindMapLabel = inlineLinkArg + " (inline)"
        else:
            inlineLabel += " " + DefInlineLeadPlaceHolder + " - " + inlineLinkArg
            inlineMindMapLabel = inlineLinkArg + " (inline)"
    else:
        inlineLabel += " " + DefInlineLeadPlaceHolder + " " + DefContdStr
        inlineMindMapLabel = "inline"

    return [inlineLabel, inlineMindMapLabel]




def parseTagListArg(idStr, idStrDefault, env, astloc, flagSort):
    # get comma separated list
    if (idStr==""):
        idStr = idStrDefault
    ids = idStr.split(",")

    # build list of tags, and keep track of every lead where you gain a tag
    tagManager = env.getTagManager()
    tagList = []
    for id in ids:
        id = id.strip()
        if (id==""):
            continue
        tag = tagManager.findTagById(id)
        if (tag is None):
            raise makeJriException("Unknown tag (\"{}\")".format(id), astloc)
        # add it to list of tags
        tagList.append(tag)

    if (flagSort):
        tagList = tagManager.sortByTypeAndObfuscatedLabel(tagList, env, False)

    return tagList
#---------------------------------------------------------------------------



















#---------------------------------------------------------------------------
def buildLatexMarkCheckboxSentence(word, count, flagPeriod, flagAddCheckbox, optionHelpful, textColor, whyLatex, upto):

    if (upto):
        uptoLatex = "up to "
    else:
        uptoLatex = ""

    countLatex = wrapTextInBold(str(count))
    if (optionHelpful==True):
        latex = DefHelpulIfText + ", " + _("mark")
    elif (optionHelpful=="hint"):
        latex = DefHintIfText + ", " + _("mark")
    else:
        latex = _("Tick")
    latex += " {}{} {} ".format(uptoLatex, countLatex, word) + _("box{} in your case log").format(jrfuncs.plurals(count,"es"))
    if (whyLatex is not None):
        if (whyLatex[0] not in string.punctuation):
            latex += " "
        latex += whyLatex
    #
    if (flagPeriod):
        latex += "."
    if (flagAddCheckbox):
        latex = generateLatexForSymbol("checkbox", None, None) + latex
    if (textColor is not None):
        latex = wrapLatexInColor(latex, textColor)
    return latex
#---------------------------------------------------------------------------





















# -------------------------------------------
def generateLatexForSymbol(symbolName, color, size):
    symbolDictLatex = {
        "checkbox": r"{\Large \faCheckSquare[regular]}",
        "ucheckbox": r"{\faSquare[regular]}",
        "clock": r"\raisebox{-4.1pt}\VarTaschenuhr",
        "document": r"{\Large \faCameraRetro}",
        "exclamation": r"{\Large \faExclamationCircle}",
        "warning": r"{\Large \faExclamationCircle}",
        "stop": r"{\Huge \faExclamationTriangle}",
        "hand": r"{\Large \faHandPointRight[regular]}",
        "choice": r"{\Large \faBalanceScale}",
        "culture": r"{\Large \faTheaterMasks}",
        "radio": r"{\Large \faVolumeUp}",
        "news": r"{\Large \faNewspaper[regular] }",
        "markerTag": r"\raisebox{-0.75pt}{\Large \faTag}",
        "markerDoc": r"\raisebox{-2.0pt}{\Large \faCameraRetro}",
        "markerGeneric" : r"{\Large \faTags}",
        "markerEvent": r"{\Large \faCalendar*[regular]}",
        "hand": r"\raisebox{-2.0pt}{\Large \faHandPointRight[regular]}",
        #"calendar": r"{\faCalendar}",
        "calendar": r"{\faCalendar*[regular]}",
        "report": r"{\faFlask}",
        "track": r"{\faCalculator}",
        "irpBAD": r"{\faMoney}",
        "irp": r"{\faMoneyBill[solid]}",
    }
    symbolDictDefaultColors = {
        "exclamation": "red",
        "stop": "red",
        "choice": "red",
        "bonus": "red",
    }

    # symbol
    if (symbolName in symbolDictLatex):
        latex = symbolDictLatex[symbolName]
    else:
        raise Exception("Runtime Error: Symbol '{}' not known; should be from: {}.".format(symbolName, symbolDictLatex.keys()))

    # spacing after
    latex += r"\mySpaceAfterSymbol "

    # color
    color = jrfuncs.overrideIfNone(color, symbolName, symbolDictDefaultColors)
    if (color is not None):
        latex = wrapLatexInColor(latex, color)

    # size
    # ATTN: TODO

    return latex
# -------------------------------------------





# -------------------------------------------
def generateLatexForDivider(env, id, astloc):
    if (id is None):
        id = "default"
    renderer = env.getRenderer()
    latex = renderer.generateLatexForDivider(id, astloc)
    return latex



def generateLatexTextColor(textColor):
    latex = r"\color{" + textColor + "}"
    return latex

def wrapLatexInColor(latex, textColor):
    return r"{" + generateLatexTextColor(textColor) + latex + r"}"

def wrapLatexInColorStart(textColor):
    return r"{" + generateLatexTextColor(textColor)

def wrapLatexInColorEnd():
    return r"}"


def wrapTextInBold(text):
    return r"\textbf{" + text + r"}"





def generateLatexBreak(breakType):
    latexDict = {
        "column": "\n\\newpage\n",
        #"column": "\n\\columnbreak\n",
        "page": "\n\\clearpage\n",
        "doublePage": "\n\\cleardoublepage\n"
    }

    if (breakType not in latexDict):
        raise makeJriException("Runtime Error: $break({}) should be from {}.", breakType, latexDict.keys())
    
    return latexDict[breakType]

def makeLatexSafeFilePath(fpath):
    fpath = fpath.replace("\\","/")
    fpath = convertEscapeUnsafePlainTextToLatexMorePermissive(fpath)
    fpath = fpath.replace("\\_","_")
    return fpath


def wrapLatexInBulletList(latex):
    latex = ""
    return latex





def generateImageEmbedLatex(env, imageFullPath, widthStr, heightStr, borderWidth, padding, align, valign, caption, captionPos, captionSize, sideRule, optionWrapText):
    # fix path
    imageFullPath = makeLatexSafeFilePath(imageFullPath)
    #
    extra = ""
    if (heightStr==""):
        heightStr = None
    if (widthStr==""):
        widthStr = None
    #
    safeHeightStr = None
    safeWidthStr = None

    # new
    safeHeightStr = convertStringToSafeLatexSize(heightStr, r"\textheight", r"0.95\dimexpr\textheight-\pagetotal\relax", r"0.80\textheight", 1.0)
    safeWidthStr = convertStringToSafeLatexSize(widthStr, r"\columnwidth", r"\columnwidth", r"0.95\columnwidth", 1.0)
    extra += "width={}, height={}".format(safeWidthStr, safeHeightStr)
    #
    if (extra != ""):
        extra += ",keepaspectratio"

    # new to fix placing in tables
    if (valign is not None) and (valign!=""):
        if (extra !=""):
            extra +=","
        extra += "valign=" + valign

    if (extra != ""):
        extra = "[" + extra + "]"
    #
    latex = "\\includegraphics{}{{{}}} ".format(extra, imageFullPath)

    # side rule lines?
    bypassTcbox = False
    if (sideRule):
        latex = latexSideRulesAround(latex, safeWidthStr)
        bypassTcbox = True

    #
    flagImageHasMargin = False
    if (bypassTcbox):
        # cannot wrap in tcbox
        # what does this flag do?
        #flagImageHasMargin = True
        pass
    elif (borderWidth>0):
        # wrap in box
        # note that this BREAKS nice table cell alignment with images so it must be turned off when embedding in table
        boxOptions = {
            "box": "imageBorder",
            "isTextSafe": True,
            # others
            "borderWidth": borderWidth,
            "padding": padding
        }
        latex = wrapInLatexBox(boxOptions, latex)
        flagImageHasMargin = True
    else:
        # we are forced to wrap in tcbox otherwise spacing margins get messed up
        latex = wrapInSimpleLatexTcBox(latex)
        flagImageHasMargin = True

    # ATTN:TODO support align right, etc.
    # ATTN: NEW WE DO NOT WANT TO BEGIN CENTER THE IMAGE IFF WE ARE GOING TO CENTER IT IN CAPTION; as it CAN sometimes lead to extra spacing betweeen image and caption
    if (caption is None) and ((align is None) or (align=="center")) and (not bypassTcbox):
        latex = "\\begin{center}" + latex + "\\end{center}"

    if (True):
        flagTightCaption = False
        flagWrapInMiniPage = not optionWrapText
        flagUnboxable = False
        latex = wrapInFigure(env, latex, caption, align, captionPos, captionSize, flagTightCaption, flagImageHasMargin, flagWrapInMiniPage, flagUnboxable, optionWrapText)

    return latex




def wrapInFigure(env, inlatex, caption, align, captionPos, captionSize, flagTightCaption, flagImageHasMargin, flagWrapInMiniPage, flagUnboxable, optionWrapText):
    if (flagUnboxable):
        if (caption is None):
            return inlatex
        return wrapInFigureCaptionNoBox(env, inlatex, caption, align, captionPos, captionSize, flagTightCaption, flagImageHasMargin)

    if (caption is not None):
        return wrapInFigureCaption(env, inlatex, caption, align, captionPos, captionSize, flagTightCaption, flagImageHasMargin, flagWrapInMiniPage, flagUnboxable, optionWrapText)
    else:
        return wrapInFigureNoCaption(env, inlatex, caption, align, captionPos, captionSize, flagTightCaption, flagImageHasMargin, flagWrapInMiniPage, flagUnboxable, optionWrapText)



def wrapInFigureCaption(env, inlatex, caption, align, captionPos, captionSize, flagTightCaption, flagImageHasMargin, flagWrapInMiniPage, flagUnboxable, optionWrapText):
    renderer = env.getRenderer()

    captionText = renderer.convertMarkdownToLatexDontVouch(caption, False, True)
    if (captionSize is not None) and (captionSize!=""):
        sizeLatex = parseFontSizeStringToLatexCommand(captionSize, True, None)
        #sizeLatex = calcLatexSizeKeywordFromBaseAndMod(captionSize, None, env, None)
        captionText = sizeLatex + " " + captionText

    if (align=="left"):
        flagWrapInFigure = False
        flagWrapInMiniPage = True
        captionMod = "Wrap"
    else:
        flagWrapInFigure = True
        flagWrapInMiniPage = False
        captionMod = "NoWrap"

    latex = ""

    latex += r"\noindent" + "\n"

    if (optionWrapText):
        latex += generateLatexBeginWrapFigureText(optionWrapText, "{l}")
        flagWrapInMiniPage = False

    if (flagWrapInFigure):
        latex += r"\vspace*{-1.5em}" + "\n"
        latex += "\\begin{figure}[H]\n"

    if (flagTightCaption):
        latex += "\\captionsetup{skip=0pt}\n"

    if (align is None) or (align=="center"):
        latex += "\\centering\n"
    #

    # save in custom box
    latex += "% Save the image box (with tcbox styling)\n"
    latex += r"\sbox{\myfigbox}{%" + "\n"

    # contents
    #latex += inlatex
    latex += inlatex.strip()

    # end custom box
    latex += r"}" + "\n"

    if (flagWrapInMiniPage):
        latex += r"\begin{minipage}{\wd\myfigbox}" + "\n"

    if (captionPos=="top"):
        # caption before image
        latex += "\n" + r"\captionCbFigBoxTop" + captionMod + "{" + captionText + "}" + "\n"
    else:
        latex += "\n" + r"\captionCbFigBoxBottomAbove" + captionMod + "\n"

    # now SHOW image saved in box
    latex += r"\usebox{\myfigbox}" + "\n"

    if (captionPos!="top"):
        # caption after image
        latex += "\n" + r"\captionCbFigBoxBottom" + captionMod + "{" + captionText + "}" + "\n"
    else:
        latex += "\n" + r"\captionCbFigBoxTopBelow" + captionMod + "\n"

    if (flagWrapInMiniPage):
        latex += r"\end{minipage}" + "\n"

    #if (captionPos=="top") and (flagWrapInFigure):
    #    latex += r"\vspace*{-1.5em}" + "\n"

    if (flagWrapInFigure):
        latex += "\\end{figure}\n"

    if (optionWrapText):
        latex += r"\end{wrapfigure}" + "\n"

    return latex





def wrapInFigureNoCaption(env, inlatex, caption, align, captionPos, captionSize, flagTightCaption, flagImageHasMargin, flagWrapInMiniPage, flagUnboxable, optionWrapText):

    # if its not left align then its fine as is, it will center without caption no problem
    if (align!="left"):
        return inlatex

    # but if we left align we want it to allow multiple images on a single line
    flagWrapInMiniPage = True

    latex = ""
    latex += r"\noindent" + "\n"

    # save in custom box
    latex += "% Save the image box (with tcbox styling)\n"
    latex += r"\sbox{\myfigbox}{%" + "\n"

    # contents
    latex += inlatex.strip()

    # end custom box
    latex += r"}" + "\n"

    if (optionWrapText):
        latex += generateLatexBeginWrapFigureText(optionWrapText, "{l}")
        flagWrapInMiniPage = False

    if (flagWrapInMiniPage):
        latex += r"\begin{minipage}{\wd\myfigbox}" + "\n"

    # now SHOW image saved in box
    latex += r"\usebox{\myfigbox}" + "\n"

    if (flagWrapInMiniPage):
        latex += r"\end{minipage}" + "\n"

    if (optionWrapText):
        latex += r"\end{wrapfigure}" + "\n"

    return latex



def generateLatexBeginWrapFigureText(optionWrapText, align):
    if (not optionWrapText):
        return ""
    latex = ""
    if ((optionWrapText=="auto") or (optionWrapText is True)):
        latex += r"\begin{wrapfigure}" + align + r"{\wd\myfigbox}" + "\n"
    elif (optionWrapText=="calc"):
        # auto calculate lines
        latex += r"\imageheightsp=\ht\myfigbox" + "\n" + r"\lineheightsp=\baselineskip" + "\n"
        latex += r"% round up: (image + line–1) / line" + "\n" + r"\wraplines=\numexpr(\imageheightsp+\lineheightsp-1)/\lineheightsp\relax" + "\n"
        latex += r"\begin{wrapfigure}[\wraplines]" + align + r"{\wd\myfigbox}" + "\n"
    elif (jrfuncs.makeInt(optionWrapText)):
        # explicit number of lines to wrap
        flagWrapLines = int(optionWrapText)
        latex += r"\begin{wrapfigure}[" + str(flagWrapLines) + "]" + align + r"{\wd\myfigbox}" + "\n"
    else:
        raise makeJriException("Could not parse wrap text option; should be ['auto','calc',int].", None)
    return latex



def wrapInFigureCaptionNoBox(env, inlatex, caption, align, captionPos, captionSize, flagTightCaption, flagImageHasMargin):
    renderer = env.getRenderer()

    captionText = renderer.convertMarkdownToLatexDontVouch(caption, False, True)
    if (captionSize is not None) and (captionSize!=""):
        sizeLatex = parseFontSizeStringToLatexCommand(captionSize, True, None)
        #sizeLatex = calcLatexSizeKeywordFromBaseAndMod(captionSize, None, env, None)
        captionText = sizeLatex + " " + captionText

    latex = "\\begin{figure}[H]\n"

#    if (flagTightCaption):
#        latex += "\captionsetup{skip=0pt}\n"

    if (flagImageHasMargin):
        commandNameMod = "Margin"
    else:
        commandNameMod = ""

    if (align is None) or (align=="center"):
        latex += "\\centering\n"
    #
    if (captionPos=="top"):
        latex += "\\captionCbTop" + commandNameMod + "{" + captionText + "}\n"
    #
    latex += inlatex
    #
    if (captionPos!="top"):
        latex += "\\captionCbBottom" + commandNameMod + "{" + captionText + "}\n"
    else:
        latex += "\\captionCbEmptyBelow" + "\n"
    latex += "\\end{figure}\n"
    return latex








def generateImageSizeLatex(imageFullPath):
    # fix path
    imageFullPath = makeLatexSafeFilePath(imageFullPath)
    #
    extra = ""
    latex = r"\sbox0{" + "\\includegraphics{}{{{}}} ".format(extra, imageFullPath) + r"}"
    latex += r"Dimentions: \uselengthunit{in}\printlength{\wd0} x \uselengthunit{in}\printlength{\ht0}"

    return latex



def convertStringToSafeLatexSize(sizeStr, fullSizeVal, remainingSizeVal, defaultSizeVal, scaleFactor):
    #
    if (sizeStr is None) or (sizeStr==""):
        return defaultSizeVal
    if (sizeStr=="remaining"):
        return remainingSizeVal
    if (sizeStr=="full"):
        return fullSizeVal

    if (not isinstance(sizeStr,str)):
        sizeStr = str(sizeStr)

    # percentage
    pattern = r'^(-?\d+(\.\d+)?(e[-+]?\d+)?)\s*%$'
    matches = re.match(pattern, sizeStr)
    if (matches is not None):
        widthVal = float(matches.group[1]) * scaleFactor
        return str(widthVal) + fullSizeVal

    # see if its a float and divide by fullsize if so
    try:
        floatVal = float(sizeStr)
        widthVal = floatVal * scaleFactor
        return str(widthVal) + fullSizeVal
    except Exception as e:
        pass
    # if it matches like "4.2in" then pass it through
    pattern = r'^-?\d+(\.\d+)?(e[-+]?\d+)?\s*(in|cm|mm)$'
    if bool(re.match(pattern, sizeStr)):
        return convertEscapeUnsafePlainTextToLatex(sizeStr)

    # reject or just pass it through as safe value?
    if (False):
        return convertEscapeUnsafePlainTextToLatex(sizeStr)
    #
    raise Exception("Bad value for image size.")


def convertNumericWidthToFraction(width, minValue = 0.01):
    # if width <1 just return it
    # if width >1 then treat it as a percentage and divide by 100
    floatVal = float(width)

    if (float(width)>1):
        width = min(width,100)
        width = max (width, 10)
        width = width / 100

    if (width < minValue):
        width = minValue

    return width
#---------------------------------------------------------------------------






#---------------------------------------------------------------------------
def convertHoursToNiceHourString(hourNumber):
    if (hourNumber==-1):
        return "anytime"
    if (hourNumber>=12):
        retv = '{}pm'.format(hourNumber-12)
    else:
        retv = '{}am'.format(hourNumber)
    return retv
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def generateLatexForPageStyle(style, astloc):
    if (style=="empty"):
        # turn off page numbering on this page?
        latex = r"\thispagestyle{empty}"
    else:
        raise makeJriException("Unknown style areguement passed to $pageStyle({})".format(style), astloc)
    return latex
#---------------------------------------------------------------------------





#---------------------------------------------------------------------------
def generateLatexCalendar(dateStartString, dateEndString, strikeStartString, strikeEndString, circleString):
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

    return latex
#---------------------------------------------------------------------------
























# -------------------------------------------
def wrapInSimpleLatexTcBox(latex):
    # if we dont do this for images, the margins around them do weird things, especially with regard to captions
    return r"\tcbox[sharp corners, size=tight, boxrule=0pt, colback=white]{" + latex + "}\n"



def wrapInLatexBox(boxOptions, text):
    if (text==""):
        # empty text, no box
        return ""
    
    # start box
    latex = wrapInLatexBoxJustStart(boxOptions)

    # main text
    isTextSafe = jrfuncs.getDictValueOrDefault(boxOptions, "isTextSafe", False)
    if (not isTextSafe):
        latex += convertEscapeUnsafePlainTextToLatex(text)
    else:
        latex += text

    # end box
    latex += wrapInLatexBoxJustEnd(boxOptions)

    return latex



def wrapInLatexBoxJustStart(boxOptions):
    # start box code
    if (not isBoxRequested(boxOptions)):
        return ""
    textColor = jrfuncs.getDictValueOrDefault(boxOptions, "textColor", None)
    symbol = jrfuncs.getDictValueOrDefault(boxOptions, "symbol", None)
    symbolColor = jrfuncs.getDictValueOrDefault(boxOptions, "symbolColor", None)
   
    # start box
    latexBoxDict = generateLatexBoxDict(boxOptions)
    if ("startFunc" in latexBoxDict):
        latex = latexBoxDict["startFunc"](boxOptions)
    else:
        latex = latexBoxDict["start"]

    # optional color
    if (textColor is not None):
        latex += generateLatexTextColor(textColor)

    # optional symbol
    if (symbol is not None) and (symbol!=""):
        latex += generateLatexForSymbol(symbol, symbolColor, None)

    return latex


def wrapInLatexBoxJustEnd(boxOptions):
    # end box
    if (not isBoxRequested(boxOptions)):
        return ""
    
    latexBoxDict = generateLatexBoxDict(boxOptions)
    latex = ""
    if ("endFunc" in latexBoxDict):
        latex += latexBoxDict["endFunc"](boxOptions)
    else:
        latex += latexBoxDict["end"]

    return latex


def generateLatexBoxDict(boxOptions):
    box = jrfuncs.getDictValueOrDefault(boxOptions, "box", None)
    width = jrfuncs.getDictValueOrDefault(boxOptions, "width", None)
    pos = jrfuncs.getDictValueOrDefault(boxOptions, "pos", None)
    if (pos is None):
        pos = "center"

    # simple left right
    posHorz = pos
    if (pos=="topLeft"):
        posHorz = "left"
    if (pos=="topRight"):
        posHorz = "right"
    #
    # alignment (messy i know)
    alignmentDict = {
        "none": {"envStart": "", "envEnd": "", "envCont": "", "envCont2": ""},
        "center": {"envStart": r"\begin{center}", "envEnd": r"\end{center}", "envCont": r"\centering"},
        "right": {"envStart": r"\begin{flushright}", "envEnd": r"\end{flushright}", "envCont": r"\raggedleft"},
        "left": {"envStart": r"\begin{flushleft}", "envEnd": r"\end{flushleft}", "envCont": r"\raggedright"},
    }
    alignmentEnvStart = alignmentDict[posHorz]["envStart"]
    alignmentEnvEnd = alignmentDict[posHorz]["envEnd"]
    alignmentCont = alignmentDict[posHorz]["envCont"]

    #
    latexDict = {
        # hours of experimenting to get this to center correctly and not add extra vertical space, etc.
        # empty means dont do any box or spacing; but we will run this func to allow symbol, text color, etc; see "invisible" if you want the box spacing and alignment
        #"empty": {"start": r"{\center\begin{minipage}[c]{$WIDTH$}" + "\n", "end":r"\end{minipage}}", "width":1},
        "empty": {"start": r"\begin{center}\begin{minipage}[c]{$WIDTH$}" + "\n", "end":r"\end{minipage}\end{center}", "width":1},
        "default": {"start": "\n" + r"{\par" + alignmentCont + r"\lfbox[border-radius=5pt, padding=8pt, margin-top=4pt, margin-bottom=2pt]{\begin{minipage}[c]{$WIDTH$}" + "\n", "end": r"\end{minipage}}\par}" + "\n\n", "width":.95},
        "compact": {"start": "\n" + r"\vspace{-0.25em}{\par" + alignmentCont + r"\lfbox[border-radius=5pt, padding=8pt, padding-top=4pt, padding-bottom=4pt, margin-top=0pt, margin-bottom=2pt]{\begin{minipage}[c]{$WIDTH$}" + "\n", "end": r"\end{minipage}}\par}" + "\n\n", "width":.95},
        # invisible just gives us the spacing/indent 
        "invisible": {"start": "\n" + r"{\par" + alignmentCont + r"{\begin{minipage}[c]{$WIDTH$}" + "\n", "end": r"\end{minipage}}\par}" + "\n\n", "width":.95},
        "rounded": {"start": "\n" + r"{\par" + alignmentCont + r"\lfbox[border-radius=5pt, padding=8pt, margin-top=4pt, margin-bottom=2pt]{\begin{minipage}[c]{$WIDTH$}" + "\n", "end": r"\end{minipage}}\par}" + "\n\n", "width":.95},
        "shadow": {"start": r"\setlength{\fboxsep}{2em} " + alignmentEnvStart + r"\shadowbox{\begin{minipage}[c]{$WIDTH$}" + "\n", "end": r"\end{minipage}}" + alignmentEnvEnd + "\n\n", "width":.80},
        "report": {"start": "\n" + r"{\par" + alignmentCont + r"\lfbox[border-style=dotted, border-color=red, border-width=1.5pt, padding=8pt, margin-top=4pt, margin-bottom=2pt]{\begin{minipage}[c]{$WIDTH$}" + "\n", "end": r"\end{minipage}}\par}" + "\n\n", "width":.95},
        "hLines": {"start": "\n" + r"{\par" + alignmentCont + r"\lfbox[padding=0em, margin=0em, border-left-width=0pt, border-right-width=0pt, border-top-width=1pt, border-bottom-width=1pt]{\begin{minipage}[c]{$WIDTH$}\vspace*{1.1em}" + "\n", "end": r"\vspace*{1em}\end{minipage}}\par}" + "\n\n", "width":.90},
        "imageBorder": {"startFunc": lambda extras: "\n" + r"\tcbox[sharp corners, size=tight, boxsep=" + str(extras["padding"]) + "pt, boxrule=" + str(extras["borderWidth"]) + "pt, colback=white]{", "end": r"}" + "\n\n"},
        # trying to support more complicated insides
        #"border": {"startFunc": lambda extras: "\n" + alignmentEnvStart + r"\tcbox[sharp corners, size=tight, boxsep=" + str(jrfuncs.getDictValueOrDefault(extras,"padding",2)) + "pt, boxrule=" + str(jrfuncs.getDictValueOrDefault(extras,"borderWidth",2)) + "pt, colback=white]{", "end": r"}" + alignmentEnvEnd + "\n\n"},
        "border": {"startFunc": lambda extras: "\n" + alignmentEnvStart + r"\begin{tcolorbox}[sharp corners, size=tight, boxsep=" + str(jrfuncs.getDictValueOrDefault(extras,"padding",2)) + "pt, boxrule=" + str(jrfuncs.getDictValueOrDefault(extras,"borderWidth",2)) + "pt, colback=white]", "end": r"\end{tcolorbox}" + alignmentEnvEnd + "\n\n"},
        "npArticle": {"startFunc": lambda extras: "\n" + alignmentEnvStart + r"\begin{tcolorbox}[sharp corners, size=tight, boxsep=" + str(jrfuncs.getDictValueOrDefault(extras,"padding",2)) + "pt, boxrule=" + str(jrfuncs.getDictValueOrDefault(extras,"borderWidth",2)) + "pt, colback=white]", "end": r"\end{tcolorbox}" + alignmentEnvEnd + "\n\n"},
    }
    # symbol
    if (box not in latexDict):
        raise Exception("Runtime Error: Box mode '{}' not known; should be from: {}.".format(box, latexDict.keys()))
    boxDict = latexDict[box]

    # replacements
    width = jrfuncs.overrideIfNone(width, "width", boxDict, .80)
    width = convertStringToSafeLatexSize(width, r"\columnwidth", r"\columnwidth", r"\columnwidth", 1.0)

    if ("start" in boxDict):
        boxDict["start"] = boxDict["start"].replace("$WIDTH$", str(width))

    return boxDict
# -------------------------------------------















#---------------------------------------------------------------------------
# box helpers
def parseArgsGenericBoxOptions(args, env, astloc, boxDefaults):
    boxOptions = {
        "box": args["box"].getWrapped(),
        "symbol": args["symbol"].getWrapped(),
        "symbolColor": args["symbolColor"].getWrapped(),
        "pos": args["pos"].getWrapped(),
        "width": args["width"].getWrapped(),
        "textColor": args["textColor"].getWrapped(),
    }
    # override with defaults
    if (boxDefaults is not None):
        for k,v in boxDefaults.items():
            if (k in boxOptions) and (boxOptions[k] is None):
                boxOptions[k] = boxDefaults[k]

    return boxOptions


def isBoxRequested(boxOptions):
	return (boxOptions["box"] is not None) and (boxOptions["box"]!="none")

def addBoxToResultsIfAppropriateStart(boxOptions, results):
	if (isBoxRequested(boxOptions)):
		results.flatAdd(vouchForLatexString(wrapInLatexBoxJustStart(boxOptions), False))

def addBoxToResultsIfAppropriateEnd(boxOptions, results):
	if (isBoxRequested(boxOptions)):
		results.flatAdd(vouchForLatexString(wrapInLatexBoxJustEnd(boxOptions), False))
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
# generic funcs

def addTargetsToResults(results, targets, rmode, env, entryp, leadp, flagChangeBlankLinesToLatexNewlines, flagStripEndingNewlines):
    # first build a list of all results
    allResults = []
    for target in targets:
        targetRetv = target.renderRun(rmode, env, entryp, leadp)
        allResults.append(targetRetv)
    #
    lastResIndex = len(allResults)-1
    if (flagStripEndingNewlines):
        while (lastResIndex>0):
            block = allResults[lastResIndex]
            if ((block!="\n") and (not isinstance(block,AstValNull)) and block!=""):
                # non-empty end item
                break
            # this last result is skippable
            lastResIndex -= 1
    # now add
    for i in range(0,lastResIndex+1):
        res = allResults[i]
        results.flatAdd(res, flagChangeBlankLinesToLatexNewlines)



def addTargetsToResultsIntoCommand(textCommand, preCommand, postCommand, results, targets, rmode, env, entryp, leadp, flagChangeBlankLinesToLatexNewlines, flagStripEndingNewlines):
    # set a command (variable) to contents of the targets, with some pre and post text
    latex = "\\def" + textCommand + " {\n"
    results.flatAdd(vouchForLatexString(latex, False))
    #
    results.flatAdd(vouchForLatexString(preCommand, False))
    #
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, flagChangeBlankLinesToLatexNewlines, flagStripEndingNewlines)
    #
    results.flatAdd(vouchForLatexString(postCommand, False))
    #
    latex = "}\n"
    results.flatAdd(vouchForLatexString(latex, False))


def addResultsToResults(results, sourceResults, flagAddNewlineAfter):
    contentList = sourceResults.getContents()
    if (len(contentList)>0):
        for r in contentList:
            results.flatAdd(r, False)
        if (flagAddNewlineAfter):
            results.flatAdd("\n")


def exceptionIfNotRenderMode(rmode, funcName, env, astloc):
    if (rmode != DefRmodeRender):
        raise makeJriException("DEBUG: function () only meant to execute in DefRmodeRender mode".format(funcName), astloc)

#---------------------------------------------------------------------------











#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def findDayByNumber(dayNumber, env, astloc, taskLabel, flagAllowTempCalculatedDay):
    dayManager = env.getDayManager()
    day = dayManager.findDayByNumber(dayNumber, flagAllowTempCalculatedDay)
    if (day is None):
        raise makeJriException("Unknown day ({}) while performing {}; days must be defined using $configureDay()".format(dayNumber, taskLabel), astloc)
    return day
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def parseFontSize(env, fontSizeString, defaultBaseSize, defaultSpacing):
    if (fontSizeString is None) or (fontSizeString==""):
        baseSize = defaultBaseSize
        spacing = defaultSpacing
    else:
        # we expect a number or a comma separated pair of numbers
        fontSizeString = fontSizeString.strip()
        parts = fontSizeString.split(",")
        if (len(parts)>2):
            raise Exception("Bad font size string")
        numbers = [float(part) for part in parts]
        if (len(numbers)==1):
            baseSize = numbers[0]
            spacing = baseSize + 1
        else:
            baseSize = numbers[0]
            spacing = numbers[1]
    #
    # modifier based on baseline font size
    renderer = env.getRenderer()
    [fontModifierAdditive, fontModifierMultiplicative] = renderer.calcDocumentFontModifer()
    if (baseSize is not None):
        baseSize += fontModifierAdditive
    if (spacing is not None):
        spacing += fontModifierAdditive

    retDict = {"base": baseSize, "spacing": spacing}
    return retDict
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
# adding text for GAINING markers
def addGainTagTextLineToResults(tag, actionKeyword, results, reportMode, astloc, entryp, leadp, useBulletIfEmptyLine, textColor):

    # get label
    flagTryToFollowCase = True
    flagBoldMarkdown = True
    classNamePlusLabel = tag.getNiceObfuscatedLabelWithType(flagBoldMarkdown, reportMode)

    actionDict = calcMarkerActionDict(actionKeyword, "all")
    endMainLocation = jrfuncs.getDictValueOrDefault(actionDict, "endMainLocation", "")       

    # gainInstruction will say something like "Circle Marker D"
    instruction = actionDict["present"] + " " + classNamePlusLabel
    # add end instructions so its now ike "Circle Marker D in your case log"
    if (endMainLocation!=""):
        instruction += " " + endMainLocation

    # add initial gain instructions
    text = instruction

    if (textColor is not None):
        results.flatAdd(vouchForLatexString(wrapLatexInColorStart(textColor), True))

    if (flagTryToFollowCase):
        deferredResult = CbDeferredBlockFollowCase(astloc, entryp, leadp, text, useBulletIfEmptyLine, True, True)
        results.flatAdd(deferredResult)
    else:
        results.flatAdd(text)

    # now docs give additional info
    if (tag.tagType == "doc"):
        # non obfucsated label
        revealedLabel = tag.getLabel()
        # additional instruction on documents
        plusInstruction = ". " + _("You have gained access to") + " {}".format(classNamePlusLabel)
        # adding its revealed label in parentheses
        if (revealedLabel is not None) and (revealedLabel!="") and (not tag.getIsCustomObfuscatedLabel()):
            plusInstruction += " ({})".format(revealedLabel)
        # add where info
        whereText = tag.getWhereText()
        if (whereText!=""):
            plusInstruction += ", " + whereText

        # add plus instruction text (minus any page number part)
        text = plusInstruction
        results.flatAdd(text)

        # add deferred page number?
        if (tag.isInBook()):
            # add deferred page number
            tagId = "DOCUMENTS>" + tag.getId()
            text = " on "
            results.flatAdd(text)
            result = CbDeferredBlockRefLead(astloc, entryp, leadp, tagId, "page")
            results.flatAdd(result)

    # now a deferred add period automatically IFF at end of line
    deferredResult = CbDeferredBlockEndLinePeriod(astloc, entryp, leadp, True)
    results.flatAdd(deferredResult)    

    if (textColor is not None):
        results.flatAdd(vouchForLatexString(wrapLatexInColorEnd(), True))





# adding text for CHECKING markers
def addCheckTagTextLineToResults(env, tagList, testType, check, actionKeyword, results, reportMode, astloc, entryp, leadp, optionNoIf):
    # text to use
    endWithOtherwiseDivider = False
    endText = ""
    if (testType == "has"):
        checkTypeText = _("have") + " "
    elif (testType == "missing"):
        checkTypeText = _("have *not*") + " "
    elif (testType == "require"):
        checkTypeText = _("have *not*") + " "
        endText = _(", stop reading now, and return here after you have.") + "\n"
        endWithOtherwiseDivider = True
    elif (testType == "hintDependencyRequire"):
        checkTypeText = _("have *not*") + " "
        endText = _(", stop reading now, and return here after you have.") + "\n"
        endWithOtherwiseDivider = False

    actionDict = calcMarkerActionDict(actionKeyword, check)
    endMainLocation = jrfuncs.getDictValueOrDefault(actionDict, "endMainLocation", "") 

    if (optionNoIf):
        ifPrefix = ""
    else:
        ifPrefix = _("If") + " "      

    if (ifPrefix!=""):
        # deferred add it to match case
        useBulletIfEmptyLine = False
        deferredResult = CbDeferredBlockFollowCase(astloc, entryp, leadp, ifPrefix, useBulletIfEmptyLine, True, True)
        results.flatAdd(deferredResult)

    # we want to SAY that the tags have been gained
    if (len(tagList)==1):
        # single tag case is easiest
        tag = tagList[0]
        classNamePlusLabel = tag.getNiceObfuscatedLabelWithType(True, reportMode)
        # gainInstruction will say something like "Circle Marker D"
        instruction = actionDict["past"] + " " + classNamePlusLabel
        # add end instructions so its now ike "Circle Marker D in your case log"
        if (endMainLocation!=""):
            instruction += " " + endMainLocation
        text = _("you {} {}").format(checkTypeText, instruction)
    else:
        # multiple tag case is a bit harder
        instruction = actionDict["past"]
        if (endMainLocation!=""):
            instruction += " " + endMainLocation
        if (check=="all"):
            if (len(tagList)==2):
                checkText = _("**both**")
            else:
                checkText = _("**all**")
            combineText = _("and")
        elif (check=="any"):
            if (len(tagList)==2):
                checkText = _("**either**")
            else:
                checkText = _("*any*")
            combineText = _("or")
        else:
            raise Exception("check parameter '{}' to requiretag should be from [any,all]".format(check))
        #
        tagLabelList = []
        for tag in tagList:
            tagLabelList.append(tag.getNiceObfuscatedLabelWithType(True, reportMode))
        tagListString = jrfuncs.makeNiceCommaAndOrList(tagLabelList, combineText)
        #
        text = _("you {} {} {} of the following {} items ({})").format(checkTypeText, instruction, checkText, len(tagList), tagListString)
    
    if (endText is not None) and (endText!=""):
        text += endText

    # add text
    results.flatAdd(text)

    if (endWithOtherwiseDivider):
        latex = generateLatexForDivider(env, "otherwise", astloc)
        results.flatAdd(vouchForLatexString(latex, False))
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
# the idea is to support more flexible ways of refering to markers (circle them, underline them, etc.)
def calcMarkerActionDict(markerActionKeyword, combinationMode):
    markerActionDict = {
        "gain": {"present": _("You have gained"), "past": _("acquired"), "found": _("found (marked or circled)"), "endMainLocation": _("(note this in your case log)")},
        "circle": {"present": _("Circle"), "past": _("circled"), "endMainLocation": _("in your case log")},
        "underline": {"present": "__" + _("Underline") + "__", "past": "__" + _("underlined") + "__", "endMainLocation": _("in your case log")},
        "strike": {"present": _("Strike through"), "past": _("struck through"), "endMainLocation": _("in your case log")},
        "mark": {"present": _("MARKED"), "past": _("marked in any way (circled, underlined, etc.)"), "endMainLocation": _("in your case log")},
        "underlineNotCircle": {"present": "__" + _("Underline") + "__", "past": "__" + _("underlined") + "__ " + _("but **not** circled"), "endMainLocation": _("in your case log")},
        "circleNotStrike": {"present": _("Circle"), "past": _("circled but **not** struck-through"), "endMainLocation": _("in your case log")},
        "acquired": {"present": _("You have gained"), "past": _("acquired"), "found": _("found (marked or circled)"), "endMainLocation": ""},
        }
    if (markerActionKeyword not in markerActionDict):
        raise Exception("Uknown marker action keyword '{}'".format(markerActionKeyword))
    return markerActionDict[markerActionKeyword]


def generateFoundGainString(actionKeyword):
    actionDict = calcMarkerActionDict(actionKeyword, "all")
    foundWord = jrfuncs.getDictValueOrDefault(actionDict, "found", "")
    if (foundWord==""):
        foundWord = jrfuncs.getDictValueOrDefault(actionDict, "past", _("found"))
    return foundWord
#---------------------------------------------------------------------------






#---------------------------------------------------------------------------
def createStartEndLatexForFontSizeString(style):
    # return a dict with start and end latex
    latexSizeCommand = parseFontSizeStringToLatexCommand(style, True, None)
    #
    retDict = {"start": latexSizeCommand + " ", "end": ""}
    return retDict
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
# this used to say NO LONGER USED but it seems like it still is
# WE SHOULD GET RID OF THESE

def convertFontSizeKeywordToIndex(fontSizeKeyword, keywordIndexModifier, env, astloc):
    if (fontSizeKeyword is None) or (fontSizeKeyword==""):
        fontSizeKeyword = "normal"

    # keyword
    if (fontSizeKeyword in latexFontSizeMap):
        # index into list
        index = list(latexFontSizeMap.keys()).index(fontSizeKeyword) + keywordIndexModifier
        return index

    # is it already a number? if so just return it
    fontSizeNumber = jrfuncs.convertToIntIfPossible(fontSizeKeyword)
    if (fontSizeNumber is not None):
        return fontSizeNumber

    # not found
    raise makeJriException("Font size keyword not understood ({}), should be a number or one from [{}].".format(fontSizeKeyword, list(latexFontSizeMap.keys())), astloc)



def calcLatexSizeKeywordFromBaseAndMod(baseSize, modSize, env, astloc):
    # we want sizeMod to be numbers or strings, we want to add them
    # where baseSize would be eg. the base size of a font, and sizeMod would be a modifier
    # but both could be string keywords or numbers
    # first convert both to numbers (we modify the modSize if a keyword is used to that the modifier is the numeric value to ADD to base size, so "normal" is 0)
    baseSize = convertFontSizeKeywordToIndex(baseSize, 0, env, astloc)
    modSize = convertFontSizeKeywordToIndex(modSize, -4, env, astloc)
    # now we add them, but we want to offset modSize to be 0 if normal (unchanged)
    finalSizeIndex = baseSize + modSize
    if (finalSizeIndex<0):
        finalSizeIndex = 0
    if (finalSizeIndex>=len(latexFontSizeMap)):
        finalSizeIndex = len(latexFontSizeMap)-1
    finalSizeLatex = list(latexFontSizeMap.values())[finalSizeIndex]
    return finalSizeLatex
#---------------------------------------------------------------------------















#---------------------------------------------------------------------------
def parseFontSizeStringToLatexCommand(fstring, flagExceptionOnBad, astloc):
    # try to convert fstring to a "fs24.2" command
    # if valid, return the latex command to set the font size
    # otherwise return None

    if (fstring is None) or (fstring==""):
        # empty size? or should we return "\normal" ?
        return ""

    # preset size
    if (fstring in latexFontSizeMap):
        return latexFontSizeMap[fstring]
            
    pattern = r"^fs(?P<number>\d+(?:\.\d+)?)$"
    match = re.match(pattern, fstring)
    if (match):
        sizeStr = match.group("number")
        sizeNum = jrfuncs.intOrFloatFromStr(sizeStr)
        # latex suggestion of baseline skip from font size
        #skipNum = 1.2 * sizeNum
        skipNum = 1.4 * sizeNum
        latex = r"\fontsize{" + sizeStr + r"}{" + str(skipNum) + r"}\selectfont" + " "
        return latex
    
    # not found
    if (flagExceptionOnBad):
        raise makeJriException("Runtime Error: Casebook font size string '{}' not understood; should be from: {} or of the format 'fs#' for explicit font size in points.".format(fstring, latexFontSizeMap.keys()), astloc)
    return None
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def getTargetResultBlockAsTextIfAppropriate(targetRetv):
    # if the results of a target block of text 
    if (isinstance(targetRetv,str)):
        text = targetRetv
    elif (isinstance(targetRetv,AstValString)):
        text = targetRetv.getUnWrappedExpect(AstValString)
    else:
        text = None
    if (text is not None):
        if (isTextLatexVouched(text)):
            text = None
    return text


def convertTargetRetvToResultList(targetRetv):
    if (isinstance(targetRetv, JrAstResultList)):
        return targetRetv
    # it might just be a simple result, so CONVERT it into a result list
    retv = JrAstResultList()
    retv.flatAdd(targetRetv)
    return retv
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def cipherMakeRandomSubstitutionKeyFromHash(key):
    # return a random 26 character substitution cipher key
    if (isinstance(key,str)):
        if (len(key)==26):
            # good, it's the right length
            # ATTN: check for uniqueness of letters?
            return key
        raise Exception("Key for substitution cipher should either be a seed number, OR a 26-letter unique string of letters")

    # ok they are passing us a key #, which we use as a seed to do a shuffle of letters
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    char_list = list(letters)
    # Seed the random number generator
    random.seed(key)
    # Shuffle the list of characters
    random.shuffle(char_list)
    # Join the list back into a string
    substitutionKey =  ''.join(char_list)
    return substitutionKey


def cipherMakeSimpleSubstitutionKeyFromKeyword(key):
    # return a 26 character substitution cipher key, which STARTS with the unique letters in the key

    return cipherMakeUniqueKeywordAlphabet(key, 26)


def cipherMakeUniqueKeywordAlphabet(key, targetlen):
    # take a keyword, and then make a targetlen (should be 25 or 26) string of letters, starting with keyword and then remaining alphabet, with no repeats
    # when the target is 25 letters, we want to drop J?
    if (targetlen==25):
        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    elif (targetlen==26):
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    else:
        raise Exception("Target length for cipherMakeUniqueKeywordAlphabet needs to be from [25,26]")
    
    # make jey uppercase
    key = key.upper()

    # thanks to chatgpt
    # Remove any characters not in the alphabet and make unique
    filtered_keyword = []
    seen = set()
    for char in key:
        if char in alphabet and char not in seen:
            filtered_keyword.append(char)
            seen.add(char)
    
    # Add remaining characters from the alphabet
    remaining_chars = [char for char in alphabet if char not in seen]
    
    # Combine into final string
    cipher_alphabet = ''.join(filtered_keyword) + ''.join(remaining_chars)
    return cipher_alphabet



def cipherSpellDigits(text):
    digit_words = {
        '0': 'zero', '1': 'one', '2': 'two', '3': 'three', 
        '4': 'four', '5': 'five', '6': 'six', '7': 'seven', 
        '8': 'eight', '9': 'nine'
    }
    
    # Replace each digit in the string with its word
    result = ''.join(digit_words[char] if char in digit_words else char for char in text)
    return result


def cipherSegment(text, block_size, pad_char):
    # Segment text into blocks of block_size
    if (len(text)==0):
        return text
    
    # chatgpt
    blocks = [text[i:i + block_size] for i in range(0, len(text), block_size)]
    
    # Pad the last block if necessary
    if len(blocks[-1]) < block_size:
        blocks[-1] += pad_char * (block_size - len(blocks[-1]))
    
    # Join blocks with spaces
    segmented_text = ' '.join(blocks)
    return segmented_text


def cipherStripChars(text, chars_to_remove):
    remove_set = set(chars_to_remove)
    # Filter out characters to remove
    filtered_text = ''.join(char for char in text if char not in remove_set)
    return filtered_text
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
class cipherMorseCode:
    def __init__(self):
        pass

    def encipher(self, text, optionKeepPunctuation=True):
        morse_code = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 
        'Z': '--..',
        # add replacements for chars that conflict with morse
        '.': '*', '-': '*'
        }

        # Convert text to uppercase
        text = text.upper()

        #
        spaceBetweenWordChar = ' / '
        spaceBetweenMorseChar = ' ~'

        morseText = ''
        lastCharFixed = False
        needSpaceBeforeMorse = False
        for index, c in enumerate(text):
            if (c in morse_code):
                if (needSpaceBeforeMorse):
                    morseText += spaceBetweenMorseChar
                morseText += morse_code[c]
                lastCharFixed = False
                needSpaceBeforeMorse = True
            else:
                if (c==' ') and (lastCharFixed):
                    # no need to put back a space if the previous character was already a punctuation, space, etc.
                    c = ' '
                elif (c==' '):
                    c = spaceBetweenWordChar
                else:
                    if (needSpaceBeforeMorse):
                        morseText += spaceBetweenMorseChar
                morseText += c
                lastCharFixed = True
                needSpaceBeforeMorse = False

        morseText = morseText.replace("  "," ")
        
        return morseText
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
class cipherPlain:
    def __init__(self):
        pass

    def encipher(self, text, optionKeepPunctuation=True):
        # Convert text to uppercase
        text = text.upper()
        return text
#---------------------------------------------------------------------------






#---------------------------------------------------------------------------
def cipherReplaceNonLettersReturnFixList(text, spaceReplaceChar, optionPadToEvenLengthPlaintext):
    fixes = []
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""
    lastCharFixed = False
    text = text.upper()
    for index, c in enumerate(text):
        if (c in alphabet):
            result += c
            lastCharFixed = False
        else:
            if (c==' ') and (lastCharFixed):
                # no need to put back a space if the previous character was already a punctuation, space, etc.
                continue
            if (c==' '):
                c = spaceReplaceChar
            fixes.append({'index': len(result), 'char': c})
            lastCharFixed = True

    if (optionPadToEvenLengthPlaintext) and (len(result)%2 == 1):
        # we need to add a plaintext X to end
        endpos = len(result)
        result += 'X'
        # but here is something subtle -- now we may need to adjust fixes to nudge them forward if they came after the last good plaintext
        for fix in fixes:
            if (fix['index'] >=endpos):
                fix['index'] += 1


    return [result, fixes]


def cipherReplaceFixList(text, fixes, newlettersize):
    if (fixes is None):
        return text
    offset = 0
    for fix in fixes:
        sindex = (fix['index'] * newlettersize) + offset
        c = fix['char']
        newcs = c
        newcs += ' ' * (newlettersize-1)
        text = text[0:sindex] + newcs + text[sindex:]
        offset += newlettersize
    return text


def cipherRemoveReplacePunctuation(text):
    # remove punctuation and dont put it back
    # spelled out punctuation
    text = text.replace(".", "stop")
    text = text.replace("%", "percent")
    text = text.replace("-", "dash")
    # remove other common punctuation (leave anything that could be significant)
    text = text.replace(";", "")
    text = text.replace(",", "")
    text = text.replace("'", "")
    text = text.replace('"', "")
    text = text.replace("#", "")
    text = text.replace("$", "")
#---------------------------------------------------------------------------






#---------------------------------------------------------------------------
def formHelperListBuild(env, listTypeStr, choices, other):
    renderer = env.getRenderer()
    choiceList = choices.split("|")
    if (other):
        choiceList.append("__other__")

    fullCommandName = "cbFormList" + listTypeStr
    #
    latex = "\\begin{" + fullCommandName + "}\n"
    for choice in choiceList:
        choice = choice.strip()
        if (choice == "__other__"):
            choiceLatex = "\\cbFormOther"
        else:
            choiceLatex = renderer.convertMarkdownToLatexDontVouch(choice, False, True)
        latex += "\\item " + choiceLatex + "\n"
    latex += "\\end{" + fullCommandName + "}\n"
    #
    return latex
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def functionRunEffectOnImagePath(env, entryp, leadp, astloc, path, effectKey, funcCallText):

    # first mark the original path as being used (for the debug report), if it can be found; if not that's ok at this point, maybe there is only the effected file and not the original
    [imageFullPath, warningText] = env.locateManagerFileWithUseNote([DefFileManagerNameImagesCase], path, "Checking for effect processing filter on image", None, leadp, env, astloc, True)

    # now let's see if the MODIFIED filename already exists (was already cached and created)
    jreffector = JrImageEffects()
    suffixKey = "suffixLong"
    modifiedPath = jreffector.suffixFilePath(path, effectKey, suffixKey)
    [effectedImageFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), modifiedPath, "Effect processing filter on image", None, leadp, env, astloc, True)
    if (effectedImageFullPath is not None):
        # already found, so we are done, just return the MODIFIED path, where it will be used
        return modifiedPath

    # ok the modified file does NOT exist yet, so we will need to make it, add it to game, and return it

    # however, noiw we complain if the real file does not exist
    if (imageFullPath is None):
        raise makeJriException("Could not find image to {}; note must be local game image (not shared).".format(funcCallText), astloc)

    # ok we found it locally, so we can make an effect version of it

    # next step, get the game model, and ask the game to make the effectified version of the image; note we pass the fully RESOLVED absolute path to the image
    game = env.getGameModel()
    retv = game.runEffectOnImageFileAddOrReplaceGameFile(effectKey, imageFullPath, suffixKey, False)
    if (not retv["success"]):
        # error
        raise makeJriException("Failed to create effect image from function {}: {}.".format(funcCallText, retv["message"]))
    
    # we created it
    # however there is one more thing we need to do, which is update the local file manager to tell it about the new file so it can find it on future requests during this run (it would find it on the next run when it rescanned)
    manager = env.getFileManager(DefFileManagerNameImagesCase)
    baseName = manager.canonicalName(modifiedPath)
    modifiedPathAbsolute = retv["outPath"]
    manager.addFile(baseName, modifiedPathAbsolute)

    # now it SHOULD be at modified path.. we can check
    if (True):
        [imageFullPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListImage(), modifiedPath, "Effect processing filter on image", None, leadp, env, astloc, True)
        if (imageFullPath is not None):
            # found it
            return modifiedPath

    # ERROR -- it should have been created but we can't find it
    raise makeJriException("Seemed to succeed at creating effect image from function {}; but could not find expected file '{}'.".format(funcCallText, modifiedPath), astloc)
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def blurbItemLatex(label, value):
    text = r"\item \textbf{" + label + "}: " + value + "\n"
    return text
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def calculateLatexForItemTimeBoxStyle(itemTime):
    if (itemTime is not None) and (itemTime != False) and (itemTime>0):
        timeText = _("Time advances {} minutes.").format(int(itemTime))
        boxOptions = {
            "box": "default",
            "isTextSafe": True,
            "symbol": "clock",
            "textColor": "red",
        }
        timeLatex = "\n" + wrapInLatexBox(boxOptions, timeText)
        return timeLatex
    # no time statement
    return None


def calculateLatexForItemTimeHeaderStyle(itemTime, defaultTime, defaultTimeStyle, zeroTimeStyle):
    # hide it?
    if (itemTime is None) or (itemTime is False):
        return None
    #
    itemTime = int(itemTime)
    if (itemTime==defaultTime) and (defaultTimeStyle=="hide"):
        return None
    if (itemTime==0) and (zeroTimeStyle=="hide"):
        return None

    # show time

    # time or none if none
    if (itemTime==0):
        innerTimeString = "none"
    else:
        if ((itemTime>=120) and (itemTime%60==0)):
            # when we have an even number of hours more than 1, report as hours
            innerTimeString = "{} hours".format(int(itemTime/60))
        else:
            innerTimeString = "{} minutes".format(itemTime)

    if (itemTime!=defaultTime):
        # show non-default time
        if (itemTime==0):
            style = zeroTimeStyle
        else:
            style = defaultTimeStyle
        if (style=="bold"):
            # bring more attention to non-default times
            innerTimeString = r"\textbf{" + innerTimeString + "}"
        elif (style=="red"):
            # bring more attention to non-default times
            innerTimeString = r"\textbf{\textcolor{red}{" + innerTimeString + "}}"

    timeStringArg = "Time: " + innerTimeString
    ltext = r"\cbsubheadingTime{" + timeStringArg + "}\n"
    return ltext
#---------------------------------------------------------------------------












#---------------------------------------------------------------------------
# Render support

def makeLatexReferenceToLeadById(astloc, entryp, lead, renderDoc, targetId, optionStyle, optionVouch):
    if (targetId is not None):
        referencedLead = renderDoc.findLeadByIdPath(targetId, astloc)
        if (referencedLead is None):
            failedFindTrace = renderDoc.generateIdTreeTrace()
            raise makeJriException("Deferred Render Syntax Error: Could not find lead with id/path: '{}'; trace = {}.".format(targetId, failedFindTrace), astloc)
    else:
        referencedLead = lead.getInlinedFromLead()
        if (referencedLead is None):
            raise makeJriException("Deferred Render Syntax Error: Could not find implicit lead (are you trying to incorrectly return from a non-inline lead?)", astloc)
    #
    return makeLatexReferenceToLead(referencedLead, optionStyle, optionVouch)


def makeLatexReferenceToLead(referencedLead, optionStyle, optionVouch):
    from .jrastfuncs import DefInlineLeadPlaceHolder

    # new style
    if (optionStyle == "full"):
        optionPage = True
        optionPageStyle = "paren"
        optionHref = True
        optionLabel = True
        optionId = True
    elif (optionStyle == "report"):
        optionPage = True
        optionPageStyle = "paren"
        optionHref = True
        optionLabel = "report"
        optionId = True
    elif (optionStyle == "label"):
        optionPage = True
        optionPageStyle = "paren"
        optionHref = True
        optionLabel = True
        optionId = True
    elif (optionStyle == "nolabel"):
        optionPage = True
        optionPageStyle = "paren"
        optionHref = True
        optionLabel = False
        optionId = True
    elif (optionStyle == "plainid"):
        optionPage = False
        optionPageStyle = "paren"
        optionHref = True
        optionLabel = False
        optionId = True
    elif (optionStyle == "page"):
        optionPage = True
        optionPageStyle = "plain"
        optionHref = True
        optionLabel = False
        optionId = False
    elif (optionStyle == "pagenum"):
        optionPage = True
        optionPageStyle = "num"
        optionHref = True
        optionLabel = False
        optionId = False
    elif (optionStyle == "pageparen"):
        optionPage = True
        optionPageStyle = "paren"
        optionHref = True
        optionLabel = False
        optionId = False
    else:
        # default
        optionPage = True
        optionPageStyle = "paren"
        optionHref = True
        optionLabel = False
        optionId = True

    referencedLeadRid = referencedLead.getRid()
    referencedLeadIdText = referencedLead.getLabelIdPreferAutoId()

    # start building text
    text = ""
    # add label?
    if (optionLabel=="report"):
        text = referencedLead.getReportToc()
    elif (optionLabel):
        label = referencedLead.getLabel()
        if (label is not None) and (label != referencedLeadIdText):
            text = referencedLeadIdText + " - " + label
        else:
            text = referencedLeadIdText
    elif (optionId):
        text = referencedLeadIdText
    else:
        text = ""

    # kludge replace
    text = text.replace(DefInlineLeadPlaceHolder, "")
    if (text.startswith(DefInlineLeadLabelStart)):
        text = text[len(DefInlineLeadLabelStart):]

    if (text!=""):
        latex = convertEscapeUnsafePlainTextToLatex(text)
        latex = preventWordWrapOnLeadIdHypenLatex(latex)
    else:
        latex = ""

    # add page number?
    if (optionPage):
        pageLatex = r"\pageref*{" + referencedLeadRid + r"}"
        if (latex!=""):
            latex += " "
        if (optionPageStyle == "paren"):
            latex+= r"(p." + pageLatex + r")"
        elif (optionPageStyle == "plain"):
            latex+= r"page " + pageLatex
        elif (optionPageStyle == "num"):
            latex+= pageLatex
        else:
            latex+= pageLatex
    # make it an href?
    if (optionHref):
        latex = r"\hyperref[{" + referencedLeadRid + r"}]{" + latex + r"}"

    # return it vouched
    if (optionVouch):
        return vouchForLatexString(latex, True)
    else:
        return latex
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def makeMiniPageBlockLatexStart(optionVouch, align):
    latex = r"\cbBlockStart{" + align + "} "

    # return it vouched
    if (optionVouch):
        return vouchForLatexString(latex, False)
    else:
        return latex


def makeMiniPageBlockLatexEnd(optionVouch):
    latex = r"\cbBlockEnd "

    # return it vouched
    if (optionVouch):
        return vouchForLatexString(latex, False)
    else:
        return latex
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def dropCapResults(dropCapsStyle, optionPreferAfterNoteType, targets, rmode, env, entryp, leadp, astloc, optionLines, optionFindent, optionNindent, optionLhang, optionProtectStyle, flagStripEndingNewlines):

    # to help us with markdown
    renderer = env.getRenderer()

    # building results
    results = JrAstResultList()

    # contents of targets
    addTargetsToResults(results, targets, rmode, env, entryp, leadp, False, flagStripEndingNewlines)
    blockContents = results.getContents()

    # has caller asked us to TRY to skip over certain note marker (like headlines and bylines in a newspaper article)? This is pretty kludgey
    startingIndex = 0
    if (optionPreferAfterNoteType is not None):
        # we prefer after a certain point; we go from BOTTOM UP to get last item
        for index in range(len(blockContents)-1, -1, -1):
            block = blockContents[index]
            if (isinstance(block, ResultAtomNote)):
                note = block.getNote()
                noteType = jrfuncs.getDictValueOrDefault(note,"type", None)
                if (noteType == optionPreferAfterNoteType):
                    # found it, so we will start here
                    startingIndex = index + 1
                    break

    lettrineOptions = "[lines={},findent={},nindent={},lhang={},realheight]".format(optionLines, optionFindent, optionNindent, optionLhang)

    # now we want to find the first textual line of results, and modify it
    didWork = False
    afterIndex = -1
    for index in range(startingIndex, len(blockContents)):
        block = blockContents[index]
        if (isinstance(block, str)):
            text = block
        elif (isinstance(block,AstValString)):
            text = block.getUnWrappedExpect(AstValString)
        else:
            # it's not text
            continue
        if (isTextLatexVouched(text)):
            # we can't operate on latex
            continue

        # make sure it's non-empty?
        # ATTN: THIS STRIP WAS CAUSING US TO LOSE TRAILING SPACE before the $ in lines like "this happened on $dayDate()"
        if (re.fullmatch(r"\s*", text)):
            continue
        #text = text.strip()
        #if (text=="\n") or (text==""):
        #    continue

        # ok we have some pure text
        [firstChar, upperCaseText, remainderText] = jrfuncs.smartSplitTextForDropCaps(text, dropCapsStyle)
        if (firstChar is not None):
            #firstChar = text[0]
            #
            if (firstChar==" "):
                raise makeJriException("First character in dropcase in space; should not happen", astloc)
            if (dropCapsStyle=="letter"):
                latexDropCaps = r"\lettrine" + lettrineOptions + "{" + firstChar + "}"
                if (upperCaseText!=""):
                    latexDropCaps += "{" + renderer.convertMarkdownToLatexDontVouch(upperCaseText, True, True) + "}"
            elif (dropCapsStyle=="word"):
                latexDropCaps = r"\lettrine" + lettrineOptions + "{" + renderer.convertMarkdownToLatexDontVouch(firstChar + upperCaseText, True, True) + "}"
            elif (dropCapsStyle=="bold"):
                # this does not use latex lettrine but just some larger size and bold
                latexDropCaps = r"{\large\bfseries " + firstChar + r"}{\large " + renderer.convertMarkdownToLatexDontVouch(upperCaseText.upper(), True, False) + "}"
                optionProtectStyle = "none"
            else:
                raise makeJriException("unknown dropcap style '{}'.".format(dropCapsStyle), astloc)
            #
            # build new results to insert at this point
            resultsIn = JrAstResultList()
            resultsIn.flatAdd(vouchForLatexString(latexDropCaps, True))
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
                lastNonNewlineIndex = len(results.getContents())-1
                # ATTN: new 5/21/25 - we try to not do this on trailing newlines
                while (lastNonNewlineIndex>0):
                    block2 = results.contents[lastNonNewlineIndex]
                    if ((block2!="\n") and (not isinstance(block2,AstValNull)) and block2!=""):
                        # non-empty end item
                        break
                    # this last result is skippable
                    lastNonNewlineIndex -= 1
                # the idea is to replace non-respected newlines with fake paragraph newlines
                for index2 in range(afterIndex, lastNonNewlineIndex+1):
                    block2 = results.contents[index2]
                    # ATTN: new 5/21/25 - we try to not do this on trailing newlines
                    if (block2=="\n"):
                        results.removeByIndex(index2)
                        results.flatInsertAtIndex(latexFpar, index2)
            #
            elif (optionProtectStyle=="gap"):
                # try to force the drop cap to force following paragraphs down
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
def latexSideRulesAround(latex, safeWidthStr):
    latex = r"\noindent\imageWithSideRules{" + latex + "}\n"
    return latex

    # old way
    if (False):
        latex = r"""% add side rules
    \par
    \noindent % Ensures no indentation
    \begin{minipage}{\columnwidth} % Uses column width instead of text width
    \setlength{\remainingwidthDivider}{\columnwidth-""" + safeWidthStr + r"""-2cm} % Total width minus image width minus space
    \hspace*{\fill}
    \raisebox{0.5em}{\rule{0.5\remainingwidthDivider}{0.4pt}} % Horizontal rule before the image, using half of the column width
    \hspace*{0.25cm} % Space between the rule and the image
    """ + latex + r"""
    \hspace*{0.25cm} % Space between the image and the rule
    \raisebox{0.5em}{\rule{0.5\remainingwidthDivider}{0.4pt}}
    \hspace*{\fill}
    \end{minipage}
    """

    return latex
#---------------------------------------------------------------------------









#---------------------------------------------------------------------------
def newsLatexFormatHeadlineString(env, text, styleString, defaultString):
    presetDict = newsGenericPreseStyleDict()
    latex = newsGenericFormatStringWithStyle(env, text, styleString, presetDict, defaultString)
    latex = r"\npHeadline{" + latex +"}\n"
    #latex = r"\begin{npHeadLineEnv}" + "\n" + latex + "\n" + r"\end{npHeadLineEnv}" + "\n"
    return latex


def newsLatexFormatBylineString(env, text, styleString, defaultString):
    presetDict = newsGenericPreseStyleDict()
    latex = newsGenericFormatStringWithStyle(env, text, styleString, presetDict, defaultString)
    latex = r"\npByLine{" + latex +"}\n"
    #latex = r"\begin{npByLineEnv}" + "\n" + latex + "\n" + r"\end{npByLineEnv}" + "\n"
    return latex


def newsGenericPreseStyleDict():
    sdict = {
        #"boldup": {"bold": True, "case": "upper"}
        "boldup": "bold=true|case=upper"
    }
    return sdict

def newsGenericFormatStringWithStyle(env, text, styleString, presetDict, defaultString):
    styleOptions = parseTextStyleOptions(styleString, presetDict, defaultString)
    # modify case
    latex = ""
    if (jrfuncs.getDictValueIsNonBlankFalse(styleOptions,"case")):
        text = jrfuncs.applyCaseChange(text, styleOptions["case"])

    formattingDict = {"start": "", "end": ""}
    #
    if (jrfuncs.getDictValueIsNonBlankFalse(styleOptions,"bold")):
        #formattingDict["start"] += r"\textbf{"
        #formattingDict["end"] += r"}"
        formattingDict["start"] += r"\bfseries "
    if (jrfuncs.getDictValueIsNonBlankFalse(styleOptions,"underline")):
        #formattingDict["start"] += r"\underline{"
        formattingDict["start"] += r"\uline{"
        formattingDict["end"] += r"}"
    if (jrfuncs.getDictValueIsNonBlankFalse(styleOptions,"italic")):
        #formattingDict["start"] += r"\textit{"
        #formattingDict["end"] += r"}"
        formattingDict["start"] += r"\itshape "

    # size MUST come after textbf orr it messed with line spacing?
    if (jrfuncs.getDictValueIsNonBlankFalse(styleOptions,"size")):
        formattingDict["start"] +=  styleOptions["size"] + " "

    if (jrfuncs.getDictValueIsNonBlankFalse(styleOptions,"fit")):
        formattingDict["start"] += r"\resizebox{\columnwidth}{!}{"
        formattingDict["end"] += r"}"

    # linespace at start
    if (jrfuncs.getDictValueIsNonBlankFalse(styleOptions,"lineSpace")):
        formattingDict["start"] = "\\setstretch{" + str(styleOptions["lineSpace"]) + "}" + formattingDict["start"]

    # convert text from markdown to latex and wrap in formatting
    renderer = env.getRenderer()
    #
    flagRemoveDoubleLineBreaks = True
    latexVersionOfMainText = renderer.convertMarkdownToLatexDontVouchDoEscapeNewlines(text, False, False, flagRemoveDoubleLineBreaks)
    #latexVersionOfMainText = renderer.convertMarkdownToLatexDontVouch(text, False, False)
    #
    latex = formattingDict["start"] + latexVersionOfMainText + formattingDict["end"]

    return latex



def parseTextStyleOptions(styleString, presetDict, defaultString):

    # ok now styleString is a string of var=val tuples separated by |
    # so is defaultString
    # and presetDict is a dictionary of them
    # we want to parse the defaults, and apply them
    # then parse the styles, and 'apply' them
    # and if we encounter a "preset=val" then parse and 'apply' preset string
    # by apply we mean set a final dictionary of values

    # ok parse assignment string with defaults and presets
    finalDict = {}
    jrfuncs.mergeVarValPairStringIntoDict(finalDict, defaultString, presetDict)
    jrfuncs.mergeVarValPairStringIntoDict(finalDict, styleString, presetDict)

    # now walk and apply style items
    sdict = {}
    for k,v in finalDict.items():
        if (k in ["underline", "bold", "italic", "fit"]):
            sdict[k] = jrfuncs.parseVarValStringAsBool(v)
        elif (k=="case"):
            if (v in ["upper","lower","title","","unchanged"]):
                sdict["case"] = v
            else:
                raise Exception("case modifier '{}' in style string not understood; stylestring ='{}'.".format(v, styleString))
        elif (k=="lineSpace"):
            sdict[k] = jrfuncs.parseVarValStringAsNumber(v)
        elif (k=="size"):
            sdict["size"] = parseFontSizeStringToLatexCommand(v, True, None)
        else:
            raise Exception("style var=val key '{}' not understood; style string should be pairs of var=val entries from [underline,bold,italic,fit,case,size] separated by | character; stylestring ='{}'.".format(k, styleString))
    return sdict
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def lookupLatexSymbol(id):
    # return None if this id is not a valid \id latex symbol
    symbolList = ["faSquare", "faCircle", "faStar"]
    if (id in symbolList):
        return id
    return None
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def safeLatexSizeFromUserString(sizeStr, astloc):
    # raise exception if base
    pattern = r'^-?\d+(\.\d+)?(e[-+]?\d+)?\s*(in|cm|mm|pt|em)$'
    if bool(re.match(pattern, sizeStr)):
        return sizeStr
    raise makeJriException("Size parameter not understood ({}).".format(sizeStr), astloc)
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def preventWordWrapOnLeadIdHypenLatex(latex):
    latex = latex.replace(r"{-}", r"\mbox{-}")
    return latex
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def resultTextOrFollowCase(text, optionFollowCase, optionUseBulletIfEmptyLine, astloc, entryp, leadp):
    if (not optionFollowCase):
        return text

    # assemble result
    results = JrAstResultList()
    #
    optionUseBulletIfEmptyLine = False
    results.flatAdd(CbDeferredBlockFollowCase(astloc, entryp, leadp, text, optionUseBulletIfEmptyLine, True, True))

    return results
#---------------------------------------------------------------------------




#---------------------------------------------------------------------------
def irpWhenText(when):
    text1 = None
    text2 = None
    if (when is not None):
        if (isinstance(when, str)):
            if (when=="morning"):
                text1 = _("tomorrow morning")
                text2 = _("at the start of your next day")
            else:
                text1 = when
        else:
            if (when==0):
                text1 = _("now")
            else:
                text1 = _("in {} hours").format(when)
    else:
        # no when info
        pass
    return [text1, text2]
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def generateLatexRuleThenLineBreak():
    return r"\hrulefill" + "\n\n"


def generatelatexLineBreak2():
    return "\n\n~\n\n"
#---------------------------------------------------------------------------







#---------------------------------------------------------------------------
# see also addToResultsAsQuestion()
def buildFormElementTextLatex(typeStr, sizeVal, choices):
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
    
    return [text, latex]
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
def generateFormTextLatex(lines, widthStr, pt):
    safeWidthStr = convertStringToSafeLatexSize(widthStr, r"\columnwidth", r"\columnwidth", r"0.90\columnwidth", 0.90)
    #
    latex = "\\nopagebreak"
    for i in range(0,lines):
        latex += "\\cbFormIndent\\cbFormLine{" + safeWidthStr + "}" + "{" + str(pt) + "pt}\n\n"
    latex += generatelatexLineBreak2()
    return latex
#---------------------------------------------------------------------------

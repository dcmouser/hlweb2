# jr ast helpers
from .jrastfuncs import getUnsafeDictValueAsString, makeLatexLinkToRid, vouchForLatexString, DefContdStr, DefInlineLeadPlaceHolder, convertEscapeUnsafePlainTextToLatex

from .jriexception import *




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



def parseTagListArg(idStr, idStrDefault, env, astloc, leadp):
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
            raise makeJriException("Unknown tag ({})".format(id), astloc)
        # add it to list of tags
        tagList.append(tag)

    return tagList
#---------------------------------------------------------------------------




















#---------------------------------------------------------------------------
def buildLatexMarkCheckboxSentence(word, count, flagPeriod, flagAddCheckbox = False, latexFontColor = None):
    countLatex = wrapTextInBold(str(count))
    latex = "Mark {} {} checkbox{} in your case log".format(countLatex, word, jrfuncs.plurals(count,"es"))
    if (flagPeriod):
        latex += "."
    if (flagAddCheckbox):
        latex = generateLatexForSymbol("checkbox", None, None) + latex
    if (latexFontColor is not None):
        latex = wrapLatexInColor(latex, latexFontColor)
    return latex




def generateLatexBoxDict(style, extras):
    if (style == True):
        style = "default"
    #

    # alignment (messy i know)
    alignmentStyle = jrfuncs.getDictValueOrDefault(extras, "alignment", "center")
    alignmentDict = {
        "none": {"envStart": "", "envEnd": "", "envCont": "", "envCont2": ""},
        "center": {"envStart": r"\begin{center}", "envEnd": r"\end{center}", "envCont": r"\centering", "envCont2": r"\center"},
        "right": {"envStart": r"\begin{flushright}", "envEnd": r"\end{flushright}", "envCont": r"\raggedleft", "envCont2": r"\raggedleft"},
        "left": {"envStart": r"\begin{flushleft}", "envEnd": r"\end{flushleft}", "envCont": r"\raggedright", "envCont2": r"\raggedright"},
    }
    alignmentEnvStart = alignmentDict[alignmentStyle]["envStart"]
    alignmentEnvEnd = alignmentDict[alignmentStyle]["envEnd"]
    alignmentCont = alignmentDict[alignmentStyle]["envCont"]
    # do we really need this or could we use \centering alignmentCont?
    alignmentCont2 = alignmentDict[alignmentStyle]["envCont"]

    #
    latexDict = {
        # hours of experimenting to get this to center correctly and not add extra vertical space, etc.
        "default": {"start": "\n" + r"{\par" + alignmentCont + r"\lfbox[border-radius=5pt, padding=8pt, margin-top=4pt, margin-bottom=2pt]{\begin{minipage}[c]{.95\columnwidth}" + "\n", "end": r"\end{minipage}}\par}" + "\n\n"},
        "rounded": {"start": "\n" + r"{\par" + alignmentCont + r"\lfbox[border-radius=5pt, padding=8pt, margin-top=4pt, margin-bottom=2pt]{\begin{minipage}[c]{.95\columnwidth}" + "\n", "end": r"\end{minipage}}\par}" + "\n\n"},
        "shadow": {"start": r"\setlength{\fboxsep}{2em} " + alignmentEnvStart + r"\shadowbox{\begin{minipage}[c]{.80\columnwidth}" + "\n", "end": r"\end{minipage}}" + alignmentEnvEnd + "\n\n"},
        "report": {"start": "\n" + r"{\par" + alignmentCont + r"\lfbox[border-style=dotted, border-color=red, border-width=1.5pt, padding=8pt, margin-top=4pt, margin-bottom=2pt]{\begin{minipage}[c]{.95\columnwidth}" + "\n", "end": r"\end{minipage}}\par}" + "\n\n"},
        "hLines": {"start": "\n" + r"{\par" + alignmentCont + r"\lfbox[padding=0em, margin=0em, border-left-width=0pt, border-right-width=0pt, border-top-width=1pt, border-bottom-width=1pt]{\begin{minipage}[c]{.90\columnwidth}\vspace*{1.1em}" + "\n", "end": r"\vspace*{1em}\end{minipage}}\par}" + "\n\n"},
        "hLinesCenter": {"start": "\n" + r"{\par" + alignmentCont + r"\lfbox[padding=1em, margin=1em, border-left-width=0pt, border-right-width=0pt, border-top-width=1pt, border-bottom-width=1pt]{\begin{minipage}[c]{.75\columnwidth}\vspace*{.2in}" + alignmentCont2 + "\n", "end": r"\vspace*{.2in}\end{minipage}}\par}" + "\n\n"},
        "imageBorder": {"startFunc": lambda extras: "\n" + r"\tcbox[sharp corners, size=tight, boxsep=" + str(extras["padding"]) + "pt, boxrule=" + str(extras["borderWidth"]) + "pt]{", "end": r"}" + "\n\n"},

    }
    # symbol
    if (style not in latexDict):
        raise Exception("Runtime Error: Box style '{}' not known; should be from: {}.".format(id, latexDict.keys()))

    return latexDict[style]





def wrapTextInLatexBox(boxStyle, text, flagIsUnsafeText, symbolName=None, latexFontColor=None, extras = None):
    if (text==""):
        return ""
    
    # start box
    latexBoxDict = generateLatexBoxDict(boxStyle, extras)
    if ("startFunc" in latexBoxDict):
        latex = latexBoxDict["startFunc"](extras)
    else:
        latex = latexBoxDict["start"]

    # optional color
    if (latexFontColor is not None):
        latex += generateLatexFontColor(latexFontColor)
    # optional symbol
    if (symbolName is not None) and (symbolName!=""):
        latex += generateLatexForSymbol(symbolName, None, None)
    # main text
    if (flagIsUnsafeText):
        latex += convertEscapeUnsafePlainTextToLatex(text)
    else:
        latex += text

    # end box
    if ("endFunc" in latexBoxDict):
        latex += latexBoxDict["endFunc"](extras)
    else:
        latex += latexBoxDict["end"]

    return latex













def generateLatexForSymbol(symbolName, color, size):
    symbolDictLatex = {
        "checkbox": r"{\Large \faCheckSquare[regular]}",
        "clock": r"\raisebox{-4.1pt}\VarTaschenuhr",
        "document": r"{\Large \faCameraRetro}",
        "exclamation": r"{\Large \faExclamationCircle}",
        "stop": r"{\Huge \faExclamationTriangle}",
        "hand": r"{\Large \faHandPointRight[regular]}",
        "choice": r"{\Large \faBalanceScale}",
        "culture": r"{\Large \faTheaterMasks}",
        "radio": r"{\Large \faVolumeUp}",
        "markerTag": r"\raisebox{-3.3pt}{\Large \faTag}",
        "markerDoc": r"\raisebox{-2.0pt}{\Large \faCameraRetro}",
        "markerGeneric" : r"{\Large \faTags}",
        "hand": r"\raisebox{-2.0pt}{\Large \faHandPointRight[regular]}",
        #"calendar": r"{\faCalendar}",
        "calendar": r"{\faCalendar*[regular]}",
        "report": r"{\faFlask}"
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
    latex += r"\hspace{0.1cm}"

    # color
    if (color is None) and (symbolName in symbolDictDefaultColors):
        color = symbolDictDefaultColors[symbolName]
    #
    if (color is not None):
        latex = wrapLatexInColor(latex, color)

    # size
    # ATTN: TODO

    return latex



def generateLatexForSeparator(id):
    if (id is None):
        id = "default"
    latexDict = {
        "default": r"\begin{center}{\pgfornament[anchor=center,ydelta=0pt,width=2cm]{80}}\end{center}%" + "\n",
        "final": r"\begin{center}{\pgfornament[anchor=center,ydelta=0pt,width=2cm]{80}}\end{center}%" + "\n",
        "lead": r"\begin{center}{\pgfornament[anchor=center,ydelta=0pt,width=3cm]{84}}\end{center}%" + "\n",
    }

    # symbol
    if (id in latexDict):
        latex = latexDict[id]
    else:
        raise Exception("Runtime Error: Style '{}' not known; should be from: {}.".format(id, latexDict.keys()))
    
    return latex



def generateLatexFontColor(latexFontColor):
    latex = r"\color{" + latexFontColor + "}"
    return latex

def wrapLatexInColor(latex, latexFontColor):
    return r"{" + generateLatexFontColor(latexFontColor) + latex + r"}"

def wrapTextInBold(text):
    return r"\textbf{" + text + r"}"


def generateLatexLineBreak():
    return r"\hrulefill" + "\n\n"


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



def wrapLatexInBulletList(latex):
    latex = ""
    return latex


def generateImageEmbedLatex(imageFullPath, widthStr, heightStr, borderWidth, padding, flagCenter, optionValign):
    # fix path
    imageFullPath = imageFullPath.replace("\\","/")
    #
    extra = ""
    if (heightStr==""):
        heightStr = None
    if (widthStr==""):
        widthStr = None
    #
    safeHeightStr = None
    safeWidthStr = None
    if (heightStr is not None) and (widthStr is not None):
        safeHeightStr = convertEscapeUnsafePlainTextToLatex(heightStr)
        safeWidthStr = convertEscapeUnsafePlainTextToLatex(heightStr)
        extra += "width={}, height={}".format(safeWidthStr, safeHeightStr)
    elif (heightStr is not None):
        safeHeightStr = convertEscapeUnsafePlainTextToLatex(heightStr)
        extra += "width={}, height={}".format("\\columnwidth", safeHeightStr)
    elif (widthStr is not None):
        safeWidthStr = convertEscapeUnsafePlainTextToLatex(widthStr)
        extra += "width={}, height={}".format(safeWidthStr, "\\textheight")
    else:
        extra += "width={}, height={}".format("\\columnwidth","\\textheight")
    #
    if (extra != ""):
        extra += ",keepaspectratio"

    # new to fix placing in tables
    if (optionValign is not None) and (optionValign!=""):
        if (extra !=""):
            extra +=","
        extra += "valign=" + optionValign

    if (extra != ""):
        extra = "[" + extra + "]"
    #
    latex = "\\includegraphics{}{{{}}} ".format(extra, imageFullPath)
    if (borderWidth>0):
        # wrap in box
        # note that this BREAKS nice table cell alignment with images so it must be turned off when embedding in table
        extras = {"borderWidth": borderWidth, "padding": padding}
        latex = wrapTextInLatexBox("imageBorder", latex, False, None, None, extras)
    if (flagCenter):
        latex = "\\begin{center}" + latex + "\\end{center}"
    return latex




def generateImageSizeLatex(imageFullPath):
    # fix path
    imageFullPath = imageFullPath.replace("\\","/")
    #
    extra = ""
    latex = r"\sbox0{" + "\\includegraphics{}{{{}}} ".format(extra, imageFullPath) + r"}"
    latex += r"Dimentions: \uselengthunit{in}\printlength{\wd0} x \uselengthunit{in}\printlength{\ht0}"

    return latex
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



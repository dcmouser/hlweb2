from .cbrender import CbRenderDoc, CbRenderSection, CbRenderLead, outChunkManager

# ast
from .jrastvals import AstValString, AstValNull
from .jrast import ResultAtomLatex, ResultAtomMarkdownString, ResultAtomPlainString, ResultAtomNote
from .jrastfuncs import getUnsafeDictValueAsString, getUnsafeDictValueAsNumber, convertEscapeUnsafePlainTextToLatex, makeLatexLabelFromRid, isTextLatexVouched, isTextLatexVouchedEmbeddable, removeLatexVouch, convertEscapeVouchedOrUnsafePlainTextToLatex, makeLatexLinkToRid, DefContdStr, vouchForLatexString, convertIdToSafeLatexId
#
from .cbdeferblock import CbDeferredBlock, CbDef_SkipNextNewline, CbDeferredBlockPotentialEndLeadTime
#
from .cbfuncs_core_support import wrapInLatexBox, makeLatexSafeFilePath, calcLatexSizeKeywordFromBaseAndMod, parseFontSizeStringToLatexCommand, calculateLatexForItemTimeBoxStyle, calculateLatexForItemTimeHeaderStyle
from .cbfuncs_core_support import makeLatexReferenceToLeadById, makeLatexReferenceToLead
from .casebookDefines import *

# translation
from .cblocale import _

# my libs
from lib.jr import jrfuncs
from lib.jr.jrfuncs import jrprint
from .jriexception import *

# markdown
from lib.jrmistle.hlmarkdown import HlMarkdown

# pylatex
import pylatex
import re

#
from lib.jr import jrpdf

# python modules
import os




# enable this to add section breaks in other places other than lead start and end
DefExtraBreakWarnSecEnd = False
DefBreakWarnSecMethod = "varset"















# derived render doc for latex stuff

class CblRenderDoc(CbRenderDoc):
    def __init__(self, jrinterp):
        super().__init__(jrinterp)
        #
        self.chunks = outChunkManager()
        self.setCurrentColumnCount(1)
        self.setLastEntryHadPageBreakAfter(True)
        #
        # markdown helper
        self.hlMarkdown = HlMarkdown(self)
        markdownOptions = {
            "forceLinebreaks": True,
            #"autoStyleQuotes": False
        }
        self.hlMarkdown.setOptions(markdownOptions)
        #
        # pdf helper
        self.jrp = jrpdf.JrPdf()
        #
        #self.tocTopLabels = []
        #
        # font support
        self.latexAdds = []
        self.fontDictionary = {}
        # default font
        self.fontDictionary["default"] = {"command": "\\normalfont", "size": "normal", "scale": 1.0, "color": None}
        #
        # predefined dividers, defined in latex)
        self.dividers = {}
        self.setDividerCommand("lead","cbDividerlead")
        self.setDividerCommand("default","cbDividerdefault")
        self.setDividerCommand("day","cbDividerday")
        self.setDividerCommand("final","cbDividerfinal")
        self.setDividerCommand("circle","cbDividercircle")
        self.setDividerCommand("square","cbDividersquare")
        self.setDividerCommand("otherwise","cbDividerotherwise")


    def setCurrentColumnCount(self, val):
        self.currentColumnCount = val
    def getCurrentColumnCount(self):
        return self.currentColumnCount
    
    def getLastEntryHadPageBreakAfter(self):
        return self.lastEntryHadPageBreakAfter
    def setLastEntryHadPageBreakAfter(self, val):
        self.lastEntryHadPageBreakAfter = val




    def printDebug(self, env):
        # internals
        jrprint("Debug rendering from CbRenderDoc ({} sections):".format(len(self.children)))
        for section in self.children.getList():
            section.printDebug(env)




    def renderToPdf(self, suffixedOutputPath, suffixedBaseFileName, flagDebug, renderSectionName):
        # latex
        env = self.getEnvironment()
        #jrprint("Generating Latex...")
        documentText = self.renderDocText(env, renderSectionName)
        # run it
        [retv, fileList] = self.saveLatexGeneratePdf(documentText, suffixedOutputPath, suffixedBaseFileName, flagDebug)
        return [retv, fileList]




    def saveLatexGeneratePdf(self, documentText, suffixedOutputPath, suffixedBaseFileName, flagDebug):
        fileList = []
        filePathMain = suffixedOutputPath + "/" + suffixedBaseFileName
        filePath = filePathMain + ".latex"
        expectedPdfFilePath = filePathMain + ".pdf"
        expectedLogFilePath = filePathMain + ".log"
        #
        if (flagDebug):
            jrprint("Saving generated latex to file \"{}\".".format(filePath))
        #
        jrfuncs.saveTxtToFile(filePath, documentText, "utf-8")
        #
        #
        success = self.generatePdf(filePath, flagDebug)
        #
        # build list of created files
        pdfExists = jrfuncs.pathExists(expectedPdfFilePath)
        if (jrfuncs.pathExists(filePath)):
            fileList.append(filePath)
        if (jrfuncs.pathExists(expectedPdfFilePath)):
            fileList.append(expectedPdfFilePath)
        if (jrfuncs.pathExists(expectedLogFilePath)):
            fileList.append(expectedLogFilePath)
        #
        success = (success and pdfExists)
        return [success, fileList]




    def generatePdf(self, filePath, flagDebug):
        # pass through render options
        if (flagDebug):
            jrprint("Generating pdf from latex..")
        #
        self.jrp.setRenderOptions(self.options)
        cleanExtras = self.getOption("cleanExtras", False)
        #
        retv = self.jrp.generatePdflatex(filePath, flagDebug, cleanExtras)

        return retv

 






    def convertMarkdownOrVouchedTextToLatex(self, text, flagProtectStartingSpace, flagConvertNewlinesToLatexSpecialNewline):
        if ("ATTN FUCK OFF" in text):
            jrprint("DEBUG BREAK")
        if (isTextLatexVouched(text)):
            # do NOT markdown strings that are vouched latex
            latexText = removeLatexVouch(text)
            return latexText
        return self.convertMarkdownToLatexDontVouch(text, flagProtectStartingSpace, flagConvertNewlinesToLatexSpecialNewline)


    def convertMarkdownToLatexDontVouch(self, text, flagProtectStartingSpace, flagConvertNewlinesToLatexSpecialNewline):
        # convert to latex using mistletoe library
        [latexText, extras] = self.hlMarkdown.renderMarkdown(text, "latex", True)
        if (flagProtectStartingSpace) and (len(latexText)>0) and (latexText[0]==" "):
            latexText = "~" + latexText[1:]

        if (flagConvertNewlinesToLatexSpecialNewline):
            # this is useful when we are passing text to a function
            #latexText = latexText.replace("\n", "\\newline ")
            latexText = latexText.replace("\n", " \\\\ ")

        return latexText
    

    def convertMarkdownToLatexDontVouchDoEscapeNewlines(self, text, flagProtectStartingSpace, flagRunUserEscapes, flagRemoveDoubleLineBreaks):
        # this has use replacing newlines but not doubling them as normal
        # this will be false if its already run
        if (flagRunUserEscapes):
            text = jrfuncs.expandUserEscapeChars(text)
        # THIS IS EVIL KLUDGE - the problem is that when we have a newline and convert to markdown, it DOUBLES the newlines, but in this context we dont want double
        latexText = self.convertMarkdownToLatexDontVouch(text, flagProtectStartingSpace, True)
        # now UNDO double newlines.. kludgey ugly i know
        if (flagRemoveDoubleLineBreaks):
            #latexText = latexText.replace("\\newline \\newline", "\\newline")
            latexText = latexText.replace(" \\\\  \\\\ ", " \\\\ ")
        else:
            latexText = latexText.replace(" \\\\  \\\\ ", " \\\\~\\\\ ")

        # clean up line break spaces
        latexText = latexText.replace(" \\\\ ", "\\\\")

        return latexText



    # rendering code taken from hlparser start by searching for "def renderLeads(...)"

    def renderMarkdownToLatex_UNUSEDWTF(self, markdownStr):
        # convert markdown to latex
        return str
    
    def buildPdfFromLatex_UNUSEDWTF(self, latexStr, outFilePath):
        # build a pdf from a latex str
        return False












    def afterTaskRenderRunProcess(self, task, rmode, env):
        # CODE RUN AFTER a TASK RENDERRUN

        # merge inline pending leads
        self.mergeQueuedInlineLeadToRenderSectionWithId(env, self.getMainLeadsSectionName())

        # now impose and OVERWRITE any task-set options onto sections
        self.imposeTaskOptionsOnSections(env)

        # any generic post rendering steps?
        # walk leads, do any final steps (for example this adds deferred time blocks to leads)
        leadList = self.calcFlatLeadList(False)
        for lead in leadList:
            self.postProcessLeadRenderRun(lead, task, rmode, env)

        # debug author report generation?
        reportMode = task.getReportMode()
        if (reportMode):
            # ATTN: 11/14/24 this is not helping
            # we need mind manager nodes for reports? 
            if (False):
                interp = self.getInterp()
                interp.mindManager.buildAndResolveNodesAndLinks(env)
            # build reports
            self.generateReportSections(env, self.getReportSectionName())
        else:
            self.hideReportSections(env, self.getReportSectionName())

        # sort entries
        self.sort()





    def imposeTaskOptionsOnSections(self, env):
        # there are options that the user can configure in their casebook file, which we can OVERWRITE in task options
        leadSection = self.getMainLeadsSection()
        #
        sectionBreak = self.getOption("sectionBreak", None)
        sectionColumns = self.getOption("sectionColumns", None)
        leadBreak = self.getOption("leadBreak", None)
        leadColumns = self.getOption("leadColumns", None)
        #
        if (sectionBreak is not None):
            leadSection.setSectionBreak(sectionBreak)
        if (sectionColumns is not None):
            leadSection.setSectionColumns(sectionColumns)
        if (leadBreak is not None):
            leadSection.setLeadBreak(leadBreak)
        if (leadColumns is not None):
            leadSection.setLeadColumns(leadColumns)


    def postProcessLeadRenderRun(self, lead, task, run, env):
        # executed after building all leads

        endTimeBlock = CbDeferredBlockPotentialEndLeadTime(None, None, self)
        lead.addBlocks(endTimeBlock)


























    def renderDocText(self, env, renderSectionName):
        # render entire document
        # NOTE: This function is called AFTER the structure of the render is built (CbRenderLead and CbRenderSection, etc.)
        # so it's job is NOT to generate the basic contents of leads, but rather to ASSEMBLE them and create final latex
        # for code that generates the main structure, see taskRenderRun()

        self.chunks.clear()

        # start stuff
        self.generateDocumentStart(env)

        if (renderSectionName is not None):
            renderSection = self.findRenderSectionById(renderSectionName)
            if (renderSection is None):
                raise makeJriException("In renderDocText, could not find render section '{}'.".format(renderSectionName), self)
            self.renderItem(env, renderSection, None)
        else:
            # walk all sections and generate latex text
            self.renderChildren(env, self.children, None)

        # turn off any multicol by reverting to single column default
        self.addChunkToSetCurrentColumnCountTo(1)

        # end stuff
        self.generateDocumentEnd(env)

        # return it
        documentText = self.assembleText()
        return documentText


    def assembleText(self):
        text = ""
        for chunk in self.chunks.getList():
            text += chunk
        return text




    def renderChildren(self, env, children, parentSection):
        for child in children.getList():
            self.renderItem(env, child, parentSection)
















    def renderItem(self, env, item, parentSection):
        optionSkipDebugText = True
        optionExceptionOnNullBlockRender = False
        #

        # items can be marked as not to be rendered
        visible = item.getVisibility()
        if (not visible):
            return
        
        # start
        allLatexText = ""

        # add any start layouts
        allLatexText += self.layoutsLatex(env, item, True)

        # generate header text toc, etc.
        # NEW: we have the option to defer this until later
        if (item.getAutoHeaderRender()):
            allLatexText += self.calcHeaderLatexForLead(env, item, parentSection, False)
        else:
            allLatexText += ""

        isLead = isinstance(item, CbRenderLead)
        if (isLead):
            useDividers = item.calcLeadDividers()
        else:
            useDividers = False

        # new "continued on next page" stuff
        flagCloseBreakwarnsec = False
        addBreakWarn = False

        if (item.getNeedsPageBreakWarning(env)):
            addBreakWarn = True
        elif (isLead):
            # whenever we use Dividers, add latex to show a Continued on next page footer if its is continues onto the next page
            if (useDividers):
                addBreakWarn = True
        else:
            # new try, if NOT a lead then always do a break
            addBreakWarn = True

        if (addBreakWarn):
            allLatexText += self.breakWarnSecStart()
            flagCloseBreakwarnsec = True

        # new compact time option
        optionTimeStyle = self.getOptionTimeStyle()

        # TIME LATEX to be added later
        # we only show time IF: this case is configured to use a clock AND we are in the proper LEADS section AND this is a "lead" (as opposed to a section) AND time!=0
        # if time = none then we use DEFAULT time, otherwise we use a multiple of clock ticks
        if ((optionTimeStyle=="box") or (optionTimeStyle is None)):
            timeLatex = self.calculateItemTimeLatexBoxStyle(env, item, parentSection)
            itemTimePos = item.getTimePos()
            if (timeLatex is not None) and (itemTimePos=="start"):
                # TIME at start
                allLatexText += timeLatex

        # item text contents
        resultList = item.blockList.getList()
        if (resultList is None):
            contents = []
        else:
            contents = resultList.getContents()

        # we accumulate contiguous markdown/plain text before we try to convert to markdown, since we need to know about linebreaks between them.
        latexBlocks = []
        markdownText = ""
        for index, block in enumerate(contents):
            if (isinstance(block, CbDeferredBlock)):
                # deferred render chunk gets handled first
                if (index==len(contents)-1):
                    nextBlock = None
                else:
                    # let's try to peek at subsequent block to pass to deferred item
                    nextBlock = contents[index+1]
                [block, newPriorMarkdownText, newNextBlock] = block.renderToLatexString(env, self, item, parentSection, markdownText, nextBlock)
                # change prior and subsequent if specified
                if (newPriorMarkdownText is not None):
                    markdownText = newPriorMarkdownText
                if (nextBlock is not None) and (newNextBlock is not None) and (newNextBlock != nextBlock):
                    # replace next block
                    contents[index+1] = newNextBlock
                # now 'block' is assigned the RESULT of deferred output, where it is handled below
                # drop down
            #
            if (isinstance(block, str)):
                text = block
            elif (isinstance(block, AstValString)):
                text = block.getUnWrappedExpect(AstValString)
            elif (isinstance(block, ResultAtomNote) or isinstance(block, ResultAtomMarkdownString)):
                # just plain text (or blank)
                text = str(block)
            elif (isinstance(block, ResultAtomLatex)):
                # temporary workaround
                text = vouchForLatexString(str(block), block.getIsLatexEmbeddable())
            elif (isinstance(block, AstValNull)):
                continue
            elif (block is None):
                jrprint("RENDER WARNING: Null block in render.")
                if (optionExceptionOnNullBlockRender):
                    raise Exception ("Internal Runtime error: Null block in render.")
                else:
                    continue
            else:
                # UNKNOWN WARNING/ERROR
                jrprint("RENDER WARNING: UNKNOWN RESULT BLOCK IN RENDER CONTENTS: {}".format(type(block)))
                continue

            # skip if it starts with "DEBUG:"
            if (optionSkipDebugText) and (text.startswith("DEBUG:")):
                continue

            # convert to markdown IFF appropriate
            if (isTextLatexVouched(text)):
                # there are TWO options here for combining some latex with mardown -- we can EITHER embed the latex as if it were a word that could be wrapped in markdown tags
                # OR we can FORCE markdown to complete before appending the latex
                isLatexEmbeddable = isTextLatexVouchedEmbeddable(text)
                if (isLatexEmbeddable):
                    # we EMBED this latex into the markdown where we will unpack it later; in this way it can be put inside markdown annotations; this can be use for word and phrase-like latex short snipped
                    markdownText += self.embedTempLatexBlockRef(len(latexBlocks))
                    latexBlockText = self.convertMarkdownOrVouchedTextToLatex(text, False, False)
                    latexBlocks.append(latexBlockText)
                else:
                    # we force markdown to complete then add latex; this should be used for sections of latex that need to be self containted and cannot be INSIDE the middle of a markdown thing
                    if (markdownText!=""):
                        markdownTextAsLatex = self.convertMarkdownOrVouchedTextToLatex(markdownText, False, False)
                        # ok now we need to REPLACE the blocks
                        markdownTextAsLatex = self.unembedTempLatexBlockRefs(markdownTextAsLatex, latexBlocks)
                        allLatexText += markdownTextAsLatex
                        markdownText = ""
                    # add latex
                    allLatexText += self.convertMarkdownOrVouchedTextToLatex(text, False, False)
            else:
                # accumulate markdown text into one big block
                markdownText += text

        # pending markdown
        if (markdownText!=""):
            markdownTextAsLatex = self.convertMarkdownOrVouchedTextToLatex(markdownText, False, False)

            # ok now we need to REPLACE the blocks
            markdownTextAsLatex = self.unembedTempLatexBlockRefs(markdownTextAsLatex, latexBlocks)

            allLatexText += markdownTextAsLatex
            markdownText = ""



        # add any end layouts
        allLatexText += self.layoutsLatex(env, item, False)


        # now we have the entire text
        # strip it
        allLatexText = allLatexText.strip()

        # contents break beforehand (note this runs even if our "contents" are blank)
        self.addChunkForBreakBefore(item, parentSection)

        if (allLatexText!=""):
            # contents columns
            self.addChunkToSetCurrentColumnCount(item, parentSection)

            # contents text
            self.chunks.append(allLatexText)

            # add linebreak since we stripped text of end linebreaks
            self.chunks.append("\n")


        # add Dividers if its a lead (as opposed to a section)
        if (isLead):
            # if we have an explicit Dividers value use it
            if (useDividers):
                # ATTN: new add a nopagebreak for Divider so it doesnt end up alone
                text = "\\nopagebreak" + self.hlMarkdown.latexDivider()
                self.chunks.append(text)

        # close any "continued on next page stuff that we started"
        if (flagCloseBreakwarnsec): 
            self.chunks.append(self.breakWarnSecEnd())
            flagCloseBreakwarnsec = False

        # contents break after (note this runs even if our "contents" are blank)
        self.addChunkForBreakAfter(item, parentSection)

        # now recursively walk all children
        if (hasattr(item, "children")):
            self.renderChildren(env, item.children, item)















    def layoutsLatex(self, env, item, flagBeginVsEnd):
        layoutNames = ["minMargins", "tight", "tightNarrowMargins", "tightWideMargins"]

        layout = item.getLayout()
        if (layout is None):
            # should we set layout based on heading style?
            headingStyle = item.calcResolvedHeadingStyle()
            if (headingStyle == "footer"):
                # use a dynamic tight margin which is based on paper size
                layout = "tight"
                # drop down
            else:
                return ""

        latex = ""
        layouts = layout.split("|")
        for layout in layouts:
            if (layout not in layoutNames):
                raise Exception("unknown layout name '{}'.".format(layout))
            if (layout == "tight"):
                # use a dynamic tight margin which is based on paper size
                if (self.isNarrowPaperSize()):
                    layout = "tightNarrowMargins"
                else:
                    layout = "tightWideMargins"
            #
            layout = jrfuncs.uppercaseFirstLetter(layout.strip())
            #
            if (flagBeginVsEnd):
                placeStr = "Begin"
            else:
                placeStr = "End"
            latex += "\\mylayout" + layout + placeStr + "\n"
        return latex







    def calcHeaderLatexForLead(self, env, item, parentSection, flagEmbeddingMidPage):
        # build the header subheading etc text for lead
        optionMaxLevel = 3
        level = item.getLevel()

        # item TITLE/LABEL
        titleOrig = item.calcDisplayTitle()
        # set toc, possibly based on title
        toc = item.getToc()
        if (toc is None):
            toc = titleOrig
        # title
        title = titleOrig
        # heading, which will replace title
        heading = item.getHeading()
        if (heading is not None):
            title = heading
        # id
        itemId = item.getId()
        #
        allLatexText = ""
        tocLatex = ""
        #
        entry = item.getEntry()

        # for debug stuff
        reportMode = env.getReportMode()
        if (reportMode):
            subheading = None
            if (toc!="") and (toc is not None):
                if (itemId is not None) and (itemId!="") and (not itemId in toc) and (not itemId in ["FRONT","REPORT"]):
                    # ADD itemid to toc
                    toc = toc + " [" + itemId + "]"
                    if ("inline" in itemId):
                        # add subheading also
                        subheading = item.getSubHeading()
                        if (subheading is not None) and (subheading!="") and (not subheading in toc):
                            toc = toc + " - "+ subheading
                else:
                    subheading = item.getSubHeading()
                    if (subheading is not None) and (subheading!="") and (not subheading in toc):
                        toc = toc + " - "+ subheading

            # add dName from hlapi if there is no custom label
            if (subheading is None) and ((item.label is None) or (item.label=="") or (item.id==item.label)):
                dName = item.getDName()
                if (dName is not None) and (not dName.lower() in toc.lower()) and (toc is not None) and (toc!=""):
                    toc += " (" + dName + ")"


            # kludge replace to remove stuff we don't nee
            if (toc is not None):
                toc = toc.replace(DefInlineLeadPlaceHolder, "")
            #
            # add item id to title when its an autoid lead
            if (title!="") and (itemId is not None) and (itemId!="") and (not itemId in title) and (not itemId in ["FRONT","REPORT"]):
                title = title + " [" + itemId +"]"

        if (title is not None):
            titleLatex = convertEscapeVouchedOrUnsafePlainTextToLatex(title)
        if (toc is not None) and (toc!=""):
            tocLatex = convertEscapeVouchedOrUnsafePlainTextToLatex(toc)

        # modifying section font details
        komaHeaderModifier = None
        #headingsWrap = False
        #headingsWrapText = ""
        headingShowNormal = True
        headingShowCompact = False
        headingCompactText = ""
        headingStyle = item.calcResolvedHeadingStyle()
        if (headingStyle is not None):
            if (headingStyle=="huge"):
                komaHeaderModifier = r"{\myHugeHeaderFontSelect}"
            elif (headingStyle=="large"):
                komaHeaderModifier = r"{\myLargeHeaderFontSelect}"
            elif (headingStyle=="smell"):
                komaHeaderModifier = r"{\mySmallHeaderFontSelect}"
            elif (headingStyle in ["header", "footer"]):
                headingShowNormal = False
                headingShowCompact = True
            elif (headingStyle in ["alsoFooter"]):
                headingShowCompact = True
            else:
                raise makeJriException("Unknown headingStyle: {}.".format(headingStyle), entry.getSourceLoc())

        # some items may want to disable their heading and toc entry
        blankHead = item.getBlankHead()
        hasTitle = (title is not None) and (title!="")

        isLead = isinstance(item, CbRenderLead)


        # TOC and title lines
        showingTitle = False
        if (not blankHead):
            showingTitle = True
            # the TOC entry
            ltext = ""

            # insist on a certain amount of space
            ltext += r"\myNeedSpaceEntry"

            if (level==1):
                if (hasTitle):
                    chapterLine = "\\chapter*{{{}}}".format(titleLatex)
                    if (flagEmbeddingMidPage):
                        # kludge to not force a page break at start of chapter
                        chapterLine = r"\myKludgeForMidPageHeader{" + chapterLine + "}" + "\n\n"
                    ltext += "\n" + self.wrapInKomaSectionModifierIfNeeded("chapter", komaHeaderModifier, chapterLine + "\n\n")
                if (toc is not None) and (toc!=""):
                    if (not hasTitle):
                        ltext += "\\phantomsection\n"
                    ltext += r"\addcontentsline{toc}{chapter}{~~" + tocLatex + "}\n"
            elif (level==2):
                if (hasTitle):
                    headingCompactText += titleLatex
                    if (headingShowNormal):
                        ltext += "\n" + self.wrapInKomaSectionModifierIfNeeded("section", komaHeaderModifier, "\\section*{{{}}}%\n\n".format(titleLatex))
                if (toc is not None) and (toc!=""):
                    if (not hasTitle):
                        ltext += "\\phantomsection\n"
                    if (tocLatex=="") or (toc==""):
                        jrprint("ATTN: DEBUG BREAK")
                    ltext += r"\addcontentsline{toc}{section}{~~" + tocLatex + "}\n"
            elif (level==3) and (optionMaxLevel>=3):
                if (hasTitle):
                    ltext += "\n" + self.wrapInKomaSectionModifierIfNeeded("subsection", komaHeaderModifier, "\\subsection*{{{}}}%\n\n".format(titleLatex))
                if (toc is not None) and (toc!=""):
                    if (not hasTitle):
                        ltext += "\\phantomsection\n"
                    ltext += r"\addcontentsline{toc}{subsection}{~~" + tocLatex + "}\n"
            elif (level==4) and (isLead):
                if (hasTitle):
                    ltext += "\n" + self.wrapInKomaSectionModifierIfNeeded("subsection", komaHeaderModifier, "\\subsection*{{{}}}%\n\n".format(titleLatex))
                if (toc is not None) and (toc!=""):
                    if (not hasTitle):
                        ltext += "\\phantomsection\n"
                    ltext += r"\addcontentsline{toc}{subsection}{~~~" + tocLatex + "}\n"
            else:
                # higher level toc headings just get shown bold
                if (hasTitle):
                    ltext += "\\textbf{{{}}}%\n\n".format(titleLatex)

            # the label that is target of hyperlink above in toc
            if (True):
                # new more permissive use of labels
                if ((toc is not None) and (toc!="")):
                    ltext += makeLatexLabelFromRid(item.getRid())
            else:
                if (level <= optionMaxLevel):
                    # add label that can be target of hyperref (needs to be unique?)
                    if ((toc is not None) and (toc!="")):
                        if (level>1):
                            if (True):
                                ltext += makeLatexLabelFromRid(item.getRid())

            # build latex
            allLatexText += ltext


        # subheading
        subheading = item.getSubHeading()
        if (subheading is not None) and (subheading!=""):
            if (showingTitle) and (title is not None) and (subheading in title):
                # no point having a subheading that is SAME as title, so clear subheading
                subheadingLatex = ""
            else:
                subheadingLatex = convertEscapeUnsafePlainTextToLatex(subheading)
        else:
            subheadingLatex = ""


        # add inlinedFromLead info to subheading
        inlinedFromLead = item.getInlinedFromLead()
        if (inlinedFromLead is not None):
            inlinedFromAddLatex = self.calcInlinedFromLatex(subheading, inlinedFromLead)
            if (subheadingLatex==""):
                subheadingLatex = _("From") + " {}".format(inlinedFromAddLatex)
            else:
                repStr = "(" + inlinedFromAddLatex + ")"
                # replace only the first
                subheadingLatex = subheadingLatex.replace(DefInlineLeadPlaceHolder, repStr, 1)

        # add continued from, which is like inlinedFrom but set on non-inline
        continuedFromStr = item.getContinuedFromLead()
        if (continuedFromStr is not None):
            continuedFromLead = self.findLeadByIdPath(continuedFromStr, entry)
            if (continuedFromLead is None):
                failedFindTrace = self.generateIdTreeTrace()
                raise JriException("Could not find lead id specified in 'continued from' ({}); trace = {}.".format(continuedFromStr, item, failedFindTrace), entry.getSourceLoc())
            continedFromLatex = self.calcInlinedFromLatex(subheading, continuedFromLead)
            continedFromLatex = " " + _("from") + " {}".format(continedFromLatex)
            if (subheadingLatex==""):
                subheadingLatex = str(DefContdStr).title() + continedFromLatex
            else:
                subheadingLatex += " (" + str(DefContdStr) + continedFromLatex + ")"

        # document link back to where it is gained from;
        # we can only do this when not in special headingstyle, AND where there is only one place the document could be gained from
        # see if this entry matches a tag name
        tagManager = env.getTagManager()
        tag = tagManager.findTagById(itemId)
        if (tag is not None) and (tag.getIsTagTypeDoc()):
            gainList = tag.getGainList(True)
            if (len(gainList)==1):
                # we can only do this if there is one and only one place where this doc is gained
                gainedLead = gainList[0]
                targetLead = gainedLead["lead"]
                targetLeadId = targetLead.getId()
                #leadRefLatex = makeLatexReferenceToLeadById(entry.getSourceLoc(), entry, item, self, targetLeadId, "full", False)
                leadRefLatex = makeLatexReferenceToLead(targetLead, "label", False)
                if (True):
                    # compact add without a linebreak
                    # we might just skip this on compact since it may be too long
                    fromLatex = _("From") + " " + leadRefLatex
                    if (True):
                        if (subheadingLatex==""):
                            subheadingLatex = fromLatex
                        else:
                            subheadingLatex += ", " + _("from") + " " + leadRefLatex
                else:
                    # add with newline
                    fromLatex = _("From") + " " + leadRefLatex
                    if (subheadingLatex==""):
                        subheadingLatex = fromLatex
                    else:
                        subheadingLatex += r"\par " + fromLatex



        subheadingLatexCompact = subheadingLatex
        if (True):
            # address as part of subheadingLatex
            address = item.calcLeadAddress()
            if (address is not None) and (address !="") and (address!="auto"):
                addressLatexCompact = convertEscapeUnsafePlainTextToLatex(address) + "\n"
                addressLatex = "\\small{{{}}}\n".format(convertEscapeUnsafePlainTextToLatex(address))
                if (subheadingLatex!=""):
                    subheadingLatexCompact += "\\newline" + addressLatexCompact
                    subheadingLatex += "\\newline" + addressLatex
                else:
                    subheadingLatexCompact = addressLatexCompact
                    subheadingLatex = addressLatex

        # SUBHEADING

        # add subheading
        newlineNeeded = False
        subheadingLatex = subheadingLatex.strip()
        if (not blankHead) and (subheadingLatex != ""):
            headingCompactText += " - " + subheadingLatexCompact.replace("\n", " - ")
            if (headingShowNormal):
                ltext = "\\cbsubheading{{{}}}\n".format(subheadingLatex)
                allLatexText += ltext
                newlineNeeded = True

        # NEW, time style in header
        optionTimeStyle = self.getOptionTimeStyle()
        
        # default section time; this is used for deciding whether to color a non-default time
        #defaultTime = self.getOptionDefaultTime()
        if (parentSection is not None):
            defaultTime = parentSection.getTime()
        else:
            defaultTime = None
        
        defaultTimeStyle = self.getOptionDefaultTimeStyle()
        zeroTimeStyle = self.getOptionZeroTimeStyle()
        if (optionTimeStyle=="header"):
            # add it to heading?
            itemTimePos = item.getTimePos()
            if (itemTimePos=="start") or (itemTimePos is None) or (itemTimePos==""):
                ltext = self.calculateItemTimeLatexHeaderStyle(env, item, parentSection, defaultTime, defaultTimeStyle, zeroTimeStyle)
                if (ltext is not None):
                    allLatexText += ltext
                    newlineNeeded = True

        #
        if (newlineNeeded):
            allLatexText += "\n"


        if (True):
            # this is used to show the heading text as part of footer or header, useful when we have full page documents like newspapers, etc.
            lcommand = None
            if (headingStyle in ["footer", "alsoFooter"]):
                lcommand = r"\overlayFootText"
            elif (headingStyle=="header"):
                lcommand = r"\overlayHeadText"
            #
            if (lcommand is not None):
                # add phantom section so links to this page will work right
                lcommand = "\\phantomsection\n" + lcommand
                allLatexText = lcommand + "{" + r"\normalfont " + headingCompactText +"}\n" + allLatexText

        return allLatexText












    # Helper code to generate "Continued on next page" text in footer automatically
    def breakWarnSecStart(self):
        # there are two ways to do this, one to wrap in an environment, which has some consequences in that it may hide stuff we do inside from outer
        # the other ways is to simply set variable directly, which is less prone to complaints
        #return "\n" + "\\begin{breakwarnsec}\n"
        if (DefBreakWarnSecMethod=="varset"):
            return r"\warnpgbrktrue "
        else:
            return r"\refstepcounter{question}\label{question-start-\thequestion}"

    def breakWarnSecEnd(self):
        #return "\n" + "\\end{breakwarnsec}\n"
        if (DefBreakWarnSecMethod=="varset"):
            return r"\warnpgbrkfalse "
        else:
            return r"\label{question-end-\thequestion}"






    def wrapInKomaSectionModifierIfNeeded(self, sectionType, komaHeaderModifier, text):
        if (komaHeaderModifier is None) or (komaHeaderModifier==""):
            return text
        text = r"\begingroup" + r"\addtokomafont{" + sectionType + "}" + komaHeaderModifier + "\n" + text + "\n" + r"\endgroup" + "\n"
        return text




    def calculateItemTimeLatexBoxStyle(self, env, item, parentSection):
        itemTime = self.calculateItemTime(env, item, parentSection)
        return calculateLatexForItemTimeBoxStyle(itemTime)

    def calculateItemTimeLatexHeaderStyle(self, env, item, parentSection, defaultTime, defaultTimeStyle, zeroTimeStyle):
        itemTime = self.calculateItemTime(env, item, parentSection)
        return calculateLatexForItemTimeHeaderStyle(itemTime, defaultTime, defaultTimeStyle, zeroTimeStyle)




    # ATTN: 6/14/25 - this is kludgey and the : around this are important to convince the CbDeferredBlockFollowCase case matching block

    def embedTempLatexBlockRef(self, blockIndex):
        text = ":XYZZYBLOCKREF{}XYZZY:".format(blockIndex)
        return text

    def unembedTempLatexBlockRefs(self, text, latexBlocks):
        blockRefRegex = r":XYZZYBLOCKREF(\d+)XYZZY:"
        text = re.sub(blockRefRegex, lambda m: self.unembedTempLatexBlockRef(m.group(1), latexBlocks), text)
        return text



    def unembedTempLatexBlockRef(self, numberStr, latexBlocks):
        try:
            index = int(numberStr)
            return latexBlocks[index]
        except Exception as e:
            raise makeJriException("INTERNAL RENDER ERROR: Could not replace latex markdown replacement palceholder block #{}".format(numberStr), None)


    def addChunkForBreakBefore(self, item, parentSection):
        breakStyle = self.calcBreakForSectionOrLead(item, parentSection, True)
        retv = self.addChunkForBreakBeforeUsingStyle(breakStyle, True)

    def addChunkForBreakAfter(self, item, parentSection):
        breakStyle = self.calcBreakForSectionOrLead(item, parentSection, False)
        retv = self.addChunkForBreakBeforeUsingStyle(breakStyle, False)
        self.setLastEntryHadPageBreakAfter(retv)

    def addChunkForBreakBeforeUsingStyle(self, breakStyleYesNo, positionBefore):
        # the tricky part here is when we have the previous item with a forced break AFTER and next item with a forced break BEFORE, we dont want to do it twice
        optionOneColumnBreakTriggersNewPage = True
        #
        newPageLatex = "\\newpage\n"
        clearDoublePageLatex = "\\cleardoublepage\n"
        if (self.getCurrentColumnCount()>1):
            newColumnLatex = "\\columnbreak\n"
        else:
            # there is only one column, should we break page or do nothing?
            if (optionOneColumnBreakTriggersNewPage):
                newColumnLatex = newPageLatex
            else:
                newColumnLatex = "\n"
        #
        if (breakStyleYesNo == "no"):
            return False
        elif (breakStyleYesNo == "yes"):
            if (not self.getLastEntryHadPageBreakAfter()) or (not positionBefore):
                # do we want to turn off any "continued on the next page" stuff when we have a manual break? this only works if we are not using the environment-based style (otherwise we would not have matching begin end)
                if (DefExtraBreakWarnSecEnd):
                    # i don't think it's very important
                    self.chunks.append(self.breakWarnSecEnd())
                #
                text = newPageLatex
                self.chunks.append(text)
            return True
        elif (breakStyleYesNo == "column"):
            if (not self.getLastEntryHadPageBreakAfter()) or (not positionBefore):
                # do we want to turn off any "continued on the next page" stuff when we have a manual break? this only works if we are not using the environment-based style (otherwise we would not have matching begin end)
                if (DefExtraBreakWarnSecEnd):
                    # i don't think it's very important
                    self.chunks.append(self.breakWarnSecEnd())
                #
                text = newColumnLatex
                self.chunks.append(text)
            return True
        elif (breakStyleYesNo == "facing"):
            # do we want to turn off any "continued on the next page" stuff when we have a manual break? this only works if we are not using the environment-based style (otherwise we would not have matching begin end)
            if (DefExtraBreakWarnSecEnd):
                # i don't think it's very important
                self.chunks.append(self.breakWarnSecEnd())
            #
            # here we want at least one newpage but maybe two to get on padd page
            if (not self.getLastEntryHadPageBreakAfter()) or (not positionBefore):
                text = newPageLatex
                self.chunks.append(text)
            text = clearDoublePageLatex
            self.chunks.append(text)
            return True
        else:
            raise makeJriException("Internal Render Error: Uknnown breakstyle in addChunkForBreakBeforeUsingStyle: {}".format(breakStyleYesNo), None)


    def calcBreakForSectionOrLead(self, item, parentSection, positionBefore):
        # from "yes", "no", "facing"
        isLead = isinstance(item, CbRenderLead)
        #
        if (isLead):
            breakStyle = item.calcLeadBreak()
        else:
            breakStyle = item.calcSectionBreak()
        #
        if (positionBefore):
            if (breakStyle in ["column"]):
                return "column"
            elif (breakStyle in ["before", "solo"]):
                return "yes"
            elif (breakStyle in ["beforeFacing", "soloFacing"]):
                return "facing"
            return "no"
        #
        if (breakStyle in ["after", "solo", "soloFacing"]):
            return "yes"
        elif (breakStyle in ["afterFacing", "soloAfterFacing"]):
            return "facing"
        return "no"




    def calcInlinedFromLatex(self, label, leadp):
        # now the REFERENCE to the original lead
        returnRid = leadp.getRid()
        returnLeadId = leadp.getLabelIdPreferAutoId()

        if (label is not None) and (label.startswith(returnLeadId)):
            # in this case the label is ALREADY what we would use as return text so we don't need to repeat
            pageNumberStyle = "page"
            returnTextLatex = makeLatexLinkToRid(returnRid, "", pageNumberStyle)
            fromLatex = "{}".format(returnTextLatex)
        else:
            pageNumberStyle = "onpage"
            returnTextLatex = makeLatexLinkToRid(returnRid, returnLeadId, pageNumberStyle)
            fromLatex = "{}".format(returnTextLatex)
        #
        return fromLatex






    def addChunkToSetCurrentColumnCount(self, item, parentSection):
        columnCount = self.calcColumnCountForSectionOrLead(item, parentSection)
        self.addChunkToSetCurrentColumnCountTo(columnCount)
    
    def addChunkToSetCurrentColumnCountTo(self, newColumnCount):
        currentColumnCount = self.getCurrentColumnCount()
        if (currentColumnCount == newColumnCount):
            # nothing to do already at this column count
            return
        # change it
        if (currentColumnCount>1):
            # we need to END our current multicol
            # do we want to turn off any "continued on the next page" stuff when we have a manual break? this only works if we are not using the environment-based style (otherwise we would not have matching begin end)
            if (DefExtraBreakWarnSecEnd):
                # i don't think it's very important
                self.chunks.append(self.breakWarnSecEnd())
            text = "\\end{multicols*}\n"
            self.chunks.append(text)
        if (newColumnCount>1):
            # start new
            text = "\\begin{multicols*}{" + str(newColumnCount) + "}\n"
            self.chunks.append(text)
        # remember
        self.setCurrentColumnCount(newColumnCount)






    def calcColumnCountForSectionOrLead(self, item, parentSection):
        isLead = isinstance(item, CbRenderLead)
        #
        if (isLead):
            columnCount = item.calcLeadColumns()
        else:
            columnCount = item.calcSectionColumns()
        #
        if (columnCount is None):
            # this should not happen as we should top out at renderdoc with defaults
            raise makeJriException("Internal Render Error: Could not find columnCount value up render hiearachy.", None)
        return columnCount














































    def loadFileFromLatexDir(self, fname):
        sourcePath = os.path.dirname(__file__)
        fullPath = sourcePath + "/latexCode/" + fname
        text = jrfuncs.loadTxtFromFile(fullPath, True, encoding="utf-8")
        return text


    def generateDocumentStart(self, env):
        self.generateDocumentStartDocClass(env)
        self.generateDocumentStartPreambles(env)
        self.generateDocumentStartMetaInfo(env)
        self.generateDocumentStartBeginDoc(env)














    def generateDocumentStartDocClass(self, env):
        # ATTN: get this from settings

        # options
        doubledSided = self.getOption("doubleSided", False)
        latexPaperSize = self.getOption("latexPaperSize", None)
        latexFontSize = self.getOption("latexFontSize", None)

        # extra options?
        extra = ""

        # latex stuff
        if (doubledSided):
            sidedLatex = "twoside=semi"
        else:
            sidedLatex = "oneside"


        # document class; sets:
        #  whether it is double sided (page numbers alternate sides) or not (always in same corner)
        #  the base font size (in points)
        #  the paper size ["letter", "A4", "A5", etc.]
        # for KOMA script, the DIV value is: DIV=15 means that the page height is divided into 15 units. The top margin is one unit, the bottom gets two units and the remaining units go to the text height
        text = self.makeLatexBoldCommentBlock("START OF CASEBOOK LATEX - DOCUMENT CLASS SETUP")
        self.chunks.append(text)

        text = r"\documentclass[" + sidedLatex + ", openany, " + str(latexFontSize) + "pt, paper=" + latexPaperSize +", DIV=15" + extra + "]{scrbook}%" + "\n"
        #
        if (self.isNarrowPaperSize()):
            # narrow margins
            text += r"\def\mygeometryMargin{1.25cm}" + "\n"
            text += r"\def\mygeometryBottom{1.75cm}" + "\n"
        else:
            # normal margins
            text += r"\def\mygeometryMargin{2cm}" + "\n"
            text += r"\def\mygeometryBottom{2.5cm}" + "\n"
        #
        self.chunks.append(text)
        #
        text = self.makeLatexBoldCommentBlock("END OF CASEBOOK LATEX - DOCUMENT CLASS SETUP")
        self.chunks.append(text)


















    def generateDocumentStartPreambles(self, env):
        # include preamble files
        preambleList = ["Packages", "Main", "News", "Fingerprint", "Effects", "Forms"]
        if (self.getOption("autoStyleQuotes", False)):
            preambleList.append("AutoQuotesOn")
        else:
            preambleList.append("AutoQuotesOff")
        #
        for preamble in preambleList:
            fname = "casebookPreamble{}.latex".format(preamble)
            text = self.loadFileFromLatexDir(fname)
            startLine = self.makeLatexBoldCommentBlock("START of CASEBOOK LATEX PREAMBLE: {}".format(preamble))
            endLine = self.makeLatexBoldCommentBlock("END of CASEBOOK LATEX PREAMBLE: {}".format(preamble))
            self.chunks.append(startLine + text + endLine)
    

        # custom preambles
        text = self.makeLatexBoldCommentBlock("START OF CASEBOOK LATEX PREAMBLE - LATE DYNAMIC")
        self.chunks.append(text)
        for latexAdd in self.latexAdds:
            self.chunks.append(latexAdd)
        text = self.makeLatexBoldCommentBlock("END OF CASEBOOK LATEX PREAMBLE - LATE DYNAMIC")
        self.chunks.append(text)




    def makeLatexBoldCommentBlock(self, text):
        blockText = "\n\n\n\n" + "% ----------------------------------------------\n" + "% " + text + "\n" + "% ----------------------------------------------\n\n\n\n"
        return blockText

    def addToPreambleLatex(self, latex):
        self.latexAdds.append(latex)





    def generateDocumentStartMetaInfo(self, env):
        info = env.getEnvValueUnwrapped(None, "info", None)
        if (info is None):
            raise self.makeRenderException(None, "Could not find 'info' object for game to retrieve author, etc.")
        #
        titleStr = getUnsafeDictValueAsString(env, info, "title", "n/a")
        authorsStr = getUnsafeDictValueAsString(env, info, "authors", "n/a")
        versionStr = getUnsafeDictValueAsString(env, info, "version", "n/a")
        dateStr =  getUnsafeDictValueAsString(env, info, "versionDate", "n/a")
        keywordsStr =  getUnsafeDictValueAsString(env, info, "keywords", "")
        if (keywordsStr!=""):
            keywordsStr = "casebook, " + keywordsStr
        else:
            keywordsStr = "casebook"
        #
        # see https://www.karlrupp.net/2016/01/pdf-metadata-in-latex-documents/
        #
        text = self.makeLatexBoldCommentBlock("START OF CASEBOOK LATEX PREAMBLE - DOCUMENT INFO")
        self.chunks.append(text)

        text = "\n"
        text += "% embed info into generated pdf\n"
        text += "\\hypersetup{\n"
        text += "pdfauthor={{{}}},\n".format(authorsStr)
        text += "pdftitle={{{}}},\n".format(titleStr)
        text += "pdfsubject={{New York Noir - {} v{}}},\n".format(titleStr, versionStr)
        #text += "\\pdfdate={{{}}},\n".format(dateStr)
        text += "pdfkeywords={{{}}},\n".format(keywordsStr)
        text += "}\n"
        text += "\\date{{{}}}\n".format(dateStr)

        # add text
        self.chunks.append(text)

        text = self.makeLatexBoldCommentBlock("END OF CASEBOOK LATEX PREAMBLE - DOCUMENT INFO")
        self.chunks.append(text)










    def generateDocumentStartBeginDoc(self, env):
        # start doc

        text = self.makeLatexBoldCommentBlock("START OF CASEBOOK LATEX - DOCUMENT START")
        self.chunks.append(text)

        text = self.loadFileFromLatexDir("casebookDocStart.latex")
        self.chunks.append(text)

        text = self.makeLatexBoldCommentBlock("END OF CASEBOOK LATEX - DOCUMENT START")
        self.chunks.append(text)











    def generateDocumentEnd(self, env):
        buildStr = convertEscapeUnsafePlainTextToLatex(env.getBuildString())
        typesetStr = convertEscapeUnsafePlainTextToLatex(env.getTypesetString(False))
        currentDateStr = convertEscapeUnsafePlainTextToLatex(jrfuncs.getNiceCurrentDateTime())

        text = self.makeLatexBoldCommentBlock("START OF CASEBOOK LATEX - DOCUMENT END")
        self.chunks.append(text)

        text = "\n\\end{{document}}\n\n% Generated by casebook tool {} [{}] on {}\n".format(buildStr, typesetStr, currentDateStr)
        # add text
        self.chunks.append(text)

        text = self.makeLatexBoldCommentBlock("END OF CASEBOOK LATEX - DOCUMENT END")
        self.chunks.append(text)





    def defineFont(self, id, path, size, scale, color, hyphenate, monoSpace, ignoreDupe, env, astloc):
        optionTexLigatures = False
        #
        if (id in self.fontDictionary):
            if (ignoreDupe):
                # do nothing one already exists with this id
                return
            raise makeJriException("Font with that id ({}) has already been defined (use defineFont with ignoreDupe=true to bypass error).".format(id), astloc)
        #
        safeId = convertIdToSafeLatexId(id)

        # find the known font reject if not known
        [fontPath, warningText] = env.locateManagerFileWithUseNote(env.calcManagerIdListFont(), path, "Font", "font", None, env, astloc, False)
    
        # split off filename from path
        [dirPath, fileName] = jrfuncs.splitFilePathToPathAndFile(fontPath)

        # path needs to end in /
        safePath = makeLatexSafeFilePath(dirPath)
        safeFontName = fileName
        fontCommand = "\\cbFont" + safeId
        #
        features = {"Path": safePath}

        if (monoSpace):
            # some of these are overridden below by other options
            features["Scale"] = "MatchLowercase"
            features["Ligatures"]="NoCommon"
            features["CharacterVariant"]="0"

        if (optionTexLigatures):
            features["Ligatures"]="TeX"
        if (scale is not None):
            features["Scale"] = str(scale)
        if (color is not None):
            features["Color"] = convertEscapeUnsafePlainTextToLatex(color)

        #
        latex = "\\newfontfamily{" + fontCommand + "}{" + safeFontName + "}[" + jrfuncs.dictToCommaString(features) + "]\n"
        self.addToPreambleLatex(latex)
        self.fontDictionary[id] = {"command": fontCommand, "size": size, "scale": scale, "color": color, "hyphenate": hyphenate, "monoSpace": monoSpace}



    def setFontWithSize(self, id, sizeMod, env, astloc):
        optionSoulColorUnderline = True
        optionThickUnderline = True
        optionShallowUnderlineDepth = True
        #
        if (id is None) and (sizeMod is None):
            raise makeJriException("No font id or size specified; use $defineFont() to add fonts.", astloc)
        if (id is None):
            # dont change font (just size)
            font = None
            fontSize = convertEscapeUnsafePlainTextToLatex(sizeMod)
            latex = ""
        else:
            if (id not in self.fontDictionary):
                raise makeJriException("No font with that id has been defined; use $defineFont() to add fonts.", astloc)
            font = self.fontDictionary[id]
            safeId = convertIdToSafeLatexId(id)
            fontCommand = "\\cbFont" + safeId
            fontSize = jrfuncs.getDictValueOrDefault(font, "size", None)
            monoSpace = jrfuncs.getDictValueOrDefault(font, "monoSpace", False)
            latex = fontCommand
            if (not font["hyphenate"]):
                latex += " \\hyphenpenalty=10000 \\exhyphenpenalty=10000 "
            color = jrfuncs.getDictValueOrDefault(font, "color", None)
            if (color is not None):
                # set explicit colors for underline, strikethrough, etc. assuming we are using soul pacakge
                if (optionSoulColorUnderline):
                    latex += "\\setulcolor{" + color + "}\\setstcolor{" + color + "}\\sethlcolor{" + color + "}"
            if (optionThickUnderline):
                latex += "\\setul{}{.2ex}"
            if (optionShallowUnderlineDepth):
                latex += "\\setuldepth{abc}"
            if (monoSpace):
                # ATTN: Unfinished
                pass

        # size modifier?
        #finalSizeLatex = calcLatexSizeKeywordFromBaseAndMod(fontSize, sizeMod, env, astloc)
        finalSizeLatex = parseFontSizeStringToLatexCommand(fontSize, True, astloc)
        latex += finalSizeLatex

        return latex


    def getFontDict(self, id, env, astloc):
        if (id not in self.fontDictionary):
            raise makeJriException("No font with that id has been defined; use $defineFont() to add fonts.", astloc)
        return self.fontDictionary[id]



    def setDividerCommand(self, id, command):
        self.dividers[id] = command
    #
    def generateLatexForDivider(self, id, astloc):
        if (id=="none"):
            return ""
        if (id not in self.dividers):
            raise makeJriException("No divider with that id has been defined; id should be from [{}] or user defined with $configureDivider().".format(self.dividers.keys()), astloc)
        return "\\" + self.dividers[id]
